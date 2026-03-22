import pandas as pd
import numpy as np
import re
import string
import pickle
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.utils import resample, shuffle

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# High-Risk Phrases for Rule-Based Override
# These phrases prioritize safety and trigger "High Anxiety" regardless of ML prediction.
HIGH_RISK_PHRASES = [
    r"kill myself", r"suicide", r"end my life", r"end it all", r"self harm",
    r"want to die", r"commit suicide", r"hurt myself", r"taking my life",
    r"don't want to live", r"better off dead", r"don't want to be here anymore"
]

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags (noise)
    text = re.sub(r'<.*?>', '', text)
    
    # Remove punctuation & special characters
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Tokenization for stopwords removal and lemmatization
    tokens = text.split()
    
    # Remove short noise tokens
    tokens = [t for t in tokens if len(t) > 1]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    
    # Rejoin
    text = ' '.join(tokens)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_risk_phrases(text):
    """Checks if the text contains any high-risk phrases."""
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

def load_and_preprocess_data(csv_path):
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return None
    
    if 'statement' in df.columns and 'status' in df.columns:
        df = df.rename(columns={'statement': 'sentence'})
        df['status'] = df['status'].astype(str).str.strip().str.capitalize()
        label_mapping = {
            'Normal': 0, 
            'Stress': 1, 
            'Anxiety': 2, 
            'Depression': 2,
            'Suicidal': 2, 
            'Bipolar': 2,
            'Personality disorder': 2
        }
        df['label'] = df['status'].map(label_mapping)
    elif 'sentence' in df.columns and 'label' in df.columns:
        df['label'] = df['label'].astype(int)
    else:
        print("CSV format incorrect.")
        return None

    print("Cleaning text...")
    df['sentence'] = df['sentence'].apply(clean_text)
    df = df.dropna(subset=['sentence', 'label'])
    df = df[df['sentence'].str.strip() != '']
    df = df.drop_duplicates(subset=['sentence'])
    
    print(f"Original dataset size: {len(df)}")
    return df

def train_and_evaluate(df):
    X = df['sentence']
    y = df['label']
    
    X_train_raw, X_test, y_train_raw, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Balance training set (Upsample High/Moderate)
    df_train = pd.DataFrame({'sentence': X_train_raw, 'label': y_train_raw})
    df_0 = df_train[df_train['label'] == 0]
    df_1 = df_train[df_train['label'] == 1]
    df_2 = df_train[df_train['label'] == 2]
    
    max_size = max(len(df_0), len(df_1), len(df_2)) 
    print(f"Balancing dataset to {max_size} samples per class (based on largest class)...")
    
    df_0_bal = resample(df_0, replace=True, n_samples=max_size, random_state=42)
    df_1_bal = resample(df_1, replace=True, n_samples=max_size, random_state=42)
    df_2_bal = resample(df_2, replace=True, n_samples=max_size, random_state=42)
    
    df_train_bal = pd.concat([df_0_bal, df_1_bal, df_2_bal])
    df_train_bal = shuffle(df_train_bal, random_state=42)
    
    X_train = df_train_bal['sentence']
    y_train = df_train_bal['label']
    
    # V6 Feature Engineering for >92% accuracy
    from sklearn.pipeline import FeatureUnion
    
    word_tfidf = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 3), 
        max_features=30000, 
        min_df=2, 
        stop_words='english',
        sublinear_tf=True
    )
    
    char_tfidf = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 5),
        max_features=10000,
        min_df=2,
        sublinear_tf=True
    )
    
    features = FeatureUnion([
        ('word', word_tfidf),
        ('char', char_tfidf)
    ])
    
    print("Vectorizing with V6 Features (Word 1-3 + Char 2-5)...")
    X_train_tfidf = features.fit_transform(X_train)
    X_test_tfidf = features.transform(X_test)
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    
    print("\n--- Training V6 Ensemble Members ---")
    
    # 1. Logistic Regression - Higher C for more sensitivity
    lr = LogisticRegression(max_iter=3000, random_state=42, C=20, solver='saga')
    
    # 2. Calibrated Linear SVC
    svc = LinearSVC(random_state=42, dual='auto', C=1.5, max_iter=2000)
    calibrated_svc = CalibratedClassifierCV(svc, cv=3, method='isotonic')
    
    # 3. Multinomial Naive Bayes - Higher smoothing
    nb = MultinomialNB(alpha=0.01)
    
    # 4. Voting Classifier (Soft Voting)
    ensemble = VotingClassifier(
        estimators=[
            ('lr', lr),
            ('svc', calibrated_svc),
            ('nb', nb)
        ],
        voting='soft',
        weights=[3, 3, 1]
    )
    
    print("Fitting V7 Ensemble...")
    ensemble.fit(X_train_tfidf, y_train)
    
    y_pred = ensemble.predict(X_test_tfidf)
    print("\nEvaluation:")
    print(classification_report(y_test, y_pred, target_names=['Low', 'Moderate', 'High']))
    
    pipeline = Pipeline([
        ('features', features),
        ('clf', ensemble)
    ])
    
    return pipeline

def save_model(model, filename='nlp_anxiety_model.pkl'):
    os.makedirs('backend/ml_models', exist_ok=True)
    filepath = os.path.join('backend/ml_models', filename)
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved: {filepath}")

def calculate_severity_score(confidence, label_idx, detected_risks):
    """
    Computes a 0-100 severity score based on ML output and detected signals.
    """
    base_scores = {0: 10, 1: 45, 2: 75}
    score = base_scores.get(label_idx, 0)
    
    # Adjust based on confidence
    score += (confidence * 15) # +0-15 based on ML certainty
    
    # Add risk phrase weight
    if detected_risks:
        score += 30 # Significant jump if critical phrases found
    
    return min(100, int(score))

def predict_v3(sentence, model):
    detected_risks = check_risk_phrases(sentence)
    
    # 1. Rule-Based Override
    if detected_risks:
        return {
            "label": "High Anxiety",
            "confidence": 0.98,
            "severity_score": 95,
            "risk_level": "Critical",
            "explanation": [f"Critical phrase detected: '{r}'" for r in detected_risks]
        }
    
    cleaned = clean_text(sentence)
    if not cleaned:
        return {
            "label": "Low Anxiety",
            "confidence": 0.0,
            "severity_score": 0,
            "risk_level": "Low",
            "explanation": ["Empty or noise-only input detected."]
        }
    
    probs = model.predict_proba([cleaned])[0]
    pred_idx = np.argmax(probs)
    conf = np.max(probs)
    
    label_map = {0: "Low Anxiety", 1: "Moderate Anxiety", 2: "High Anxiety"}
    risk_map = {0: "Low", 1: "Medium", 2: "High"}
    
    severity = calculate_severity_score(conf, pred_idx, detected_risks)
    
    # Final Risk Level Adjustment
    risk_level = risk_map[pred_idx]
    if severity > 90: risk_level = "Critical"
    elif severity > 70: risk_level = "High"
    elif severity > 40: risk_level = "Medium"
    else: risk_level = "Low"

    # Uncertainty Handling
    if conf < 0.60:
        return {
            "label": "UNCERTAIN",
            "confidence": float(conf),
            "severity_score": severity,
            "risk_level": risk_level,
            "explanation": ["Confidence below 60% threshold. Prediction may be unreliable."]
        }

    return {
        "label": label_map[pred_idx],
        "confidence": float(conf),
        "severity_score": severity,
        "risk_level": risk_level,
        "explanation": [f"ML Ensemble prediction with {conf*100:.1f}% confidence."]
    }

if __name__ == "__main__":
    df = load_and_preprocess_data('Combined Data.csv')
    if df is not None:
        model = train_and_evaluate(df)
        save_model(model, 'nlp_anxiety_model_v8.pkl')
        
        # Quick test
        print("\n--- V3 Production Test ---")
        tests = ["I'm happy", "I feel a bit anxious", "I want to kill myself", "I don't know"]
        for t in tests:
            res = predict_v3(t, model)
            print(f"Input: {t}\nResult: {res}\n")
