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
