import os
import re
import pickle
import random
from dotenv import load_dotenv
# NOTE: Heavy imports (torch, sentence_transformers, textblob, nltk) are intentionally
# deferred to inside functions. This lets uvicorn bind the port INSTANTLY on Render.
# Importing torch/sentence_transformers at module level takes 3-5 min on Render Free tier.

# Use the new google.genai SDK
try:
    from google import genai as google_genai
    from google.genai import types as genai_types
except ImportError:
    google_genai = None
    genai_types = None

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None
if google_genai and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        gemini_client = google_genai.Client(api_key=GEMINI_API_KEY)
        print("Gemini API (google.genai) configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        gemini_client = None
else:
    print("Warning: GEMINI_API_KEY not found or default. Gemini analysis will be skipped.")

# Lazy-load artifacts
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "anxiety_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "vectorizer.pkl")

model = None
vectorizer = None
lemmatizer = None
stop_words = None

def initialize_nltk():
    """Download NLTK data if not already present."""
    global lemmatizer, stop_words
    if lemmatizer is not None and stop_words is not None:
        return
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
        print("NLTK initialized successfully.")
    except Exception as e:
        print(f"Error initializing NLTK: {e}")

def _load_models():
    """Load scikit-learn model and vectorizer."""
    global model, vectorizer
    initialize_nltk()
    
    if model is not None and vectorizer is not None:
        return True
            
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # We need the vectorizer used during training
        if os.path.exists(VECTORIZER_PATH):
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
        else:
            print(f"Warning: Vectorizer not found at {VECTORIZER_PATH}. ML predictions may fail.")
            
        print("ML Model and Vectorizer loaded successfully.")
        return True
    except Exception as e:
        print(f"Error loading model artifacts: {e}")
        return False

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_gemini_reasoning(user_sentence):
    """Step 3 — Gemini Reasoning as per user requirements."""
    if not gemini_client:
        return None, "Gemini API not configured."

    prompt = f"""You are an assistant that detects social anxiety from sentences.

Classify the following sentence into one of these categories:

Low Anxiety
Moderate Anxiety
High Anxiety

Guidelines:

Low Anxiety:
Confidence, comfort, positive social interaction.

Moderate Anxiety:
Nervousness, hesitation, worry, overthinking.

High Anxiety:
Avoidance, panic, fear of judgement, physical anxiety symptoms.

Analyze the emotional meaning of the sentence, not just keywords.

Sentence:
{user_sentence}

Return only:

Anxiety Level: <Low / Moderate / High>
Short Reason: <One sentence explanation>"""

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                max_output_tokens=150,
                temperature=0.1
            ) if genai_types else None
        )
        content = response.text.strip()
        
        # Parse content
        level = "Moderate"
        reason = "Classification by AI reasoning."
        
        if "Anxiety Level:" in content:
            level_part = content.split("Anxiety Level:")[1].split("\n")[0].strip()
            if "High" in level_part: level = "High"
            elif "Low" in level_part: level = "Low"
            else: level = "Moderate"
            
        if "Short Reason:" in content:
            reason = content.split("Short Reason:")[1].strip()
            
        return level, reason
    except Exception as e:
        print(f"Gemini error: {e}")
        return None, None

def get_suggestions(level):
    suggestion_pools = {
        "Low": [
            "You're doing okay! Keep focusing on your strengths.",
            "Try a quick 2-minute mindfulness exercise.",
            "Reframe any minor negative thoughts into positive ones.",
            "Take a moment to appreciate a small win from your day.",
            "Focus on your breath for 60 seconds to stay grounded.",
            "Remember that everyone feels a bit self-conscious sometimes.",
            "Channel your energy into a hobby you truly enjoy.",
            "Practice a small act of kindness to boost your mood.",
            "Visualize a place where you feel completely safe and relaxed.",
            "Listen to a song that makes you feel motivated and happy."
        ],
        "Moderate": [
            "Practice deep breathing: Inhale for 4s, hold for 7s, exhale for 8s.",
            "Take a short break and step away from the stressor.",
            "Write down your worries to get them out of your head.",
            "Try the 5-4-3-2-1 grounding technique to stay present.",
            "Remind yourself that thoughts are not always facts.",
            "Go for a short 5-minute walk to clear your mind.",
            "Stretch your body to release physical tension in your shoulders.",
            "Challenge one negative thought with a more balanced perspective.",
            "Focus on what you can control right now, and let go of the rest.",
            "Sip some cold water and focus on the sensation of its temperature."
        ],
        "High": [
            "Ground yourself: Name 5 things you see, 4 you feel, 3 you hear.",
            "Reach out to a trusted friend or family member for support.",
            "Consider speaking with a mental health professional if this persists.",
            "Remember: This feeling is temporary and will pass.",
            "If you're feeling overwhelmed, try to find a quiet space for a moment.",
            "Focus on the physical sensation of your feet on the floor.",
            "Don't be afraid to take a step back from social situations if needed.",
            "Be kind to yourself—you are doing your best in a difficult moment.",
            "Short-term distraction (like counting backwards) can help break an anxiety loop.",
            "Remind yourself of a time you successfully managed a similar feeling."
        ],
        "Uncertain": [
            "I'm not exactly sure what you mean — could you try explaining how you're feeling differently?",
            "I want to make sure I understand you correctly. Could you share more about your emotions?",
            "If you're just typing to test me, that's okay too! But I'm here if you need real support.",
            "It's okay if you find it hard to put your feelings into words right now.",
            "Take your time. I'm here to listen whenever you're ready to share.",
            "Sometimes emotions are complex. Try describing one specific thing you're feeling."
        ]
    }
    
    pool = suggestion_pools.get(level, [])
    return random.sample(pool, min(len(pool), 3)) if pool else []

def analyze_anxiety(text):
    """Follows the Step 1-4 logic requested by the user."""
    if not _load_models():
        return None

    # Step 1 — ML Prediction
    cleaned = clean_text(text)
    ml_level = "Low"
    ml_confidence = 0.0
    probabilities = [0.0, 0.0, 0.0]

    if vectorizer and model:
        try:
            features = vectorizer.transform([cleaned])
            probabilities = model.predict_proba(features)[0].tolist()
            ml_confidence = max(probabilities)
            
            # Map index to Level
            # Assuming labels were 0:Low, 1:Moderate, 2:High (standard for this project)
            levels = {0: "Low", 1: "Moderate", 2: "High"}
            prediction_idx = int(model.predict(features)[0])
            ml_level = levels.get(prediction_idx, "Low")
        except Exception as e:
            print(f"ML Step 1 error: {e}")

    # Step 2 — Confidence Check
    final_level = ml_level
    final_explanation = f"Classification based on ML model trained on dataset (Confidence: {ml_confidence*100:.1f}%)."
    
    # Step 3 & 4 — Gemini Reasoning if confidence < 75%
    if ml_confidence < 0.75:
        gemini_level, gemini_reason = get_gemini_reasoning(text)
        if gemini_level:
            final_level = gemini_level
            final_explanation = f"Refined by Gemini Reasoning: {gemini_reason}"
            final_confidence = 0.85 # High default for Gemini agreement
        else:
            final_confidence = ml_confidence
    else:
        final_confidence = ml_confidence

    # Sentiment for UI metrics
    from textblob import TextBlob
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity

    return {
        "anxiety_level": final_level,
        "sentiment_score": sentiment_score,
        "explanation": final_explanation,
        "suggestions": get_suggestions(final_level),
        "confidence": final_confidence * 100.0,
        "probabilities": probabilities
    }
