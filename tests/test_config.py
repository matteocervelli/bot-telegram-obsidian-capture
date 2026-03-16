"""Tests for Settings properties."""

from pathlib import Path


def test_settings_properties():
    """All four Path properties build correctly from vault_path."""
    from src.config import settings

    vault = settings.vault_path
    assert settings.inbox_path == vault / settings.inbox_folder
    assert settings.attachments_path == vault / settings.attachments_folder
    assert settings.daily_notes_path == vault / settings.daily_notes_folder
    assert settings.task_inbox_path == vault / settings.task_inbox_file
    # Sanity: all return Path objects
    assert isinstance(settings.inbox_path, Path)
    assert isinstance(settings.attachments_path, Path)
    assert isinstance(settings.daily_notes_path, Path)
    assert isinstance(settings.task_inbox_path, Path)
