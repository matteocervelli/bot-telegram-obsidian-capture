"""Tests for note_writer service."""

from datetime import datetime
from unittest.mock import patch


def test_create_text_note(temp_vault):
    """Test creating a basic text note."""
    from src.services.note_writer import create_note

    with (
        patch("src.services.note_writer.settings") as mock_settings,
        patch("src.services.note_writer.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.inbox_path = temp_vault / "+"
        mock_settings.timezone = "UTC"
        mock_settings.note_filename_format = "%Y-%m-%d %H%M"
        mock_dt.now.return_value = datetime(2026, 1, 24, 14, 30, 0)

        path = create_note(content="Test content", note_type="text")

        assert path.exists()
        content = path.read_text()
        assert "dateCreated:" in content
        assert "source: telegram" in content
        assert "type: text" in content
        assert "Test content" in content


def test_create_note_with_attachment(temp_vault):
    """Test creating a note with attachment embed."""
    from src.services.note_writer import create_note

    with (
        patch("src.services.note_writer.settings") as mock_settings,
        patch("src.services.note_writer.datetime") as mock_dt,
    ):
        mock_settings.vault_path = temp_vault
        mock_settings.inbox_path = temp_vault / "+"
        mock_settings.timezone = "UTC"
        mock_settings.note_filename_format = "%Y-%m-%d %H%M"
        mock_dt.now.return_value = datetime(2026, 1, 24, 14, 30, 0)

        path = create_note(
            content="Caption",
            note_type="photo",
            attachment_path="+/attachments/test.jpg",
        )

        content = path.read_text()
        assert "![[+/attachments/test.jpg]]" in content
        assert "Caption" in content
