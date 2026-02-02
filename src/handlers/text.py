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

    # Check for task syntax: "task: ..." or "Task: ..."
    if text.lower().startswith("task:"):
        from src.services.task_manager import add_task

        task_path = add_task(text)
        log.info("task_added", path=str(task_path))
        await message.reply_text("✓ Task added")
        return

    # Check for daily mode
    is_daily = context.user_data.get("daily_mode", False)
    section_time = None
    if is_daily:
        from src.services.daily_notes import append_to_daily

        note_path, section_time = append_to_daily(content=text)
    else:
        note_path = create_note(content=text)
    log.info("note_created", path=str(note_path))

    # Track for undo
    context.user_data["last_capture"] = {
        "note_path": note_path,
        "attachments": [],
        "is_daily": is_daily,
        "section_time": section_time,
    }

    await message.reply_text("✓ Captured")
