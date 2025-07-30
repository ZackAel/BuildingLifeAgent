import datetime
import os

CONTACTS_FILE = 'data/contacts.csv'

def _ensure_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'a'):
            pass

def log_interaction(name: str):
    """Record an interaction with a contact."""
    if not name:
        return
    _ensure_file()
    now = datetime.date.today().isoformat()
    lines = {}
    try:
        with open(CONTACTS_FILE, 'r') as f:
            for line in f:
                if ',' in line:
                    n, date = line.strip().split(',', 1)
                    lines[n] = date
    except FileNotFoundError:
        pass
    lines[name] = now
    with open(CONTACTS_FILE, 'w') as f:
        for n, date in lines.items():
            f.write(f"{n},{date}\n")

def contacts_needing_ping(weeks: int = 2):
    """Return list of contacts not pinged in given weeks."""
    _ensure_file()
    threshold = datetime.date.today() - datetime.timedelta(weeks=weeks)
    stale = []
    with open(CONTACTS_FILE, 'r') as f:
        for line in f:
            if ',' not in line:
                continue
            name, date = line.strip().split(',', 1)
            try:
                last = datetime.date.fromisoformat(date)
                if last < threshold:
                    stale.append(name)
            except ValueError:
                continue
    return stale
