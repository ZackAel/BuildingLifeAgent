"""Helpers for interacting with Gmail.

These functions are intentionally lightweight to keep the project dependency
free. They provide simple hooks for generating replies and analysing email mood
without directly calling the Gmail API. Integrations can be added on top of
these helpers in a real environment.
"""
from __future__ import annotations

from typing import Iterable

from gemini_api import ask_gemini
from .style_analyzer import detect_style, apply_style


def draft_reply(incoming_email: str, sent_emails: Iterable[str]) -> str:
    """Generate a reply suggestion for ``incoming_email``.

    ``sent_emails`` should contain a collection of previous emails written by the
    user so that the function can mimic their style.
    """
    style = detect_style(sent_emails)
    prompt = (
        "Reply to the email below in the user's typical style.\n"
        "Email:\n" + incoming_email
    )
    base_reply = ask_gemini(prompt)
    return apply_style(base_reply, style)


def analyze_email_mood(email_text: str) -> str:
    """Return a short message about the mood of ``email_text``."""
    style = detect_style([email_text])
    if style["terse_score"] > 0.8:
        return "Your emails seem terse today, everything okay?"
    if style["terse_score"] < 0.3:
        return "You're quite chatty today!"
    return "Your email tone looks normal."


def inbox_zero_cheer(processed: int, total: int) -> str:
    """Return a gamified cheer message for inbox processing."""
    if total == 0:
        return "Inbox already clear! 🎉"
    ratio = processed / total
    if ratio >= 1.0:
        return "Inbox Zero achieved! 🏆"
    elif ratio >= 0.5:
        return "Halfway there, keep going! 💪"
    return "Let's tackle those emails!"
