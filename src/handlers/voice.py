"""Voice message handler."""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

from src.services.note_writer import create_note
from src.services.transcription import transcribe_voice

log = structlog.get_logger()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages."""
    message = update.message
    if not message or not message.voice:
        return

    voice = message.voice
    log.info("received_voice", user_id=message.from_user.id, duration=voice.duration)

    # Download voice file
    file = await context.bot.get_file(voice.file_id)
    ogg_data = await file.download_as_bytearray()

    # Transcribe
    await message.reply_text("🎙 Transcribing...")
    try:
        transcription = await transcribe_voice(bytes(ogg_data))
    except Exception as e:
        log.error("transcription_failed", error=str(e))
        await message.reply_text("❌ Transcription failed")
        return

    if not transcription:
        await message.reply_text("❌ No speech detected")
        return

    note_path = create_note(content=transcription, note_type="voice")
    log.info("note_created", path=str(note_path))

    await message.reply_text(f"✓ Captured ({voice.duration}s)")
