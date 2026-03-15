import os
import re
import pickle
import random
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai
from dotenv import load_dotenv
from textblob import TextBlob
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use gemini-flash-latest which appeared in the model list
        gemini_model = genai.GenerativeModel('gemini-flash-latest')
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        gemini_model = None
else:
    print("Warning: GEMINI_API_KEY not found or default. Gemini analysis will be skipped.")
    gemini_model = None

# Lazy-load artifacts (avoids blocking uvicorn port binding on Render)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models", "anxiety_model.pkl")

model = None
embedder = None

def _load_models():
    """Load ML models on first use (lazy loading) to avoid startup timeout."""
    global model, embedder
    if model is not None and embedder is not None:
        return True
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Scikit-learn Logistic Regression Model loaded successfully.")
        print("Loading SentenceTransformer ('all-MiniLM-L6-v2')...")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("SentenceTransformer loaded successfully.")
        return True
    except Exception as e:
        print(f"Error loading model artifacts: {e}")
        model = None
        embedder = None
        return False

# Initialize NLTK
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Remove HTML/URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Handle common contractions
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'s", " is", text)
    text = re.sub(r"'d", " would", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'t", " not", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'m", " am", text)

    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    tokens = text.split()
    # We still clean to reduce noise
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 1]
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
            
        # Check for 5+ consecutive vowels or 6+ consecutive consonants (relaxed for common words)
        if re.search(r'[aeiouAEIOU]{5,}', word) or re.search(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{6,}', word):
            if word.lower() not in ["strength", "lengths", "straight"]: 
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
    # Return a random sample of 3 suggestions (or fewer if the pool is small)
    return random.sample(pool, min(len(pool), 3)) if pool else []

def get_gemini_analysis(text):
    if not gemini_model:
        return None, None, None

    prompt = f"""
    Analyze this sentence for social anxiety indicators: "{text}"
    
    Provide your analysis in exactly three labeled sections:
    LEVEL: <Low / Moderate / High>
    REASON: <One short sentence explaining why>
    SUGGESTIONS: <Exactly three practical, personalized, and empathetic tips for the user, separated by semicolons>

    Classification Guide:
    - Low: Confidence, positive socializing, relaxed.
    - Moderate: Shyness, slight worry, awkwardness, overthinking.
    - High: Fear of judgment, intense physical signs (panic, heart racing), total avoidance, terror.
    """
    
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=250,
                temperature=0.2
            )
        )
        content = response.text.strip()
        # Robust Section Splitting
        sections = re.split(r"(LEVEL|REASON|SUGGESTIONS):", content, flags=re.IGNORECASE)
        
        # Mapping results
        results = {}
        for i in range(1, len(sections), 2):
            key = sections[i].upper()
            val = sections[i+1].strip() if (i+1) < len(sections) else ""
            results[key] = val

        anxiety_level = results.get("LEVEL", "Low").capitalize()
        # Ensure it's one of the expected values
        if "High" in anxiety_level: anxiety_level = "High"
        elif "Moderate" in anxiety_level: anxiety_level = "Moderate"
        else: anxiety_level = "Low"

        reason = results.get("REASON", "Semantic analysis confirmed.")
        s_raw = results.get("SUGGESTIONS", "")
        
        suggestions = []
        if s_raw:
            # Split by common bullet patterns, newlines, or semicolons
            split_res = re.split(r'[;•\*\-\n]|\d\.', s_raw)
            suggestions = [s.strip() for s in split_res if len(s.strip()) > 5]
            suggestions = suggestions[:3] # Ensure only 3

        return anxiety_level, reason, suggestions
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None, None, None


def analyze_anxiety(text):
    if not _load_models():
        return None

    cleaned = clean_text(text)

    # Edge-case: extreme gibberish or empty string
    if is_gibberish(text) or not cleaned.strip():
        return {
            "anxiety_level": "Low",
            "sentiment_score": 0.0,
            "explanation": "Input was identified as potentially irrelevant or nonsensical.",
            "suggestions": get_suggestions("Low"),
            "confidence": 100.0,
            "probabilities": [1.0, 0.0, 0.0]
        }

    # 1. Get Semantic Intensity Score and record matches
    text_lower = f" {text.lower()} "
    intensity_score = 0
    high_matches = []
    mod_matches = []
    
    strong_high_patterns = {
        "terrified": r"\bterrified\b|\bterrify\w*\b",
        "panic": r"\bpanic\w*\b",
        "fear": r"\bfear\b|\bfearful\b",
        "heart racing": r"\bheart\s+race\w*\b|\bheart\s+racing\b|\bracing\s+heart\b",
        "shaking hands": r"\bhands?\s+shak\w*\b|\bshak\w*\s+hands?\b",
        "overwhelmed": r"\boverwhelmed\b",
        "avoidance of people": r"\bavoid\s+.*people\b|\bavoid\s+.*person\b",
        "avoidance of speaking": r"\bavoid\s+.*speak\w*\b|\bavoid\s+.*talking\b",
        "avoidance of social events": r"\bavoid\s+.*social\s+event\w*\b|\bavoid\s+.*gathering\w*\b|\bavoid\s+.*party\b",
        "extreme nervousness": r"\bextremely\s+nervous\b|\bextremely\s+anxious\b|\bintense\s+anxiety\b",
        "intense fear": r"\bintense\s+fear\b",
        "fear of judgment": r"\bjudged?\b|\bjudgement\b|\bcriticiz\w*\b",
        "eye contact avoidance": r"\beye\s+contact\b",
        "crowds": r"\bcrowds?\b",
        "anxious": r"\banxious\b",
        "worry": r"\bworry\b|\bworried\b",
        "anxiety": r"\banxiety\b",
        "restless": r"\brestless\w*\b",
        "sleep issues": r"\btrouble\s+sleep\w*\b|\bsleepless\b|\bcannot\s+sleep\b"
    }
    
    for label, pattern in strong_high_patterns.items():
        if re.search(pattern, text_lower):
            intensity_score += 3
            high_matches.append(label)
            
    moderate_patterns = {
        "nervous": r"\bnervous\b",
        "shy": r"\bshy\b",
        "uncomfortable": r"\buncomfortable\b",
        "hesitant": r"\bhesitate\b|\bhesitant\b",
        "awkward": r"\bawkward\b",
        "tense": r"\btense\b|\btension\b",
        "overthinking": r"\boverthink\w*\b",
        "slight anxiety": r"\bslightly\s+anxious\b|\bslight\s+anxiety\b"
    }
    
    for label, pattern in moderate_patterns.items():
        if re.search(pattern, text_lower):
            intensity_score += 2
            mod_matches.append(label)

    # Low indicators check
    low_patterns = [r"\benjoy\s+.*meeting\b", r"\bfeel\s+confident\b", r"\brelaxed\b", r"\bhappy\s+to\s+socialize\b"]
    has_low = False
    for pattern in low_patterns:
        if re.search(pattern, text_lower):
            has_low = True
            if not high_matches and not mod_matches:
                intensity_score -= 2

    # PRIORITY OVERRIDE
    if high_matches:
        intensity_score = max(intensity_score, 3)
        score_level = "High"
    elif mod_matches:
        intensity_score = max(intensity_score, 2)
        score_level = "Moderate"
    else:
        score_level = "Low"

    # 2. Get ML Prediction
    features = embedder.encode([cleaned])
    prediction_idx = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0].tolist()
    confidence = float(max(probabilities))

    levels = {0: "Low", 1: "Moderate", 2: "High"}
    ml_predicted_level = levels.get(prediction_idx, "Low")
    
    print(f"DEBUG: text='{text}', score={intensity_score}, score_level='{score_level}', ml='{ml_predicted_level}'")

    # 3. Apply Conflict Resolution
    severity_order = {"High": 2, "Moderate": 1, "Low": 0}
    current_best_level = score_level
    if severity_order[ml_predicted_level] > severity_order[score_level]:
        current_best_level = ml_predicted_level

    # 4. Integrate Gemini Analysis
    gemini_level, gemini_reason, gemini_suggestions = get_gemini_analysis(text)
    
    # Sentiment & Default Suggestions
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    suggestions = get_suggestions(current_best_level)
    
    final_anxiety_level = current_best_level
    final_suggestions = suggestions # Default to local randomized
    
    # Generate Local Analysis Reason
    local_reason = ""
    if high_matches:
        local_reason = f"Identified strong anxiety triggers: {', '.join(high_matches)}."
    elif mod_matches:
        local_reason = f"Detected moderate anxiety indicators: {', '.join(mod_matches)}."
    else:
        local_reason = f"Classification based on overall sentence structure and sentiment."

    analysis_explanation = f"Analysis: {local_reason}"
    
    if gemini_level:
        # Prioritize Gemini Suggestions if API is working
        if gemini_suggestions and len(gemini_suggestions) >= 2:
            final_suggestions = gemini_suggestions
            print(f"DEBUG: Using personalized suggestions from Gemini.")

        # Accuracy Tuning: Multi-Factor Severity Rule
        # If Gemini is High, we almost always trust it unless local is empty/gibberish
        if severity_order[gemini_level] > severity_order[current_best_level]:
            final_anxiety_level = gemini_level
            analysis_explanation = f"Gemini Analysis: {gemini_reason} (Advanced semantic detection)"
        elif gemini_level == current_best_level:
            # Both match
            analysis_explanation = f"Analysis: {gemini_reason} (Confirmed by semantic analysis)"
            confidence = min(confidence * 1.15, 0.99) # Higher boost for agreement
        else:
            # Local was higher (e.g. physical trigger caught by local but missed by Gemini)
            analysis_explanation = f"{local_reason} Gemini detected '{gemini_level}' but higher severity logic was prioritized for safety."
    
    anxiety_level = final_anxiety_level
    
    # Calibrate confidence based on final level and agreements
    if anxiety_level == "High":
        if high_matches or gemini_level == "High":
            confidence = max(confidence, 0.95)
    elif anxiety_level == "Moderate":
        confidence = max(confidence, 0.88)
    elif anxiety_level == "Low":
        confidence = max(confidence, 0.96)

    # Final result structure
    return {
        "anxiety_level": anxiety_level,
        "sentiment_score": sentiment_score,
        "explanation": analysis_explanation,
        "suggestions": final_suggestions,
        "confidence": confidence * 100.0,
        "probabilities": probabilities
    }
