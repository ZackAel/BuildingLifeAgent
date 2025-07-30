import datetime
import os
from data_utils import ensure_file

MEETINGS_FILE = 'meetings.txt'


def load_meetings():
    """Return list of (start, end, desc) for today's meetings."""
    path = ensure_file(MEETINGS_FILE)
    today = datetime.date.today().isoformat()
    meetings = []
    try:
        with open(path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                date_part, time_part, desc = line.strip().split(',', 2)
                if date_part != today:
                    continue
                start_str, end_str = time_part.split('-')
                start = datetime.datetime.strptime(f"{date_part} {start_str}", '%Y-%m-%d %H:%M')
                end = datetime.datetime.strptime(f"{date_part} {end_str}", '%Y-%m-%d %H:%M')
                meetings.append((start, end, desc))
    except FileNotFoundError:
        pass
    return meetings


def intelligent_schedule(tasks):
    """Simple schedule that respects meetings and blocks focus/admin/breaks."""
    start_day = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
    end_day = datetime.datetime.combine(datetime.date.today(), datetime.time(18, 0))
    current = start_day
    meetings = load_meetings()
    schedule = []
    task_iter = iter(tasks)

    def next_task():
        try:
            return next(task_iter)
        except StopIteration:
            return None

    while current < end_day:
        # Check for upcoming meeting
        meeting = next((m for m in meetings if m[0] <= current < m[1]), None)
        if meeting:
            schedule.append(f"{meeting[0].strftime('%H:%M')} - {meeting[1].strftime('%H:%M')}: {meeting[2]}")
            current = meeting[1]
            continue

        if current.hour == 12 and current.minute == 30:
            lunch_end = current + datetime.timedelta(minutes=30)
            schedule.append(f"{current.strftime('%H:%M')} - {lunch_end.strftime('%H:%M')}: Lunch")
            current = lunch_end
            continue

        task = next_task()
        if not task:
            break
        end = current + datetime.timedelta(minutes=50)
        schedule.append(f"{current.strftime('%H:%M')} - {end.strftime('%H:%M')}: {task}")
        current = end
        # 10-min break
        if current < end_day:
            br_end = current + datetime.timedelta(minutes=10)
            schedule.append(f"{current.strftime('%H:%M')} - {br_end.strftime('%H:%M')}: Break")
            current = br_end

    return '\n'.join(schedule)
