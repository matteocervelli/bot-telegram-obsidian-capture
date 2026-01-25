"""Photo message handler."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.file_manager import save_attachment
from src.services.note_writer import create_note

log = structlog.get_logger()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photo messages."""
    message = update.message
    if not message or not message.photo:
        return

    # Get largest photo size
    photo = message.photo[-1]
    caption = message.caption or ""

    log.info("received_photo", user_id=message.from_user.id, file_id=photo.file_id)

    # Download photo
    file = await context.bot.get_file(photo.file_id)
    photo_data = await file.download_as_bytearray()

    # Save attachment
    _, wikilink_path = save_attachment(bytes(photo_data), "jpg")

    note_path = create_note(
        content=caption,
        note_type="photo",
        attachment_path=wikilink_path,
    )
    log.info("note_created", path=str(note_path))

    await message.reply_text("✓ Captured")
