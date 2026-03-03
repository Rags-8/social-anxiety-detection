import pickle
import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

# Load artifacts
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "anxiety_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "vectorizer.pkl")

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("Model and Vectorizer loaded successfully.")
except FileNotFoundError:
    print("Error: Model artifacts not found. Please train the model first.")
    model = None
    vectorizer = None

# Initialize NLTK
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

def is_gibberish(text):
    if not text or len(text) < 3:
        return False
    
    # Check for nonsense word patterns
    words = text.split()
    for word in words:
        # Check for long words
        if len(word) > 12:
            vowels = re.findall(r'[aeiouAEIOU]', word)
            # Long words with very few vowels
            if not vowels or len(vowels) / len(word) < 0.20:
                return True
            # Long words with TOO many vowels (nonsense like "aogiehskldiou...")
            if len(vowels) / len(word) > 0.40 and len(word) > 15:
                # If it's very long and almost half vowels, and doesn't look like common long words
                return True
                
        # Check for repeated characters (e.g., "aaaaa")
        if re.search(r'(.)\1{4,}', word):
            return True
            
        # Check for 5+ consecutive vowels or 5+ consecutive consonants
        if re.search(r'[aeiouAEIOU]{5,}', word) or re.search(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{5,}', word):
            if word.lower() not in ["strength", "lengths"]: # Common English words with many consonants
                return True
            
    # Check for random keyboard mashing (high consonant density)
    if len(text) > 10:
        consonants = re.findall(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]', text)
        vowels = re.findall(r'[aeiouAEIOU]', text)
        if not vowels:
            return True
        if len(consonants) / len(text) > 0.85:
            return True
            
    return False

def get_suggestions(level):
    if level == "Low":
        return [
            "You're doing okay! Keep focusing on your strengths.",
            "Try a quick 2-minute mindfulness exercise.",
            "Reframe any minor negative thoughts into positive ones."
        ]
    elif level == "Moderate":
        return [
            "Practice deep breathing: Inhale for 4s, hold for 7s, exhale for 8s.",
            "Take a short break and step away from the stressor.",
            "Write down your worries to get them out of your head."
        ]
    elif level == "High":
        return [
            "Ground yourself: Name 5 things you see, 4 you feel, 3 you hear.",
            "Reach out to a trusted friend or family member.",
            "Consider speaking with a mental health professional if this persists.",
            "Remember: This feeling is temporary and will pass."
        ]
    elif level == "Uncertain":
        return [
            "I'm not exactly sure what you mean — could you try explaining how you're feeling in a different way?",
            "I want to make sure I understand you correctly. Could you share more about your emotions?",
            "If you're just typing to test me, that's okay too! But I'm here if you need real support."
        ]
    return []

def analyze_anxiety(text):
    if not model or not vectorizer:
        return None

    # Gibberish check
    if is_gibberish(text):
        return {
            "anxiety_level": "Uncertain",
            "sentiment_score": 0.0,
            "suggestions": get_suggestions("Uncertain"),
            "confidence": 0.0,
            "probabilities": [0.0, 0.0, 0.0]
        }

    cleaned = clean_text(text)

    # Guard: if cleaned text is empty (e.g. user typed only numbers/symbols)
    if not cleaned.strip():
        return {
            "anxiety_level": "Uncertain",
            "sentiment_score": 0.0,
            "suggestions": get_suggestions("Uncertain"),
            "confidence": 0.0,
            "probabilities": [0.0, 0.0, 0.0]
        }

    features = vectorizer.transform([cleaned])

    # Predict
    prediction_idx = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))

    levels = {0: "Low", 1: "Moderate", 2: "High"}

    # Confidence threshold: if model is not confident, say "Uncertain"
    if confidence < 0.45:
        anxiety_level = "Uncertain"
    else:
        anxiety_level = levels.get(prediction_idx, "Uncertain")

    # Sentiment
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity

    suggestions = get_suggestions(anxiety_level)

    return {
        "anxiety_level": anxiety_level,
        "sentiment_score": sentiment_score,
        "suggestions": suggestions,
        "confidence": confidence,
        "probabilities": probabilities.tolist()
    }
