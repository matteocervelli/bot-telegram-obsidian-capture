# Roadmap

## Planned

- Scheduled captures (send a note at a future time) #3
- Multi-vault support (route messages to different vaults by tag) #4
- Rich text formatting preservation (bold, italic from Telegram) #5
- Image OCR fallback (extract text from photos without captions) #6

## In Progress

_Nothing currently in progress._

## Released

### v0.2.0 — 2026-02-02

- Task management system: `/task`, `/task_list`, `/done`
- Obsidian Tasks plugin compatibility (`#to/do`, `#to/follow-up`)
- Due date flags: `--today`, `--tomorrow`, `--yesterday`, `--YYYY-MM-DD`
- `task: ...` text prefix shortcut
- Telegram em-dash conversion

### v0.1.1 — 2026-01-25

- `/undo` command (works in daily mode too)
- `/daily` command to toggle daily note mode
- Daily note support: appends with `### HH:MM` sections
- Video message transcription (regular + video circles)

### v0.1.0 — 2026-01-24

- Initial release
- Text, voice, photo, document capture
- Voice transcription via Eleven Labs Scribe
- Kepano-style filenames (`YYYY-MM-DD HHmm.md`)
- User whitelist, Docker support, configurable vault path
