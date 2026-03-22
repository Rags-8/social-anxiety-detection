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
            "Practice the 4-7-8 breathing technique: breathe in for 4s, hold for 7s, exhale for 8s.",
            "Try the 5-4-3-2-1 grounding exercise to return your focus to the present space.",
            "Step away to a quiet space and allow yourself a moment to recalibrate.",
            "Listen to a calming playlist or ambient nature sounds.",
            "Splash cold water on your face to help reset your nervous system.",
            "Write down your overwhelming thoughts in a 'brain dump' to clear your mind.",
            "Use a weighted blanket or a firm hug to feel more secure and grounded.",
            "Focus on a single, repetitive task like folding laundry or sorting items.",
            "Gently stretch your neck and shoulders to release accumulated tension.",
            "Remind yourself with an affirmation: 'This feeling is temporary and I am safe.'",
            "Try progressive muscle relaxation: tense and then release each muscle group.",
            "Limit sensory input by dimming the lights or using noise-canceling headphones.",
            "Sip on some warm, caffeine-free herbal tea like chamomile or peppermint.",
            "Reach out to a trusted friend or family member just to hear a familiar voice.",
            "Engage in a quick, high-intensity movement like jumping jacks to burn off excess energy.",
            "Focus on an Object: Describe a nearby object in extreme detail to yourself.",
            "Change your environment: if you're inside, step outside for just one minute.",
            "Practice box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s."
        ],
        'Moderate Anxiety': [
            "Take three slow, deep breaths, focusing specifically on the exhale.",
            "Acknowledge your uneasy feelings without self-judgment; they will pass.",
            "Break your current stressful situation down into one small, manageable step.",
            "Go for a 10-minute brisk walk to change your perspective and move your body.",
            "Organize your immediate workspace to create a sense of order and control.",
            "Listen to an uplifting podcast or a favorite upbeat song.",
            "Practice mindful observation: pick one thing in your view and notice its colors.",
            "Check your posture—straightening your spine can often improve your mood.",
            "Hydrate yourself with a full glass of cool water.",
            "Write a quick to-do list for tomorrow to get worries out of your head.",
            "Spend five minutes engaging with a pet or looking at photos of nature.",
            "Identify one thing you can control in this moment and focus on that.",
            "Try a quick creative outlet: doodle, hum, or write a single sentence.",
            "Visualize a 'peaceful place' where you feel completely at ease.",
            "Set a 5-minute timer and dedicate it solely to a relaxing activity.",
            "Practice 'half-smiling': slightly upturn your lips to relax your facial muscles."
        ],
        'Low Anxiety': [
            "Keep leveraging the positive coping strategies that brought you this peace today.",
            "Consider jotting down what's working well for you in a journal right now.",
            "Stay actively engaged and fully present in what you are current doing.",
            "Practice a moment of gratitude: name three things you are thankful for today.",
            "Plan a small reward for yourself later to celebrate your balanced state.",
            "Engage in a hobby that makes you feel competent and happy.",
            "Offer a kind word or small gesture of help to someone else.",
            "Try learning one new small fact or skill today to keep your mind growing.",
            "Perform a quick sun salutation or light yoga stretch to maintain your flow.",
            "Reflect on a recent success, no matter how small it might seem.",
            "Spend time in nature or simply sit by a window to soak in the light.",
            "Call someone you haven't spoken to in a while just to say hello.",
            "Prepare a healthy, nourishing meal for yourself.",
            "Take a moment to simply 'be' without checking your phone or a screen.",
            "Document this feeling of peace so you can remind yourself of it later."
        ],
        'Uncertain': [
            "Try to reflect on how you're feeling and describe it in a few more words.",
            "Take a moment to relax, breathe deeply, and center yourself.",
            "Write your thoughts down as they come; clarity often follows expression.",
            "Talk to someone you trust about how you're feeling right now.",
            "Close your eyes for 30 seconds and just focus on the sound of your breath.",
            "Consider if there was a specific trigger for your current feeling."
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
