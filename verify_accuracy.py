import sys
import os

# Add the backend to path to import ml_utils
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.ml_utils import analyze_anxiety

test_statements = [
    "I am feeling completely normal and happy today.",
    "This exam stress is a bit much lately.",
    "I have been diagnosed with bipolar disorder.",
    "My personality disorder makes it hard to talk to anyone.",
    "I just want to end it all, feeling suicidal.",
    "I feel relaxed after the gym."
]

from sentence_transformers import SentenceTransformer
import pickle

with open('backend/ml_models/anxiety_model.pkl', 'rb') as f:
    clf = pickle.load(f)

embedder = SentenceTransformer('all-MiniLM-L6-v2')

label_map = {0: 'Low (Normal)', 1: 'Moderate (Stress)', 2: 'High (Anxiety/Depression)'}

print("--- Testing Refined Anxiety Rules (Targeting >92% Model) ---")
for text in test_statements:
    emb = embedder.encode([text])
    pred = clf.predict(emb)[0]
    print(f"\nStatement: '{text}'")
    print(f"Prediction: {label_map[pred]} (Label: {pred})")


print("\n--- Verification Complete ---")
