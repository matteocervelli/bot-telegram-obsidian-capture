# Getting Started

Quick setup to get the bot running and capturing to your Obsidian vault.

## Prerequisites

- Telegram account
- Obsidian vault (local or synced)
- Eleven Labs account (Creator plan or above — for Scribe transcription)
- Docker (recommended) or Python 3.11+ + `uv`
- `ffmpeg` (local dev only; included in Docker image)

## Step 1: Create Telegram Bot

1. Open Telegram → search `@BotFather` → send `/newbot`
2. Choose a name and username (must end in `bot`)
3. **Save the token** — format: `123456789:ABCdef...`

To get your user ID:

1. Search `@userinfobot` → send `/start`
2. **Save your user ID** (a number like `123456789`)

## Step 2: Get Eleven Labs API Key

1. Go to [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys
2. Copy your key

> Note: Scribe is only available on Creator plan and above.

## Step 3: Configure Environment

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Minimum required variables:

```bash
TELEGRAM_TOKEN=123456789:ABCdef...
TELEGRAM_USER_ID=123456789
ELEVENLABS_API_KEY=your-key
VAULT_PATH=/absolute/path/to/your/vault
```

See [Configuration Reference](api-reference.md) for all options.

## Step 4: Run with Docker (Recommended)

```bash
docker compose up -d --build
docker compose logs -f   # should show "bot_ready"
```

## Step 5: Verify

Send a text message to your bot. A timestamped note should appear in your vault's `+/` folder within seconds.

## Next Steps

- [Capture Features](feature-capture.md) — text, voice, photo, document
- [Task Management](feature-tasks.md) — `/task`, `/task_list`, `/done`
- [Daily Notes Mode](how-to-daily-notes.md) — append to daily notes
