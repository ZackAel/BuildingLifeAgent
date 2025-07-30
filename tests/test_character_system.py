from game_engine import character_system
import data_utils


def test_pet_stage():
    assert character_system.get_pet_stage(0) == "egg"
    assert character_system.get_pet_stage(6) == "baby"
    assert character_system.get_pet_stage(12) == "teen"


def test_skill_unlock():
    skills = character_system.unlocked_skills(10)
    assert "Focus Mode" in skills
    assert "Deep Work" in skills
    assert "Hyper Productivity" not in skills


def test_guild_join(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    character_system.join_guild("Adventurers", "Alice")
    character_system.join_guild("Adventurers", "Bob")
    members = character_system.get_guild_members("Adventurers")
    assert set(members) == {"Alice", "Bob"}


def test_boss_battle(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, "DATA_DIR", tmp_path)
    character_system.start_boss("ProjectX", 50)
    remaining = character_system.damage_boss("ProjectX", 20)
    assert remaining == 30
    remaining = character_system.damage_boss("ProjectX", 30)
    assert remaining == 0