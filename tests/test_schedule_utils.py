import importlib
from pathlib import Path
import os
import datetime
import data_utils


def test_meetings_file_migration(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    old = Path("meetings.txt")
    old.write_text("2024-01-01,09:00-10:00,Test Meeting\n")
    # import after patching to trigger migration
    schedule_utils = importlib.import_module("schedule_utils")
    importlib.reload(schedule_utils)
    new_path = tmp_path / "data" / "meetings.txt"
    assert new_path.exists()
    assert not old.exists()
    assert schedule_utils.MEETINGS_FILE == "data/meetings.txt"
    with open(new_path) as f:
        assert "Test Meeting" in f.read()
    old.unlink(missing_ok=True)

def test_ensure_file_nested(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    p = data_utils.ensure_file("nested/file.txt")
    assert Path(p) == tmp_path / "nested" / "file.txt"
    assert Path(p).exists()



def test_task_history_prediction(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    schedule_utils = importlib.reload(importlib.import_module("schedule_utils"))
    schedule_utils.record_task_completion("Test", 30)
    schedule_utils.record_task_completion("Test", 60)
    assert schedule_utils.predict_task_duration("Test") == 45


def test_schedule_respects_predictions_and_meetings(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    schedule_utils = importlib.reload(importlib.import_module("schedule_utils"))
    schedule_utils.record_task_completion("Task1", 30)

    def fake_google_events():
        start = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 30))
        end = start + datetime.timedelta(minutes=30)
        return [(start, end, "Google Event")]

    monkeypatch.setattr(schedule_utils, "fetch_google_calendar_events", fake_google_events)
    monkeypatch.setattr(schedule_utils, "fetch_outlook_events", lambda: [])

    schedule = schedule_utils.intelligent_schedule(["Task1"])
    assert "09:00 - 09:30: Task1" in schedule
    assert "09:30 - 10:00: Google Event" in schedule
