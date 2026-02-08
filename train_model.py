import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove non-alphabetic characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    text = clean_text(text)
    words = text.split()
    # Remove stopwords and lemmatize
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def map_label(label):
    label = str(label).strip()
    if label == 'Normal':
        return 'Low Anxiety'
    elif label in ['Stress', 'Anxiety']:
        return 'Moderate Anxiety'
    elif label in ['Depression', 'Suicidal', 'Bipolar', 'Personality disorder']:
        return 'High Anxiety'
    else:
        return 'Moderate Anxiety' # Default fallback

def main():
    print("Loading dataset...")
    # Dynamic path to Downloads folder
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    data_path = os.path.join(downloads_path, "Combined Data.csv")
    
    print(f"Looking for dataset at: {data_path}")
    
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {data_path}")
        return

    # Check for required columns
    if 'statement' not in df.columns or 'status' not in df.columns:
        print("Error: Dataset must contain 'statement' and 'status' columns.")
        print(f"Columns found: {df.columns}")
        return

    print("Mapping labels...")
    df['anxiety_level'] = df['status'].apply(map_label)
    
    # Filter out empty statements
    df = df.dropna(subset=['statement'])
    df['clean_statement'] = df['statement'].apply(preprocess_text)
    
    # Remove empty cleaned statements
    df = df[df['clean_statement'] != ""]

    print("Target distribution:")
    print(df['anxiety_level'].value_counts())

    X = df['clean_statement']
    y = df['anxiety_level']

    # content is statement, target is anxiety_level
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print("Training model...")
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_train_tfidf, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test_tfidf)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred))

    # Save model and vectorizer
    # Use relative path 'backend/models'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(current_dir, "backend", "models")
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(model, os.path.join(model_dir, "anxiety_model.pkl"))
    joblib.dump(vectorizer, os.path.join(model_dir, "tfidf_vectorizer.pkl"))
    print(f"Model and vectorizer saved to {model_dir}")

if __name__ == "__main__":
    main()
