"""Tests for file_manager service."""

from unittest.mock import patch


def test_save_attachment(temp_vault):
    """Test saving an attachment file."""
    from src.services.file_manager import save_attachment

    with patch("src.services.file_manager.settings") as mock_settings:
        mock_settings.vault_path = temp_vault
        mock_settings.attachments_path = temp_vault / "+" / "attachments"
        mock_settings.attachments_folder = "+/attachments"
        mock_settings.timezone = "UTC"

        test_data = b"fake image data"
        file_path, wikilink = save_attachment(test_data, "jpg")

        assert file_path.exists()
        assert file_path.read_bytes() == test_data
        assert wikilink.startswith("+/attachments/tg-")
        assert wikilink.endswith(".jpg")
