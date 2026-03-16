# Capture Features

All message types the bot accepts and how they're stored in Obsidian.

## Text Messages

Send any text message → creates a timestamped note in `inbox_folder` (default: `+`).

**Note format:**

```markdown
---
dateCreated: 2026-03-16
tags:
  - s/telegram
  - k/journal
---

Your captured text here...
```

**Filename:** `YYYY-MM-DD HHmm.md` (configurable via `NOTE_FILENAME_FORMAT`)

If a note with the same minute already exists, seconds are appended: `YYYY-MM-DD HHmmSS.md`.

### Task prefix shortcut

Start a message with `task:` (case-insensitive) to add it as a task instead of a note:

```
task: Buy milk
```

Equivalent to `/task Buy milk`.

## Voice Messages

Send a voice memo → bot transcribes via Eleven Labs Scribe → saves note with transcript.

**Flow:**

1. Bot replies "🎙 Transcribing..."
2. Downloads OGG file → converts to MP3 via pydub/ffmpeg
3. Sends to Eleven Labs Scribe API
4. Creates note with transcript text

## Video Messages

Send a video or video circle (video note) → saves mp4 attachment + attempts audio transcription.

**Flow:**

1. Bot replies "Processing video..."
2. Saves video as attachment (`vid-TIMESTAMP.mp4` for regular video, `vnote-TIMESTAMP.mp4` for video circles)
3. Extracts audio and transcribes (non-fatal — capture succeeds even if transcription fails)
4. Creates note with transcription (if available) and embedded video

## Photos

Send a photo (with or without caption) → saves image + creates note.

**Storage:**

- Image saved to `attachments_folder` (default: `+/attachments`) with filename `tg-YYYY-MM-DD-HHmmSS.jpg`
- Note contains Obsidian embed: `![[+/attachments/tg-2026-03-16-143000.jpg]]`
- Caption (if any) included as body text

## Documents

Send any file (PDF, Word, etc.) → saves file + creates note with original filename reference.

**Storage:**

- File saved to `attachments_folder` with filename `doc-YYYY-MM-DD-HHmmSS.EXT`
- Note body contains `Original filename: \`original-name.ext\`` and an embed link
- Caption (if any) is prepended to the note body

## Undo Last Capture

`/undo` deletes the last captured note and its attachments.

**Behavior:**

- Normal mode: deletes the entire note file + attachments
- Daily notes mode: removes only the last section from the daily note (leaves earlier captures intact)
- Single-use: one undo per session (clears after use)

> If files were already deleted, bot replies "Files already removed".
