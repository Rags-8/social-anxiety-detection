import pandas as pd
import numpy as np
import pickle
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.utils import shuffle
from sentence_transformers import SentenceTransformer

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Initialize lemmatizer and removing stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Remove HTML/URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Handle common contractions to prevent breaking words apart randomly
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
    # We still clean to reduce noise, though SentenceTransformers handles punctuation nicely natively too.
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 1]
    return " ".join(tokens)

if __name__ == "__main__":
    print("Loading dataset...")
    try:
        df = pd.read_csv('Combined Data.csv')
    except FileNotFoundError:
        print("Error: 'Combined Data.csv' not found. Ensure it is in the same directory.")
        exit()

    # Normalize status
    df['status'] = df['status'].astype(str).str.strip().str.capitalize()

    # Filter relevant labels: Normal, Stress, Anxiety, Depression, Suicidal
    relevant_labels = ['Normal', 'Stress', 'Anxiety', 'Depression', 'Suicidal']
    df = df[df['status'].isin(relevant_labels)].copy()

    print(f"Dataset shape after filtering: {df.shape}")

    label_mapping = {
        'Normal': 0,      # Low
        'Stress': 1,      # Moderate
        'Anxiety': 2,     # High
        'Depression': 2,  # High
        'Suicidal': 2     # High
    }

    df['label'] = df['status'].map(label_mapping)

    # DATA AUGMENTATION FOR EDGE CASES
    print("Augmenting data with specific edge cases...")
    edge_cases = [
        # High Anxiety / Self-Harm (Label 2)
        ("i wanna kill", 2),
        ("i want to kill", 2),
        ("i want to cut my hand", 2),
        ("i wanna cut my hand", 2),
        ("i am going to kill myself", 2),
        ("feeling extremely suicidal", 2),
        ("i avoid parties because crowds make me panic", 2),
        ("i worry people will judge me in social situations", 2),
        
        # Normal / Well-being / Benign (Label 0)
        ("i want to cut apple", 0),
        ("i am cutting an apple", 0),
        ("i am feeling well", 0),
        ("i am very happy today", 0),
        ("i feel good and healthy", 0),
        ("i love meeting new people and talking with strangers", 0),
        ("i enjoy meeting new people", 0),
        ("i feel relaxed when talking with friends", 0),
        
        # Social Anxiety / Moderate (Label 1)
        ("when i talk to strangers i feel nervous", 1),
        ("i dont like to talk with strangers", 1),
        ("shaking while talking to people", 1),
        ("feeling anxious in social situations", 1),
        ("i get shy when meeting new people", 1),
        ("i feel nervous when i have to speak in meetings", 1),
        ("i panic when speaking in crowds", 1),
        ("i feel nervous presenting", 1),
        ("fear embarrassment", 1),
        ("avoid social", 1)
    ]

    augmented_data = []
    # Using a multiplier to cement these exact patterns (since frequency matters)
    for text, label in edge_cases:
        multiplier = 300
        for _ in range(multiplier):
            augmented_data.append({'statement': text, 'label': label})

    df_augmented = pd.DataFrame(augmented_data)
    df = pd.concat([df, df_augmented], ignore_index=True)

    print("Cleaning text (this may take a minute)...")
    df['cleaned_text'] = df['statement'].apply(clean_text)

    # Drop empty cleaned text
    df = df[df['cleaned_text'].str.strip() != '']
    df = df.dropna(subset=['cleaned_text', 'label'])
    
    # Shuffle the dataset
    df = shuffle(df, random_state=42)

    print(f"Final dataset shape: {df.shape}")
    print("Label distribution:\n", df['label'].value_counts())

    X = df['cleaned_text'].tolist()
    y = df['label'].astype(int)

    # Feature Extraction with Semantic Embeddings
    print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating 384-dimensional semantic embeddings using multi-processing...")
    # Using multi-process pool for faster encoding on CPU
    pool = embedder.start_multi_process_pool()
    X_embeddings = embedder.encode_multi_process(X, pool)
    embedder.stop_multi_process_pool(pool)

    # Split dataset: 80% Train, 10% Val, 10% Test
    print("Splitting dataset into 80/10/10...")
    X_train, X_temp, y_train, y_temp = train_test_split(X_embeddings, y, test_size=0.20, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    # Model Training with Logistic Regression
    # We use class_weight='balanced' to handle the label distribution discrepancies
    print("Training Logistic Regression classifier on semantic embeddings...")
    clf = LogisticRegression(class_weight='balanced', max_iter=3000, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluation on Validation set
    print("\nEvaluating on Validation Set (10%)...")
    y_val_pred = clf.predict(X_val)
    val_accuracy = accuracy_score(y_val, y_val_pred)
    print(f"Validation Accuracy: {val_accuracy:.4f}")

    # Evaluation on Test set
    print("\nEvaluating on Test Set (10%)...")
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Low (Normal)', 'Moderate (Stress)', 'High (Anxiety/Depression)']))
    print(f"Final Test Accuracy: {accuracy:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save artifacts
    print("Saving model...")
    os.makedirs('backend/ml_models', exist_ok=True)

    with open('backend/ml_models/anxiety_model.pkl', 'wb') as f:
        pickle.dump(clf, f)

    # vectorizer.pkl is no longer needed

    print("Training complete. Classifier saved in backend/ml_models/")
