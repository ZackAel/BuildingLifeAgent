"""Calendar helpers for finding optimal task slots and meeting prep."""
from __future__ import annotations

import datetime
from typing import Iterable, Tuple

from schedule_utils import load_meetings
from gemini_api import ask_gemini

Task = Tuple[str, int]  # (task description, duration in minutes)


def schedule_tasks(tasks: Iterable[Task]) -> Iterable[Tuple[str, datetime.datetime, datetime.datetime]]:
    """Return a simple schedule for ``tasks`` around today's meetings.

    Meetings are loaded using :func:`schedule_utils.load_meetings` and tasks are
    placed in the earliest available slots between 09:00 and 17:00.
    """
    day = datetime.date.today()
    start = datetime.datetime.combine(day, datetime.time(9, 0))
    end = datetime.datetime.combine(day, datetime.time(17, 0))
    meetings = sorted(load_meetings(), key=lambda m: m[0])
    tasks_iter = iter(list(tasks))
    current = start
    schedule = []

    def next_task():
        try:
            return next(tasks_iter)
        except StopIteration:
            return None

    for meeting in meetings:
        while current + datetime.timedelta(minutes=5) <= meeting[0]:
            task = next_task()
            if not task:
                break
            dur = datetime.timedelta(minutes=task[1])
            if current + dur > meeting[0]:
                break
            schedule.append((task[0], current, current + dur))
            current += dur
        current = max(current, meeting[1])

    task = next_task()
    while task and current < end:
        dur = datetime.timedelta(minutes=task[1])
        if current + dur > end:
            break
        schedule.append((task[0], current, current + dur))
        current += dur
        task = next_task()

    return schedule


def meeting_prep_bot(docs: str) -> str:
    """If a meeting starts within 15 minutes, return a summary of ``docs``."""
    now = datetime.datetime.now()
    for start, end, desc in load_meetings():
        if now <= start <= now + datetime.timedelta(minutes=15):
            prompt = f"Summarize the following for upcoming meeting '{desc}':\n{docs}"
            return ask_gemini(prompt)
    return ""
