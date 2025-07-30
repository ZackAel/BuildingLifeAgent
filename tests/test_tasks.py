import os
import tasks
import data_utils


def test_save_and_load_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    tasks.save_tasks(["task1", "task2"])
    assert (tmp_path / "tasks.txt").exists()
    assert tasks.load_tasks() == ["task1", "task2"]


def test_load_tasks_skips_code_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    path = tmp_path / "tasks.txt"
    path.write_text("task1\nimport os\ndef foo(): pass\nfrom x import y\n")
    assert tasks.load_tasks() == ["task1"]


def test_complete_task(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    tasks.complete_task("done")
    with open(tmp_path / "completed_tasks.txt") as f:
        assert f.read().strip() == "done"
