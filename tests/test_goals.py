import goals
import data_utils


def test_save_and_load_goal(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    goals.save_goal("Goal 1")
    goals.save_goal("Goal 2")
    assert goals.load_goals() == ["Goal 1", "Goal 2"]
