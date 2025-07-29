import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

prompt = "Summarize the latest news about AI in 3 bullet points"
body = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=body)

if response.ok:
    data = response.json()
    print("\nGemini says:")
    print(data['candidates'][0]['content']['parts'][0]['text'])
else:
    print("Error:", response.status_code, response.text)
