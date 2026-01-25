# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-01-25

### Added

- `/undo` command to delete last captured note and attachments
- `/daily` command to toggle daily note mode (`/daily`, `/daily on`, `/daily off`)
- Daily note support: captures append to `YYYY-MM-DD.md` with `## HH:MM` sections
- Video message support with automatic transcription
- Video circle (video note) support with automatic transcription
- `transcribe_mp3()` function for direct MP3 transcription
- `DAILY_NOTES_FOLDER` configuration option (default: `calendar/days`)
- `DAILY_NOTE_FORMAT` configuration option (default: `%Y-%m-%d`)

### Changed

- `/undo` in daily mode now removes only the last section, not the entire file
- Handlers now track `is_daily` and `section_time` for smart undo behavior

### Fixed

- Video transcription now works correctly (was failing due to double OGG→MP3 conversion)

## [0.1.0] - 2026-01-24

### Added

- Initial release
- Text message capture to Obsidian notes
- Voice message transcription via Eleven Labs Scribe API
- Photo capture with automatic attachment organization
- Document capture with original filename preservation
- User whitelist for security (single-user bot)
- Kepano-style filenames (`YYYY-MM-DD HHmm.md`)
- Obsidian-native frontmatter with tags
- Docker support with docker-compose
- Configurable vault path, inbox folder, and attachments folder
- Timezone support for timestamps

[Unreleased]: https://github.com/matteocervelli/bot-telegram-obsidian-capture/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/matteocervelli/bot-telegram-obsidian-capture/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/matteocervelli/bot-telegram-obsidian-capture/releases/tag/v0.1.0
