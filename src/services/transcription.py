"""Eleven Labs Scribe API integration for voice transcription."""

import tempfile
from pathlib import Path

import httpx
from pydub import AudioSegment

from src.config import settings

SCRIBE_API_URL = "https://api.elevenlabs.io/v1/speech-to-text"


async def transcribe_voice(ogg_data: bytes) -> str:
    """
    Transcribe voice message using Eleven Labs Scribe API.

    Args:
        ogg_data: Raw OGG/Opus audio data from Telegram

    Returns:
        Transcribed text
    """
    # Convert OGG to MP3 (Scribe accepts mp3, wav, etc.)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_file:
        ogg_file.write(ogg_data)
        ogg_path = Path(ogg_file.name)

    mp3_path = ogg_path.with_suffix(".mp3")

    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(mp3_path, format="mp3")

        # Send to Scribe API
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(mp3_path, "rb") as f:
                response = await client.post(
                    SCRIBE_API_URL,
                    headers={"xi-api-key": settings.elevenlabs_api_key},
                    files={"file": ("voice.mp3", f, "audio/mpeg")},
                    data={"model_id": "scribe_v1"},
                )
                response.raise_for_status()
                result = response.json()
                return result.get("text", "")
    finally:
        # Cleanup temp files
        ogg_path.unlink(missing_ok=True)
        if mp3_path.exists():
            mp3_path.unlink(missing_ok=True)
