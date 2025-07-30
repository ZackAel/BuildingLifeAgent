import os
from collections import defaultdict
from data_utils import ensure_file

TASK_FILE = 'tasks.txt'
COMPLETED_FILE = 'completed_tasks.txt'


def _load_lines(file: str):
    path = ensure_file(file)
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def _parse_task(line: str):
    if '|' in line:
        task, skill = [part.strip() for part in line.split('|', 1)]
        return task, skill
    return line, None


def skill_progress():
    """Return mapping of skill -> completed count."""
    lines = _load_lines(COMPLETED_FILE)
    counts = defaultdict(int)
    for line in lines:
        _, skill = _parse_task(line)
        if skill:
            counts[skill] += 1
    return counts


def skills_from_tasks():
    """Return set of skills from tasks list."""
    lines = _load_lines(TASK_FILE)
    skills = set()
    for line in lines:
        _, skill = _parse_task(line)
        if skill:
            skills.add(skill)
    return skills
