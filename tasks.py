from data_utils import ensure_file, get_path

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
