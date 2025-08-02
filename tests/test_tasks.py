import os
import tasks
import data_utils


def test_save_and_load_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    sample = [{"name": "task1", "difficulty": "short"}, {"name": "task2", "difficulty": "long"}]
    tasks.save_tasks(sample)
    assert (tmp_path / "tasks.txt").exists()
    assert tasks.load_tasks() == ["task1", "task2"]
    detailed = tasks.load_tasks_with_difficulty()
    assert detailed == sample


def test_load_tasks_skips_code_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    path = tmp_path / "tasks.txt"
    path.write_text("task1|short\nimport os\ndef foo(): pass\nfrom x import y\n")
    assert tasks.load_tasks() == ["task1"]
    assert tasks.load_tasks_with_difficulty() == [{"name": "task1", "difficulty": "short"}]


def test_complete_task(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    tasks.complete_task("done")
    with open(tmp_path / "completed_tasks.txt") as f:
        assert f.read().strip() == "done"
