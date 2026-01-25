"""Document/file message handler."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.file_manager import save_attachment
from src.services.note_writer import create_note

log = structlog.get_logger()


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming document messages."""
    message = update.message
    if not message or not message.document:
        return

    document = message.document
    caption = message.caption or ""
    filename = document.file_name or "file"

    log.info("received_document", user_id=message.from_user.id, filename=filename)

    # Download document
    file = await context.bot.get_file(document.file_id)
    doc_data = await file.download_as_bytearray()

    # Get extension from original filename
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "bin"

    # Save attachment
    _, wikilink_path = save_attachment(bytes(doc_data), extension, prefix="doc")

    note_content = (
        f"{caption}\n\nOriginal filename: `{filename}`"
        if caption
        else f"Original filename: `{filename}`"
    )

    note_path = create_note(content=note_content, attachment_path=wikilink_path)
    log.info("note_created", path=str(note_path))

    await message.reply_text("✓ Captured")
