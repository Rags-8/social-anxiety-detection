import os
import sys

# Add backend directory to sys.path to allow imports
backend_dir = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_\backend"
sys.path.append(backend_dir)

from app.prediction_system import predict_with_words

res3 = predict_with_words("I am sweat and panic so much", "Moderate Anxiety", 0.8)
print("TEST 3 - Override ML:", res3['prediction'], res3.get('reason', res3.get('suggestion')))
print("Detected words:", res3.get('detected_words'))
