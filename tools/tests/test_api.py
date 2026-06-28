import requests
import json

try:
    res = requests.post("http://127.0.0.1:5000/jarvis", json={"message": "hello"})
    print("Status Code:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", e)
