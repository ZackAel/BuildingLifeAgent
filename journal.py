import datetime
from data_utils import ensure_file

JOURNAL_FILE = ensure_file("journal.txt")

def log_entry(text: str) -> None:
    """Append a journal entry with timestamp."""
    if not text:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(JOURNAL_FILE, "a") as f:
        f.write(f"{timestamp} | {text}\n")


def load_entries(count: int = 10):
    """Return the last `count` journal entries."""
    path = ensure_file("journal.txt")
    try:
        with open(path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines[-count:]
    except FileNotFoundError:
        return []
