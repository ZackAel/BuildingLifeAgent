import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MISSING_KEY_MSG = "GEMINI_API_KEY not found. AI features are unavailable."

def ask_gemini(prompt: str) -> str:
    if not API_KEY:
        return MISSING_KEY_MSG

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={API_KEY}"
    )
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.ok:
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Error: {response.status_code} {response.text}")


def has_api_key() -> bool:
    """Return True if the Gemini API key is configured."""
    return bool(API_KEY)
