"""Daily note append/create service."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import settings


def append_to_daily(
    content: str,
    attachment_path: str | None = None,
) -> tuple[Path, str]:
    """
    Append content to today's daily note, creating it if needed.

    Args:
        content: The content to append
        attachment_path: Optional wikilink path to attachment

    Returns:
        Tuple of (path to daily note, section time string for undo)
    """
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)

    # Build daily note path
    filename = now.strftime(settings.daily_note_format) + ".md"
    note_path = settings.daily_notes_path / filename

    # Ensure directory exists
    note_path.parent.mkdir(parents=True, exist_ok=True)

    # Build section header
    section_time = now.strftime("%H:%M")
    time_header = f"## {section_time}"

    # Build section content
    section_content = content
    if attachment_path:
        if content:
            section_content = f"{content}\n\n![[{attachment_path}]]"
        else:
            section_content = f"![[{attachment_path}]]"

    if note_path.exists():
        # Append to existing daily note
        existing = note_path.read_text(encoding="utf-8")
        new_content = f"{existing}\n{time_header}\n{section_content}\n"
    else:
        # Create new daily note with frontmatter
        frontmatter = f"""---
dateCreated: {now.strftime("%Y-%m-%d")}
tags:
  - k/daily
---"""
        new_content = f"{frontmatter}\n\n{time_header}\n{section_content}\n"

    note_path.write_text(new_content, encoding="utf-8")
    return note_path, section_time
