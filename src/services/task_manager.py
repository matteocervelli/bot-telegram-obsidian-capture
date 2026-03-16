"""Task management service for adding, searching, and completing tasks."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.config import settings


@dataclass
class TaskLocation:
    """Tracks where a task lives in the vault for completion."""

    file_path: Path
    line_number: int
    task_text: str


def parse_date_arg(arg: str) -> str | None:
    """
    Parse date argument, handling Telegram dash conversion and relative dates.

    Telegram converts -- to em-dash (—) or en-dash (–), so we accept all variants.

    Args:
        arg: Raw argument like "--2026-02-10", "—today", "--tomorrow"

    Returns:
        Date string in YYYY-MM-DD format, or None if not a valid date arg
    """
    # Strip leading dashes (both -- and em/en-dash)
    cleaned = arg.lstrip("-–—")

    if not cleaned:
        return None

    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()

    # Check for relative dates
    if cleaned == "today":
        return today.strftime("%Y-%m-%d")
    elif cleaned == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif cleaned == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # Check for explicit date YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
        return cleaned

    return None


def _normalize_task(
    raw_text: str,
    follow_up: bool = False,
    due_date: str | None = None,
) -> str:
    """
    Normalize raw input to proper task format.

    Args:
        raw_text: Raw task text from user
        follow_up: If True, use #to/follow-up tag instead of #to/do
        due_date: Optional due date in YYYY-MM-DD format

    Returns:
        Formatted task like '- [ ] #to/do Buy milk 📅 2026-02-10'
    """
    text = raw_text.strip()

    # Remove "task:" prefix if present (case-insensitive)
    if text.lower().startswith("task:"):
        text = text[5:].strip()

    # Choose tag based on follow_up flag
    tag = settings.task_tag_followup if follow_up else settings.task_tag

    # Build task: - [ ] #to/do description
    # Always rebuild to ensure consistent format
    if text.startswith("- [ ]"):
        # Strip existing checkbox to rebuild
        text = text[5:].strip()
    elif text.startswith("- "):
        text = text[2:].strip()
    elif text.startswith("-"):
        text = text[1:].strip()

    # Remove any existing #to tags to avoid duplication
    text = re.sub(r"#to/(do|follow-up)\s*", "", text).strip()

    # Build final format: - [ ] #to/do description
    result = f"- [ ] {tag} {text}"

    # Add due date if provided
    if due_date:
        result = f"{result} 📅 {due_date}"

    return result


def add_task(
    task_text: str,
    follow_up: bool = False,
    due_date: str | None = None,
) -> Path:
    """
    Append a task to the task inbox file.

    Args:
        task_text: Raw task text
        follow_up: If True, use #to/follow-up tag
        due_date: Optional due date in YYYY-MM-DD format

    Returns:
        Path to the task inbox file
    """
    normalized = _normalize_task(task_text, follow_up=follow_up, due_date=due_date)
    inbox_path = settings.task_inbox_path

    # Ensure parent directory exists
    inbox_path.parent.mkdir(parents=True, exist_ok=True)

    if inbox_path.exists():
        existing = inbox_path.read_text(encoding="utf-8")
        # Ensure newline before appending
        if existing and not existing.endswith("\n"):
            existing += "\n"
        new_content = existing + normalized + "\n"
    else:
        new_content = normalized + "\n"

    inbox_path.write_text(new_content, encoding="utf-8")
    return inbox_path


def _extract_due_date(task_text: str) -> str | None:
    """Extract due date from task text (📅 YYYY-MM-DD pattern)."""
    match = re.search(r"📅\s*(\d{4}-\d{2}-\d{2})", task_text)
    return match.group(1) if match else None


def _get_vault_md_files() -> list[Path]:
    """Return all .md files in vault sorted by mtime descending."""
    try:
        return sorted(
            settings.vault_path.rglob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return []


def _scan_file_for_tasks(
    file_path: Path,
    pattern: re.Pattern,
    due_before: str | None,
) -> list[TaskLocation]:
    """Return matching TaskLocation objects from a single file."""
    # Skip hidden directories (.obsidian, .git, etc.)
    if any(part.startswith(".") for part in file_path.parts):
        return []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    results = []
    for line_num, line in enumerate(lines, start=1):
        if not pattern.match(line):
            continue
        # Apply due_before filter: skip tasks with due date after filter date
        if due_before:
            task_due = _extract_due_date(line)
            if task_due and task_due > due_before:
                continue
        results.append(TaskLocation(file_path=file_path, line_number=line_num, task_text=line))
    return results


def search_tasks(
    limit: int | None = None,
    due_before: str | None = None,
) -> list[TaskLocation]:
    """Search entire vault for unchecked #to/do or #to/follow-up tasks.

    Args:
        limit: Maximum tasks to return (uses settings.task_list_limit if None)
        due_before: Only return tasks due on or before this date (YYYY-MM-DD).
                    Tasks without a due date are always included.
    """
    limit = limit or settings.task_list_limit
    pattern = re.compile(r"^- \[ \] #to/(do|follow-up)\b.*", re.MULTILINE)
    tasks: list[TaskLocation] = []

    for file_path in _get_vault_md_files():
        tasks.extend(_scan_file_for_tasks(file_path, pattern, due_before))
        if len(tasks) >= limit:
            return tasks[:limit]

    return tasks


def complete_task(location: TaskLocation) -> bool:
    """
    Mark a task as complete by changing [ ] to [x] and adding completion date.

    Args:
        location: TaskLocation with file path and line number

    Returns:
        True if task was completed, False if task changed/not found
    """
    try:
        lines = location.file_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False

    # Line numbers are 1-indexed
    line_idx = location.line_number - 1

    if line_idx < 0 or line_idx >= len(lines):
        return False

    current_line = lines[line_idx]

    # Verify line matches what we expect (handles concurrent modifications)
    if current_line != location.task_text:
        return False

    # Replace unchecked with checked
    new_line = current_line.replace("- [ ]", "- [x]", 1)

    # Add completion date
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).strftime("%Y-%m-%d")
    new_line = f"{new_line.rstrip()} ✅ {today}"

    lines[line_idx] = new_line

    # Write back
    location.file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def format_task_list(tasks: list[TaskLocation]) -> str:
    """
    Format tasks for Telegram display as numbered list with task type prefix.

    Args:
        tasks: List of TaskLocation objects

    Returns:
        Numbered list like "1. DO: Buy milk 📅 2026-02-10\n2. FOLLOW-UP: Call John"
    """
    if not tasks:
        return "No open tasks found"

    lines = []
    for i, task in enumerate(tasks, start=1):
        # Determine task type prefix
        if "#to/follow-up" in task.task_text:
            prefix = "FOLLOW-UP:"
        else:
            prefix = "DO:"

        # Extract task description: strip "- [ ] #to/do " or "- [ ] #to/follow-up "
        desc = task.task_text
        # Remove checkbox
        if desc.startswith("- [ ] "):
            desc = desc[6:]
        # Remove #to/do or #to/follow-up tag
        desc = re.sub(r"^#to/(do|follow-up)\s*", "", desc)
        # Keep due date 📅 visible, just clean up extra whitespace
        desc = desc.strip()

        lines.append(f"{i}. {prefix} {desc}")

    return "\n".join(lines)
