"""Message handlers package."""

from src.handlers.commands import handle_daily, handle_undo
from src.handlers.document import handle_document
from src.handlers.photo import handle_photo
from src.handlers.text import handle_text
from src.handlers.video import handle_video, handle_video_note
from src.handlers.voice import handle_voice

__all__ = [
    "handle_text",
    "handle_voice",
    "handle_photo",
    "handle_document",
    "handle_video",
    "handle_video_note",
    "handle_undo",
    "handle_daily",
]
