import datetime
import os
from collections import Counter
from data_utils import ensure_file

MOOD_FILE = 'mood_log.txt'
TASK_FILE = 'tasks.txt'


def _load_moods(days: int = 7):
    path = ensure_file(MOOD_FILE)
    moods = []
    threshold = datetime.datetime.now() - datetime.timedelta(days=days)
    try:
        with open(path, 'r') as f:
            for line in f:
                ts, mood, _ = line.strip().split(',', 2)
                ts_dt = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                if ts_dt >= threshold:
                    moods.append(mood.lower())
    except FileNotFoundError:
        pass
    return moods


def _load_task_count(days: int = 7):
    path = ensure_file(TASK_FILE)
    try:
        with open(path, 'r') as f:
            return len([line for line in f if line.strip()])
    except FileNotFoundError:
        return 0


def burnout_warning():
    moods = _load_moods()
    mood_counter = Counter(moods)
    workload = _load_task_count()
    if workload > 10 and (mood_counter.get('stressed', 0) + mood_counter.get('tired', 0)) >= 3:
        return 'Your workload and recent mood suggest burnout risk. Consider reducing tasks and scheduling restorative breaks.'
    return None
