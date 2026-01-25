"""Pytest configuration and fixtures."""

import os

# Set test environment variables BEFORE any src imports
# This must happen at module level, before pytest collects tests
os.environ.setdefault("TELEGRAM_TOKEN", "test-token-123")
os.environ.setdefault("TELEGRAM_USER_ID", "123456789")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-api-key")
os.environ.setdefault("VAULT_PATH", "/tmp/test-vault")
os.environ.setdefault("INBOX_FOLDER", "+")
os.environ.setdefault("ATTACHMENTS_FOLDER", "+/attachments")
os.environ.setdefault("TIMEZONE", "UTC")

import pytest


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault structure."""
    inbox = tmp_path / "+"
    inbox.mkdir()
    attachments = tmp_path / "+" / "attachments"
    attachments.mkdir()
    return tmp_path
