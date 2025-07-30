from typing import List, Tuple
from data_utils import ensure_file


BOARD_FILE = ensure_file("community_board.txt")


def post_commitment(user: str, goal: str) -> None:
    """Post a commitment to the community board."""
    with open(BOARD_FILE, "a") as f:
        f.write(f"{user}:{goal}\n")


def get_commitments() -> List[Tuple[str, str]]:
    """Return list of (user, goal) from the board."""
    commitments = []
    try:
        with open(BOARD_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                user, goal = line.strip().split(":", 1)
                commitments.append((user, goal))
    except FileNotFoundError:
        pass
    return commitments
