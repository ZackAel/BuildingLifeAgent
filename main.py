import time
import argparse
import sys
import os
import datetime
from gemini_api import ask_gemini
from tasks import load_tasks, save_tasks
from goals import load_goals
from motivation import get_motivational_message
from mood import log_mood, get_today_mood, journaling_prompt
import random
from streak import update_streak, get_current_streak
from streak import get_current_streak
from mood import get_today_mood
import datetime


# === CONFIGURATION ===
DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.txt")
GOALS_FILE = os.path.join(DATA_DIR, "goals.txt")
MOOD_FILE = os.path.join(DATA_DIR, "mood_log.txt")
STREAK_FILE = os.path.join(DATA_DIR, "streak.txt")
JOURNAL_FILE = os.path.join(DATA_DIR, "journal.txt")
ACTIVITY_FILE = "data/activity_log.txt"

DEFAULT_INTERVAL_SECONDS = 3600  # 1 hour
TEST_INTERVAL_SECONDS = 60       # 1 minute (for quick testing)

def ensure_data_files():
    """Make sure data directory and files exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in [TASKS_FILE, GOALS_FILE, MOOD_FILE, STREAK_FILE, JOURNAL_FILE]:
        if not os.path.exists(path):
            with open(path, "a"):
                pass

def prioritize_tasks(tasks):
    from mood import get_today_mood
    import datetime
    mood, _ = get_today_mood()
    hour = datetime.datetime.now().hour
    prompt = "Prioritize these tasks for today"
    if mood:
        prompt += f" (user is feeling {mood})"
    if 6 <= hour < 12:
        prompt += " (it's morning)"
    elif 12 <= hour < 18:
        prompt += " (it's afternoon)"
    elif 18 <= hour < 23:
        prompt += " (it's evening)"
    prompt += ":\n" + "\n".join(f"- {t}" for t in tasks)
    return ask_gemini(prompt)

def mentor_check_in():
    print("\n👤 Mentor Check-In:")
    last_mood, _ = get_today_mood()
    print("What is one tiny step you could do right now for your main goal?")
    input("(Type it or press Enter to skip): ")

    if last_mood:
        print(f"Based on your mood ({last_mood}), remember: progress isn't always linear. Keep showing up!")
mentor_check_in()


def check_goals(goals):
    """Ask Gemini for a supportive check-in on goals."""
    prompt = "Here are my goals:\n" + "\n".join(f"- {g}" for g in goals) + \
             "\nHow am I doing today? Give a supportive check-in."
    return ask_gemini(prompt)

def add_task():
    task = input("Enter a new task (leave empty to cancel): ").strip()
    if task:
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)
        print(f"✅ Task added: {task}")

def add_goal():
    goal = input("Enter a new goal (leave empty to cancel): ").strip()
    if goal:
        with open(GOALS_FILE, "a") as f:
            f.write(goal + "\n")
        print(f"✅ Goal added: {goal}")

reminders = [
    "Take a moment to stand up and stretch! 🧘",
    "Drink some water 💧",
    "Look away from your screen for 20 seconds 👀",
    "Take a deep breath and check in with yourself 🌱",
    "Good job! Keep up the great work 🚀"
]

def random_reminder():
    mood, _ = get_today_mood()
    if not mood:
        return random.choice(reminders)
    mood = mood.lower()
    if "tired" in mood:
        return "Take a 5-minute stretch and let your eyes rest! 💤"
    if "stressed" in mood:
        return "Pause for three deep breaths. Small breaks help! 🌱"
    if "happy" in mood or "motivated" in mood:
        return "Ride that positive wave! What’s your next move?"
    return random.choice(reminders)


def log_activity(action, detail="", mood=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACTIVITY_FILE, "a") as f:
        f.write(f"{now},{action},{detail},{mood}\n")


def add_mood():
    print("\nHow are you feeling today? (e.g. happy, stressed, calm, tired, motivated, etc.)")
    mood = input("Your mood: ").strip()
    if mood:
        note = input("Want to add a short note or skip? (press Enter to skip): ").strip()
        log_mood(mood, note)
        print("✅ Mood logged!")

from mood import get_today_mood

def mood_based_message():
    mood, note = get_today_mood()
    if not mood:
        return "Take care of yourself today!"
    mood = mood.lower()
    if "stressed" in mood or "tired" in mood:
        return "You’re doing your best! Try a 2-minute break and breathe. 🌱"
    elif "happy" in mood or "motivated" in mood:
        return "Keep up the good energy! 🚀 What’s one thing you’re excited to tackle next?"
    elif "calm" in mood:
        return "Great to hear you’re calm. Remember to pace yourself today."
    else:
        return "Every feeling is valid. You got this!"

def notify(message):
    try:
        import platform
        if platform.system() == "Darwin":
            os.system(f"""osascript -e 'display notification "{message}" with title "AI Agent"'""")
        elif platform.system() == "Linux":
            os.system(f'notify-send "AI Agent" "{message}"')
        # Windows notification can be added with plyer
    except Exception:
        pass
run_agent()

def show_progress_bars():
    try:
        streak = get_current_streak()
        done = 0
        total = len(load_tasks())
        with open("data/completed_tasks.txt", "r") as f:
            done = len([l for l in f if l.strip()])
        task_bar = "🟩" * done + "⬜" * (total)
        print(f"Tasks: {task_bar} ({done}/{total})")
        streak_bar = "🔥" * streak
        print(f"Streak: {streak_bar} ({streak})")
    except Exception:
        pass


def show_journaling_prompt():
    prompt = journaling_prompt()
    print("\nMini Reflection / Journaling Prompt:")
    print(f"  {prompt}")
    note = input("Your response (or press Enter to skip): ")
    if note:
        with open(JOURNAL_FILE, "a") as f:
            today = datetime.date.today().isoformat()
            f.write(f"{today}: {prompt} | {note}\n")
        print("📝 Response saved!")

def show_menu():
    while True:
        print("\nAI Agent Menu:")
        print("  [1] Add new task")
        print("  [2] Add new goal")
        print("  [3] Log my mood")
        print("  [4] Get a journaling prompt")
        print("  [5] Mark a task as completed")
        print("  [ENTER] Continue\n")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_task()
        elif choice == "2":
            add_goal()
        elif choice == "3":
            add_mood()
        elif choice == "4":
            show_journaling_prompt()
        elif choice == "5":
            tasks = load_tasks()
            for i, t in enumerate(tasks, 1):
                print(f"    [{i}] {t}")
            idx = input("Select task number to mark as completed: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(tasks):
                task = tasks.pop(int(idx) - 1)
                complete_task(task)
                save_tasks(tasks)
                print(f"✅ Task completed: {task}")
            else:   
                print("Invalid selection.")
        else:
            break

def summarize_journal():
    try:
        with open("data/journal.txt", "r") as f:
            entries = [l.strip() for l in f.readlines() if l.strip()][-7:]
        if entries:
            summary = ask_gemini("Summarize the key themes from these journal entries:\n" + "\n".join(entries))
            print("\n📝 Weekly Reflection Summary:\n", summary)
    except Exception:
        pass

def show_task_progress():
    total = len(load_tasks())
    try:
        with open("data/completed_tasks.txt", "r") as f:
            done = len([l for l in f if l.strip()])
    except FileNotFoundError:
        done = 0
    bar = "🟩" * done + "⬜" * (max(total - done, 0))
    print(f"Task Progress: {bar} ({done}/{done+total})")

def sync_with_notion():
    # TODO: Connect to Notion API, push/pull tasks
    pass

def speak(text):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def run_agent():
    show_menu()
    print("🔄 Loading your tasks and goals...")

    try:
        tasks = load_tasks()
        goals = load_goals()
    except Exception as e:
        print(f"⚠️ Error loading tasks or goals: {e}")
        return

    summarize_journal()

    try:
        print("\n📋 Prioritized Tasks:")
        print(prioritize_tasks(tasks))
        print("\n🗓️ Sample Daily Schedule:")
        print(create_schedule(tasks))
    except Exception as e:
        print(f"⚠️ Error prioritizing tasks: {e}")

    try:
        print("\n🎯 Goal Check-in:")
        print(check_goals(goals))
    except Exception as e:
        print(f"⚠️ Error checking goals: {e}")

    try:
        print("\n💬 Motivational Message:")
        print(get_motivational_message())
        notify(random_reminder())
    except Exception as e:
        print(f"⚠️ Error fetching motivational message: {e}")

    # Show progress bars
    show_progress_bars()

    # Suggest habit/routine changes
    suggest_routine_change()
    
    # NEW: Show current streak
    try:
        streak = get_current_streak()
        print(f"\n🔥 Current streak: {streak} day(s) of daily check-ins!")
        print_streak_bar(streak)  # <-- Add this line
        if streak and streak % 5 == 0:
            print("🏆 Amazing! You've hit a 5-day streak! Treat yourself to something nice today.")

    except Exception:
        pass


    # NEW: Mini daily reflection prompt
    print("\n📝 Mini Reflection:")
    print(journaling_prompt())
    input("Take a moment to reflect (press Enter when ready)...")

    print("\n⏰ Quick Reminder:", random_reminder())
    print("\n✅ Done! Will repeat after interval...\n")

def suggest_routine_change():
    try:
        with open("data/mood_log.txt", "r") as f:
            last_week = [l.strip() for l in f.readlines() if l.strip()][-7:]
        if not last_week:
            return
        tired_count = sum("tired" in l for l in last_week)
        stressed_count = sum("stressed" in l for l in last_week)
        if tired_count >= 3:
            print("🔁 Noticing you often feel tired. Consider shifting your bedtime, or adding a short walk during your afternoon.")
        if stressed_count >= 3:
            print("🌱 Stress is showing up a lot. Maybe try scheduling a no-meeting block or a midday relaxation.")
    except Exception:
        pass


def print_streak_bar(streak):
    bar = "🟩" * streak
    print(f"Streak: {bar} ({streak})")

def create_schedule(tasks):
    # Example with Gemini (can swap for local logic)
    prompt = (
        "Plan a daily schedule from 9am to 6pm. "
        "Distribute these tasks, add a 10-min break every hour, "
        "add a 30-min lunch at 12:30pm, suggest focus/deep work blocks, and order tasks logically:\n"
        + "\n".join(f"- {t}" for t in tasks)
    )
    return ask_gemini(prompt)


def countdown(seconds):
    print(f"⏳ Waiting {seconds//60} min {seconds%60} sec until next check-in...")
    try:
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            print(f"\r⏰ Next check-in in: {time_str} ", end="")
            time.sleep(1)
        print("\r", end="")  # Clear line
    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully. Have a great day!")
        sys.exit(0)

if __name__ == "__main__":
    ensure_data_files()
    parser = argparse.ArgumentParser(description="Your AI Productivity Agent")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS,
                        help="Seconds between check-ins (default: 3600, 1 hour). Use a lower number to test quickly.")
    args = parser.parse_args()
    interval = args.interval

    print("Your AI Agent is running! (Press Ctrl+C to exit)\n")
    try:
        while True:
            run_agent()
            countdown(interval)
    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully. Have a great day!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
