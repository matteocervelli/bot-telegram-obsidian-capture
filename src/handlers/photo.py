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
    file_path, wikilink_path = save_attachment(bytes(photo_data), "jpg")

    # Check for daily mode
    is_daily = context.user_data.get("daily_mode", False)
    section_time = None
    if is_daily:
        from src.services.daily_notes import append_to_daily

        note_path, section_time = append_to_daily(content=caption, attachment_path=wikilink_path)
    else:
        note_path = create_note(content=caption, attachment_path=wikilink_path)
    log.info("note_created", path=str(note_path))

    # Track for undo
    context.user_data["last_capture"] = {
        "note_path": note_path,
        "attachments": [file_path],
        "is_daily": is_daily,
        "section_time": section_time,
    }

    await message.reply_text("✓ Captured")
