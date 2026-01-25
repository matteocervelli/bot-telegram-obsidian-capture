"""Video processing service for audio extraction."""

import tempfile
from pathlib import Path

from pydub import AudioSegment


def extract_audio_from_video(video_data: bytes, extension: str = "mp4") -> bytes:
    """
    Extract audio track from video and convert to MP3.

    Args:
        video_data: Raw video file bytes
        extension: Video file extension (mp4, mov, etc.)

    Returns:
        MP3 audio bytes
    """
    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as video_file:
        video_file.write(video_data)
        video_path = Path(video_file.name)

    mp3_path = video_path.with_suffix(".mp3")

    try:
        # pydub uses ffmpeg under the hood to handle video files
        audio = AudioSegment.from_file(video_path, format=extension)
        audio.export(mp3_path, format="mp3")

        return mp3_path.read_bytes()
    finally:
        # Cleanup temp files
        video_path.unlink(missing_ok=True)
        mp3_path.unlink(missing_ok=True)
