"""Utility functions for analyzing and applying a user's email style."""
from __future__ import annotations

from typing import Iterable, Dict


def detect_style(emails: Iterable[str]) -> Dict[str, float]:
    """Return a simple style profile based on average sentence length.

    Parameters
    ----------
    emails:
        Iterable of email strings written by the user.

    Returns
    -------
    Dict[str, float]
        Dictionary with keys ``avg_length`` and ``terse_score``. ``avg_length``
        is the average number of words per sentence. ``terse_score`` is a
        normalized value between 0 and 1 where higher means shorter emails.
    """
    total_sentences = 0
    total_words = 0
    for mail in emails:
        sentences = [s for s in mail.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        total_sentences += len(sentences)
        for s in sentences:
            total_words += len(s.split())
    if total_sentences == 0:
        return {"avg_length": 0.0, "terse_score": 0.0}
    avg_length = total_words / total_sentences
    # Map avg length roughly to a 0-1 scale where <8 words is very terse.
    terse_score = max(0.0, min(1.0, (12 - avg_length) / 12))
    return {"avg_length": avg_length, "terse_score": terse_score}


def apply_style(text: str, style: Dict[str, float]) -> str:
    """Apply the detected style to ``text``.

    Currently this only shortens or lengthens the text slightly based on the
    ``terse_score`` value.
    """
    words = text.split()
    terse_score = style.get("terse_score", 0.5)
    if terse_score > 0.7 and len(words) > 12:
        # shorten by removing filler words
        trimmed = [w for w in words if w.lower() not in {"just", "really", "very"}]
        words = trimmed[: max(10, int(len(trimmed) * 0.8))]
    elif terse_score < 0.3:
        # expand slightly
        words.append("Thanks!")
    return " ".join(words)
