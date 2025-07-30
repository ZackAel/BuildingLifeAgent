import datetime
from mood import get_today_mood
from data_utils import ensure_file

ENERGY_FILE = ensure_file("energy_log.txt")


def compute_energy_index() -> int:
    """Compute a simple energy index based on time of day and mood."""
    now = datetime.datetime.now()
    base = 50
    hour = now.hour
    if 6 <= hour < 12:
        base += 20
    elif 12 <= hour < 18:
        base += 10
    elif 18 <= hour < 22:
        base += 0
    else:
        base -= 10

    mood, _ = get_today_mood()
    if mood:
        mood = mood.lower()
        if "tired" in mood or "stressed" in mood:
            base -= 15
        elif "happy" in mood or "motivated" in mood:
            base += 15
    index = max(0, min(100, base))
    log_energy(index)
    return index


def log_energy(index: int) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ENERGY_FILE, "a") as f:
        f.write(f"{timestamp},{index}\n")


def get_last_energy() -> int:
    try:
        with open(ENERGY_FILE, "r") as f:
            line = list(f.readlines())[-1]
            return int(line.strip().split(",")[1])
    except Exception:
        return 50
