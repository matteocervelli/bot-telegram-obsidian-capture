"""Video message handlers."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.file_manager import save_attachment
from src.services.note_writer import create_note
from src.services.transcription import transcribe_mp3
from src.services.video_processor import extract_audio_from_video

log = structlog.get_logger()


def _build_video_note_content(caption: str, transcription: str | None) -> str:
    """Combine caption and transcription into note body."""
    if not transcription:
        return caption
    transcription_block = f"**Transcription:**\n{transcription}"
    return f"{caption}\n\n{transcription_block}" if caption else transcription_block


async def _try_transcribe(message, video_data: bytes, log_key: str) -> str | None:
    """Extract audio from video bytes and transcribe. Returns None on failure."""
    try:
        await message.reply_text("Processing video...")
        mp3_data = extract_audio_from_video(video_data, "mp4")
        return await transcribe_mp3(mp3_data)
    except Exception as e:
        log.warning(log_key, error=str(e))
        return None


async def _save_video_capture(
    message,
    context: ContextTypes.DEFAULT_TYPE,
    note_content: str,
    wikilink_path: str,
    file_path,
    duration: int,
) -> None:
    """Write note (daily or regular), record undo state, reply to user."""
    is_daily = context.user_data.get("daily_mode", False)
    section_time = None
    if is_daily:
        from src.services.daily_notes import append_to_daily

        note_path, section_time = append_to_daily(
            content=note_content, attachment_path=wikilink_path
        )
    else:
        note_path = create_note(content=note_content, attachment_path=wikilink_path)
    log.info("note_created", path=str(note_path))

    context.user_data["last_capture"] = {
        "note_path": note_path,
        "attachments": [file_path],
        "is_daily": is_daily,
        "section_time": section_time,
    }
    await message.reply_text(f"✓ Captured ({duration}s)")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming video messages (can have captions)."""
    message = update.message
    if not message or not message.video:
        return

    video = message.video
    caption = message.caption or ""
    log.info("received_video", user_id=message.from_user.id, duration=video.duration)

    file = await context.bot.get_file(video.file_id)
    video_data = bytes(await file.download_as_bytearray())
    file_path, wikilink_path = save_attachment(video_data, "mp4", prefix="vid")

    transcription = await _try_transcribe(message, video_data, "video_transcription_failed")
    note_content = _build_video_note_content(caption, transcription)
    await _save_video_capture(
        message, context, note_content, wikilink_path, file_path, video.duration
    )


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming video notes (video circles, no captions)."""
    message = update.message
    if not message or not message.video_note:
        return

    video_note = message.video_note
    log.info("received_video_note", user_id=message.from_user.id, duration=video_note.duration)

    file = await context.bot.get_file(video_note.file_id)
    video_data = bytes(await file.download_as_bytearray())
    file_path, wikilink_path = save_attachment(video_data, "mp4", prefix="vnote")

    transcription = await _try_transcribe(message, video_data, "video_note_transcription_failed")
    note_content = _build_video_note_content("", transcription)
    await _save_video_capture(
        message, context, note_content, wikilink_path, file_path, video_note.duration
    )
