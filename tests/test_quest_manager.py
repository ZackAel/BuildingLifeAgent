from game_engine import quest_manager
import data_utils


def test_quest_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    quest_manager.add_quest("defeat bug", 10)
    assert quest_manager.load_quests() == [("defeat bug", 10)]
    assert quest_manager.get_xp() == 0
    gained = quest_manager.complete_quest("defeat bug")
    assert gained == 10
    assert quest_manager.get_xp() == 10
    assert quest_manager.load_quests() == []
