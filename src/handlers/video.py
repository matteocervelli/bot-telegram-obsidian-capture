"""Video message handlers."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.file_manager import save_attachment
from src.services.note_writer import create_note
from src.services.transcription import transcribe_mp3
from src.services.video_processor import extract_audio_from_video

log = structlog.get_logger()


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming video messages (can have captions)."""
    message = update.message
    if not message or not message.video:
        return

    video = message.video
    caption = message.caption or ""

    log.info("received_video", user_id=message.from_user.id, duration=video.duration)

    # Download video
    file = await context.bot.get_file(video.file_id)
    video_data = await file.download_as_bytearray()

    # Save video attachment
    file_path, wikilink_path = save_attachment(bytes(video_data), "mp4", prefix="vid")

    # Try to extract audio and transcribe (non-fatal on failure)
    transcription = None
    try:
        await message.reply_text("Processing video...")
        mp3_data = extract_audio_from_video(bytes(video_data), "mp4")
        transcription = await transcribe_mp3(mp3_data)
    except Exception as e:
        log.warning("video_transcription_failed", error=str(e))

    # Build note content
    note_content = caption
    if transcription:
        if note_content:
            note_content = f"{note_content}\n\n**Transcription:**\n{transcription}"
        else:
            note_content = f"**Transcription:**\n{transcription}"

    # Check for daily mode
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

    # Track for undo
    context.user_data["last_capture"] = {
        "note_path": note_path,
        "attachments": [file_path],
        "is_daily": is_daily,
        "section_time": section_time,
    }

    await message.reply_text(f"✓ Captured ({video.duration}s)")


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming video notes (video circles, no captions)."""
    message = update.message
    if not message or not message.video_note:
        return

    video_note = message.video_note

    log.info("received_video_note", user_id=message.from_user.id, duration=video_note.duration)

    # Download video note
    file = await context.bot.get_file(video_note.file_id)
    video_data = await file.download_as_bytearray()

    # Save video attachment
    file_path, wikilink_path = save_attachment(bytes(video_data), "mp4", prefix="vnote")

    # Try to extract audio and transcribe (non-fatal on failure)
    transcription = None
    try:
        await message.reply_text("Processing video...")
        mp3_data = extract_audio_from_video(bytes(video_data), "mp4")
        transcription = await transcribe_mp3(mp3_data)
    except Exception as e:
        log.warning("video_note_transcription_failed", error=str(e))

    # Build note content
    note_content = ""
    if transcription:
        note_content = f"**Transcription:**\n{transcription}"

    # Check for daily mode
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

    # Track for undo
    context.user_data["last_capture"] = {
        "note_path": note_path,
        "attachments": [file_path],
        "is_daily": is_daily,
        "section_time": section_time,
    }

    await message.reply_text(f"✓ Captured ({video_note.duration}s)")
