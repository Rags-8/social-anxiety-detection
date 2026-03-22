import os
import sys

# Add backend directory to sys.path to allow imports
backend_dir = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_\backend"
sys.path.append(backend_dir)

from app.prediction_system import predict_with_words

tests = [
    ("I feel more happy", "High Anxiety", 0.9),  # ML is very confident it is High
    ("I feel calm and relaxed", "High Anxiety", 0.9), # ML is very confident it is High
    ("I panic and start sweating", "Low Anxiety", 0.9), # ML says Low, keywords override to High
    ("I feel slightly awkward", "Low Anxiety", 0.9), # ML says Low, Keywords say Mod
    ("I can't stop crying", "Low Anxiety", 0.9) # Distress keyword override to High
]

print("--- PIPELINE VERIFICATION ---")
for sentence, fake_ml, fake_conf in tests:
    res = predict_with_words(sentence, fake_ml, fake_conf)
    print(f"INPUT:  '{sentence}'")
    print(f"OUTPUT: [{res['prediction']}] - {res.get('reason')}")
    print("---")
