from data_utils import ensure_file

QUEST_FILE = "quests.txt"
XP_FILE = "xp.txt"


def load_quests():
    path = ensure_file(QUEST_FILE)
    quests = []
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            desc, xp_str = line.strip().split("|", 1)
            quests.append((desc, int(xp_str)))
    return quests


def add_quest(description: str, xp: int) -> None:
    path = ensure_file(QUEST_FILE)
    with open(path, "a") as f:
        f.write(f"{description}|{int(xp)}\n")


def _get_xp_path():
    return ensure_file(XP_FILE)


def get_xp() -> int:
    path = _get_xp_path()
    try:
        with open(path, "r") as f:
            return int(f.read().strip() or 0)
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0


def _save_xp(xp: int) -> None:
    path = _get_xp_path()
    with open(path, "w") as f:
        f.write(str(xp))


def add_xp(amount: int) -> int:
    xp = get_xp() + int(amount)
    _save_xp(xp)
    return xp


def complete_quest(description: str) -> int:
    quests = load_quests()
    remaining = []
    gained = 0
    for desc, xp in quests:
        if desc == description:
            gained = xp
        else:
            remaining.append((desc, xp))
    path = ensure_file(QUEST_FILE)
    with open(path, "w") as f:
        for desc, xp in remaining:
            f.write(f"{desc}|{xp}\n")
    if gained:
        add_xp(gained)
    return gained
