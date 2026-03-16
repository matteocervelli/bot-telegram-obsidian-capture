"""Tests for transcription service (mocked httpx + pydub)."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


async def test_transcribe_mp3_returns_text():
    """transcribe_mp3 posts to ElevenLabs and returns text field."""
    from src.services.transcription import transcribe_mp3

    mock_response = MagicMock()
    mock_response.json.return_value = {"text": "Hello world"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("src.services.transcription.httpx.AsyncClient", return_value=mock_client):
        result = await transcribe_mp3(b"fake-mp3-data")

    assert result == "Hello world"
    mock_client.post.assert_called_once()


async def test_transcribe_mp3_empty_response():
    """transcribe_mp3 returns empty string when text field is missing."""
    from src.services.transcription import transcribe_mp3

    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("src.services.transcription.httpx.AsyncClient", return_value=mock_client):
        result = await transcribe_mp3(b"fake-mp3-data")

    assert result == ""


async def test_transcribe_voice_returns_text():
    """transcribe_voice converts OGG→MP3, posts to ElevenLabs, cleans up."""
    from src.services.transcription import transcribe_voice

    mock_audio = MagicMock()

    def fake_export(path, format=None):
        Path(path).write_bytes(b"fake-mp3")  # create the file so cleanup branch runs

    mock_audio.export.side_effect = fake_export

    mock_response = MagicMock()
    mock_response.json.return_value = {"text": "Voice text here"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("src.services.transcription.AudioSegment.from_ogg", return_value=mock_audio):
        with patch("src.services.transcription.httpx.AsyncClient", return_value=mock_client):
            result = await transcribe_voice(b"fake-ogg-data")

    assert result == "Voice text here"
    mock_audio.export.assert_called_once()
