from typing import Dict, List


def _jaccard(a: set, b: set) -> float:
    """Return Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def match_partners(user_goals: Dict[str, List[str]]) -> Dict[str, str]:
    """Return best match for each user based on goal overlap."""
    users = list(user_goals.keys())
    goal_sets = {u: set(g) for u, g in user_goals.items()}
    matches: Dict[str, str] = {}
    for u in users:
        best_match = None
        best_score = -1.0
        for v in users:
            if u == v:
                continue
            score = _jaccard(goal_sets[u], goal_sets[v])
            if score > best_score:
                best_score = score
                best_match = v
        if best_match is not None:
            matches[u] = best_match
    return matches
