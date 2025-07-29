from data_utils import ensure_file, get_path

def load_tasks():
    path = ensure_file("tasks.txt")
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_tasks(tasks):
    path = ensure_file("tasks.txt")
    with open(path, "w") as f:
        for task in tasks:
            f.write(task + "\n")

def complete_task(task):
    path = ensure_file("completed_tasks.txt")
    with open(path, "a") as f:
        f.write(task + "\n")
