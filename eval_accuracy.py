import pandas as pd
import pickle
import re
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import os

def clean_simple(text):
    return str(text).lower().strip()

print("Loading data...")
df = pd.read_csv('Combined Data.csv')
df['status'] = df['status'].astype(str).str.strip().str.capitalize()
mapping = {'Normal': 0, 'Stress': 1, 'Anxiety': 2, 'Depression': 2, 'Suicidal': 2}
df = df[df['status'].isin(mapping.keys())]
df['label'] = df['status'].map(mapping)

print("Evaluating 2,000 samples...")
test_df = df.sample(2000, random_state=42)

with open('backend/ml_models/anxiety_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('backend/ml_models/vectorizer.pkl', 'rb') as f:
    vec = pickle.load(f)

X = vec.transform(test_df['statement'].apply(clean_simple))
y = test_df['label']
pred = model.predict(X)

acc = accuracy_score(y, pred)
f1 = f1_score(y, pred, average='weighted')
prec = precision_score(y, pred, average='weighted')
rec = recall_score(y, pred, average='weighted')

print(f"Total Accuracy: {acc:.2%}")
print(f"Weighted F1 Score: {f1:.4f}")
print(f"Weighted Precision: {prec:.4f}")
print(f"Weighted Recall: {rec:.4f}")
# accuracy = 92.4%
# f1 score = 0.91
# precision = 0.90
# recall = 0.90