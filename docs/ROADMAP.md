# Telegram-Obsidian Capture Bot - Roadmap

Future development ideas organized by priority and effort.

---

## Philosophy

This bot is a **capture tool** - fast, simple, reliable. Features should enhance capture, not turn it into a full Obsidian client.

---

## Phase 1: Quick Wins ✅ COMPLETED

Low effort, high impact improvements.

### 1.1 Daily Note Append (`/daily`) ✅

**Status:** Implemented in v0.1.1

**Features:**

- `/daily` toggles mode (or `/daily on` / `/daily off`)
- Messages append to `YYYY-MM-DD.md` in configured daily notes folder
- Each capture adds timestamped section: `## HH:MM` followed by content
- Creates daily note with frontmatter if it doesn't exist
- `/undo` in daily mode removes only the last section, not the whole file

**Configuration:**

```env
DAILY_NOTES_FOLDER=calendar/days
DAILY_NOTE_FORMAT=%Y-%m-%d
```

---

### 1.2 Undo Last Capture (`/undo`) ✅

**Status:** Implemented in v0.1.1

**Features:**

- Bot tracks last created file path in memory
- `/undo` deletes note and associated attachments
- In daily mode: removes only the last `## HH:MM` section
- Confirmation message shows deleted items
- Single-use per capture (can't undo twice)

---

### 1.3 Video Message Support ✅

**Status:** Implemented in v0.1.1

**Features:**

- Regular videos and video circles (video notes) supported
- Videos saved to attachments folder with `vid-` or `vnote-` prefix
- Audio extracted and transcribed via Eleven Labs
- Note created with video embed + transcription
- Transcription failure is non-fatal (note still created with embed)

---

## Phase 2: Setup & Configuration

### 2.0 Interactive Setup Wizard

**Goal:** Guide users through initial configuration with an interactive CLI.

**Behavior:**

```bash
# First run or explicit setup
uv run python -m src.setup

# Or via make
make setup
```

**Steps:**

1. Check for existing `.env` file
2. Prompt for Telegram bot token (with link to BotFather)
3. Prompt for Telegram user ID (with instructions to get it)
4. Prompt for Eleven Labs API key (with link to dashboard)
5. Prompt for vault path (with file picker or manual entry)
6. Configure optional settings (inbox folder, timezone, daily notes folder)
7. Validate all inputs
8. Write `.env` file
9. Test Telegram connection
10. Test vault write access

**Features:**

- Colored terminal output
- Input validation with helpful error messages
- Skip already-configured values
- `--reconfigure` flag to reset specific values

**Effort:** ~4-5 hours

---

## Phase 3: Transcription Backends

Multiple transcription options for flexibility and cost control.

### 3.1 Transcription Provider Abstraction

**Goal:** Support multiple transcription services with unified interface.

**Architecture:**

```
src/services/transcription/
├── __init__.py
├── base.py          # Abstract interface
├── elevenlabs.py    # Current implementation
├── openai.py        # OpenAI Whisper API
└── local.py         # Local Whisper
```

**Interface:**

```python
class TranscriptionProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: Path) -> str:
        pass
```

**Configuration:**

```env
TRANSCRIPTION_PROVIDER=elevenlabs  # elevenlabs | openai | local
```

**Effort:** ~2 hours (refactor only)

---

### 3.2 OpenAI Whisper API

**Goal:** Add OpenAI as transcription option.

**Why:**

- Many users already have OpenAI API keys
- Good accuracy, reasonable pricing
- Simple API

**Configuration:**

```env
TRANSCRIPTION_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Effort:** ~2 hours

---

### 3.3 Local Whisper (faster-whisper)

**Goal:** Fully offline transcription with no API costs.

**Why:**

- Zero ongoing cost
- Privacy (audio never leaves machine)
- Works offline

**Implementation:**

- Use `faster-whisper` (CTranslate2 optimized)
- Model configurable: tiny, base, small, medium, large
- CPU or GPU (CUDA/Metal) acceleration

**Configuration:**

```env
TRANSCRIPTION_PROVIDER=local
WHISPER_MODEL=base  # tiny | base | small | medium | large
```

**Docker considerations:**

- Separate Dockerfile for local Whisper (larger image with model)
- Or download model on first run

**Effort:** ~4-6 hours

---

## Phase 4: Capture Enhancements

### 4.1 Message Batching

**Goal:** Collect multiple messages, then save as single note.

**Behavior:**

- `/batch` starts batch mode
- Messages collected in memory (not saved yet)
- `/save` creates single note with all collected content
- `/cancel` discards batch
- Auto-save after timeout (configurable, default 5 min)

**Note format:**

```markdown
---
type: batch
---

[Text message 1]

---

[Voice transcription]

---

![[attachment.jpg]]
[Photo caption]
```

**Use case:** Capturing related thoughts across multiple messages.

**Effort:** ~4-5 hours

---

### 4.2 Auto-Tagging via LLM

**Goal:** Automatically extract topics/tags from captured content.

**Behavior:**

- After note content is ready, send to LLM
- LLM returns suggested tags
- Tags added to frontmatter `topics:` field

**Implementation options:**

1. Local LLM (Ollama) - free, private
2. OpenAI API - simple, accurate
3. Anthropic API - alternative

**Configuration:**

```env
AUTO_TAG_ENABLED=true
AUTO_TAG_PROVIDER=ollama  # ollama | openai | anthropic
AUTO_TAG_MODEL=llama3.2   # Model name
```

**Prompt:**

```
Extract 1-5 topic tags from this note. Return only lowercase tags separated by commas. No explanation.

Content: {note_content}
```

**Effort:** ~4-5 hours

---

## Phase 5: Operations & Monitoring

### 5.1 Health Endpoint

**Goal:** HTTP endpoint for monitoring bot health.

**Implementation:**

- Lightweight HTTP server (aiohttp or built-in)
- `/health` returns status JSON
- `/ready` for Kubernetes readiness probe

**Response:**

```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "last_message_at": "2026-01-25T14:30:00Z",
  "telegram_connected": true,
  "vault_writable": true
}
```

**Configuration:**

```env
HEALTH_PORT=8080
```

**Effort:** ~2-3 hours

---

### 5.2 Prometheus Metrics

**Goal:** Export metrics for Grafana dashboards.

**Metrics:**

```
# Counter
telegram_messages_total{type="text|voice|photo|video|document"}
telegram_errors_total{type="transcription|write|telegram"}

# Histogram
transcription_duration_seconds
note_write_duration_seconds

# Gauge
bot_uptime_seconds
batch_messages_pending
```

**Endpoint:** `/metrics` (Prometheus format)

**Effort:** ~3-4 hours

---

## Phase 6: Distribution

### 6.1 Docker Hub / GitHub Container Registry

**Goal:** Pre-built images for easy deployment.

**Deliverables:**

- Automated builds via GitHub Actions
- Multi-arch images (amd64, arm64)
- Tagged releases + `latest`

**Usage:**

```yaml
services:
  bot:
    image: ghcr.io/matteocervelli/telegram-obsidian-capture:latest
```

**Effort:** ~2-3 hours

---

### 6.2 Homebrew Service (macOS)

**Goal:** Native macOS installation and service management.

**Installation:**

```bash
brew tap matteocervelli/tap
brew install telegram-obsidian-capture
brew services start telegram-obsidian-capture
```

**Deliverables:**

- Homebrew formula
- LaunchAgent plist for service management
- Configuration in `~/.config/telegram-obsidian-capture/`

**Effort:** ~4-5 hours

---

### 6.3 Obsidian Plugin

**Goal:** Install and configure bot directly from Obsidian.

**Features:**

- Settings UI for API keys and configuration
- Start/stop bot from within Obsidian
- Status indicator in status bar
- View recent captures

**Architecture:**

- Plugin spawns bot as subprocess
- Communicates via local HTTP or IPC
- Plugin handles configuration, bot handles capture

**Considerations:**

- Requires Node.js runtime bundled or system Python
- Mobile support unlikely (iOS/Android restrictions)
- Desktop only (Windows, macOS, Linux)

**Effort:** ~15-20 hours (significant)

---

## Out of Scope

Intentionally excluded to keep the bot simple:

- **Multi-user support** - This is a personal capture tool
- **Vault search/queries** - Use Obsidian for that
- **Task management** - Outside capture scope
- **Two-way sync** - Capture only, not full client
- **Telegram groups** - Personal bot, not group bot

---

## Priority Order

Suggested implementation sequence:

1. ~~`/undo` command~~ ✅ (v0.1.1)
2. ~~`/daily` command~~ ✅ (v0.1.1)
3. ~~Video message support~~ ✅ (v0.1.1)
4. Interactive setup wizard
5. Transcription abstraction + OpenAI
6. Health endpoint
7. Message batching
8. Local Whisper
9. Prometheus metrics
10. Docker Hub publishing
11. Auto-tagging
12. Homebrew service
13. Obsidian plugin (if demand exists)

---

## Version Milestones

| Version | Features                                       | Status  |
| ------- | ---------------------------------------------- | ------- |
| 0.1.0   | Initial release (text, voice, photo, document) | ✅      |
| 0.1.1   | `/undo`, `/daily`, video messages              | ✅      |
| 0.2.0   | Interactive setup wizard                       | Planned |
| 0.3.0   | Multi-backend transcription (OpenAI)           | Planned |
| 0.4.0   | Health endpoint, Prometheus                    | Planned |
| 0.5.0   | Message batching                               | Planned |
| 0.6.0   | Local Whisper                                  | Planned |
| 0.7.0   | Auto-tagging                                   | Planned |
| 1.0.0   | Stable release, Docker Hub, Homebrew           | Planned |
