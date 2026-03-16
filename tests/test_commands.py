"""Tests for command handlers (/undo, /daily)."""

from unittest.mock import AsyncMock, MagicMock


async def test_handle_undo_with_capture(temp_vault):
    """Test /undo deletes the last captured note."""
    from src.handlers.commands import handle_undo

    # Create a test note file
    note_path = temp_vault / "+" / "test-note.md"
    note_path.write_text("Test content")
    assert note_path.exists()

    # Mock update and context
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {
        "last_capture": {
            "note_path": note_path,
            "attachments": [],
        }
    }

    await handle_undo(update, context)

    assert not note_path.exists()
    assert context.user_data["last_capture"] is None
    update.message.reply_text.assert_called_once()
    assert "test-note.md" in update.message.reply_text.call_args[0][0]


async def test_handle_undo_with_attachment(temp_vault):
    """Test /undo deletes note and attachments."""
    from src.handlers.commands import handle_undo

    # Create test files
    note_path = temp_vault / "+" / "test-note.md"
    note_path.write_text("Test content")
    attachment_path = temp_vault / "+" / "attachments" / "test.jpg"
    attachment_path.write_bytes(b"fake image")

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {
        "last_capture": {
            "note_path": note_path,
            "attachments": [attachment_path],
        }
    }

    await handle_undo(update, context)

    assert not note_path.exists()
    assert not attachment_path.exists()
    reply = update.message.reply_text.call_args[0][0]
    assert "test-note.md" in reply
    assert "test.jpg" in reply


async def test_handle_undo_nothing_to_undo():
    """Test /undo with no previous capture."""
    from src.handlers.commands import handle_undo

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {}

    await handle_undo(update, context)

    update.message.reply_text.assert_called_once_with("Nothing to undo")


async def test_handle_daily_toggle_on():
    """Test /daily toggles mode on."""
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {}
    context.args = []

    await handle_daily(update, context)

    assert context.user_data["daily_mode"] is True
    update.message.reply_text.assert_called_once_with("Daily mode: ON")


async def test_handle_daily_toggle_off():
    """Test /daily toggles mode off when already on."""
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {"daily_mode": True}
    context.args = []

    await handle_daily(update, context)

    assert context.user_data["daily_mode"] is False
    update.message.reply_text.assert_called_once_with("Daily mode: OFF")


async def test_handle_daily_explicit_on():
    """Test /daily on explicitly enables mode."""
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {}
    context.args = ["on"]

    await handle_daily(update, context)

    assert context.user_data["daily_mode"] is True


async def test_handle_daily_explicit_off():
    """Test /daily off explicitly disables mode."""
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {"daily_mode": True}
    context.args = ["off"]

    await handle_daily(update, context)

    assert context.user_data["daily_mode"] is False


async def test_undo_removes_last_section_from_daily_note(temp_vault):
    """Test /undo removes only the last ### HH:MM section from a daily note."""
    from src.handlers.commands import handle_undo

    daily_note = temp_vault / "calendar" / "days" / "2026-03-16.md"
    daily_note.parent.mkdir(parents=True, exist_ok=True)
    daily_note.write_text("### 09:15\n\nFirst capture\n\n### 14:30\n\nSecond capture\n")

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {
        "last_capture": {
            "note_path": daily_note,
            "attachments": [],
            "is_daily": True,
            "section_time": "14:30",
        }
    }

    await handle_undo(update, context)

    remaining = daily_note.read_text()
    assert "14:30" not in remaining
    assert "First capture" in remaining
    reply = update.message.reply_text.call_args[0][0]
    assert "section 14:30" in reply


async def test_handle_undo_files_already_removed(temp_vault):
    """Test /undo when note file no longer exists."""
    from src.handlers.commands import handle_undo

    missing_note = temp_vault / "+" / "gone.md"  # does not exist

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {
        "last_capture": {
            "note_path": missing_note,
            "attachments": [],
            "is_daily": False,
            "section_time": None,
        }
    }

    await handle_undo(update, context)

    update.message.reply_text.assert_called_once_with("Files already removed")


async def test_remove_last_daily_section_file_missing(tmp_path):
    """_remove_last_daily_section returns False when file does not exist."""
    from src.handlers.commands import _remove_last_daily_section

    result = _remove_last_daily_section(tmp_path / "nonexistent.md", "10:00")
    assert result is False


async def test_remove_last_daily_section_no_match(tmp_path):
    """_remove_last_daily_section returns False when section not found."""
    from src.handlers.commands import _remove_last_daily_section

    note = tmp_path / "daily.md"
    note.write_text("### 09:00\n\nContent\n")

    result = _remove_last_daily_section(note, "14:00")
    assert result is False


async def test_handle_daily_invalid_arg():
    """Test /daily with an unknown argument replies with usage."""
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    context.args = ["maybe"]

    await handle_daily(update, context)

    update.message.reply_text.assert_called_once_with("Usage: /daily, /daily on, /daily off")


# ─── handle_task ─────────────────────────────────────────────────────────────


async def test_handle_task_no_args():
    """Test /task with no arguments replies with usage."""
    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = []

    await handle_task(update, context)

    update.message.reply_text.assert_called_once_with(
        "Usage: /task Buy milk [--follow-up] [--today]"
    )


async def test_handle_task_only_flags_no_text():
    """Test /task with only a flag and no task text replies with usage."""
    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["--follow-up"]

    await handle_task(update, context)

    update.message.reply_text.assert_called_once_with(
        "Usage: /task Buy milk [--follow-up] [--today]"
    )


async def test_handle_task_adds_basic_task(temp_vault):
    """Test /task Buy milk creates a task and replies ✓."""
    from unittest.mock import patch

    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["Buy", "milk"]

    with patch(
        "src.services.task_manager.add_task", return_value=temp_vault / "tasks.md"
    ) as mock_add:
        await handle_task(update, context)

    mock_add.assert_called_once_with("Buy milk", follow_up=False, due_date=None)
    update.message.reply_text.assert_called_once_with("✓ Task added")


async def test_handle_task_follow_up_flag(temp_vault):
    """Test /task with --follow-up sets follow_up=True."""
    from unittest.mock import patch

    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["Call", "John", "--follow-up"]

    with patch(
        "src.services.task_manager.add_task", return_value=temp_vault / "tasks.md"
    ) as mock_add:
        await handle_task(update, context)

    mock_add.assert_called_once_with("Call John", follow_up=True, due_date=None)


async def test_handle_task_with_due_date(temp_vault):
    """Test /task with --today sets due_date."""
    from unittest.mock import patch

    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["Meeting", "--today"]

    with patch(
        "src.services.task_manager.add_task", return_value=temp_vault / "tasks.md"
    ) as mock_add:
        await handle_task(update, context)

    call_kwargs = mock_add.call_args
    assert call_kwargs[1]["due_date"] is not None  # today resolved to a date string
    assert call_kwargs[1]["follow_up"] is False


# ─── handle_task_list ────────────────────────────────────────────────────────


async def test_handle_task_list_no_tasks():
    """Test /task_list when no tasks exist."""
    from unittest.mock import patch

    from src.handlers.commands import handle_task_list

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = []

    with patch("src.services.task_manager.search_tasks", return_value=[]):
        await handle_task_list(update, context)

    update.message.reply_text.assert_called_once_with("No open tasks found")


async def test_handle_task_list_no_tasks_with_filter():
    """Test /task_list --today when no matching tasks."""
    from unittest.mock import patch

    from src.handlers.commands import handle_task_list

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["--today"]

    with patch("src.services.task_manager.search_tasks", return_value=[]):
        await handle_task_list(update, context)

    reply = update.message.reply_text.call_args[0][0]
    assert "No tasks due by" in reply


async def test_handle_task_list_shows_tasks():
    """Test /task_list with tasks replies with formatted list."""
    from pathlib import Path
    from unittest.mock import patch

    from src.handlers.commands import handle_task_list
    from src.services.task_manager import TaskLocation

    fake_task = TaskLocation(
        file_path=Path("/vault/tasks.md"),
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = []
    context.user_data = {}

    with patch("src.services.task_manager.search_tasks", return_value=[fake_task]):
        with patch("src.services.task_manager.format_task_list", return_value="1. DO: Buy milk"):
            await handle_task_list(update, context)

    update.message.reply_text.assert_called_once_with("1. DO: Buy milk")
    assert context.user_data["last_task_list"] == [fake_task]


# ─── handle_done ─────────────────────────────────────────────────────────────


async def test_handle_done_no_args():
    """Test /done with no args replies with usage."""
    from src.handlers.commands import handle_done

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = []

    await handle_done(update, context)

    update.message.reply_text.assert_called_once_with("Usage: /done 3")


async def test_handle_done_invalid_number():
    """Test /done with non-numeric arg."""
    from src.handlers.commands import handle_done

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["abc"]

    await handle_done(update, context)

    update.message.reply_text.assert_called_once_with("Usage: /done 3 (number required)")


async def test_handle_done_no_task_list():
    """Test /done when no prior /task_list was run."""
    from src.handlers.commands import handle_done

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["1"]
    context.user_data = {}

    await handle_done(update, context)

    update.message.reply_text.assert_called_once_with("Run /task_list first")


async def test_handle_done_out_of_range():
    """Test /done N when N > number of tasks."""
    from pathlib import Path

    from src.handlers.commands import handle_done
    from src.services.task_manager import TaskLocation

    fake_task = TaskLocation(
        file_path=Path("/vault/tasks.md"),
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["99"]
    context.user_data = {"last_task_list": [fake_task]}

    await handle_done(update, context)

    reply = update.message.reply_text.call_args[0][0]
    assert "Invalid number" in reply


async def test_handle_done_success():
    """Test /done N completes the task and replies ✓."""
    from pathlib import Path
    from unittest.mock import patch

    from src.handlers.commands import handle_done
    from src.services.task_manager import TaskLocation

    fake_task = TaskLocation(
        file_path=Path("/vault/tasks.md"),
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["1"]
    context.user_data = {"last_task_list": [fake_task]}

    with patch("src.services.task_manager.complete_task", return_value=True):
        await handle_done(update, context)

    reply = update.message.reply_text.call_args[0][0]
    assert "✓ Done" in reply
    assert context.user_data["last_task_list"] is None


async def test_handle_done_task_changed():
    """Test /done when task was modified since last_task_list."""
    from pathlib import Path
    from unittest.mock import patch

    from src.handlers.commands import handle_done
    from src.services.task_manager import TaskLocation

    fake_task = TaskLocation(
        file_path=Path("/vault/tasks.md"),
        line_number=1,
        task_text="- [ ] #to/do Buy milk",
    )

    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["1"]
    context.user_data = {"last_task_list": [fake_task]}

    with patch("src.services.task_manager.complete_task", return_value=False):
        await handle_done(update, context)

    update.message.reply_text.assert_called_once_with(
        "Task changed or missing. Run /task_list again"
    )


# ─── message=None early returns ──────────────────────────────────────────────


async def test_handle_undo_no_message():
    from src.handlers.commands import handle_undo

    update = MagicMock()
    update.message = None
    await handle_undo(update, MagicMock())  # should not raise


async def test_handle_daily_no_message():
    from src.handlers.commands import handle_daily

    update = MagicMock()
    update.message = None
    await handle_daily(update, MagicMock())


async def test_handle_task_no_message():
    from src.handlers.commands import handle_task

    update = MagicMock()
    update.message = None
    await handle_task(update, MagicMock())


async def test_handle_task_list_no_message():
    from src.handlers.commands import handle_task_list

    update = MagicMock()
    update.message = None
    await handle_task_list(update, MagicMock())


async def test_handle_done_no_message():
    from src.handlers.commands import handle_done

    update = MagicMock()
    update.message = None
    await handle_done(update, MagicMock())
