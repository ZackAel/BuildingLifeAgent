import datetime

MOOD_FILE = "data/mood_log.txt"

def log_mood(mood, note=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MOOD_FILE, "a") as f:
        f.write(f"{now},{mood},{note}\n")


def get_today_mood():
    today = datetime.date.today().isoformat()
    try:
        with open(MOOD_FILE, "r") as f:
            for line in reversed(f.readlines()):
                date, mood, note = line.strip().split(",", 2)
                if date == today:
                    return mood, note
        return None, None
    except FileNotFoundError:
        return None, None

def journaling_prompt():
    mood, _ = get_today_mood()
    base_prompts = [
        "What's one thing you're grateful for today?",
        "Describe a challenge and how you handled it.",
        "What energized you today?",
        "Write a short note to your future self.",
        "What made you smile today?"
    ]
    if mood:
        mood = mood.lower()
        if "stressed" in mood:
            return "What’s one small thing you can let go of today to reduce stress?"
        elif "happy" in mood:
            return "Capture this moment: What’s making you happy right now?"
        elif "tired" in mood:
            return "How can you recharge this evening? What does your body need?"
    import random
    return random.choice(base_prompts)

