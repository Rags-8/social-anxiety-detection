
import sys
import os
from dotenv import load_dotenv

# Add the backend/app to path
sys.path.append(os.path.join(os.getcwd(), "backend", "app"))

# Load env
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from ml_utils import analyze_anxiety

test_cases = [
    "I feel nervous about the presentation.",
    "I am terrified of talking to strangers.",
    "I'm a bit shy but I like meeting people.",
    "I heart racing when I see a crowd.", # High indicator
]

print("Starting Debug Prediction Tests...")
print("-" * 30)

for text in test_cases:
    print(f"\nAnalyzing: '{text}'")
    result = analyze_anxiety(text)
    if result:
        print(f"Level: {result['anxiety_level']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Confidence: {result['confidence']:.2f}%")
    else:
        print("Error: Analysis failed.")

print("\n--- Tests Complete ---")
