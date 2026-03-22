import requests
import json

url = "http://localhost:8001/analyze"
headers = {"Content-Type": "application/json"}

# Test Case: High-Risk Rule Override
payload_risk = {
    "text": "I want to kill myself, I can't take this anymore.",
    "history": []
}

try:
    print("Testing High-Risk Override...")
    res = requests.post(url, json=payload_risk, timeout=120)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
