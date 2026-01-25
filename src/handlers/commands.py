"""Command handlers for /undo and /daily."""

import re

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


def _remove_last_daily_section(note_path, section_time: str) -> bool:
    """Remove the last section from a daily note. Returns True if section removed."""
    if not note_path.exists():
        return False

    content = note_path.read_text(encoding="utf-8")

    # Find ALL sections matching ## HH:MM pattern and remove only the LAST one
    # Section starts with ## HH:MM and ends at next ## or end of file
    pattern = rf"\n## {re.escape(section_time)}\n.*?(?=\n## |\Z)"
    matches = list(re.finditer(pattern, content, flags=re.DOTALL))

    if not matches:
        return False

    # Remove the last match
    last_match = matches[-1]
    new_content = content[: last_match.start()] + content[last_match.end() :]

    note_path.write_text(new_content, encoding="utf-8")
    return True


async def handle_undo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /undo command - deletes last captured note/section and attachments."""
    message = update.message
    if not message:
        return

    last_capture = context.user_data.get("last_capture")
    if not last_capture:
        await message.reply_text("Nothing to undo")
        return

    note_path = last_capture.get("note_path")
    attachments = last_capture.get("attachments", [])
    is_daily = last_capture.get("is_daily", False)
    section_time = last_capture.get("section_time")
    deleted_items = []

    if is_daily and section_time:
        # Remove only the last section from daily note
        if note_path and _remove_last_daily_section(note_path, section_time):
            deleted_items.append(f"section {section_time}")
            log.info("daily_section_removed", path=str(note_path), time=section_time)
    else:
        # Delete entire note (non-daily mode)
        if note_path and note_path.exists():
            note_path.unlink()
            deleted_items.append(note_path.name)
            log.info("note_deleted", path=str(note_path))

    # Delete attachments
    for attachment_path in attachments:
        if attachment_path and attachment_path.exists():
            attachment_path.unlink()
            deleted_items.append(attachment_path.name)
            log.info("attachment_deleted", path=str(attachment_path))

    # Clear last_capture (single-use undo)
    context.user_data["last_capture"] = None

    if deleted_items:
        await message.reply_text(f"Deleted: {', '.join(deleted_items)}")
    else:
        await message.reply_text("Files already removed")


async def handle_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /daily command - toggle daily note mode."""
    message = update.message
    if not message:
        return

    # Parse arguments: /daily, /daily on, /daily off
    args = context.args or []

    if not args:
        # Toggle current state
        current = context.user_data.get("daily_mode", False)
        context.user_data["daily_mode"] = not current
    elif args[0].lower() == "on":
        context.user_data["daily_mode"] = True
    elif args[0].lower() == "off":
        context.user_data["daily_mode"] = False
    else:
        await message.reply_text("Usage: /daily, /daily on, /daily off")
        return

    mode = context.user_data.get("daily_mode", False)
    status = "ON" if mode else "OFF"
    log.info("daily_mode_changed", mode=mode)
    await message.reply_text(f"Daily mode: {status}")
