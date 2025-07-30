import datetime
import mood

class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2023, 1, 1)

class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2023, 1, 1, 12, 0, 0)


def test_log_mood_writes_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(mood, "MOOD_FILE", tmp_path / "mood_log.txt")
    monkeypatch.setattr(mood.datetime, "datetime", FixedDateTime)
    mood.log_mood("Happy", "Great")
    content = (tmp_path / "mood_log.txt").read_text().strip()
    assert "Happy,Great" in content


def test_get_today_mood(tmp_path, monkeypatch):
    monkeypatch.setattr(mood, "MOOD_FILE", tmp_path / "mood_log.txt")
    monkeypatch.setattr(mood.datetime, "date", FixedDate)
    (tmp_path / "mood_log.txt").write_text("2023-01-01,Happy,Great\n")
    assert mood.get_today_mood() == ("Happy", "Great")


def test_journaling_prompt(monkeypatch):
    monkeypatch.setattr(mood, "get_today_mood", lambda: ("stressed", ""))
    prompt = mood.journaling_prompt()
    assert "reduce stress" in prompt
