import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Pre-load NLTK silently
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Exact same function used in ml_utils.py"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Load model and vectorizer
with open('backend/ml_models/anxiety_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('backend/ml_models/vectorizer.pkl', 'rb') as f:
    vec = pickle.load(f)

levels = {0: 'Low', 1: 'Moderate', 2: 'High'}
tests = [
    ('I feel calm and happy today, everything is fine',           'Low'),
    ('Work is overwhelming me and I feel very stressed',          'Moderate'),
    ('I cannot stop panicking and I cannot breathe, I am terrified', 'High'),
    ('I feel anxious and nervous in social situations, my heart is racing', 'High'),
    ('I am a little worried about my upcoming meeting',           'Moderate'),
]

print('=== PREDICTION SMOKE TEST (with NLTK preprocessing) ===')
passed = 0
for text, expected in tests:
    cleaned    = clean_text(text)
    feat       = vec.transform([cleaned])
    idx        = model.predict(feat)[0]
    proba      = model.predict_proba(feat)[0]
    pred       = levels[idx]
    confidence = max(proba)
    status     = 'PASS' if pred == expected else 'FAIL'
    if status == 'PASS':
        passed += 1
    print(f'  {status} | Expected={expected:8s}  Got={pred:8s}  ({confidence:.0%} conf)')
    print(f'       Raw:     {text}')
    print(f'       Cleaned: {cleaned}')
    print()

print(f'Result: {passed}/{len(tests)} tests passed')
