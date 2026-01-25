"""Message handlers package."""

from src.handlers.document import handle_document
from src.handlers.photo import handle_photo
from src.handlers.text import handle_text
from src.handlers.voice import handle_voice

__all__ = ["handle_text", "handle_voice", "handle_photo", "handle_document"]
