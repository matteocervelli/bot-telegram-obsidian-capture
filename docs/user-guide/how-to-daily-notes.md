# Daily Notes Mode

Append captures to a daily note (`YYYY-MM-DD.md`) instead of creating individual note files.

## Enabling Daily Notes Mode

```
/daily        # toggle (on if off, off if on)
/daily on     # explicitly enable
/daily off    # explicitly disable
```

The bot confirms: `Daily mode: ON` or `Daily mode: OFF`.

> **Session-scoped:** Daily mode is per-session (bot restart resets to off).

## How It Works

When daily mode is ON:

- The bot appends to `{DAILY_NOTES_FOLDER}/{YYYY-MM-DD}.md` (default: `calendar/days/2026-03-16.md`)
- Each capture gets its own `### HH:MM` section header
- If the daily note doesn't exist, it's created

**Example daily note after 3 captures:**

```markdown
### 09:15

Meeting with client about Q1 review

### 11:32

🎙 Transcription: Voice note about project timeline...

### 14:07

![[+/attachments/tg-2026-03-16-140700.jpg]]
Photo from site visit
```

## Undo in Daily Mode

`/undo` in daily mode removes only the **last section** (the most recent `### HH:MM` block) from the daily note — it does not delete the entire file.

Earlier captures in the same daily note are preserved.

## Configuration

| Variable             | Default         | Description                     |
| -------------------- | --------------- | ------------------------------- |
| `DAILY_NOTES_FOLDER` | `calendar/days` | Folder for daily notes          |
| `DAILY_NOTE_FORMAT`  | `%Y-%m-%d`      | Filename format for daily notes |

> Change `DAILY_NOTE_FORMAT` to match your Obsidian daily notes template (e.g., `%d-%m-%Y` for European format).
