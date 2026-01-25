# CLAUDE.md

Project-specific instructions for Claude Code. See [README.md](README.md) for setup and configuration.

## Architecture

```
handlers (Telegram message types) → services (business logic) → filesystem (Obsidian vault)
```

### Key Files

- `src/bot.py` - Entry point, handler registration, user whitelist
- `src/config.py` - Settings via pydantic-settings (env vars)
- `src/handlers/` - Message type handlers (text, voice, photo, document)
- `src/services/` - Business logic (transcription, note writing, file management)

### Data Flow

1. User sends message to Telegram bot
2. Handler receives message, validates user whitelist
3. If voice: download → convert OGG→MP3 → send to Eleven Labs Scribe → get text
4. If media: download → save to attachments folder
5. Note writer creates timestamped markdown file with frontmatter
6. Obsidian Sync propagates to all devices

## Development Commands

```bash
uv run pytest tests/ -v              # Run tests
uv run pytest --cov=src              # Run with coverage
uv run ruff check src/ tests/        # Linting
uv run ruff format src/ tests/       # Formatting
```

## Testing

Tests use mocked settings with temporary directories - no real vault needed.

## Code Standards

- Type hints on all functions
- Async/await for Telegram handlers
- structlog for structured logging
- pydantic-settings for configuration
