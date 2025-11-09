from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from googletrans import Translator
import mysql.connector
import random

app = Flask(__name__)
translator = Translator()

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chatbot_db"
)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS justice_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(255),
    trust_score FLOAT,
    responsiveness_score FLOAT,
    fairness_score FLOAT,
    accessibility_score FLOAT,
    corruption_score FLOAT,
    community_justice_score FLOAT,
    suggestions TEXT,
    justice_sentiment VARCHAR(50),
    overall_score FLOAT
)
""")

# Justice-related questions (10+ for interactive chat)
justice_questions = {
    "trust": "How much do you trust the justice system in your district?",
    "responsiveness": "How responsive are legal and grievance services?",
    "fairness": "Do you think laws are applied fairly in your district?",
    "accessibility": "Are legal services easily accessible to everyone?",
    "corruption": "Have you observed corruption or unfair practices in legal matters?",
    "community_justice": "Do local communities resolve issues fairly?",
    "justice_suggestions": "What changes would make justice more effective in your district?",
    "timely_resolution": "Do cases get resolved in a timely manner?",
    "legal_awareness": "Are citizens aware of their legal rights?",
    "support_services": "Are there enough support services like legal aid and counseling?",
    "police_cooperation": "Do you feel the police cooperate fairly in legal disputes?"
}

# Keywords for scoring
keywords_dict = {
    "trust": ["trust", "honest", "reliable", "transparent"],
    "responsiveness": ["fast", "responsive", "quick", "helpful"],
    "fairness": ["fair", "unfair", "bias", "impartial", "justice"],
    "accessibility": ["access", "reachable", "available", "easy", "helpful"],
    "corruption": ["corrupt", "bribe", "unfair", "illegal", "fraud"],
    "community_justice": ["community", "local", "participation", "resolve", "fair"],
    "timely_resolution": ["timely", "delay", "slow", "efficient", "quick"],
    "legal_awareness": ["aware", "knowledge", "rights", "inform", "understand"],
    "support_services": ["aid", "support", "counsel", "assistance", "help"],
    "police_cooperation": ["police", "cooperate", "helpful", "support"]
}

# References / Suggested Reading
justice_references = [
    {"title": "India Justice Report 2020", "link": "https://indiajusticereport.org/files/IJR_2020_National_Factsheet.pdf"},
    {"title": "India Justice Report 2025", "link": "https://indiajusticereport.org/files/IJR%204_Full%20Report_English_Low.pdf"},
    {"title": "Legal Needs in Rural India: Challenges & Response of Legal Aid", "link": "https://clp.law.harvard.edu/wp-content/uploads/2023/06/Legal-needs-in-Rural-India-conference-paper-Sunil-Chauhan.pdf"},
    {"title": "Access to Justice for Marginalised People in India", "link": "https://mslr.pubpub.org/pub/ii7rd56v"},
    {"title": "A Reality Check on Free Legal Aid in India", "link": "https://ijlr.iledu.in/wp-content/uploads/2025/04/V4I524.pdf"},
    {"title": "Responsible Artificial Intelligence for the Indian Justice System", "link": "https://vidhilegalpolicy.in/wp-content/uploads/2021/04/Responsible-AI-in-the-Indian-Justice-System-A-Strategy-Paper.pdf"}
]

# NLP scoring
def keyword_score(text, category):
    words = text.lower().split()
    matches = sum(word in words for word in keywords_dict.get(category, []))
    return min(matches + 1, 5)

def analyze_score(text, category):
    polarity = TextBlob(text).sentiment.polarity
    if polarity <= -0.6: polarity_score = 1
    elif polarity <= -0.2: polarity_score = 2
    elif polarity <= 0.2: polarity_score = 3
    elif polarity <= 0.6: polarity_score = 4
    else: polarity_score = 5
    k_score = keyword_score(text, category)
    return round((polarity_score + k_score) / 2, 2)

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1: return "positive"
    elif polarity < -0.1: return "negative"
    else: return "neutral"

def select_next_category(scores_dict):
    unanswered = [k for k, v in scores_dict.items() if v is None]
    return random.choice(unanswered) if unanswered else None

# Translation
def translate_to_english(text):
    detected = translator.detect(text)
    if detected.lang != 'en':
        translated = translator.translate(text, src=detected.lang, dest='en')
        return translated.text, detected.lang
    return text, 'en'

def translate_to_user_language(text, lang):
    if lang != 'en':
        translated = translator.translate(text, src='en', dest=lang)
        return translated.text
    return text

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_chat", methods=["POST"])
def start_chat():
    district = request.form.get("district")
    session_data = {
        "district": district,
        "justice_scores": {k: None for k in justice_questions.keys()},
        "trust_responsiveness_scores": {"trust": None, "responsiveness": None},
        "chat_history": [],
        "user_lang": "en"
    }
    first_cat = select_next_category(session_data["justice_scores"])
    question = justice_questions[first_cat]
    return jsonify({
        "message": f"Hello! Let's start your justice feedback for {district}.",
        "question": question,
        "category": first_cat,
        "session": session_data
    })

@app.route("/next_question", methods=["POST"])
def next_question():
    data = request.json
    session_data = data["session"]
    last_answer = data.get("answer")
    last_category = data.get("category")
    bot_reply = ""

    if last_answer and last_category:
        user_text, user_lang = translate_to_english(last_answer)
        session_data["user_lang"] = user_lang
        score = analyze_score(user_text, last_category)
        sentiment = analyze_sentiment(user_text)
        session_data["chat_history"].append({
            "category": last_category,
            "answer": last_answer,
            "score": score,
            "sentiment": sentiment
        })

        session_data["justice_scores"][last_category] = score
        if last_category in ["trust", "responsiveness"]:
            session_data["trust_responsiveness_scores"][last_category] = score

        bot_reply = f"Your input for {last_category} seems {sentiment}."

    # Select next question
    if None in session_data["justice_scores"].values():
        next_cat = select_next_category(session_data["justice_scores"])
        question = justice_questions[next_cat]
    else:
        # Calculate scores
        trust_score = session_data["trust_responsiveness_scores"]["trust"]
        responsiveness_score = session_data["trust_responsiveness_scores"]["responsiveness"]
        j_scores = [v for k,v in session_data["justice_scores"].items() if k not in ["trust", "responsiveness", "justice_suggestions"]]
        fairness_score = session_data["justice_scores"].get("fairness",0)
        accessibility_score = session_data["justice_scores"].get("accessibility",0)
        corruption_score = session_data["justice_scores"].get("corruption",0)
        community_score = session_data["justice_scores"].get("community_justice",0)

        overall_score = round(sum([v for v in [trust_score,responsiveness_score]+j_scores if v is not None])/len([v for v in [trust_score,responsiveness_score]+j_scores if v is not None]),2)

        suggestions = ""
        for entry in session_data["chat_history"]:
            if entry["category"]=="justice_suggestions":
                suggestions = entry["answer"]

        # Save to DB
        cursor.execute("""
            INSERT INTO justice_feedback (
                district, trust_score, responsiveness_score, fairness_score,
                accessibility_score, corruption_score, community_justice_score,
                suggestions, justice_sentiment, overall_score
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session_data["district"], trust_score, responsiveness_score, fairness_score,
            accessibility_score, corruption_score, community_score,
            suggestions, "N/A", overall_score
        ))
        conn.commit()

        return jsonify({
            "bot_reply": bot_reply,
            "message": "✅ Justice feedback session completed.",
            "done": True,
            "references": justice_references
        })

    question_translated = translate_to_user_language(question, session_data["user_lang"])
    return jsonify({
        "bot_reply": bot_reply,
        "question": question_translated,
        "category": next_cat,
        "session": session_data
    })

if __name__ == "__main__":
    app.run(debug=True)
