from flask import Flask, render_template
import mysql.connector
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import seaborn as sns

app = Flask(__name__)

# ------------------ DB Connection ------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="chatbot_db"
    )

def fetch_feedback():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM justice_feedback", conn)
    conn.close()
    return df


# ------------------ HELPER ------------------
def create_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color="white", colormap='magma').generate(text)
    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def create_corr_heatmap(df):
    plt.figure(figsize=(6, 5))
    sns.heatmap(df.select_dtypes(include=['float','int']).corr(), annot=True, cmap='coolwarm')
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# ----------- MAIN RENDER FUNCTION ----------
def render_dashboard(df):

    if df.empty:
        df = pd.DataFrame(columns=['district','trust_score','responsiveness_score','community_justice_score','suggestions','overall_score'])

    total_feedbacks = len(df)
    avg_sentiment = df['overall_score'].mean() if total_feedbacks>0 else 0
    positive_pct = len(df[df['overall_score']>3]) / total_feedbacks * 100 if total_feedbacks>0 else 0
    avg_trust = df['trust_score'].mean() if 'trust_score' in df else 0
    most_mentioned_district = df['district'].mode()[0] if total_feedbacks>0 else "N/A"
    districts = fetch_feedback()['district'].dropna().unique().tolist()

    df['sentiment']=np.select([(df['overall_score']>=4),(df['overall_score']<=2)],['Positive','Negative'],default='Neutral')
    pie_html = px.pie(df,names='sentiment',title='Sentiment Breakdown',
                     color='sentiment',color_discrete_map={'Positive':'green','Neutral':'yellow','Negative':'red'}).to_html(full_html=False)

    radar_df=df.groupby('district')[['trust_score','responsiveness_score','community_justice_score']].mean().reset_index()
    radar_fig=go.Figure()
    for _,row in radar_df.iterrows():
        radar_fig.add_trace(go.Scatterpolar(r=[row['trust_score'],row['responsiveness_score'],row['community_justice_score']],
                                            theta=['Trust','Responsiveness','Community'],fill='toself',name=row['district']))
    radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,5])),showlegend=True)
    radar_html=radar_fig.to_html(full_html=False)

    bar_html=px.bar(df.groupby('district')[['trust_score']].mean().reset_index(),
                    x='district',y='trust_score',title='Trust Score by District').to_html(full_html=False)

    if 'created_at' in df.columns:
        df['month']=pd.to_datetime(df['created_at']).dt.to_period('M')
        line_html=px.line(df.groupby('month')['overall_score'].mean().reset_index(),
                          x='month',y='overall_score',title='Sentiment Trend Over Time').to_html(full_html=False)
    else:
        line_html="<p>No date field</p>"

    wc_img=create_wordcloud(' '.join(df['suggestions'].dropna().astype(str)))
    corr_img=create_corr_heatmap(df)
    scatter_html=px.scatter(df,x='overall_score',y='trust_score',color='district',title='Sentiment vs Trust').to_html(full_html=False)

    df['justice_index']=0.4*df['trust_score']+0.3*df['responsiveness_score']+0.3*df['community_justice_score']
    index_html=px.bar(df,x='district',y='justice_index',color='justice_index',title='Justice Index by District').to_html(full_html=False)

    return render_template('dashboard.html',
                           total_feedbacks=total_feedbacks,avg_sentiment=avg_sentiment,
                           positive_pct=positive_pct,avg_trust=avg_trust,
                           most_mentioned_district=most_mentioned_district,
                           pie_html=pie_html,radar_html=radar_html,bar_html=bar_html,
                           line_html=line_html,wc_img=wc_img,corr_img=corr_img,
                           scatter_html=scatter_html,index_html=index_html,
                           districts=districts)


# ------------ ROUTES -------------
@app.route('/')
def dashboard():
    df = fetch_feedback()
    return render_dashboard(df)

@app.route("/<district>")
def filter_district(district):
    df = fetch_feedback()
    df2 = df[df['district']==district]
    return render_dashboard(df2)

@app.route("/tamil_heatmap")
def tamil_heatmap():
    df = fetch_feedback()
    counts = df.groupby('district')['overall_score'].mean().to_dict()
    return render_template("tamil_heatmap.html", counts=counts)


if __name__ == '__main__':
    app.run(debug=True)
