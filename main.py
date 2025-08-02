import datetime
import os
import random
import sys
import time

from gemini_api import ask_gemini
from goals import load_goals
from mood import get_today_mood, journaling_prompt, log_mood
from motivation import get_motivational_message
from streak import get_current_streak, update_streak
from tasks import load_tasks, save_tasks, complete_task, record_task_date, get_task_age_days
from energy import compute_energy_index
from relationships import contacts_needing_ping, log_interaction
from learning import skill_progress
from guardrails import burnout_warning
from schedule_utils import intelligent_schedule
from notification_manager import NotificationManager


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

# initialize notification manager
notifier = NotificationManager()

def ensure_data_files():
    """Make sure data directory and files exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in [TASKS_FILE, GOALS_FILE, MOOD_FILE, STREAK_FILE, JOURNAL_FILE]:
        if not os.path.exists(path):
            with open(path, "a"):
                pass

def prioritize_tasks(tasks):
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
        record_task_date(task)
        print(f"✅ Task added: {task}")

def add_goal():
    goal = input("Enter a new goal (leave empty to cancel): ").strip()
    if goal:
        with open(GOALS_FILE, "a") as f:
            f.write(goal + "\n")
        print(f"✅ Goal added: {goal}")

def log_contact():
    name = input("Who did you interact with? ").strip()
    if name:
        log_interaction(name)
        print(f"✅ Interaction with {name} logged.")

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
        if any(k in mood.lower() for k in ["tired", "stressed"]):
            mindfulness_break()


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

def notify(message: str, actions: dict | None = None) -> None:
    """Display a notification. If actions provided, show interactive popup."""
    try:
        if actions:
            notifier.send_interactive(message, actions)
        else:
            notifier.send_alert(message)
    except Exception:
        # Notifications are optional; ignore errors quietly
        pass

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
        print("  [6] Log interaction with contact")
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
        elif choice == "6":
            log_contact()
        else:
            break

def check_stuck_tasks(tasks):
    for t in tasks:
        if get_task_age_days(t) > 2:
            print(f"🔄 '{t}' has been around for a while. Break it down or defer?")

def energy_based_suggestion(tasks, energy):
    if energy >= 70:
        print("\n⚡ Energy high! Ideal time for deep work.")
        if tasks:
            print("Focus on:", tasks[0])
    elif energy <= 40:
        print("\n😌 Energy low. Pick an easy task or take a break.")
    else:
        print("\nEnergy level is steady.")

def mindfulness_break():
    print("\n🧘 Let's take a 60-second breathing break.")
    for i in range(60, 0, -1):
        print(f"{i} ", end="", flush=True)
        time.sleep(1)
    print("\nDone!")

def conversational_response(text: str) -> str:
    if any(k in text.lower() for k in ["putting off", "stuck", "procrastinat"]):
        prompt = (
            f"The user says: '{text}'. Help them using a short 5-Whys coaching "
            "conversation and suggest small sub-tasks or accountability options."
        )
    else:
        prompt = f"Friendly productivity coach response to: '{text}'"
    return ask_gemini(prompt)

def chat_with_agent():
    msg = input("Anything you'd like to chat about? (Enter to skip) ").strip()
    if msg:
        print(conversational_response(msg))

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
        os.environ.setdefault("PYTHONWARNINGS", "ignore")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def run_agent():
    mentor_check_in()
    show_menu()
    chat_with_agent()
    print("🔄 Loading your tasks and goals...")

    try:
        tasks = load_tasks()
        goals = load_goals()
    except Exception as e:
        print(f"⚠️ Error loading tasks or goals: {e}")
        return

    summarize_journal()
    energy = compute_energy_index()
    print(f"\n⚡ Energy index: {energy}/100")

    try:
        print("\n📋 Prioritized Tasks:")
        print(prioritize_tasks(tasks))
        print("\n🗓️ Sample Daily Schedule:")
        print(create_schedule(tasks))
        print("\n🗓️ Intelligent Schedule:")
        print(intelligent_schedule(tasks))
    except Exception as e:
        print(f"⚠️ Error prioritizing tasks: {e}")

    try:
        print("\n🎯 Goal Check-in:")
        print(check_goals(goals))
    except Exception as e:
        print(f"⚠️ Error checking goals: {e}")

    try:
        progress = skill_progress()
        if progress:
            print("\n📚 Learning Progress:")
            for skill, count in progress.items():
                print(f"  {skill}: {count} completed task(s)")
    except Exception:
        pass

    try:
        stale = contacts_needing_ping()
        if stale:
            print("\n👥 Consider reaching out to:", ", ".join(stale))
    except Exception:
        pass

    try:
        warn = burnout_warning()
        if warn:
            print("\n⚠️ Burnout Guardrail:", warn)
    except Exception:
        pass

    try:
        print("\n💬 Motivational Message:")
        message = get_motivational_message()
        print(message)
        notify(message)
        notify(random_reminder())
        if tasks:
            def mark_first():
                task = tasks.pop(0)
                complete_task(task)
                save_tasks(tasks)
            notify(f"Next task: {tasks[0]}", actions={"Mark Done": mark_first, "Log Mood": add_mood})
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
    if energy <= 40:
        mindfulness_break()
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
    """Run the agent once in console mode."""
    ensure_data_files()
    run_agent()