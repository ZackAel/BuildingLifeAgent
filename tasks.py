from data_utils import ensure_file, get_path
import datetime

# File storing when tasks were first added
TASK_DATES_FILE = ensure_file("task_dates.txt")

def load_tasks():
    path = ensure_file("tasks.txt")
    with open(path, "r") as f:
        tasks = []
        for line in f:
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.startswith(("def ", "from ", "import ")):
                continue
            tasks.append(cleaned)
        return tasks

def save_tasks(tasks):
    path = ensure_file("tasks.txt")
    with open(path, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def complete_task(task):
    path = ensure_file("completed_tasks.txt")
    with open(path, "a") as f:
        f.write(task + "\n")

    # remove task date entry when completed
    try:
        lines = []
        with open(TASK_DATES_FILE, "r") as fdates:
            lines = [l for l in fdates.readlines() if l.strip() and not l.startswith(task + "|")]
        with open(TASK_DATES_FILE, "w") as fdates:
            fdates.writelines(lines)
    except Exception:
        pass

def record_task_date(task: str) -> None:
    """Record the date a task was added."""
    today = datetime.date.today().isoformat()
    with open(TASK_DATES_FILE, "a") as f:
        f.write(f"{task}|{today}\n")

def get_task_age_days(task: str) -> int:
    """Return how many days ago the task was first logged."""
    try:
        with open(TASK_DATES_FILE, "r") as f:
            for line in f:
                if line.startswith(task + "|"):
                    date_str = line.strip().split("|", 1)[1]
                    added = datetime.date.fromisoformat(date_str)
                    return (datetime.date.today() - added).days
    except Exception:
        pass
    return 0
