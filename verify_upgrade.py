import sys
import os
import json
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.ml_utils import analyze_anxiety

def test_api_upgrade():
    test_cases = [
        "I'm feeling a bit nervous about the meeting tomorrow, but I think I'll be fine.",
        "I am absolutely terrified of the party tonight. My heart is racing just thinking about it.",
        "I feel confident and happy to meet my new colleagues today!"
    ]
    
    for i, text in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: '{text}' ---")
        result = analyze_anxiety(text)
        if result:
            print(f"Detected Level: {result['anxiety_level']}")
            print(f"Confidence: {result['confidence']:.2f}%")
            print(f"Explanation: {result['explanation']}")
            print("Suggestions:")
            for s in result['suggestions']:
                print(f"  - {s}")
        else:
            print("Error: Analysis failed.")

if __name__ == "__main__":
    test_api_upgrade()
