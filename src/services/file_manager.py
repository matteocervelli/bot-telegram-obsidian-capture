"""Attachment file handling service."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import settings


def save_attachment(data: bytes, extension: str, prefix: str = "tg") -> tuple[Path, str]:
    """
    Save attachment to the attachments folder.

    Args:
        data: Raw file bytes
        extension: File extension (e.g., 'jpg', 'pdf')
        prefix: Filename prefix

    Returns:
        Tuple of (absolute path, wikilink path for embedding)
    """
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)

    filename = f"{prefix}-{now.strftime('%Y-%m-%d-%H%M%S')}.{extension}"
    file_path = settings.attachments_path / filename

    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(data)

    # Return wikilink-compatible path relative to vault
    wikilink_path = f"{settings.attachments_folder}/{filename}"
    return file_path, wikilink_path
