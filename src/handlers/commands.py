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


async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /task command - add a new task to inbox.

    Flags:
        --follow-up: Use #to/follow-up tag instead of #to/do
        --YYYY-MM-DD or --today/--tomorrow: Set due date
        Note: Telegram may convert -- to em-dash (—), both work
    """
    message = update.message
    if not message:
        return

    args = context.args or []
    if not args:
        await message.reply_text("Usage: /task Buy milk [--follow-up] [--today]")
        return

    from src.services.task_manager import add_task, parse_date_arg

    # Parse flags (handle both -- and em/en-dash variants)
    follow_up = False
    due_date = None
    task_words = []

    for arg in args:
        # Check for --follow-up (with dash variants)
        if arg.lstrip("-–—") == "follow-up":
            follow_up = True
        # Check for date argument
        elif parsed_date := parse_date_arg(arg):
            due_date = parsed_date
        else:
            task_words.append(arg)

    if not task_words:
        await message.reply_text("Usage: /task Buy milk [--follow-up] [--today]")
        return

    task_text = " ".join(task_words)

    task_path = add_task(task_text, follow_up=follow_up, due_date=due_date)
    log.info(
        "task_added", path=str(task_path), task=task_text, follow_up=follow_up, due_date=due_date
    )
    await message.reply_text("✓ Task added")


async def handle_task_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /task_list command - list open tasks with #to/do or #to/follow-up tags.

    Optional filter:
        --YYYY-MM-DD or --today: Show only tasks due on or before this date
    """
    message = update.message
    if not message:
        return

    from src.services.task_manager import format_task_list, parse_date_arg, search_tasks

    # Parse optional date filter
    due_filter = None
    for arg in context.args or []:
        if parsed_date := parse_date_arg(arg):
            due_filter = parsed_date
            break

    tasks = search_tasks(due_before=due_filter)

    if not tasks:
        if due_filter:
            await message.reply_text(f"No tasks due by {due_filter}")
        else:
            await message.reply_text("No open tasks found")
        return

    # Store task list for /done command
    context.user_data["last_task_list"] = tasks

    formatted = format_task_list(tasks)
    await message.reply_text(formatted)


async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /done N command - complete task N from last /task_list."""
    message = update.message
    if not message:
        return

    args = context.args or []
    if not args:
        await message.reply_text("Usage: /done 3")
        return

    try:
        task_num = int(args[0])
    except ValueError:
        await message.reply_text("Usage: /done 3 (number required)")
        return

    last_tasks = context.user_data.get("last_task_list", [])
    if not last_tasks:
        await message.reply_text("Run /task_list first")
        return

    if task_num < 1 or task_num > len(last_tasks):
        await message.reply_text(f"Invalid number. Range: 1-{len(last_tasks)}")
        return

    from src.services.task_manager import complete_task

    location = last_tasks[task_num - 1]
    success = complete_task(location)

    if success:
        # Clear the list to prevent stale completions
        context.user_data["last_task_list"] = None

        # Extract task description for confirmation (strip checkbox and tag)
        task_desc = re.sub(r"^- \[ \] #to/(do|follow-up)\s*", "", location.task_text)
        log.info("task_completed", file=str(location.file_path), line=location.line_number)
        await message.reply_text(f"✓ Done: {task_desc}")
    else:
        await message.reply_text("Task changed or missing. Run /task_list again")
