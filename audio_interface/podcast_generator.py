"""Utilities to create a short spoken briefing.

This module generates a small "podcast" style audio summary using
pyttsx3 when available. It falls back to printing the text if the
text-to-speech engine cannot be loaded.
"""

from __future__ import annotations

import datetime
import os
from typing import Iterable, Optional

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None


def generate_briefing(lines: Iterable[str], filename: Optional[str] = None) -> str:
    """Speak or save a morning briefing.

    Parameters
    ----------
    lines:
        Iterable of lines to include in the briefing.
    filename:
        Optional path to save the spoken audio. If not provided the
        text is spoken aloud using pyttsx3.

    Returns
    -------
    str
        The full text of the briefing.
    """
    date = datetime.date.today().strftime("%A, %B %d")
    text = f"Good morning! Today is {date}.\n" + "\n".join(lines)

    if pyttsx3 is None:
        print(text)
        return text

    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    engine = pyttsx3.init()
    if filename:
        engine.save_to_file(text, filename)
        engine.runAndWait()
    else:
        engine.say(text)
        engine.runAndWait()
    return text
