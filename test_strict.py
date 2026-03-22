import os
import sys

# Add backend directory to sys.path to allow imports
backend_dir = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_\backend"
sys.path.append(backend_dir)

from app.prediction_system import predict_with_words

tests = [
    ("I enjoyed spending time with my friends", "Low Anxiety", 0.6), # generic ML
    ("I feel calm and relaxed", "Low Anxiety", 0.9),
    ("I feel slightly awkward talking to strangers", "Low Anxiety", 0.6), # ML failed -> Mod fallback
    ("I panic and start sweating", "Moderate Anxiety", 0.6) # ML failed -> High fallback override
]

for sentence, fake_ml, fake_conf in tests:
    res = predict_with_words(sentence, fake_ml, fake_conf)
    print(f"[{res['prediction']}] - {sentence}")
    print(f"Suggestions: {res.get('suggestions', 'NONE')}")
    print("---")
