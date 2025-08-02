import datetime
import json
import os
from data_utils import ensure_file, get_path

OLD_MEETINGS_FILE = "meetings.txt"
MEETINGS_FILE = "data/meetings.txt"
TASK_HISTORY_FILE = "data/task_history.json"

# migrate old meetings file if needed
new_path = get_path(MEETINGS_FILE)
if os.path.exists(OLD_MEETINGS_FILE) and not os.path.exists(new_path):
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    os.rename(OLD_MEETINGS_FILE, new_path)


def load_meetings():
    """Return list of (start, end, desc) for today's meetings including calendar events."""
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

    # merge external calendar events
    meetings.extend(fetch_google_calendar_events())
    meetings.extend(fetch_outlook_events())

    # add a default lunch break
    lunch_start = datetime.datetime.combine(datetime.date.today(), datetime.time(12, 30))
    lunch_end = lunch_start + datetime.timedelta(minutes=30)
    meetings.append((lunch_start, lunch_end, "Lunch"))

    meetings.sort(key=lambda m: m[0])
    return meetings

def fetch_google_calendar_events():
    """Fetch today's events from Google Calendar using service account credentials."""
    creds_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    if not creds_file:
        return []
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception:
        return []

    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        start = datetime.datetime.combine(datetime.date.today(), datetime.time.min).isoformat() + 'Z'
        end = datetime.datetime.combine(datetime.date.today(), datetime.time.max).isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=start, timeMax=end,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
    except Exception:
        return []

    meetings = []
    for event in events:
        start_time = event['start'].get('dateTime') or event['start'].get('date')
        end_time = event['end'].get('dateTime') or event['end'].get('date')
        if not start_time or not end_time:
            continue
        try:
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except Exception:
            continue
        meetings.append((start_dt, end_dt, event.get('summary', 'Google Event')))
    return meetings


def fetch_outlook_events():
    """Fetch today's events from Outlook using Microsoft Graph API."""
    token = os.getenv("OUTLOOK_TOKEN")
    if not token:
        return []
    try:
        import requests
    except Exception:
        return []

    start = datetime.datetime.combine(datetime.date.today(), datetime.time.min).isoformat()
    end = datetime.datetime.combine(datetime.date.today(), datetime.time.max).isoformat()
    url = (
        "https://graph.microsoft.com/v1.0/me/calendarview"
        f"?startDateTime={start}&endDateTime={end}"
    )
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json().get('value', [])
    except Exception:
        return []

    meetings = []
    for event in data:
        try:
            start_dt = datetime.datetime.fromisoformat(event['start']['dateTime'])
            end_dt = datetime.datetime.fromisoformat(event['end']['dateTime'])
        except Exception:
            continue
        meetings.append((start_dt, end_dt, event.get('subject', 'Outlook Event')))
    return meetings


def load_task_history():
    path = ensure_file(TASK_HISTORY_FILE)
    try:
        with open(path) as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_task_history(history):
    path = ensure_file(TASK_HISTORY_FILE)
    with open(path, 'w') as f:
        json.dump(history, f)


def record_task_completion(task, duration_minutes):
    """Record the completion time for a task."""
    history = load_task_history()
    history.setdefault(task, []).append(duration_minutes)
    save_task_history(history)


def predict_task_duration(task, default=50):
    """Predict task duration in minutes based on history."""
    history = load_task_history()
    durations = history.get(task)
    if not durations:
        return default
    return sum(durations) / len(durations)



def intelligent_schedule(tasks):
    """Schedule tasks around meetings using predicted durations."""
    start_day = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
    end_day = datetime.datetime.combine(datetime.date.today(), datetime.time(18, 0))
    current = start_day
    meetings = load_meetings()
    schedule = []
    task_index = 0

    def schedule_tasks_until(limit):
        nonlocal current, task_index
        while task_index < len(tasks) and current < limit:
            task = tasks[task_index]
            duration = datetime.timedelta(minutes=predict_task_duration(task))
            if current + duration > limit:
                break
            end = current + duration
            schedule.append(f"{current.strftime('%H:%M')} - {end.strftime('%H:%M')}: {task}")
            current = end
            # 10-min break if it fits before the limit
            br_end = current + datetime.timedelta(minutes=10)
            if br_end <= limit:
                schedule.append(f"{current.strftime('%H:%M')} - {br_end.strftime('%H:%M')}: Break")
                current = br_end
            task_index += 1

    for meeting in meetings:
        schedule_tasks_until(meeting[0])
        if current <= meeting[0]:
            current = meeting[0]
        if current < meeting[1]:
            schedule.append(f"{meeting[0].strftime('%H:%M')} - {meeting[1].strftime('%H:%M')}: {meeting[2]}")
            current = meeting[1]
    schedule_tasks_until(end_day)

    return '\n'.join(schedule)
