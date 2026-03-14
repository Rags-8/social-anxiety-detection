
import sys
import os

# Add the backend/app to path
sys.path.append(os.path.join(os.getcwd(), "backend", "app"))

from ml_utils import analyze_anxiety

test_cases = [
    # New cases for generalization
    ("I feel like everyone is staring at me during lunch.", "Moderate"), # Score 0, ML should catch social pressure
    ("I'm terrified of being judged by my peers.", "High"),            # Score 3 (terrified)
    ("I had a great time at the park today.", "Low"),                   # Score 0, ML should catch positive sentiment
    ("My heart starts pounding when I have to introduce myself.", "High"), # Score 3 (heart racing/pounding variant?) wait, heart racing is +3.
    ("I'm a bit shy but I manage.", "Moderate"),                       # Score 2 (shy)
    ("I feel overwhelmed when I'm in a large group of people.", "High"), # Score 3 (overwhelmed)
    ("I overthink every conversation I have.", "Moderate"),            # Score 2 (overthink)
    ("I enjoy meeting new people at the library.", "Low"),             # Score -2 (enjoy meeting people)
    ("I avoid going to the grocery store because of the crowds.", "High"), # Score 3 (avoid people/crowds)
]

print("Starting Generalization Tests...")
all_passed = True
for text, expected in test_cases:
    result = analyze_anxiety(text)
    if result:
        predicted = result["anxiety_level"]
        confidence = result["confidence"]
        # In this hybrid system, we want to see if it catches the spirit. 
        # For generalization, sometimes "expected" is subjective, but these are clear.
        if predicted == expected:
            print(f"PASS: '{text}' -> {predicted} ({confidence:.2f}%)")
        else:
            print(f"FAIL: '{text}' -> Got {predicted}, Expected {expected} ({confidence:.2f}%)")
            all_passed = False
    else:
        print(f"ERROR: Could not analyze '{text}'")
        all_passed = False

if all_passed:
    print("\nAll generalization test cases passed!")
else:
    print("\nSome test cases failed. This might be due to ML model bias or scoring gaps.")
