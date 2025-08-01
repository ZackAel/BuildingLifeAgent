import datetime
from data_utils import ensure_file

JOURNAL_FILE = ensure_file("journal.txt")


def log_entry(title: str, text: str | None = None) -> None:
    """Append a journal entry with timestamp.

    Parameters
    ----------
    title:
        Title of the journal entry. If ``text`` is ``None`` this is treated as
        the entry text for backward compatibility.
    text:
        Body of the journal entry. Optional to maintain support for calls that
        only provided a single ``text`` argument.
    """

    # Backward compatibility: allow calls like ``log_entry("text only")``
    if text is None:
        title, text = "", title

    if not text:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(JOURNAL_FILE, "a") as f:
        f.write(f"{timestamp} | {title} | {text}\n")


def load_entries(count: int = 10):
    """Return the last ``count`` journal entries as tuples.

    Each entry is a tuple ``(timestamp, title, text)``. Older entries without a
    title are returned with an empty string for the title.
    """
    path = ensure_file("journal.txt")
    try:
        entries = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" | ", 2)
                if len(parts) == 3:
                    timestamp, title, text = parts
                elif len(parts) == 2:
                    # Legacy format without title
                    timestamp, text = parts
                    title = ""
                else:
                    # Unexpected format; treat the whole line as text
                    timestamp, title, text = "", "", line
                entries.append((timestamp, title, text))
        return entries[-count:]
    except FileNotFoundError:
        return []
