from data_utils import ensure_file, get_path

def load_goals():
    path = ensure_file("goals.txt")
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_goal(goal):
    path = ensure_file("goals.txt")
    with open(path, "a") as f:
        f.write(goal + "\n")
