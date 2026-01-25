# Telegram-Obsidian Capture Bot - PRP

## Project Summary

Self-hosted Telegram bot for quick capture to Obsidian vault using Kepano's interstitial journaling style. Send text, voice, or images via Telegram chat and they appear as timestamped notes in your vault.

**Inspiration:** [Kepano's vault](https://stephango.com/vault) - fractal/interstitial journaling with timestamped notes.

---

## Finalized Decisions

| Decision          | Choice                      | Notes                                            |
| ----------------- | --------------------------- | ------------------------------------------------ |
| **Platform**      | Telegram                    | Best bot API, works offline-to-online            |
| **Transcription** | Eleven Labs Scribe API      | User has subscription, 99 languages, auto-detect |
| **Vault Sync**    | Obsidian Sync (primary)     | Already in use; Syncthing under evaluation       |
| **Destination**   | `+/` (inbox)                | Standard inbox for processing                    |
| **Filename**      | `YYYY-MM-DD HHmm.md`        | Kepano style, e.g., `2026-01-24 1430.md`         |
| **Daily Link**    | `dateCreated` property      | Enables base queries by date                     |
| **Language**      | Auto-detect                 | Scribe handles multilingual                      |
| **Hosting**       | Ubuntu VM → Beelink mini PC | Dev then production                              |

---

## Functional Requirements

- [ ] **Text capture**: Receive text messages → create timestamped note
- [ ] **Voice capture**: Receive voice → transcribe via Scribe → create note
- [ ] **Photo capture**: Receive images → embed in note with caption
- [ ] **Document capture**: Receive files → store and link in note
- [ ] **Frontmatter**: Apply `dateCreated`, `source: telegram`, `type`, `tags: [inbox]`
- [ ] **Attachments**: Store in `+/attachments/` with wikilink embeds

---

## Non-Functional Requirements

- [ ] Self-hosted (no external SaaS except Eleven Labs for transcription)
- [ ] Background service via systemd
- [ ] User whitelist (only accept from your Telegram ID)
- [ ] No exposed ports (outbound polling only)
- [ ] Auto-restart on failure
- [ ] Low resource usage for mini PC

---

## Technical Stack

| Component        | Choice                   | Rationale                        |
| ---------------- | ------------------------ | -------------------------------- |
| Language         | Python 3.11+             | Async support, good libs         |
| Bot Framework    | python-telegram-bot v21+ | Well-maintained, async           |
| Transcription    | Eleven Labs Scribe API   | User subscription, high accuracy |
| Audio Processing | FFmpeg + pydub           | Convert Telegram OGG/Opus        |
| Config           | pydantic-settings        | Type-safe, env vars              |
| Service          | systemd                  | Standard Linux daemon            |
| Logging          | structlog                | Structured, debuggable           |

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Beelink Mini PC                         │
│                                                             │
│  ┌─────────────────┐       ┌─────────────────┐             │
│  │  Telegram Bot   │       │    Nextcloud    │             │
│  │  (systemd)      │       │    (docker)     │             │
│  └────────┬────────┘       └─────────────────┘             │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  Obsidian Vault │ ◄──── Obsidian Sync ───► Mac/Mobile  │
│  │  (local folder) │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘

Flow:
1. User sends message to Telegram bot
2. Bot receives via polling (no exposed ports)
3. If voice: download OGG → convert → send to Scribe API → get text
4. If photo: download → save to +/attachments/
5. Create note in +/ with timestamp filename
6. Obsidian Sync propagates to all devices
```

---

## Note Template

**Text capture example:**

```markdown
---
dateCreated: 2026-01-24T14:30:00
source: telegram
type: text
topics:
tags:
  - inbox
aliases:
---

Quick thought about the project - need to revisit the API design.
```

**Voice capture example:**

```markdown
---
dateCreated: 2026-01-24T14:35:00
source: telegram
type: voice
topics:
tags:
  - inbox
aliases:
---

Meeting notes from call with Marco. He mentioned three key points: first, timeline shifts by two weeks. Second, budget pending from finance. Third, involve design team earlier.
```

**Photo capture example:**

```markdown
---
dateCreated: 2026-01-24T14:40:00
source: telegram
type: photo
topics:
tags:
  - inbox
aliases:
---

Whiteboard from brainstorming session

![[+/attachments/tg-2026-01-24-1440.jpg]]
```

---

## Daily Note Integration

The `dateCreated` property enables Obsidian Bases to query captures by date.

**Example Base query for daily note:**

```text
source = telegram AND dateCreated contains "2026-01-24"
```

This shows all Telegram captures for that day, allowing review during daily/weekly note processing.

---

## Project Structure

```text
telegram-obsidian-capture/
├── src/
│   ├── __init__.py
│   ├── bot.py                 # Entry point, handlers registration
│   ├── config.py              # Settings via pydantic-settings
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── text.py            # Text message handler
│   │   ├── voice.py           # Voice message handler
│   │   ├── photo.py           # Photo handler
│   │   └── document.py        # Document/file handler
│   └── services/
│       ├── __init__.py
│       ├── transcription.py   # Eleven Labs Scribe integration
│       ├── note_writer.py     # Obsidian note creation
│       └── file_manager.py    # Attachment handling
├── tests/
│   ├── __init__.py
│   ├── test_handlers.py
│   ├── test_transcription.py
│   └── test_note_writer.py
├── scripts/
│   ├── install.sh             # Setup script
│   └── telegram-capture.service  # systemd unit file
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Configuration

**.env file:**

```bash
TELEGRAM_TOKEN=your-bot-token
TELEGRAM_USER_ID=123456789  # Your Telegram user ID (whitelist)
ELEVENLABS_API_KEY=your-scribe-key
VAULT_PATH=/path/to/obsidian/vault
INBOX_FOLDER=+
ATTACHMENTS_FOLDER=+/attachments
NOTE_FILENAME_FORMAT=%Y-%m-%d %H%M
TIMEZONE=Europe/Rome
```

---

## Implementation Phases

### Phase 1: Core Setup

- Project scaffolding with pyproject.toml
- Telegram bot registration via BotFather
- Basic text message → note flow
- Configuration system with pydantic-settings
- Unit tests for note_writer

### Phase 2: Voice Transcription

- FFmpeg setup for audio conversion
- Eleven Labs Scribe API integration
- Voice message download → convert → transcribe → note
- Error handling for API failures

### Phase 3: Media Handling

- Photo download and storage
- Caption extraction and embedding
- Document/file handler
- Attachment naming convention

### Phase 4: Deployment

- systemd service configuration
- Installation script for Ubuntu
- Vault sync verification
- README documentation

### Phase 5: Enhancements (Future)

- `/status` command for health check
- `/daily` command to append to daily note instead
- Inline keyboard for quick categorization
- OCR for images (optional)
- Multiple vault support

---

## Verification Plan

| Test      | Action                     | Expected Result                     |
| --------- | -------------------------- | ----------------------------------- |
| Text      | Send "Test capture" to bot | Note `+/2026-01-24 1430.md` created |
| Voice     | Send 30s voice message     | Note with transcription in body     |
| Photo     | Send photo with caption    | Note with embed and caption         |
| Service   | Reboot mini PC             | Bot auto-starts, captures work      |
| Sync      | Create capture on mini PC  | Appears on Mac within minutes       |
| Whitelist | Send from other account    | Message rejected                    |

---

## Security Considerations

1. **User whitelist**: Only accept messages from configured Telegram user ID
2. **No exposed ports**: Bot uses polling, not webhooks
3. **Secrets in env**: Never commit tokens to git
4. **Local vault access**: Bot writes directly to filesystem
5. **Scribe API**: Audio sent to Eleven Labs (acceptable per user decision)

---

## Open Items for Future

- [ ] Syncthing evaluation as Obsidian Sync alternative
- [ ] Self-hosted Garage S3 for attachment backup
- [ ] WhatsApp support (more complex API)
- [ ] Bot commands for folder routing
- [ ] Inline keyboard for tagging on capture

---

## Resources

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [Eleven Labs Scribe API](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- [tg2obsidian reference](https://github.com/dimonier/tg2obsidian)
- [Kepano's vault philosophy](https://stephango.com/vault)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
