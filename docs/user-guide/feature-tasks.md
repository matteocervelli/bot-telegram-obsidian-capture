# Task Management

Add, list, and complete tasks in your Obsidian vault from Telegram.

Tasks are stored in a single inbox file (default: `+/task-inbox.md`) using [Obsidian Tasks](https://obsidian-tasks.netlify.app/) compatible format.

## Adding Tasks

### /task command

```
/task Buy milk
/task Call dentist --follow-up
/task Submit report --today
/task Review PR --tomorrow
/task File taxes --2026-04-15
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--follow-up` | Uses `#to/follow-up` tag (default: `#to/do`) |
| `--today` | Sets due date to today |
| `--tomorrow` | Sets due date to tomorrow |
| `--yesterday` | Sets due date to yesterday |
| `--YYYY-MM-DD` | Sets explicit due date |

> **Telegram em-dash note:** Telegram on mobile often converts `--` to `—` (em-dash). Both work — the bot handles all dash variants transparently.

### task: text prefix

You can also add tasks by starting a regular message with `task:`:

```
task: Buy milk
task: Call dentist
```

This is equivalent to `/task Buy milk` but works as a plain text message (no slash command needed).

### Task format in vault

Tasks are stored as:

```markdown
- [ ] #to/do Buy milk
- [ ] #to/follow-up Call dentist
- [ ] #to/do Submit report 📅 2026-03-16
```

## Listing Tasks

```
/task_list           # all open tasks (up to TASK_LIST_LIMIT, default 10)
/task_list --today   # only tasks due today or earlier
/task_list --2026-04-01  # only tasks due by April 1st
```

Tasks are displayed as a numbered list:

```
1. DO: Buy milk
2. FOLLOW-UP: Call dentist
3. DO: Submit report 📅 2026-03-16
```

**Search behavior:**

- Scans the entire vault (all `.md` files)
- Skips hidden directories (`.obsidian/`, `.git/`, etc.)
- Sorted by file modification time (newest files first)
- Tasks without a due date are always included in filtered queries

## Completing Tasks

After running `/task_list`, use `/done N` to complete a task by its number:

```
/done 1    # complete task #1 from last list
/done 3    # complete task #3 from last list
```

**What happens:**

- Task checkbox changes from `[ ]` to `[x]`
- Completion date appended: `✅ 2026-03-16`
- Task list is cleared (run `/task_list` again to see updated state)

**Safety check:** If the task line changed since you listed it (concurrent edit), the bot reports "Task changed or missing. Run /task_list again" without modifying anything.

## Configuration

| Variable            | Default           | Description                        |
| ------------------- | ----------------- | ---------------------------------- |
| `TASK_INBOX_FILE`   | `+/task-inbox.md` | File where new tasks are appended  |
| `TASK_TAG`          | `#to/do`          | Tag for regular tasks              |
| `TASK_TAG_FOLLOWUP` | `#to/follow-up`   | Tag for follow-up tasks            |
| `TASK_LIST_LIMIT`   | `10`              | Max tasks returned by `/task_list` |
