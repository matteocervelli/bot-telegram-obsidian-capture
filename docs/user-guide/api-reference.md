# Configuration Reference

All environment variables. Set in `.env` (or pass as environment variables to Docker).

## Required

| Variable             | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| `TELEGRAM_TOKEN`     | Bot token from @BotFather                                          |
| `TELEGRAM_USER_ID`   | Your Telegram user ID (whitelist — bot only responds to this user) |
| `ELEVENLABS_API_KEY` | Eleven Labs API key (for voice/video transcription via Scribe)     |
| `VAULT_PATH`         | Absolute path to your Obsidian vault                               |

## Note Storage

| Variable               | Default         | Description                                  |
| ---------------------- | --------------- | -------------------------------------------- |
| `INBOX_FOLDER`         | `+`             | Subfolder in vault for new notes             |
| `ATTACHMENTS_FOLDER`   | `+/attachments` | Subfolder for photos and documents           |
| `NOTE_FILENAME_FORMAT` | `%Y-%m-%d %H%M` | Python strftime format for note filenames    |
| `TIMEZONE`             | `Europe/Rome`   | Timezone for timestamps (any IANA zone name) |

## Daily Notes

| Variable             | Default         | Description                     |
| -------------------- | --------------- | ------------------------------- |
| `DAILY_NOTES_FOLDER` | `calendar/days` | Subfolder for daily notes files |
| `DAILY_NOTE_FORMAT`  | `%Y-%m-%d`      | Filename format for daily notes |

## Task Management

| Variable            | Default           | Description                                  |
| ------------------- | ----------------- | -------------------------------------------- |
| `TASK_INBOX_FILE`   | `+/task-inbox.md` | Path (relative to vault) for task inbox      |
| `TASK_TAG`          | `#to/do`          | Obsidian Tasks tag for regular tasks         |
| `TASK_TAG_FOLLOWUP` | `#to/follow-up`   | Obsidian Tasks tag for follow-up tasks       |
| `TASK_LIST_LIMIT`   | `10`              | Max number of tasks returned by `/task_list` |

## Optional

| Variable   | Default | Description                                                    |
| ---------- | ------- | -------------------------------------------------------------- |
| `BOT_NAME` | `None`  | Display name for the bot (reference only, not used at runtime) |

## Example .env

```bash
# Required
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_USER_ID=123456789
ELEVENLABS_API_KEY=sk_...
VAULT_PATH=/Users/you/Documents/MyVault

# Note storage (optional — these are the defaults)
INBOX_FOLDER=+
ATTACHMENTS_FOLDER=+/attachments
NOTE_FILENAME_FORMAT=%Y-%m-%d %H%M
TIMEZONE=Europe/Rome

# Daily notes (optional)
DAILY_NOTES_FOLDER=calendar/days
DAILY_NOTE_FORMAT=%Y-%m-%d

# Tasks (optional)
TASK_INBOX_FILE=+/task-inbox.md
TASK_TAG=#to/do
TASK_TAG_FOLLOWUP=#to/follow-up
TASK_LIST_LIMIT=10
```

## Notes

- **Security:** `TELEGRAM_USER_ID` acts as a whitelist — only messages from this user ID are processed. All other users are silently ignored.
- **Vault path:** Must be an absolute path. The bot creates `INBOX_FOLDER` and `ATTACHMENTS_FOLDER` if they don't exist.
- **Timezone:** Used for note timestamps and relative date calculation (`--today`, `--tomorrow`). Should match your Obsidian vault timezone.
