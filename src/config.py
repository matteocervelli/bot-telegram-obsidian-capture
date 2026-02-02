"""Configuration via pydantic-settings with env var support."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram
    telegram_token: str
    telegram_user_id: int  # Whitelist: only accept from this user
    bot_name: str | None = None  # For reference only

    # Eleven Labs Scribe
    elevenlabs_api_key: str

    # Vault paths
    vault_path: Path
    inbox_folder: str = "+"
    attachments_folder: str = "+/attachments"

    # Note formatting
    note_filename_format: str = "%Y-%m-%d %H%M"
    timezone: str = "Europe/Rome"

    # Daily notes
    daily_notes_folder: str = "calendar/days"
    daily_note_format: str = "%Y-%m-%d"

    # Task management
    task_inbox_file: str = "+/task-inbox.md"
    task_tag: str = "#to/do"
    task_tag_followup: str = "#to/follow-up"
    task_list_limit: int = 10

    @property
    def inbox_path(self) -> Path:
        return self.vault_path / self.inbox_folder

    @property
    def attachments_path(self) -> Path:
        return self.vault_path / self.attachments_folder

    @property
    def daily_notes_path(self) -> Path:
        return self.vault_path / self.daily_notes_folder

    @property
    def task_inbox_path(self) -> Path:
        return self.vault_path / self.task_inbox_file


settings = Settings()
