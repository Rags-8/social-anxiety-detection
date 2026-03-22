import requests
import json
import time

def test_diversity():
    url = "http://localhost:8001/predict"
    payload = {"text": "I am very anxious about the presentation tomorrow. I feel judged by everyone."}
    
    all_suggestions = []
    
    print("Testing suggestion diversity (5 iterations)...")
    for i in range(5):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            suggestions = data.get("suggestions", [])
            print(f"Iteration {i+1} suggestions: {suggestions[:1]}...") # Print first one for brevity
            all_suggestions.append(tuple(sorted(suggestions)))
        except Exception as e:
            print(f"Error in iteration {i+1}: {e}")
            return
            
    unique_sets = len(set(all_suggestions))
    print(f"\nUnique suggestion sets: {unique_sets}/5")
    
    if unique_sets > 1:
        print("Success: Suggestions are diverse!")
    else:
        print("Failure: Suggestions are still the same!")

if __name__ == "__main__":
    test_diversity()
