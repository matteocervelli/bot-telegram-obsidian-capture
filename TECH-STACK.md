# Tech Stack

## Runtime

| Component         | Technology          | Version  |
| ----------------- | ------------------- | -------- |
| Language          | Python              | 3.11+    |
| Bot framework     | python-telegram-bot | ≥21.0    |
| Configuration     | pydantic-settings   | ≥2.0     |
| HTTP client       | httpx               | ≥0.27    |
| Audio processing  | pydub + ffmpeg      | ≥0.25    |
| Logging           | structlog           | ≥24.0    |
| Transcription API | Eleven Labs Scribe  | REST API |

## Infrastructure

| Component         | Technology                                        |
| ----------------- | ------------------------------------------------- |
| Container runtime | Docker (Python 3.11-slim)                         |
| Orchestration     | docker-compose                                    |
| Storage           | Host filesystem (Obsidian vault via volume mount) |
| CI/CD             | GitHub Actions (Docker image → ghcr.io)           |

## Development

| Tool                    | Purpose                             |
| ----------------------- | ----------------------------------- |
| uv                      | Dependency management + virtual env |
| pytest + pytest-asyncio | Test runner (async mode)            |
| pytest-cov              | Coverage reporting                  |
| ruff                    | Linting + formatting                |
| hatchling               | Build backend                       |

## Architecture

```
telegram API
     │
     ▼
python-telegram-bot (polling)
     │
     ├── handlers/        ← message type routing (text, voice, photo, document, video)
     │        │
     │        ▼
     └── services/        ← business logic
              ├── note_writer.py      ← create timestamped .md files
              ├── daily_notes.py      ← append to daily note
              ├── task_manager.py     ← Obsidian Tasks plugin format
              ├── transcription.py    ← Eleven Labs Scribe API
              ├── video_processor.py  ← ffmpeg audio extraction
              └── file_manager.py     ← attachment saving
                       │
                       ▼
              Obsidian vault (filesystem)
```

## Key Design Decisions

- **Single-user bot**: user whitelist enforced at handler registration, not per-message — keeps handlers clean
- **No database**: all state lives in the Obsidian vault markdown files; `context.user_data` holds only ephemeral session state (undo tracking, daily mode flag)
- **Non-fatal transcription**: video/voice transcription failures are caught and logged; note is still created without transcript
- **Kepano filename convention**: `YYYY-MM-DD HHmm.md` for lexicographic chronological sorting in Obsidian
