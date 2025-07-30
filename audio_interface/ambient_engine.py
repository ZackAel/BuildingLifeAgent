"""Simple ambient sound controller for different agent modes."""

from __future__ import annotations

import os
from typing import Dict

try:
    import simpleaudio as sa  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sa = None


SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

# Map mode name to wav filename within SOUNDS_DIR
MODE_SOUNDS: Dict[str, str] = {
    "focus": "focus.wav",
    "break": "break.wav",
    "relax": "relax.wav",
}

_current_play = None


def play_mode(mode: str) -> None:
    """Play a short ambient sound for the given mode.

    If the ``simpleaudio`` package is unavailable or the sound file
    cannot be found, a message is printed instead.
    """
    filename = MODE_SOUNDS.get(mode)
    if not filename:
        return
    path = os.path.join(SOUNDS_DIR, filename)
    if sa is None or not os.path.exists(path):
        print(f"[ambient:{mode}] {filename}")
        return

    global _current_play
    if _current_play is not None:
        _current_play.stop()
    wave = sa.WaveObject.from_wave_file(path)
    _current_play = wave.play()


def stop() -> None:
    """Stop any currently playing ambient sound."""
    global _current_play
    if _current_play is not None:
        _current_play.stop()
        _current_play = None


def suggest_playlist(task_type: str, count: int = 5) -> str:
    """Return a short playlist suggestion via Gemini."""
    from gemini_api import ask_gemini

    prompt = (
        f"Suggest a {count}-song playlist for {task_type} work. "
        "List songs on separate lines in 'Artist - Title' format."
    )
    try:
        return ask_gemini(prompt)
    except Exception:
        return ""
