import datetime
import os

STREAK_FILE = "data/streak.txt"

def update_streak():
    today = datetime.date.today()
    if not os.path.exists(STREAK_FILE):
        with open(STREAK_FILE, "w") as f:
            f.write(f"{today.isoformat()},1\n")
        return 1

    with open(STREAK_FILE, "r") as f:
        lines = f.readlines()
        if not lines:
            # Empty file; initialize streak
            last_date = today - datetime.timedelta(days=1)
            streak = 0
        else:
            last = lines[-1].strip()
            last_date_str, streak_str = last.split(",")
            last_date = datetime.date.fromisoformat(last_date_str)
            streak = int(streak_str)

    if today == last_date:
        return streak
    elif today == last_date + datetime.timedelta(days=1):
        streak += 1
    else:
        streak = 1

    with open(STREAK_FILE, "a") as f:
        f.write(f"{today.isoformat()},{streak}\n")
    return streak

def get_current_streak():
    if not os.path.exists(STREAK_FILE):
        return 0
    with open(STREAK_FILE, "r") as f:
        lines = f.readlines()
        if not lines:
            return 0
        last = lines[-1].strip()
        _, streak_str = last.split(",")
        return int(streak_str)
