import importlib
from pathlib import Path
import os
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
