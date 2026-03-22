import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.utils import shuffle
from sentence_transformers import SentenceTransformer

EMBED_CACHE = 'embeddings_cache.npy'
LABEL_CACHE = 'labels_cache.npy'

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

if __name__ == "__main__":
    print("Loading dataset...")
    try:
        df = pd.read_csv('Combined Data.csv')
    except FileNotFoundError:
        print("Error: 'Combined Data.csv' not found.")
        exit()

    df['status'] = df['status'].astype(str).str.strip().str.capitalize()

    relevant_labels = ['Normal', 'Stress', 'Anxiety', 'Depression', 'Suicidal', 'Bipolar', 'Personality disorder']
    df = df[df['status'].isin(relevant_labels)].copy()

    print(f"Dataset shape after filtering: {df.shape}")

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
    
    # Downsample the massive majority classes to speed up local CPU embedding
    # Target: ~12,000 per class maximum.
    # Label 2 has ~37k, Label 0 has ~18k, Label 1 has ~3k originally.
    
    df_0 = df[df['label'] == 0]
    df_1 = df[df['label'] == 1]
    df_2 = df[df['label'] == 2]

    # Sample down to max 2000 per class to make CPU training extremely fast
    if len(df_0) > 2000: df_0 = df_0.sample(n=2000, random_state=42)
    if len(df_1) > 2000: df_1 = df_1.sample(n=2000, random_state=42)
    if len(df_2) > 2000: df_2 = df_2.sample(n=2000, random_state=42)

    df = pd.concat([df_0, df_1, df_2])

    # Augmentation - to boost 'Moderate' (Stress) up to par
    print("Augmenting data with specific edge cases...")
    edge_cases = [
        # High (Label 2)
        ("i wanna kill", 2), ("i want to kill myself", 2), ("feeling suicidal", 2),
        ("i am depressed", 2), ("depression is ruining my life", 2),
        ("bipolar disorder makes it hard", 2), ("i have a personality disorder", 2),
        ("anxiety ruining my life", 2), ("panic attack in public", 2),
        ("scared of people judging me", 2), ("i cant function due to anxiety", 2),
        ("hopeless and empty inside", 2),

        # Normal / Low (Label 0)
        ("i am feeling well", 0), ("i am very happy today", 0),
        ("i feel good and healthy", 0), ("everything is normal", 0),
        ("i feel relaxed", 0), ("having a great day", 0),

        # Stress / Moderate (Label 1) - HEAVY
        ("i am feeling stressed", 1), ("too much work stress", 1),
        ("overwhelmed by tension", 1), ("moderate pressure at work", 1),
        ("i feel overloaded", 1), ("exam stress is high", 1),
        ("tired and stressed", 1), ("life is a bit much lately", 1),
        ("feeling constant pressure", 1), ("work is stressful but manageable", 1),
        ("deadlines are stressing me out", 1), ("family pressure is building", 1),
        ("i am overwhelmed with responsibilities", 1),
    ]

    augmented_data = []
    for text, label in edge_cases:
        multiplier = 600 if label == 1 else 100
        for _ in range(multiplier):
            augmented_data.append({'statement': text, 'label': label})

    df = pd.concat([df, pd.DataFrame(augmented_data)], ignore_index=True)

    print("Cleaning text...")
    df['cleaned_text'] = df['statement'].apply(clean_text)
    df = df[df['cleaned_text'].str.strip() != '']
    df = df.dropna(subset=['cleaned_text', 'label'])
    df = shuffle(df, random_state=42)

    print(f"Final dataset shape: {df.shape}")
    print("Label distribution:\n", df['label'].value_counts())

    X = df['cleaned_text'].tolist()
    y = df['label'].astype(int).values

    # ---- EMBEDDING WITH CACHE ----
    # If embeddings are cached with the same size, skip re-generation
    if os.path.exists(EMBED_CACHE) and os.path.exists(LABEL_CACHE):
        cached_y = np.load(LABEL_CACHE)
        if len(cached_y) == len(y):
            print(f"Loading cached embeddings from '{EMBED_CACHE}'...")
            X_embeddings = np.load(EMBED_CACHE)
        else:
            print("Cache size mismatch. Regenerating embeddings...")
            os.remove(EMBED_CACHE)
            os.remove(LABEL_CACHE)
    
    if not os.path.exists(EMBED_CACHE):
        print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"Generating embeddings for {len(X)} samples (batch=256)...")
        X_embeddings = embedder.encode(X, batch_size=256, show_progress_bar=True)
        np.save(EMBED_CACHE, X_embeddings)
        np.save(LABEL_CACHE, y)
        print("Embeddings cached to disk.")
    # ---- END EMBEDDING ----

    # Split 80/10/10
    print("Splitting dataset into 80/10/10...")
    X_train, X_temp, y_train, y_temp = train_test_split(X_embeddings, y, test_size=0.20, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    # ---- MODEL: RandomForest (high accuracy, parallelized) ----
    print("Training Random Forest classifier...")
    clf = RandomForestClassifier(
        n_estimators=300,
        class_weight='balanced',
        max_depth=None,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Validation
    y_val_pred = clf.predict(X_val)
    val_acc = accuracy_score(y_val, y_val_pred)
    print(f"\nValidation Accuracy: {val_acc:.4f}")

    # Test
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Low (Normal)', 'Moderate (Stress)', 'High (Anxiety/Depression)']))
    print(f"Final Test Accuracy: {accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    print("Saving model...")
    os.makedirs('backend/ml_models', exist_ok=True)
    with open('backend/ml_models/anxiety_model.pkl', 'wb') as f:
        pickle.dump(clf, f)

    print("Training complete. Classifier saved in backend/ml_models/")
