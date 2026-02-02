"""Tests for task_manager service."""

from datetime import datetime
from unittest.mock import patch


def test_normalize_task_default_tag():
    """Raw text gets #to/do tag and checkbox."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        result = _normalize_task("Buy milk")
        assert result == "- [ ] #to/do Buy milk"


def test_normalize_task_follow_up_flag():
    """follow_up=True uses #to/follow-up tag."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        result = _normalize_task("Call John", follow_up=True)
        assert result == "- [ ] #to/follow-up Call John"


def test_normalize_task_with_due_date():
    """Due date adds 📅 emoji."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        result = _normalize_task("Buy milk", due_date="2026-02-10")
        assert result == "- [ ] #to/do Buy milk 📅 2026-02-10"


def test_normalize_task_follow_up_with_due_date():
    """Both flags work together."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        result = _normalize_task("Call John", follow_up=True, due_date="2026-02-15")
        assert result == "- [ ] #to/follow-up Call John 📅 2026-02-15"


def test_normalize_task_strips_prefix():
    """task: prefix is removed."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        result = _normalize_task("task: Buy milk")
        assert result == "- [ ] #to/do Buy milk"


def test_normalize_task_removes_existing_tag():
    """Existing #to/do or #to/follow-up tags are replaced."""
    from src.services.task_manager import _normalize_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        # User sends text that already has a tag
        result = _normalize_task("- [ ] #to/do Buy milk", follow_up=True)
        # Should switch to follow-up
        assert result == "- [ ] #to/follow-up Buy milk"


def test_add_task_creates_inbox_file(temp_vault):
    """Task inbox created if doesn't exist."""
    from src.services.task_manager import add_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_inbox_path = temp_vault / "+" / "task-inbox.md"
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"

        path = add_task("Buy milk")

        assert path.exists()
        content = path.read_text()
        assert "- [ ] #to/do Buy milk" in content


def test_add_task_with_flags(temp_vault):
    """Task with flags formatted correctly."""
    from src.services.task_manager import add_task

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_inbox_path = temp_vault / "+" / "task-inbox.md"
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"

        add_task("Call John", follow_up=True, due_date="2026-02-15")

        content = mock_settings.task_inbox_path.read_text()
        assert "- [ ] #to/follow-up Call John 📅 2026-02-15" in content


def test_search_tasks_finds_both_tag_types(temp_vault):
    """Finds tasks with both #to/do and #to/follow-up."""
    from src.services.task_manager import search_tasks

    # Create files with different task types
    (temp_vault / "tasks.md").write_text("- [ ] #to/do Task one\n- [ ] #to/follow-up Task two\n")

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        mock_settings.task_list_limit = 10

        tasks = search_tasks()

        assert len(tasks) == 2
        task_texts = [t.task_text for t in tasks]
        assert "- [ ] #to/do Task one" in task_texts
        assert "- [ ] #to/follow-up Task two" in task_texts


def test_search_tasks_skips_completed(temp_vault):
    """Ignores [x] tasks."""
    from src.services.task_manager import search_tasks

    (temp_vault / "tasks.md").write_text("- [x] #to/do Done task\n- [ ] #to/do Open task\n")

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        mock_settings.task_list_limit = 10

        tasks = search_tasks()

        assert len(tasks) == 1
        assert tasks[0].task_text == "- [ ] #to/do Open task"


def test_search_tasks_respects_limit(temp_vault):
    """Stops at limit."""
    from src.services.task_manager import search_tasks

    tasks_content = "\n".join([f"- [ ] #to/do Task {i}" for i in range(20)])
    (temp_vault / "tasks.md").write_text(tasks_content)

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        mock_settings.task_list_limit = 5

        tasks = search_tasks()

        assert len(tasks) == 5


def test_search_tasks_skips_hidden_dirs(temp_vault):
    """Ignores .obsidian/ and .git/ directories."""
    from src.services.task_manager import search_tasks

    hidden = temp_vault / ".obsidian"
    hidden.mkdir()
    (hidden / "config.md").write_text("- [ ] #to/do Hidden task\n")
    (temp_vault / "visible.md").write_text("- [ ] #to/do Visible task\n")

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        mock_settings.task_list_limit = 10

        tasks = search_tasks()

        assert len(tasks) == 1
        assert tasks[0].task_text == "- [ ] #to/do Visible task"


def test_complete_task_marks_done_with_date(temp_vault):
    """Changes [ ] to [x] and adds completion date."""
    import re

    from src.services.task_manager import TaskLocation, complete_task

    task_file = temp_vault / "tasks.md"
    task_file.write_text("- [ ] #to/do Buy milk\n")

    location = TaskLocation(
        file_path=task_file,
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.timezone = "UTC"

        result = complete_task(location)

    assert result is True
    content = task_file.read_text()
    # Check [x] and completion date pattern ✅ YYYY-MM-DD
    assert "- [x] #to/do Buy milk ✅" in content
    assert re.search(r"✅ \d{4}-\d{2}-\d{2}", content)
    assert "- [ ]" not in content


def test_complete_task_returns_false_if_changed(temp_vault):
    """Returns False if line was modified since search."""
    from src.services.task_manager import TaskLocation, complete_task

    task_file = temp_vault / "tasks.md"
    task_file.write_text("- [ ] #to/do Different text\n")

    location = TaskLocation(
        file_path=task_file,
        line_number=1,
        task_text="- [ ] #to/do Buy milk",  # Doesn't match file
    )

    result = complete_task(location)

    assert result is False
    content = task_file.read_text()
    assert "- [ ] #to/do Different text" in content


def test_complete_task_returns_false_if_file_missing(temp_vault):
    """Returns False if file was deleted."""
    from src.services.task_manager import TaskLocation, complete_task

    location = TaskLocation(
        file_path=temp_vault / "nonexistent.md",
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    result = complete_task(location)
    assert result is False


def test_format_task_list_with_type_prefix():
    """Shows DO: or FOLLOW-UP: prefix and keeps due date."""
    from pathlib import Path

    from src.services.task_manager import TaskLocation, format_task_list

    tasks = [
        TaskLocation(Path("/vault/a.md"), 1, "- [ ] #to/do Buy milk"),
        TaskLocation(Path("/vault/b.md"), 2, "- [ ] #to/follow-up Call John 📅 2026-02-15"),
    ]

    result = format_task_list(tasks)

    assert result == "1. DO: Buy milk\n2. FOLLOW-UP: Call John 📅 2026-02-15"


def test_format_task_list_empty():
    """Returns message for empty list."""
    from src.services.task_manager import format_task_list

    result = format_task_list([])
    assert result == "No open tasks found"


def test_parse_date_arg_explicit_date():
    """Parses explicit YYYY-MM-DD date."""
    from src.services.task_manager import parse_date_arg

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.timezone = "UTC"

        # Double dash
        assert parse_date_arg("--2026-02-10") == "2026-02-10"
        # Em-dash (Telegram converts)
        assert parse_date_arg("—2026-02-10") == "2026-02-10"
        # En-dash
        assert parse_date_arg("–2026-02-10") == "2026-02-10"


def test_parse_date_arg_relative_dates():
    """Parses today, tomorrow, yesterday."""

    from src.services.task_manager import parse_date_arg

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.timezone = "UTC"

        with patch("src.services.task_manager.datetime") as mock_dt:
            # Mock today as 2026-02-02
            mock_dt.now.return_value.date.return_value = datetime(2026, 2, 2).date()

            assert parse_date_arg("--today") == "2026-02-02"
            assert parse_date_arg("—tomorrow") == "2026-02-03"
            assert parse_date_arg("--yesterday") == "2026-02-01"


def test_parse_date_arg_invalid():
    """Returns None for invalid input."""
    from src.services.task_manager import parse_date_arg

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.timezone = "UTC"

        assert parse_date_arg("--invalid") is None
        assert parse_date_arg("not-a-date") is None
        assert parse_date_arg("--") is None


def test_search_tasks_due_before_filter(temp_vault):
    """Filters tasks by due date."""
    from src.services.task_manager import search_tasks

    (temp_vault / "tasks.md").write_text(
        "- [ ] #to/do Task no date\n"
        "- [ ] #to/do Task early 📅 2026-02-01\n"
        "- [ ] #to/do Task late 📅 2026-02-15\n"
    )

    with patch("src.services.task_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.task_tag = "#to/do"
        mock_settings.task_tag_followup = "#to/follow-up"
        mock_settings.task_list_limit = 10

        # Filter: due on or before 2026-02-05
        tasks = search_tasks(due_before="2026-02-05")

        assert len(tasks) == 2
        task_texts = [t.task_text for t in tasks]
        # Task with no date is included
        assert "- [ ] #to/do Task no date" in task_texts
        # Task due 2026-02-01 is included
        assert "- [ ] #to/do Task early 📅 2026-02-01" in task_texts
        # Task due 2026-02-15 is excluded
        assert "- [ ] #to/do Task late 📅 2026-02-15" not in task_texts
