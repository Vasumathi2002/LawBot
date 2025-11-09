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
CREATE TABLE IF NOT EXISTS district_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(255),
    trust_score INT,
    responsiveness_score INT,
    infrastructure_score INT,
    public_services_score INT,
    safety_score INT,
    environment_score INT,
    transport_score INT,
    community_score INT,
    economic_score INT,
    sentiment_score INT,
    justice_score INT,
    justice_sentiment VARCHAR(50),
    overall_score FLOAT
)
""")

# Questions
district_questions = {
    "trust": "How much do you trust your local administration?",
    "responsiveness": "How responsive are the services in your district?",
    "infrastructure": "What do you think about the infrastructure in your district?",
    "public_services": "How satisfied are you with health, education, and sanitation services?",
    "safety": "Do you feel safe in your district?",
    "environment": "How would you rate the cleanliness and environmental quality of your district?",
    "transport": "How effective is the public transport and road infrastructure?",
    "community": "Are citizens involved in local decisions?",
    "economic": "Are there enough job and business opportunities in your district?"
}

justice_questions = {
    "justice": "How do you think justice can be achieved in your district?",
    "fairness": "Do you think laws are applied fairly in your district?",
    "accessibility": "Are legal and grievance services easily accessible?",
    "corruption": "Have you observed corruption or unfair practices?",
    "community_justice": "Do local communities resolve issues fairly?",
    "justice_suggestions": "What changes would make justice more effective in your district?"
}

keywords_dict = {
    "trust": ["trust", "honest", "transparent", "reliable"],
    "responsiveness": ["fast", "responsive", "quick", "helpful"],
    "infrastructure": ["road", "transport", "building", "infrastructure", "utilities"],
    "public_services": ["health", "education", "hospital", "school", "sanitation"],
    "safety": ["safe", "security", "police", "crime", "danger"],
    "environment": ["clean", "pollution", "green", "environment", "waste"],
    "transport": ["bus", "train", "road", "traffic", "transport"],
    "community": ["community", "participation", "citizen", "involvement"],
    "economic": ["job", "business", "opportunity", "economy", "market"],
    "justice": ["justice", "law", "fair", "rights", "court", "equality"]
}

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
        "district_scores": {k: None for k in district_questions.keys()},
        "justice_scores": {k: None for k in justice_questions.keys()},
        "chat_history": [],
        "user_lang": "en",
        "question_count": 0,
        "max_questions": 5
    }
    return jsonify({"message": f"Hello! Let's start your feedback for {district}.", "session": session_data})

@app.route("/next_question", methods=["POST"])
def next_question():
    data = request.json
    session_data = data["session"]
    last_answer = data.get("answer")
    last_category = data.get("category")

    response_templates = {
        "trust": ["Trust is {sentiment_word}.", "I see that trust is {sentiment_word}."],
        "responsiveness": ["Responsiveness is {sentiment_word}.", "Services responsiveness feels {sentiment_word}."],
        "infrastructure": ["Infrastructure seems {sentiment_word}.", "Noted, infrastructure is {sentiment_word}."],
        "public_services": ["Public services are {sentiment_word}."],
        "safety": ["Safety is {sentiment_word}."],
        "environment": ["Environmental quality is {sentiment_word}."],
        "transport": ["Transport is {sentiment_word}."],
        "community": ["Community participation is {sentiment_word}."],
        "economic": ["Economic opportunities appear {sentiment_word}."],
        "justice": ["Justice seems {sentiment_word}."],
        "fairness": ["Fairness is {sentiment_word}."],
        "accessibility": ["Legal accessibility is {sentiment_word}."],
        "corruption": ["Corruption perception is {sentiment_word}."],
        "community_justice": ["Community justice seems {sentiment_word}."],
        "justice_suggestions": ["Suggestions noted."]
    }

    sentiment_to_word = {"positive": "good", "neutral": "okay", "negative": "poor"}
    bot_reply = ""

    if last_answer and last_category:
        user_text, user_lang = translate_to_english(last_answer)
        session_data["user_lang"] = user_lang
        score = analyze_score(user_text, last_category)
        sentiment = analyze_sentiment(user_text)
        session_data["chat_history"].append(
            {"category": last_category, "answer": last_answer, "score": score, "sentiment": sentiment})

        if last_category in session_data["district_scores"]:
            session_data["district_scores"][last_category] = score
        elif last_category in session_data["justice_scores"]:
            session_data["justice_scores"][last_category] = score

        template_list = response_templates.get(last_category, ["Thanks for your feedback."])
        bot_reply = random.choice(template_list).format(sentiment_word=sentiment_to_word.get(sentiment, "okay"))

    session_data["question_count"] += 1
    max_questions = session_data.get("max_questions", 5)

    if session_data["question_count"] >= max_questions:
        d_scores = [v for v in session_data["district_scores"].values() if v is not None]
        j_scores = [v for v in session_data["justice_scores"].values() if v is not None]
        sentiment_score = round(sum(d_scores)/len(d_scores), 2) if d_scores else 0
        justice_score = round(sum(j_scores)/len(j_scores), 2) if j_scores else 0

        justice_sentiment_counts = {"positive":0,"neutral":0,"negative":0}
        for entry in session_data["chat_history"]:
            if entry["category"] in session_data["justice_scores"]:
                justice_sentiment_counts[entry["sentiment"]] += 1
        justice_sentiment = max(justice_sentiment_counts, key=justice_sentiment_counts.get)
        overall_score = round((sentiment_score + justice_score)/2, 2)

        cursor.execute("""
            INSERT INTO district_feedback (
                district, trust_score, responsiveness_score, infrastructure_score,
                public_services_score, safety_score, environment_score, transport_score,
                community_score, economic_score, sentiment_score, justice_score,
                justice_sentiment, overall_score
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session_data["district"],
            session_data["district_scores"]["trust"],
            session_data["district_scores"]["responsiveness"],
            session_data["district_scores"]["infrastructure"],
            session_data["district_scores"]["public_services"],
            session_data["district_scores"]["safety"],
            session_data["district_scores"]["environment"],
            session_data["district_scores"]["transport"],
            session_data["district_scores"]["community"],
            session_data["district_scores"]["economic"],
            sentiment_score,
            justice_score,
            justice_sentiment,
            overall_score
        ))
        conn.commit()

        return jsonify({"bot_reply": bot_reply, "message":"✅ Feedback session completed.", "done": True})

    if None in session_data["district_scores"].values():
        next_cat = select_next_category(session_data["district_scores"])
        question = district_questions[next_cat]
    elif None in session_data["justice_scores"].values():
        next_cat = select_next_category(session_data["justice_scores"])
        question = justice_questions[next_cat]
    else:
        return jsonify({"bot_reply": bot_reply, "message":"All questions answered.", "done": True})

    question_translated = translate_to_user_language(question, session_data["user_lang"])
    return jsonify({
        "bot_reply": bot_reply,
        "question": question_translated,
        "category": next_cat,
        "session": session_data
    })

if __name__ == "__main__":
    app.run(debug=True)
