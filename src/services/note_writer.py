"""Obsidian note creation service."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import settings


def create_note(
    content: str,
    note_type: str = "text",
    attachment_path: str | None = None,
) -> Path:
    """
    Create a timestamped note in the inbox folder.

    Args:
        content: The note body text
        note_type: One of text, voice, photo, document
        attachment_path: Optional wikilink path to attachment

    Returns:
        Path to the created note file
    """
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)

    # Build frontmatter
    frontmatter = f"""---
dateCreated: {now.isoformat(timespec="seconds")}
source: telegram
type: {note_type}
topics:
tags:
  - inbox
aliases:
---"""

    # Build body
    body = content

    # Add attachment embed if present
    if attachment_path:
        body = f"{content}\n\n![[{attachment_path}]]" if content else f"![[{attachment_path}]]"

    note_content = f"{frontmatter}\n\n{body}\n"

    # Generate filename
    filename = now.strftime(settings.note_filename_format) + ".md"
    note_path = settings.inbox_path / filename

    # Handle same-minute collision by appending seconds
    if note_path.exists():
        filename = now.strftime("%Y-%m-%d %H%M%S") + ".md"
        note_path = settings.inbox_path / filename

    # Ensure directory exists
    note_path.parent.mkdir(parents=True, exist_ok=True)

    note_path.write_text(note_content, encoding="utf-8")
    return note_path
