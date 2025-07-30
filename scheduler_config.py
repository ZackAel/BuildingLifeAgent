from __future__ import annotations
import os
import json
from dataclasses import dataclass
from typing import Optional
from mood import get_today_mood

CONFIG_FILE = os.path.join("data", "scheduler_config.json")

@dataclass
class SchedulerConfig:
    """User preferences for the beast scheduler."""
    interval_minutes: int = 60
    start_hour: int = 9
    end_hour: int = 21
    mood_adjust: bool = True


def load_config() -> SchedulerConfig:
    """Load scheduler preferences from disk."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            return SchedulerConfig(**data)
        except Exception:
            pass
    return SchedulerConfig()


def save_config(cfg: SchedulerConfig) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg.__dict__, f, indent=2)


def get_adjusted_interval(cfg: Optional[SchedulerConfig] = None) -> int:
    """Return the sleep interval (seconds) adjusted based on mood."""
    if cfg is None:
        cfg = load_config()
    interval = cfg.interval_minutes * 60
    if cfg.mood_adjust:
        mood, _ = get_today_mood()
        if mood:
            mood = mood.lower()
            if "tired" in mood:
                interval = int(interval * 1.5)
            elif "stressed" in mood:
                interval = int(interval * 1.2)
    return max(60, int(interval))
