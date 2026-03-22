import requests
import json

def test_deletion():
    base_url = "http://localhost:8001"
    
    # 1. Create a dummy prediction
    print("Creating dummy prediction...")
    payload = {"text": "DELETE_TEST_MESSAGE"}
    response = requests.post(f"{base_url}/predict", json=payload)
    if response.status_code != 200:
        print(f"Failed to create prediction: {response.text}")
        return
        
    # 2. Find the ID of the dummy prediction in history
    print("Fetching history...")
    response = requests.get(f"{base_url}/history")
    history = response.json()
    test_item = next((item for item in history if item['text'] == "DELETE_TEST_MESSAGE"), None)
    
    if not test_item:
        print("Failed to find dummy prediction in history.")
        return
    
    item_id = test_item['id']
    print(f"Found dummy prediction with ID: {item_id}")
    
    # 3. Delete the dummy prediction
    print(f"Deleting item {item_id}...")
    response = requests.delete(f"{base_url}/history/{item_id}")
    if response.status_code == 200:
        print("Delete request successful.")
    else:
        print(f"Delete request failed: {response.status_code} - {response.text}")
        return
        
    # 4. Verify it's gone
    print("Verifying deletion...")
    response = requests.get(f"{base_url}/history")
    history = response.json()
    test_item_after = next((item for item in history if item['id'] == item_id), None)
    
    if not test_item_after:
        print("Success: Item is no longer in history!")
    else:
        print("Failure: Item still exists in history!")

if __name__ == "__main__":
    test_deletion()
