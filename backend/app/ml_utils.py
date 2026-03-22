import os
import re
import pickle
import random
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Specific imports deferred to avoid startup latency
# import nltk, sklearn etc. are handled inside initialize_nltk and get_model

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Lazy-load artifacts
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "nlp_anxiety_model_v6.pkl")

_model = None
lemmatizer = None
stop_words = None

def initialize_nltk():
    """Download NLTK data if not already present."""
    global lemmatizer, stop_words
    try:
        import nltk
        from nltk.corpus import stopwords as nltk_stopwords
        from nltk.stem import WordNetLemmatizer
        
        try:
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            
        lemmatizer = WordNetLemmatizer()
        stop_words = set(nltk_stopwords.words('english'))
        return True
    except Exception as e:
        print(f"Error initializing NLTK: {e}")
        return False

def get_model():
    """Lazy-load the ensemble model."""
    global _model
    if _model is None:
        initialize_nltk()
        if os.path.exists(MODEL_PATH):
            print(f"Loading pipeline from {MODEL_PATH}...")
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
            print("Ensemble pipeline loaded successfully.")
        else:
            print(f"Warning: Model not found at {MODEL_PATH}")
    return _model

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Standard cleaning aligned with V3 training script
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = text.split()
    
    # Use initialized NLTK components
    if stop_words and lemmatizer:
        tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 1]
    
    text = ' '.join(tokens)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_risk_phrases(text):
    text_lower = text.lower()
    # Expanded V3 Risks
    RISK_PATTERNS = [
        r"kill myself", r"suicide", r"end my life", r"end it all", r"self harm",
        r"want to die", r"commit suicide", r"hurt myself", r"taking my life",
        r"no reason to live", r"carbon monoxide", r"overdose", r"cut my wrist",
        r"goodbye world", r"last note"
    ]
    detected = []
    for phrase in RISK_PATTERNS:
        if re.search(phrase, text_lower):
            detected.append(phrase)
    return detected

def calculate_severity_score(confidence, label_idx, detected_risks):
    """
    Computes a 0-100 severity score based on ML output and detected signals.
    """
    base_scores = {0: 10, 1: 45, 2: 75}
    score = base_scores.get(label_idx, 0)
    score += (confidence * 15)
    if detected_risks:
        score += 30
    return min(100, int(score))

def get_v3_suggestions(category):
    """
    Randomly select 3 unique suggestions from the specified category pool.
    """
    suggestion_pools = {
        'High Anxiety': [
            "Practice deep breathing exercises",
            "Try a short guided meditation",
            "Step outside for fresh air",
            "Talk to a trusted friend or family member",
            "Write down your thoughts to clear your mind",
            "Take a short break from stressful situations",
            "Listen to calming music",
            "Focus on grounding techniques (5-4-3-2-1 method)",
            "Consider talking to a professional"
        ],
        'Low Anxiety': [
            "Maintain a healthy daily routine",
            "Try light physical activity like walking",
            "Spend time on a hobby you enjoy",
            "Practice gratitude journaling",
            "Take short breaks during the day",
            "Stay connected with friends",
            "Get enough quality sleep",
            "Limit overthinking by focusing on tasks",
            "Listen to relaxing music"
        ],
        'Neutral': [
            "Keep up your positive routine",
            "Stay active and engaged in your work",
            "Spend time with friends or family",
            "Continue learning and growing",
            "Maintain a balanced lifestyle",
            "Take short breaks to refresh your mind"
        ],
        'Uncertain': [
            "Try to reflect on how you're feeling",
            "Take a moment to relax and breathe",
            "Write your thoughts down",
            "Talk to someone about how you feel"
        ]
    }
    
    pool = suggestion_pools.get(category, suggestion_pools['Uncertain'])
    return random.sample(pool, min(len(pool), 3))

def analyze_anxiety(text: str, history: list = None):
    """
    Advanced AI Analysis Logic with Slang Handling, Dynamic Suggestions, and Timestamps.
    """
    model = get_model()
    if not model:
        return None

    # STEP 2: Handle real-world language (Slang Mapping)
    slang_map = {
        "idk": "I don't know",
        "kinda": "kind of",
        "lowkey": "slightly"
    }
    processed_text = text.lower()
    for slang, formal in slang_map.items():
        processed_text = re.sub(rf'\b{slang}\b', formal, processed_text)

    # STEP 1: Understand
    text_lower = processed_text
    words = text_lower.split()
    is_short = len(words) < 3
    
    # Emotional tone and anxiety signals
    anxiety_signals = ['fear', 'nervous', 'anxious', 'scared', 'judged', 'judge', 'watching', 'uncomfortable', 'crowds', 'crowded', 'panic', 'heart', 'racing', 'shaking', 'social', 'presentation', 'public', 'weird', 'awkward', 'embarrassed', 'sweat', 'overwhelmed']
    positive_signals = ['happy', 'good', 'well', 'relaxed', 'calm', 'fine', 'ok']
    negative_signals = ['sad', 'bad', 'depressed', 'hurt', 'pain', 'stress', 'worried']
    
    has_anxiety = any(re.search(r'\b' + re.escape(s) + r'\b', text_lower) for s in anxiety_signals)
    has_pos = any(re.search(r'\b' + re.escape(s) + r'\b', text_lower) for s in positive_signals)
    has_neg = any(re.search(r'\b' + re.escape(s) + r'\b', text_lower) for s in negative_signals)
    
    # STEP 3 & 4: Detection & Classification
    detected_risks = check_risk_phrases(text)
    
    # ML Prediction (Baseline)
    cleaned = clean_text(text_lower)
    if not cleaned:
        probs = [1.0, 0.0, 0.0] 
    else:
        probs = model.predict_proba([cleaned])[0]
    
    pred_idx = np.argmax(probs)
    conf = float(np.max(probs))
    
    label_map = {0: "Low Anxiety", 1: "Moderate Anxiety", 2: "High Anxiety"}
    prediction = label_map[pred_idx]
    
    reason = "Based on ML Ensemble analysis of textual features and emotional signals."
    follow_up = None

    # Overrides based on new rules
    direct_trigger = any(re.search(r'\b' + re.escape(s) + r'\b', text_lower) for s in ['judged', 'judge', 'watching', 'panic', 'heart', 'racing', 'shaking', 'crowded', 'sweat', 'awkward', 'embarrassed'])
    if direct_trigger:
        prediction = "High Anxiety"
        conf = max(conf, 0.90)
        reason = "Direct physiological or social anxiety triggers detected."

    no_emotion = not (has_anxiety or has_pos or has_neg)
    if no_emotion and not detected_risks and not direct_trigger and pred_idx == 0:
        prediction = "Neutral"
        conf = max(conf, 0.85)
        reason = "Neutral statement with no significant emotional signals detected."

    if detected_risks:
        prediction = "High Anxiety"
        conf = 0.98
        reason = "Critical safety phrases detected requiring immediate attention."

    if has_pos and (has_anxiety or has_neg):
        prediction = "Low Anxiety"
        conf *= 0.8
        reason = "Mixed emotional signals detected; adjusting classification."

    if is_short:
        conf *= 0.7
        reason += " (Confidence reduced due to very short input)"

    if conf < 0.60:
        prediction = "Uncertain"
        follow_up = "Could you tell me more about how you're feeling or the situation you're in?"
        reason = "Insufficient or conflicting signals to provide a certain classification."

    # STEP 5: Dynamic Suggestions
    suggestion_category = prediction
    if prediction == "Moderate Anxiety": suggestion_category = "High Anxiety"
    suggestions = get_v3_suggestions(suggestion_category)

    # STEP 6: Timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Severity and Risk for internal use
    label_idx_map = {"Low Anxiety": 0, "Moderate Anxiety": 1, "High Anxiety": 2, "Neutral": 0, "Uncertain": 1}
    severity = calculate_severity_score(conf, label_idx_map.get(prediction, 1), detected_risks)
    
    if severity > 90: risk_level = "Critical"
    elif severity > 70: risk_level = "High"
    elif severity > 40: risk_level = "Medium"
    else: risk_level = "Low"

    explanation = [f"Input: \"{text}\"", f"Prediction: {prediction}", f"Confidence: {conf*100:.1f}%", f"Reason: {reason}", f"Timestamp: {current_time}"]
    if follow_up:
        explanation.append(f"Follow-up: {follow_up}")

    return {
        "anxiety_level": prediction,
        "confidence": conf,
        "severity_score": severity,
        "risk_level": risk_level,
        "explanation": explanation,
        "suggestions": suggestions,
        "reason": reason,
        "follow_up_question": follow_up,
        "formatted_timestamp": current_time
    }
