import requests
import time
import sys

def verify():
    url = "http://localhost:8000/analyze"
    payload = {"text": "I feel nervous when talking to people."}
    
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("Server is up!")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    else:
        print("Server failed to start in time.")
        sys.exit(1)

    print(f"Testing {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Response:", data)
        
        # Basic validation
        assert "anxiety_level" in data
        assert "suggestions" in data
        print("Verification Successful!")
    except Exception as e:
        print(f"Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
