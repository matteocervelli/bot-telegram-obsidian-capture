"""Tests for message handlers (text, voice, photo, document, video)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ─── helpers ────────────────────────────────────────────────────────────────


def _make_update(text=None, voice=None, photo=None, document=None, video=None, video_note=None):
    """Build a minimal fake Telegram Update."""
    update = MagicMock()
    msg = MagicMock()
    msg.reply_text = AsyncMock()
    msg.from_user.id = 123456789
    msg.text = text
    msg.voice = voice
    msg.photo = photo
    msg.document = document
    msg.video = video
    msg.video_note = video_note
    msg.caption = None
    update.message = msg
    return update


def _make_context(daily_mode=False):
    """Build a minimal fake CallbackContext."""
    ctx = MagicMock()
    ctx.user_data = {"daily_mode": daily_mode} if daily_mode else {}
    file_mock = MagicMock()
    file_mock.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-data"))
    ctx.bot.get_file = AsyncMock(return_value=file_mock)
    return ctx


FAKE_NOTE = Path("/tmp/test-vault/+/2026-01-01 1200.md")
FAKE_ATTACH = Path("/tmp/test-vault/+/attachments/tg-abc.jpg")
FAKE_WIKILINK = "+/attachments/tg-abc.jpg"


# ─── text handler ───────────────────────────────────────────────────────────


@patch("src.handlers.text.create_note", return_value=FAKE_NOTE)
async def test_handle_text_basic(mock_create):
    """Plain text → creates note, replies ✓ Captured."""
    from src.handlers.text import handle_text

    update = _make_update(text="Hello world")
    ctx = _make_context()

    await handle_text(update, ctx)

    mock_create.assert_called_once_with(content="Hello world")
    update.message.reply_text.assert_called_once_with("✓ Captured")
    assert ctx.user_data["last_capture"]["note_path"] == FAKE_NOTE
    assert ctx.user_data["last_capture"]["attachments"] == []


@patch("src.services.task_manager.add_task", return_value=FAKE_NOTE)
async def test_handle_text_task_prefix(mock_add_task):
    """'task: ...' text → routes to task manager."""
    from src.handlers.text import handle_text

    update = _make_update(text="task: Buy milk")
    ctx = _make_context()

    await handle_text(update, ctx)

    mock_add_task.assert_called_once_with("task: Buy milk")
    update.message.reply_text.assert_called_once_with("✓ Task added")


@patch("src.services.daily_notes.append_to_daily", return_value=(FAKE_NOTE, "12:00"))
async def test_handle_text_daily_mode(mock_append):
    """daily_mode=True → appends to daily note."""
    from src.handlers.text import handle_text

    update = _make_update(text="Daily capture")
    ctx = _make_context(daily_mode=True)

    await handle_text(update, ctx)

    mock_append.assert_called_once_with(content="Daily capture")
    assert ctx.user_data["last_capture"]["is_daily"] is True
    assert ctx.user_data["last_capture"]["section_time"] == "12:00"


async def test_handle_text_no_message():
    """Missing message → returns early, no error."""
    from src.handlers.text import handle_text

    update = MagicMock()
    update.message = None
    ctx = _make_context()

    await handle_text(update, ctx)  # should not raise


# ─── voice handler ──────────────────────────────────────────────────────────


@patch("src.handlers.voice.create_note", return_value=FAKE_NOTE)
@patch(
    "src.handlers.voice.transcribe_voice", new_callable=AsyncMock, return_value="Hello from voice"
)
async def test_handle_voice_basic(mock_transcribe, mock_create):
    """Voice → transcribes, creates note, replies ✓ Captured."""
    from src.handlers.voice import handle_voice

    voice = MagicMock()
    voice.file_id = "voice-file-123"
    voice.duration = 5
    update = _make_update(voice=voice)
    ctx = _make_context()

    await handle_voice(update, ctx)

    mock_transcribe.assert_called_once()
    mock_create.assert_called_once_with(content="Hello from voice")
    update.message.reply_text.assert_called_with("✓ Captured (5s)")


@patch(
    "src.handlers.voice.transcribe_voice", new_callable=AsyncMock, side_effect=Exception("API down")
)
async def test_handle_voice_transcription_error(mock_transcribe):
    """Transcription exception → replies ❌ Transcription failed."""
    from src.handlers.voice import handle_voice

    voice = MagicMock()
    voice.file_id = "voice-file-123"
    voice.duration = 3
    update = _make_update(voice=voice)
    ctx = _make_context()

    await handle_voice(update, ctx)

    update.message.reply_text.assert_called_with("❌ Transcription failed")


@patch("src.handlers.voice.transcribe_voice", new_callable=AsyncMock, return_value="")
async def test_handle_voice_no_speech(mock_transcribe):
    """Empty transcription → replies ❌ No speech detected."""
    from src.handlers.voice import handle_voice

    voice = MagicMock()
    voice.file_id = "voice-file-123"
    voice.duration = 1
    update = _make_update(voice=voice)
    ctx = _make_context()

    await handle_voice(update, ctx)

    update.message.reply_text.assert_called_with("❌ No speech detected")


# ─── photo handler ──────────────────────────────────────────────────────────


@patch("src.handlers.photo.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.photo.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
async def test_handle_photo_basic(mock_save, mock_create):
    """Photo → saves attachment, creates note, replies ✓ Captured."""
    from src.handlers.photo import handle_photo

    photo_size = MagicMock()
    photo_size.file_id = "photo-file-123"
    update = _make_update(photo=[photo_size])
    ctx = _make_context()

    await handle_photo(update, ctx)

    mock_save.assert_called_once_with(b"fake-data", "jpg")
    mock_create.assert_called_once_with(content="", attachment_path=FAKE_WIKILINK)
    update.message.reply_text.assert_called_once_with("✓ Captured")
    assert ctx.user_data["last_capture"]["attachments"] == [FAKE_ATTACH]


@patch("src.handlers.photo.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.photo.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
async def test_handle_photo_with_caption(mock_save, mock_create):
    """Photo with caption → caption included in note."""
    from src.handlers.photo import handle_photo

    photo_size = MagicMock()
    photo_size.file_id = "photo-file-456"
    update = _make_update(photo=[photo_size])
    update.message.caption = "My photo caption"
    ctx = _make_context()

    await handle_photo(update, ctx)

    mock_create.assert_called_once_with(content="My photo caption", attachment_path=FAKE_WIKILINK)


# ─── document handler ───────────────────────────────────────────────────────


@patch("src.handlers.document.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.document.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
async def test_handle_document_basic(mock_save, mock_create):
    """Document → saves attachment, creates note with filename."""
    from src.handlers.document import handle_document

    doc = MagicMock()
    doc.file_id = "doc-file-123"
    doc.file_name = "report.pdf"
    update = _make_update(document=doc)
    ctx = _make_context()

    await handle_document(update, ctx)

    mock_save.assert_called_once_with(b"fake-data", "pdf", prefix="doc")
    call_content = mock_create.call_args[1]["content"]
    assert "report.pdf" in call_content
    update.message.reply_text.assert_called_once_with("✓ Captured")


@patch("src.handlers.document.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.document.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
async def test_handle_document_no_extension(mock_save, mock_create):
    """File without extension → uses 'bin' as extension."""
    from src.handlers.document import handle_document

    doc = MagicMock()
    doc.file_id = "doc-file-456"
    doc.file_name = "noextension"
    update = _make_update(document=doc)
    ctx = _make_context()

    await handle_document(update, ctx)

    mock_save.assert_called_once_with(b"fake-data", "bin", prefix="doc")


@patch("src.handlers.document.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.document.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
async def test_handle_document_with_caption(mock_save, mock_create):
    """Document with caption → caption prepended to note content."""
    from src.handlers.document import handle_document

    doc = MagicMock()
    doc.file_id = "doc-file-789"
    doc.file_name = "notes.txt"
    update = _make_update(document=doc)
    update.message.caption = "My notes file"
    ctx = _make_context()

    await handle_document(update, ctx)

    call_content = mock_create.call_args[1]["content"]
    assert "My notes file" in call_content
    assert "notes.txt" in call_content


# ─── video handler ──────────────────────────────────────────────────────────


@patch("src.handlers.video.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.video.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch("src.handlers.video.extract_audio_from_video", return_value=b"mp3-data")
@patch("src.handlers.video.transcribe_mp3", new_callable=AsyncMock, return_value="Video transcript")
async def test_handle_video_with_transcription(
    mock_transcribe, mock_extract, mock_save, mock_create
):
    """Video → transcribes audio, includes transcript in note."""
    from src.handlers.video import handle_video

    video = MagicMock()
    video.file_id = "vid-file-123"
    video.duration = 10
    update = _make_update(video=video)
    ctx = _make_context()

    await handle_video(update, ctx)

    mock_transcribe.assert_called_once_with(b"mp3-data")
    call_content = mock_create.call_args[1]["content"]
    assert "Video transcript" in call_content
    update.message.reply_text.assert_called_with("✓ Captured (10s)")


@patch("src.handlers.video.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.video.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch("src.handlers.video.extract_audio_from_video", side_effect=Exception("ffmpeg missing"))
async def test_handle_video_transcription_fails_gracefully(mock_extract, mock_save, mock_create):
    """Video transcription failure → still creates note (non-fatal)."""
    from src.handlers.video import handle_video

    video = MagicMock()
    video.file_id = "vid-file-456"
    video.duration = 8
    update = _make_update(video=video)
    ctx = _make_context()

    await handle_video(update, ctx)

    # Note still created despite transcription error
    mock_create.assert_called_once()
    update.message.reply_text.assert_called_with("✓ Captured (8s)")


@patch("src.handlers.video.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.video.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch("src.handlers.video.extract_audio_from_video", return_value=b"mp3-data")
@patch(
    "src.handlers.video.transcribe_mp3", new_callable=AsyncMock, return_value="Circle transcript"
)
async def test_handle_video_note(mock_transcribe, mock_extract, mock_save, mock_create):
    """Video note (circle) → transcribes, creates note."""
    from src.handlers.video import handle_video_note

    video_note = MagicMock()
    video_note.file_id = "vnote-file-123"
    video_note.duration = 15
    update = _make_update(video_note=video_note)
    ctx = _make_context()

    await handle_video_note(update, ctx)

    mock_transcribe.assert_called_once_with(b"mp3-data")
    call_content = mock_create.call_args[1]["content"]
    assert "Circle transcript" in call_content
    update.message.reply_text.assert_called_with("✓ Captured (15s)")


# ─── early returns (message=None) ────────────────────────────────────────────


async def test_handle_voice_no_message():
    from src.handlers.voice import handle_voice

    update = MagicMock()
    update.message = None
    await handle_voice(update, MagicMock())


async def test_handle_photo_no_message():
    from src.handlers.photo import handle_photo

    update = MagicMock()
    update.message = None
    await handle_photo(update, MagicMock())


async def test_handle_document_no_message():
    from src.handlers.document import handle_document

    update = MagicMock()
    update.message = None
    await handle_document(update, MagicMock())


async def test_handle_video_no_message():
    from src.handlers.video import handle_video

    update = MagicMock()
    update.message = None
    await handle_video(update, MagicMock())


async def test_handle_video_note_no_message():
    from src.handlers.video import handle_video_note

    update = MagicMock()
    update.message = None
    await handle_video_note(update, MagicMock())


# ─── daily mode branches ──────────────────────────────────────────────────────


@patch("src.handlers.photo.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch(
    "src.services.daily_notes.append_to_daily",
    return_value=(FAKE_NOTE, "14:30"),
)
async def test_handle_photo_daily_mode(mock_append, mock_save):
    """Photo in daily mode → appends to daily note."""
    from src.handlers.photo import handle_photo

    photo_size = MagicMock()
    photo_size.file_id = "photo-daily"
    update = _make_update(photo=[photo_size])
    ctx = _make_context(daily_mode=True)

    await handle_photo(update, ctx)

    mock_append.assert_called_once()
    assert ctx.user_data["last_capture"]["is_daily"] is True


@patch("src.handlers.document.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch(
    "src.services.daily_notes.append_to_daily",
    return_value=(FAKE_NOTE, "14:30"),
)
async def test_handle_document_daily_mode(mock_append, mock_save):
    """Document in daily mode → appends to daily note."""
    from src.handlers.document import handle_document

    doc = MagicMock()
    doc.file_id = "doc-daily"
    doc.file_name = "file.pdf"
    update = _make_update(document=doc)
    ctx = _make_context(daily_mode=True)

    await handle_document(update, ctx)

    mock_append.assert_called_once()
    assert ctx.user_data["last_capture"]["is_daily"] is True


@patch("src.handlers.voice.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.voice.transcribe_voice", new_callable=AsyncMock, return_value="Speech")
@patch(
    "src.services.daily_notes.append_to_daily",
    return_value=(FAKE_NOTE, "14:30"),
)
async def test_handle_voice_daily_mode(mock_append, mock_transcribe, mock_create):
    """Voice in daily mode → appends transcription to daily note."""
    from src.handlers.voice import handle_voice

    voice = MagicMock()
    voice.file_id = "voice-daily"
    voice.duration = 4
    update = _make_update(voice=voice)
    ctx = _make_context(daily_mode=True)

    await handle_voice(update, ctx)

    mock_append.assert_called_once_with(content="Speech")
    assert ctx.user_data["last_capture"]["is_daily"] is True


@patch("src.handlers.video.create_note", return_value=FAKE_NOTE)
@patch("src.handlers.video.save_attachment", return_value=(FAKE_ATTACH, FAKE_WIKILINK))
@patch("src.handlers.video.extract_audio_from_video", return_value=b"mp3")
@patch("src.handlers.video.transcribe_mp3", new_callable=AsyncMock, return_value="Vid speech")
@patch(
    "src.services.daily_notes.append_to_daily",
    return_value=(FAKE_NOTE, "14:30"),
)
async def test_handle_video_daily_mode(
    mock_append, mock_transcribe, mock_extract, mock_save, mock_create
):
    """Video in daily mode → appends to daily note."""
    from src.handlers.video import handle_video

    video = MagicMock()
    video.file_id = "vid-daily"
    video.duration = 6
    update = _make_update(video=video)
    ctx = _make_context(daily_mode=True)

    await handle_video(update, ctx)

    mock_append.assert_called_once()
    assert ctx.user_data["last_capture"]["is_daily"] is True


# ─── note_writer same-minute collision ───────────────────────────────────────


def test_create_note_same_minute_collision(temp_vault):
    """When expected filename exists, falls back to seconds-precision name."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from src.services.note_writer import create_note

    with patch("src.services.note_writer.settings") as m:
        m.timezone = "UTC"
        m.note_filename_format = "%Y-%m-%d %H%M"
        m.inbox_path = temp_vault / "+"

        tz = ZoneInfo("UTC")
        now = datetime.now(tz)
        collision_name = now.strftime("%Y-%m-%d %H%M") + ".md"
        (temp_vault / "+" / collision_name).write_text("existing")

        result = create_note("New note")

    assert result.name != collision_name
    assert result.exists()
