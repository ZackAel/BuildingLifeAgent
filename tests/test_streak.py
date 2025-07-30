import datetime
import streak


def freeze_date(monkeypatch, date_value):
    class FakeDate(datetime.date):
        @classmethod
        def today(cls):
            return date_value
    monkeypatch.setattr(streak.datetime, "date", FakeDate)


def test_update_and_get_streak(tmp_path, monkeypatch):
    monkeypatch.setattr(streak, "STREAK_FILE", tmp_path / "streak.txt")

    freeze_date(monkeypatch, datetime.date(2023, 1, 1))
    assert streak.update_streak() == 1
    assert streak.get_current_streak() == 1

    freeze_date(monkeypatch, datetime.date(2023, 1, 2))
    assert streak.update_streak() == 2
    assert streak.get_current_streak() == 2

    freeze_date(monkeypatch, datetime.date(2023, 1, 4))
    assert streak.update_streak() == 1
    assert streak.get_current_streak() == 1



def test_update_streak_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr(streak, "STREAK_FILE", tmp_path / "streak.txt")
    # create empty file
    open(streak.STREAK_FILE, "w").close()

    freeze_date(monkeypatch, datetime.date(2023, 1, 5))
    assert streak.update_streak() == 1
    assert streak.get_current_streak() == 1
