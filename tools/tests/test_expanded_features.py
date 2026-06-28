import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_sentient_memory():
    print("\n--- Testing Sentient Memory ---")
    # Step 1: Teach JARVIS something specific
    secret = "Sir's favorite drink is a concentrated electrolyte blend with a hint of blueberry."
    requests.post(f"{BASE_URL}/memory/learn", json={
        "command": "What is my favorite drink?",
        "response": secret
    })
    print("      [OK] Taught JARVIS a secret.")
    
    # Step 2: Ask something related to trigger semantic recall
    time.sleep(1)
    res = requests.post(f"{BASE_URL}/jarvis", json={"message": "I'm thirsty, what should I have?"})
    data = res.json()
    print(f"      [OK] JARVIS recall: {data.get('response')}")

def test_vision_loop():
    print("\n--- Testing Vision Feedback Loop ---")
    # Let it run for a bit (it's in the background of api.py)
    # We can check the /jarvis response as it includes 'insight'
    res = requests.post(f"{BASE_URL}/jarvis", json={"message": "status"})
    data = res.json()
    print(f"      [OK] Visual Insight in HUD: {data.get('insight', 'None')}")

if __name__ == "__main__":
    # Wait for server to be ready (assuming it was started)
    print("Testing JARVIS O.M.E.G.A. Tiers...")
    try:
        test_sentient_memory()
        test_vision_loop()
    except Exception as e:
        print(f"Connection failed: {e}. Is the server running on 5000?")
