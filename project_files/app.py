import streamlit as st
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

nltk.download('stopwords')
nltk.download('wordnet')

# Load model and vectorizer
model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

anxiety_keywords = [
    "nervous", "anxious", "panic", "scared",
    "afraid", "shy", "fear", "embarrassed",
    "public", "people", "talk", "speak"
]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

def sentiment_score(text):
    return TextBlob(text).sentiment.polarity

def predict_social_anxiety(text):
    cleaned = clean_text(text)
    vector = vectorizer.transform([cleaned])
    ml_pred = model.predict(vector)[0]

    sentiment = sentiment_score(text)
    keyword_hits = sum(1 for w in anxiety_keywords if w in text.lower())

    if ml_pred == 2 or (sentiment < -0.4 and keyword_hits >= 2):
        return "High Social Anxiety Risk"
    elif ml_pred == 1 or (sentiment < -0.1 and keyword_hits >= 1):
        return "Moderate Social Anxiety Risk"
    else:
        return "Low Social Anxiety Risk"

def get_suggestions(risk):
    if risk == "High Social Anxiety Risk":
        return [
            "🌱 Practice slow breathing for 5 minutes.",
            "📝 Write down your anxious thoughts.",
            "🤝 Talk to someone you trust.",
            "🧑‍⚕️ Consider professional help if needed."
        ]
    elif risk == "Moderate Social Anxiety Risk":
        return [
            "🙂 Use positive self-talk.",
            "🎧 Listen to calming music.",
            "📆 Prepare before social situations.",
            "🧘 Try short relaxation techniques."
        ]
    else:
        return [
            "✅ You appear emotionally stable.",
            "💪 Maintain healthy social habits.",
            "🌼 Continue self-care routines."
        ]

# ---------------- UI ----------------
st.title("Social Anxiety Detection using AI")
st.write("Enter a message to analyze social anxiety level")

user_input = st.text_area("Your message")

if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("Please enter some text")
    else:
        risk = predict_social_anxiety(user_input)
        st.success(risk)

        st.subheader("Suggestions")
        for s in get_suggestions(risk):
            st.write("•", s)

        st.info("⚠️ Educational purpose only. Not a medical diagnosis.")
