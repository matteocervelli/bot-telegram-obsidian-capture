"""Tests for daily_notes service."""

from datetime import datetime
from unittest.mock import patch


def test_append_to_daily_creates_new_note(temp_vault):
    """Test creating a new daily note."""
    from src.services.daily_notes import append_to_daily

    with (
        patch("src.services.daily_notes.settings") as mock_settings,
        patch("src.services.daily_notes.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.daily_notes_path = temp_vault / "Dailies"
        mock_settings.timezone = "UTC"
        mock_settings.daily_note_format = "%Y-%m-%d"
        mock_dt.now.return_value = datetime(2026, 1, 25, 14, 30, 0)

        path, section_time = append_to_daily(content="First entry")

        assert path.exists()
        assert section_time == "14:30"
        content = path.read_text()
        assert "dateCreated: 2026-01-25" in content
        assert "k/daily" in content
        assert "## 14:30" in content
        assert "First entry" in content


def test_append_to_daily_appends_to_existing(temp_vault):
    """Test appending to an existing daily note."""
    from src.services.daily_notes import append_to_daily

    # Create existing daily note
    dailies = temp_vault / "Dailies"
    dailies.mkdir()
    existing_path = dailies / "2026-01-25.md"
    existing_path.write_text("""---
dateCreated: 2026-01-25
tags:
  - k/daily
---

## 10:00
Morning entry
""")

    with (
        patch("src.services.daily_notes.settings") as mock_settings,
        patch("src.services.daily_notes.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.daily_notes_path = dailies
        mock_settings.timezone = "UTC"
        mock_settings.daily_note_format = "%Y-%m-%d"
        mock_dt.now.return_value = datetime(2026, 1, 25, 15, 45, 0)

        path, section_time = append_to_daily(content="Afternoon entry")

        assert path == existing_path
        assert section_time == "15:45"
        content = path.read_text()
        assert "## 10:00" in content
        assert "Morning entry" in content
        assert "## 15:45" in content
        assert "Afternoon entry" in content


def test_append_to_daily_with_attachment(temp_vault):
    """Test appending content with attachment."""
    from src.services.daily_notes import append_to_daily

    with (
        patch("src.services.daily_notes.settings") as mock_settings,
        patch("src.services.daily_notes.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.daily_notes_path = temp_vault / "Dailies"
        mock_settings.timezone = "UTC"
        mock_settings.daily_note_format = "%Y-%m-%d"
        mock_dt.now.return_value = datetime(2026, 1, 25, 16, 0, 0)

        path, section_time = append_to_daily(
            content="Photo caption",
            attachment_path="+/attachments/photo.jpg",
        )

        assert section_time == "16:00"
        content = path.read_text()
        assert "## 16:00" in content
        assert "Photo caption" in content
        assert "![[+/attachments/photo.jpg]]" in content


def test_append_to_daily_attachment_only(temp_vault):
    """Test appending attachment with no text content."""
    from src.services.daily_notes import append_to_daily

    with (
        patch("src.services.daily_notes.settings") as mock_settings,
        patch("src.services.daily_notes.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.daily_notes_path = temp_vault / "Dailies"
        mock_settings.timezone = "UTC"
        mock_settings.daily_note_format = "%Y-%m-%d"
        mock_dt.now.return_value = datetime(2026, 1, 25, 17, 30, 0)

        path, section_time = append_to_daily(
            content="",
            attachment_path="+/attachments/doc.pdf",
        )

        assert section_time == "17:30"
        content = path.read_text()
        assert "## 17:30" in content
        assert "![[+/attachments/doc.pdf]]" in content
