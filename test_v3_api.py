import requests
import json

url = "http://localhost:8001/analyze"
payload = {
    "text": "I feel very anxious right now.",
    "history": ["I had a panic attack yesterday.", "Everything feels overwhelming."]
}
headers = {"Content-Type": "application/json"}

try:
    print("Sending request to /analyze...")
    response = requests.post(url, json=payload, timeout=120)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
