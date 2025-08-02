"""Voice journaling utilities."""

from __future__ import annotations
import os
from typing import Optional

try:
    import speech_recognition as sr  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sr = None

from journal import log_entry
from gemini_api import ask_gemini


def record_entry(duration: int = 30) -> Optional[str]:
    """Record audio from the microphone and transcribe it.

    Parameters
    ----------
    duration:
        Maximum recording time in seconds.

    Returns
    -------
    Optional[str]
        The transcribed text, or ``None`` if recording failed.
    """
    if sr is None:
        print("Speech recognition not available.")
        return None
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, phrase_time_limit=duration)
            text = r.recognize_google(audio)
        except Exception:
            return None

    log_entry("", text)
    return text


def analyze_entry(text: str) -> str:
    """Analyze a journal entry using Gemini for insights."""
    if not text:
        return ""
    prompt = (
        "Provide a short reflection on the following journal entry:\n" + text
    )
    try:
        return ask_gemini(prompt)
    except Exception:
        return ""
