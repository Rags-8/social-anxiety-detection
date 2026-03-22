import os
import re
import csv
from datetime import datetime, timezone

try:
    import nltk
    from nltk.stem import WordNetLemmatizer
except ImportError:
    pass

WORD_DICTIONARY = None
lemmatizer = None

# Import suggestions pool from ml_utils
from .ml_utils import get_v3_suggestions

def load_word_dictionary():
    global WORD_DICTIONARY
    if WORD_DICTIONARY is not None:
        return WORD_DICTIONARY
        
    WORD_DICTIONARY = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    files = {
        "High": os.path.join(base_dir, "high_anxiety_words.csv"),
        "Moderate": os.path.join(base_dir, "moderate_anxiety_words.csv"),
        "Low": os.path.join(base_dir, "low_anxiety_words.csv")
    }
    
    for label, filepath in files.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row['word'].strip().lower()
                    weight = int(row['weight'])
                    
                    if word not in WORD_DICTIONARY:
                         WORD_DICTIONARY[word] = (label, weight)
                    else:
                         existing_label, existing_weight = WORD_DICTIONARY[word]
                         if weight > existing_weight:
                             WORD_DICTIONARY[word] = (label, weight)
                         elif weight == existing_weight:
                             priority = {"High": 3, "Moderate": 2, "Low": 1}
                             if priority[label] > priority[existing_label]:
                                 WORD_DICTIONARY[word] = (label, weight)
                                 
    return WORD_DICTIONARY

def init_nlp():
    global lemmatizer
    if lemmatizer is None:
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        lemmatizer = WordNetLemmatizer()
    return lemmatizer

def predict_with_words(text: str, ml_prediction: str, ml_confidence: float) -> dict:
    word_dict = load_word_dictionary()
    lemma = init_nlp()
    
    # Preprocess input
    text_lower = str(text).lower()
    text_clean = re.sub(r'[^\w\s\']', ' ', text_lower)
    tokens = text_clean.split()
    lemmatized_tokens = [lemma.lemmatize(t) for t in tokens if len(t) > 2]
    
    # Negative Distress Detection (STEP 0)
    distress_keywords = ['crying', "can't stop", 'breakdown', 'pain', 'hurt']
    has_distress = any(dk in text_lower for dk in distress_keywords)
    
    # Sentiment Override (STEP 2)
    positive_keywords = ['happy', 'calm', 'relaxed', 'confident', 'peaceful']
    has_positive = any(pk in text_lower for pk in positive_keywords)
    
    scores = {"High": 0, "Moderate": 0, "Low": 0}
    raw_detected = []
    
    for word in lemmatized_tokens:
        if word in word_dict:
            label, weight = word_dict[word]
            raw_detected.append({"word": word, "label": label, "weight": weight})

    detected_words = []
    for dw in raw_detected:
        w = dw['weight']
        lbl = dw['label']
        
        # Rule: Only consider words with weight >= 2. Ignore weak words completely.
        if w < 2:
            continue
            
        impact = w * 2 if w >= 3 else w
        scores[lbl] += impact
        detected_words.append(dw)
            
    high = scores["High"]
    mod = scores["Moderate"]
    low = scores["Low"]
    
    # Format ML prediction to match labels
    ml_label = "High Anxiety" if "High" in ml_prediction else ("Moderate Anxiety" if "Moderate" in ml_prediction else "Low Anxiety")
    
    final_pred = None
    final_conf = 0.0
    reason = ""
    
    # Format ML prediction to match labels
    ml_label = "High Anxiety" if "High" in ml_prediction else ("Moderate Anxiety" if "Moderate" in ml_prediction else "Low Anxiety")
    
    final_pred = None
    final_conf = 0.0
    reason = ""
    
    # 1. TOP PRIORITY: Safety/Distress Check (Non-negotiable)
    if has_distress:
        final_pred = "High Anxiety"
        final_conf = 0.95
        reason = "Distress signals detected (crying, pain, break down, etc)."
    # 2. SECOND PRIORITY: ML Model (User requested Combined Data.csv first)
    elif ml_confidence > 0.45:
        final_pred = ml_label
        final_conf = ml_confidence
        reason = f"Validated by ML Ensemble ({ml_prediction} with {ml_confidence*100:.1f}% confidence)."
        
        # Check if keywords strongly disagree with a "Low" prediction
        if ml_label == "Low Anxiety" and scores["High"] >= 5:
            final_pred = "Moderate Anxiety"
            reason = "ML suggests Low, but High-Anxiety keywords detected; adjusting to Moderate for safety."
    # 3. THIRD PRIORITY: Sentiment Override
    elif has_positive:
        final_pred = "Low Anxiety"
        final_conf = 0.90
        reason = "Clear positive sentiment detected."
    # 4. FOURTH PRIORITY: Keyword Scoring Pass (Fallback)
    elif len(detected_words) > 0:
        strong_high_count = sum(1 for dw in detected_words if dw['label'] == 'High' and dw['weight'] >= 3)
        raw_high_score = sum(dw['weight'] for dw in detected_words if dw['label'] == 'High')
        
        if raw_high_score >= 5 and (strong_high_count >= 2 or (strong_high_count >= 1 and ml_label == "High Anxiety")):
            final_pred = "High Anxiety"
            final_conf = max(0.85, ml_confidence)
            reason = "Matches strong high-anxiety keywords."
        elif mod > 0 or low > 0:
            if mod >= low:
                final_pred = "Moderate Anxiety"
                final_conf = 0.80
                reason = "Keyword evaluation leaning Moderate."
            else:
                final_pred = "Low Anxiety"
                final_conf = 0.80
                reason = "Keyword evaluation leaning Low."
        else:
            final_pred = "Moderate Anxiety"
            final_conf = 0.80
            reason = "Generalized anxiety signals detected."
    else:
        final_pred = "Uncertain"
        final_conf = ml_confidence
        reason = "Insufficient emotional signals found."

    timestamp = datetime.now(timezone.utc).isoformat()

    if final_pred == "Uncertain":
        return {
            "prediction": "Uncertain",
            "suggestion": "Can you describe how you feel more clearly?",
            "follow_up": [
                "Do you feel nervous in social situations?",
                "Do you experience symptoms like sweating or heart racing?"
            ]
        }
        
    # Use randomized suggestions from ml_utils pool
    suggestions = get_v3_suggestions(final_pred)
    
    return {
        "prediction": final_pred,
        "confidence": round(min(1.0, final_conf), 3),
        "reason": reason,
        "detected_words": detected_words,
        "timestamp": timestamp,
        "suggestions": suggestions
    }
