from gemini_api import ask_gemini

def get_motivational_message():
    prompt = "Give me a short, powerful motivational message for someone building their dream AI agent."
    return ask_gemini(prompt)
