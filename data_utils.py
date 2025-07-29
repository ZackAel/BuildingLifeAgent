import os

DATA_DIR = "data"

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def ensure_file(filename):
    ensure_dir()
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        with open(path, "a"):
            pass
    return path

def get_path(filename):
    return os.path.join(DATA_DIR, filename)

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
