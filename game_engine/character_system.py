import json
from typing import List
from data_utils import ensure_file

BOSS_FILE = "bosses.json"
GUILD_FILE = "guilds.json"

PET_STAGES = ["egg", "baby", "teen", "adult", "legendary"]
SKILL_TIERS = {3: "Focus Mode", 7: "Deep Work", 14: "Hyper Productivity"}


def get_pet_stage(streak: int) -> str:
    index = min(streak // 5, len(PET_STAGES) - 1)
    return PET_STAGES[index]


def unlocked_skills(streak: int) -> List[str]:
    skills = []
    for days, skill in sorted(SKILL_TIERS.items()):
        if streak >= days:
            skills.append(skill)
    return skills


# --- Boss battle helpers ---

def _boss_path():
    return ensure_file(BOSS_FILE)


def _load_bosses():
    path = _boss_path()
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_bosses(bosses) -> None:
    path = _boss_path()
    with open(path, "w") as f:
        json.dump(bosses, f)


def start_boss(name: str, hp: int) -> None:
    bosses = _load_bosses()
    bosses[name] = {"hp": hp, "max_hp": hp}
    _save_bosses(bosses)


def damage_boss(name: str, damage: int) -> int:
    bosses = _load_bosses()
    if name not in bosses:
        return 0
    bosses[name]["hp"] = max(0, bosses[name]["hp"] - damage)
    remaining = bosses[name]["hp"]
    if remaining == 0:
        del bosses[name]
    _save_bosses(bosses)
    return remaining


# --- Guild management ---

def _guild_path():
    return ensure_file(GUILD_FILE)


def _load_guilds():
    path = _guild_path()
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_guilds(guilds) -> None:
    path = _guild_path()
    with open(path, "w") as f:
        json.dump(guilds, f)


def join_guild(guild_name: str, member: str) -> None:
    guilds = _load_guilds()
    members = guilds.setdefault(guild_name, [])
    if member not in members:
        members.append(member)
    _save_guilds(guilds)


def get_guild_members(guild_name: str) -> List[str]:
    guilds = _load_guilds()
    return guilds.get(guild_name, [])
