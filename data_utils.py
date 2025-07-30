import os

DATA_DIR = "data"

def ensure_dir():
    os.makedirs(str(DATA_DIR), exist_ok=True)

def ensure_file(filename):
    """Ensure a file exists within ``DATA_DIR`` and return its path."""
    ensure_dir()
    data_dir = str(DATA_DIR)
    if os.path.isabs(filename):
        path = filename
    elif os.path.normpath(filename).startswith(data_dir + os.sep):
        path = filename
    else:
        path = os.path.join(data_dir, filename)

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "a"):
            pass
    return path

def get_path(filename):
    return os.path.join(str(DATA_DIR), filename)
