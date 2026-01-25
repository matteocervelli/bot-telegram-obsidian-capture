"""Text message handler."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.note_writer import create_note

log = structlog.get_logger()


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    message = update.message
    if not message or not message.text:
        return

    text = message.text
    log.info("received_text", user_id=message.from_user.id, length=len(text))

    note_path = create_note(content=text, note_type="text")
    log.info("note_created", path=str(note_path))

    await message.reply_text("✓ Captured")
