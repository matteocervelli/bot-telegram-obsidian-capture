# Telegram-Obsidian Capture Bot - Setup Guide

Step-by-step guide to get the bot running. Execute each phase in order.

---

## Phase 1: Telegram Bot Registration

### Step 1.1: Create Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Obsidian Capture")
4. Choose a username (must end in `bot`, e.g., `my_obsidian_capture_bot`)
5. **Save the token** - looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 1.2: Get Your Telegram User ID

1. Search for `@userinfobot` in Telegram
2. Send `/start`
3. **Save your user ID** - a number like `123456789`

This ID is your whitelist - the bot will only respond to you.

### Step 1.3: Configure Bot Settings (Optional)

Send these commands to `@BotFather`:

```
/setdescription
Quick capture to Obsidian vault

/setabouttext
Send text, voice, photos, or files to capture as timestamped notes.

/setuserpic
[Upload an icon if desired]
```

---

## Phase 2: Eleven Labs API Key

### Step 2.1: Get Scribe API Key

1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign in to your account
3. Navigate to **Profile** → **API Keys**
4. Create or copy your API key
5. **Save the API key**

Note: Scribe is available on Creator plan and above.

---

## Phase 3: Local Environment Setup

### Step 3.1: Install System Dependencies

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install -y ffmpeg
```

### Step 3.2: Verify Python and uv

```bash
python3 --version  # Should be 3.11+
uv --version       # Should be installed
```

If uv not installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3.3: Clone and Install Dependencies

```bash
cd /Users/matteocervelli/dev/projects/bot-telegram-obsidian-capture
uv sync
```

---

## Phase 4: Configuration

### Step 4.1: Create .env File

```bash
cp .env.example .env
```

### Step 4.2: Edit .env with Your Values

Open `.env` and fill in:

```bash
# From Phase 1.1
TELEGRAM_TOKEN=your-bot-token-here

# From Phase 1.2
TELEGRAM_USER_ID=your-user-id-here

# From Phase 2.1
ELEVENLABS_API_KEY=your-api-key-here

# Your Obsidian vault path (absolute path)
VAULT_PATH=/Users/matteocervelli/path/to/your/vault

# Inbox settings (usually keep defaults)
INBOX_FOLDER=+
ATTACHMENTS_FOLDER=+/attachments

# Timestamp settings
NOTE_FILENAME_FORMAT=%Y-%m-%d %H%M
TIMEZONE=Europe/Rome
```

### Step 4.3: Verify Vault Path

Ensure your vault path exists and the inbox folder is writable:

```bash
ls -la "$VAULT_PATH"
mkdir -p "$VAULT_PATH/+"
mkdir -p "$VAULT_PATH/+/attachments"
```

---

## Phase 5: Local Testing

### Step 5.1: Run Tests

```bash
uv run pytest tests/ -v
```

All 3 tests should pass.

### Step 5.2: Start Bot Locally

```bash
uv run python -m src.bot
```

You should see:

```
starting_bot user_id=123456789
bot_ready
```

### Step 5.3: Test Each Message Type

1. **Text**: Send a text message to your bot
   - Check: Note appears in `+/` folder with timestamp filename

2. **Voice**: Send a voice message
   - Check: Bot replies "🎙 Transcribing..."
   - Check: Note appears with transcribed text

3. **Photo**: Send a photo with caption
   - Check: Image saved in `+/attachments/`
   - Check: Note has embed `![[+/attachments/tg-...jpg]]`

4. **Document**: Send a PDF or file
   - Check: File saved in `+/attachments/`
   - Check: Note links to file

### Step 5.4: Verify Obsidian Sync

If using Obsidian Sync:

1. Create a capture on the bot
2. Open Obsidian on another device
3. Verify the note appears within 1-2 minutes

---

## Phase 6: Production Deployment (Ubuntu)

### Step 6.1: Prepare Server

SSH into your Ubuntu server (Beelink mini PC):

```bash
ssh user@your-server-ip
```

### Step 6.2: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv ffmpeg git
```

### Step 6.3: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart shell
```

### Step 6.4: Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/bot-telegram-obsidian-capture.git
cd bot-telegram-obsidian-capture
```

Or copy from your dev machine:

```bash
# From your Mac:
rsync -avz --exclude='.venv' --exclude='__pycache__' \
  /Users/matteocervelli/dev/projects/bot-telegram-obsidian-capture/ \
  user@server:~/telegram-obsidian-capture/
```

### Step 6.5: Create .env on Server

```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

Update `VAULT_PATH` to match your server's vault location.

### Step 6.6: Install Dependencies

```bash
uv sync
```

### Step 6.7: Test Bot on Server

```bash
uv run python -m src.bot
```

Send a test message. Ctrl+C when confirmed working.

### Step 6.8: Install systemd Service

```bash
# Edit service file with correct paths
nano scripts/telegram-capture.service

# Update these lines:
# User=your-username
# WorkingDirectory=/home/your-username/telegram-obsidian-capture
# EnvironmentFile=/home/your-username/telegram-obsidian-capture/.env
# ExecStart=/home/your-username/telegram-obsidian-capture/.venv/bin/python -m src.bot

# Install service
sudo cp scripts/telegram-capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-capture
sudo systemctl start telegram-capture
```

### Step 6.9: Verify Service Running

```bash
sudo systemctl status telegram-capture
journalctl -u telegram-capture -f
```

---

## Phase 7: Troubleshooting

### Bot Not Responding

```bash
# Check if running
sudo systemctl status telegram-capture

# Check logs
journalctl -u telegram-capture -n 50

# Restart
sudo systemctl restart telegram-capture
```

### Transcription Failing

- Verify `ELEVENLABS_API_KEY` is correct
- Check your Eleven Labs subscription includes Scribe
- Check FFmpeg is installed: `ffmpeg -version`

### Notes Not Appearing

- Verify `VAULT_PATH` is correct and writable
- Check inbox folder exists: `ls -la $VAULT_PATH/+`
- Check bot logs for errors

### Wrong User Rejected

- Verify `TELEGRAM_USER_ID` matches your actual ID
- Get ID again from `@userinfobot`

### Service Won't Start

```bash
# Check for syntax errors
uv run python -c "from src.config import settings; print(settings)"

# Run manually to see errors
cd ~/telegram-obsidian-capture
uv run python -m src.bot
```

---

## Quick Reference

### Commands

```bash
# Local development
uv sync                          # Install deps
uv run python -m src.bot         # Run bot
uv run pytest tests/ -v          # Run tests
uv run ruff check src/           # Lint
uv run ruff format src/          # Format

# Production (Ubuntu)
sudo systemctl start telegram-capture
sudo systemctl stop telegram-capture
sudo systemctl restart telegram-capture
sudo systemctl status telegram-capture
journalctl -u telegram-capture -f
```

### File Locations

| File             | Purpose                         |
| ---------------- | ------------------------------- |
| `.env`           | Your credentials (never commit) |
| `src/bot.py`     | Entry point                     |
| `src/config.py`  | Settings                        |
| `+/`             | Inbox folder in vault           |
| `+/attachments/` | Media files                     |

### Note Format

```markdown
---
dateCreated: 2026-01-24T14:30:00+01:00
source: telegram
type: text|voice|photo|document
topics:
tags:
  - inbox
aliases:
---

Your captured content here...
```

---

## Checklist

- [ ] Bot registered with @BotFather
- [ ] Telegram user ID obtained
- [ ] Eleven Labs API key obtained
- [ ] FFmpeg installed
- [ ] `.env` configured
- [ ] Local tests pass
- [ ] Local bot test successful
- [ ] Text capture works
- [ ] Voice capture works
- [ ] Photo capture works
- [ ] Document capture works
- [ ] Obsidian Sync confirmed
- [ ] Production server prepared
- [ ] systemd service installed
- [ ] Service auto-starts on reboot
