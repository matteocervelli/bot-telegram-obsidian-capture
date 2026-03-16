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
