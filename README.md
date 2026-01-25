# Telegram → Obsidian Capture Bot

A personal Telegram bot that captures messages (text, voice, photos, documents) and saves them as timestamped markdown notes in your Obsidian vault.

## Features

- **Voice transcription** via Eleven Labs Scribe API (high-quality multilingual)
- **Video messages** with automatic transcription (regular videos + video circles)
- **Photo & document capture** with automatic attachment organization
- **Text messages** saved directly as notes
- **Daily note mode** (`/daily`) - append captures to today's daily note
- **Undo command** (`/undo`) - delete last capture (works with daily mode too)
- **Kepano-style filenames** (`YYYY-MM-DD HHmm.md`) for clean chronological sorting
- **User whitelist** - only responds to your Telegram account
- **Obsidian-native frontmatter** with tags and timestamps
- **Docker support** for easy deployment anywhere

## Quick Start

### Docker (Recommended)

**Using pre-built image:**

```bash
# Pull the image
docker pull ghcr.io/matteocervelli/telegram-obsidian-capture:latest

# Create .env file with your configuration
cat > .env << EOF
TELEGRAM_TOKEN=your-bot-token
TELEGRAM_USER_ID=your-user-id
ELEVENLABS_API_KEY=your-api-key
VAULT_PATH=/vault
EOF

# Run with volume mount to your vault
docker run -d \
  --name telegram-obsidian-bot \
  --env-file .env \
  -v /path/to/your/vault:/vault \
  ghcr.io/matteocervelli/telegram-obsidian-capture:latest
```

**Building from source:**

```bash
# Clone and configure
git clone https://github.com/matteocervelli/bot-telegram-obsidian-capture.git
cd bot-telegram-obsidian-capture
cp .env.example .env
# Edit .env with your tokens and paths

# Run
docker compose up -d --build

# Check logs
docker compose logs -f
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/matteocervelli/bot-telegram-obsidian-capture.git
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
| `DAILY_NOTES_FOLDER`   | Daily notes folder path           | `calendar/days` |
| `DAILY_NOTE_FORMAT`    | strftime format for daily notes   | `%Y-%m-%d`      |

## Commands

| Command  | Description                                   |
| -------- | --------------------------------------------- |
| `/daily` | Toggle daily note mode (or `/daily on`/`off`) |
| `/undo`  | Delete last capture (section in daily mode)   |

## Note Format

Notes are created with Obsidian-compatible frontmatter:

```markdown
---
dateCreated: 2026-01-25
tags:
  - s/telegram
  - k/journal
---

Your captured content here...
```

Daily notes use a different format with timestamped sections:

```markdown
---
dateCreated: 2026-01-25
tags:
  - k/daily
---

## 14:30

First capture of the day

## 15:45

![[+/attachments/photo-2026-01-25-154532.jpg]]
Photo caption here
```

## Deployment

See [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md) for full deployment instructions including:

- Telegram bot registration
- Eleven Labs API setup
- Docker deployment (recommended)
- Native systemd service (Ubuntu)
- Troubleshooting

### Docker Deployment

```bash
docker compose up -d --build
docker compose logs -f  # View logs
```

### Native systemd (Ubuntu)

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

## Support

If you find this useful, [buy me a coffee](https://adli.men/coffee).

## License

[Polyform Noncommercial 1.0.0](LICENSE) - free for personal use, not for commercial purposes.
