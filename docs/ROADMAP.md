# Telegram-Obsidian Capture Bot - Roadmap

Future development ideas organized by priority and effort.

---

## Philosophy

This bot is a **capture tool** - fast, simple, reliable. Features should enhance capture, not turn it into a full Obsidian client.

---

## Phase 1: Quick Wins

Low effort, high impact improvements.

### 1.1 Daily Note Append (`/daily`)

**Goal:** Append content to today's daily note instead of creating a new file.

**Behavior:**

- `/daily` toggles mode (or `/daily on` / `/daily off`)
- When enabled, messages append to `YYYY-MM-DD.md` in configured daily notes folder
- Each capture adds timestamped section: `## 14:30` followed by content
- If daily note doesn't exist, create it with standard frontmatter

**Configuration:**

```env
DAILY_NOTES_FOLDER=Daily Notes
DAILY_NOTE_FORMAT=%Y-%m-%d
```

**Effort:** ~2-3 hours

---

### 1.2 Undo Last Capture (`/undo`)

**Goal:** Delete the last created note (for mistakes/duplicates).

**Behavior:**

- Bot tracks last created file path in memory
- `/undo` deletes that file and clears the reference
- Confirmation message: "Deleted: 2026-01-25 1430.md"
- Only works once per capture (can't undo twice)

**Safety:**

- Only deletes files in inbox folder (never outside)
- Attachments deleted if note contained them

**Effort:** ~1-2 hours

---

### 1.3 Video Message Support

**Goal:** Capture video messages with both video file and transcription.

**Behavior:**

1. Download video from Telegram
2. Save to attachments folder (like photos)
3. Extract audio track
4. Transcribe audio (reuse voice transcription pipeline)
5. Create note with video embed and transcription

**Note format:**

```markdown
---
type: video
---

![[+/attachments/tg-video-20260125-1430.mp4]]

[Transcription]
Your transcribed content here...
```

**Technical:**

- FFmpeg already available (used for voice)
- Extract audio: `ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3`
- Telegram video notes (circles) and regular videos both supported

**Effort:** ~3-4 hours

---

## Phase 2: Transcription Backends

Multiple transcription options for flexibility and cost control.

### 2.1 Transcription Provider Abstraction

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

### 2.2 OpenAI Whisper API

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

### 2.3 Local Whisper (faster-whisper)

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

## Phase 3: Capture Enhancements

### 3.1 Message Batching

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

### 3.2 Auto-Tagging via LLM

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

## Phase 4: Operations & Monitoring

### 4.1 Health Endpoint

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

### 4.2 Prometheus Metrics

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

## Phase 5: Distribution

### 5.1 Docker Hub / GitHub Container Registry

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

### 5.2 Homebrew Service (macOS)

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

### 5.3 Obsidian Plugin

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

1. `/undo` command (quick win, safety feature)
2. `/daily` command (common workflow)
3. Video message support (completes media types)
4. Transcription abstraction + OpenAI
5. Health endpoint
6. Message batching
7. Local Whisper
8. Prometheus metrics
9. Docker Hub publishing
10. Auto-tagging
11. Homebrew service
12. Obsidian plugin (if demand exists)

---

## Version Milestones

| Version | Features                             |
| ------- | ------------------------------------ |
| 0.2.0   | `/undo`, `/daily` commands           |
| 0.3.0   | Video messages                       |
| 0.4.0   | Multi-backend transcription (OpenAI) |
| 0.5.0   | Health endpoint, Prometheus          |
| 0.6.0   | Message batching                     |
| 0.7.0   | Local Whisper                        |
| 0.8.0   | Auto-tagging                         |
| 1.0.0   | Stable release, Docker Hub, Homebrew |
