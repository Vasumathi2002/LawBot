# LawBot
Demo : https://drive.google.com/file/d/1oxudknzPrwmtIPhfD0SlzmlqOkV8CWKL/view?usp=sharing
🔍 OVERVIEW

This project collects district-level citizen feedback about justice, administration, and local governance, performs sentiment and NLP-based scoring, stores it in a MySQL database, and visualizes it through Flask-powered dashboards using Plotly, Seaborn, and WordCloud.

It integrates Natural Language Processing (TextBlob, Google Translate) for multilingual text analysis, Flask APIs for chatbot interaction, and Power BI-like visualizations for data-driven decision-making.

⚙️ SYSTEM COMPONENTS & WORKFLOW
1️⃣ Frontend (Flask Web App)

The system starts with a web form where users select their district.

Users chat with an interactive justice feedback bot that asks structured questions (e.g., trust, fairness, corruption, accessibility).

Responses are analyzed in real-time.

Files involved:

project.py → Justice System Feedback Chatbot

app.py → District Administration & Justice Feedback Chatbot

templates/index.html → Chat interface (Flask-rendered)

2️⃣ Backend (Flask APIs + NLP Engine)

Both project.py and app.py are Flask servers that handle real-time chat sessions:

🔹 Text Preprocessing & Translation

Uses Google Translator API to detect and translate user messages to English for NLP.

Supports feedback in multiple Indian languages (Tamil, Hindi, etc.).

🔹 NLP & Scoring

Uses TextBlob for sentiment polarity (positive, neutral, negative).

Custom keyword matching improves category-wise scores (trust, responsiveness, corruption, etc.).

Converts qualitative answers into numeric scores (1–5) for analytics.

🔹 Data Storage

Feedback responses are inserted into MySQL tables:

justice_feedback (justice-related)

district_feedback (district-level)

Each entry includes:

District name

Multiple score fields

Overall & sentiment score

Suggestions text

3️⃣ Visualization & Dashboard Layer

Managed by powerbiapp.py.

📊 Dashboard Features:

Pulls feedback from MySQL using pandas.read_sql().

Renders analytical visuals via Plotly, Matplotlib, and Seaborn.

Generates:

Pie chart → Sentiment breakdown

Radar chart → District-wise comparison

Bar chart → Trust & Justice Index

Line chart → Sentiment trends

Word Cloud → Most frequent citizen suggestions

Heatmap → Correlation matrix between justice metrics

Scatter plot → Sentiment vs Trust

“Justice Index” → Weighted average (Trust: 40%, Responsiveness: 30%, Community: 30%)

🌐 Routes:

/ → Main dashboard (all districts)

/<district> → Filter dashboard for one district

/tamil_heatmap → District heatmap (uses india-districts-727.json for mapping)

4️⃣ Data API Layer

File: load_data.py

Provides lightweight JSON endpoints for front-end or Power BI connectors:

/counts → Returns district-wise feedback counts/average values from MySQL.

Uses CORS so JavaScript or BI tools can fetch data from localhost safely.

5️⃣ Chatbot Training (Optional Module)

File: nlp_analysis.py

Trains a basic ChatterBot using predefined conversations.

Enables local chatbot interaction for AI testing before web integration.

🧩 DATABASE SCHEMA
Table: justice_feedback
Field	Type	Description
id	INT	Primary key
district	VARCHAR	District name
trust_score	FLOAT	Citizen trust level
responsiveness_score	FLOAT	Government service response
fairness_score	FLOAT	Legal fairness perception
accessibility_score	FLOAT	Accessibility to justice services
corruption_score	FLOAT	Corruption level indicator
community_justice_score	FLOAT	Local resolution fairness
suggestions	TEXT	Citizen’s improvement suggestions
justice_sentiment	VARCHAR	Sentiment (positive/neutral/negative)
overall_score	FLOAT	Average sentiment score
🧮 EVALUATION METRICS
Metric	Description
Polarity Score	Derived from TextBlob sentiment polarity
Keyword Score	Based on presence of key thematic words
Justice Index	Weighted index combining key justice indicators
Overall Score	Average across multiple category scores
Sentiment Distribution	% Positive, Neutral, Negative feedback
💡 HOW THE DASHBOARD WORKS

Data Ingestion: User feedback stored in MySQL.

Data Fetching: Flask dashboard fetches via SQL queries.

Data Processing: Python libraries (pandas, numpy) clean & transform data.

Visualization: Plotly and Matplotlib generate live interactive charts.

Display: Dashboard HTML templates render visuals dynamically in browser.

Optional Mapping: GeoJSON (india-districts-727.json) creates district heatmaps.

🔗 APIs / External Libraries Used
Library	Purpose
Flask	Backend web framework
MySQL Connector	Database integration
TextBlob	Sentiment analysis
Googletrans	Language detection & translation
Plotly / Seaborn / Matplotlib	Visualization
WordCloud	Suggestion keyword visualization
Pandas / Numpy	Data manipulation
CORS	Secure cross-origin API calls
🎯 OUTCOME

✅ Citizens can share justice-related feedback interactively.
✅ The system automatically quantifies qualitative text.
✅ District administrators can monitor justice perception through dashboards.
✅ The Justice Index helps compare fairness & responsiveness across districts.
✅ Power BI–style analytics (via Plotly) allows decision-makers to improve governance.
