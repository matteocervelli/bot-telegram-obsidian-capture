# Telegram → Obsidian Capture Bot

A personal Telegram bot that captures messages (text, voice, photos, documents) and saves them as timestamped markdown notes in your Obsidian vault.

## Features

- **Voice transcription** via Eleven Labs Scribe API (high-quality multilingual)
- **Photo & document capture** with automatic attachment organization
- **Text messages** saved directly as notes
- **Kepano-style filenames** (`YYYY-MM-DD HHmm.md`) for clean chronological sorting
- **User whitelist** - only responds to your Telegram account
- **Obsidian-native frontmatter** with type, source, and tags

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/bot-telegram-obsidian-capture.git
cd bot-telegram-obsidian-capture

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your tokens and paths

# Run the bot
uv run python -m src.bot
```

## Requirements

- Python 3.11+
- [FFmpeg](https://ffmpeg.org/) (for voice message conversion)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Eleven Labs API Key (from [elevenlabs.io](https://elevenlabs.io))

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable               | Description                       | Default         |
| ---------------------- | --------------------------------- | --------------- |
| `TELEGRAM_TOKEN`       | Bot token from @BotFather         | required        |
| `TELEGRAM_USER_ID`     | Your Telegram user ID (whitelist) | required        |
| `ELEVENLABS_API_KEY`   | Eleven Labs API key for Scribe    | required        |
| `VAULT_PATH`           | Absolute path to Obsidian vault   | required        |
| `INBOX_FOLDER`         | Inbox folder name                 | `+`             |
| `ATTACHMENTS_FOLDER`   | Attachments path                  | `+/attachments` |
| `NOTE_FILENAME_FORMAT` | strftime format for filenames     | `%Y-%m-%d %H%M` |
| `TIMEZONE`             | Timezone for timestamps           | `Europe/Rome`   |

## Note Format

Notes are created with Obsidian-compatible frontmatter:

```markdown
---
dateCreated: 2026-01-24T14:30:00+01:00
source: telegram
type: voice
topics:
tags:
  - inbox
aliases:
---

Transcribed content here...
```

## Deployment

See [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md) for full deployment instructions including:

- Telegram bot registration
- Eleven Labs API setup
- systemd service configuration (Ubuntu)
- Troubleshooting

Quick systemd deployment:

```bash
./scripts/install.sh
sudo systemctl enable telegram-capture
sudo systemctl start telegram-capture
```

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) for details.
