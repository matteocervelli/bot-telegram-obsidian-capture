"""Tests for video_processor service."""

from unittest.mock import MagicMock, patch


def test_extract_audio_from_video_calls_pydub():
    """Test that audio extraction uses pydub correctly."""
    from src.services.video_processor import extract_audio_from_video

    fake_video_data = b"fake video data"
    fake_mp3_data = b"fake mp3 data"

    with (
        patch("src.services.video_processor.tempfile") as mock_tempfile,
        patch("src.services.video_processor.AudioSegment") as mock_audio_segment,
        patch("src.services.video_processor.Path") as mock_path_class,
    ):
        # Setup temp file mock
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__ = MagicMock(return_value=mock_temp_file)
        mock_temp_file.__exit__ = MagicMock(return_value=False)
        mock_temp_file.name = "/tmp/test.mp4"
        mock_tempfile.NamedTemporaryFile.return_value = mock_temp_file

        # Setup path mock
        mock_video_path = MagicMock()
        mock_mp3_path = MagicMock()
        mock_mp3_path.read_bytes.return_value = fake_mp3_data
        mock_video_path.with_suffix.return_value = mock_mp3_path
        mock_path_class.return_value = mock_video_path

        # Setup audio segment mock
        mock_audio = MagicMock()
        mock_audio_segment.from_file.return_value = mock_audio

        result = extract_audio_from_video(fake_video_data, "mp4")

        # Verify pydub was called
        mock_audio_segment.from_file.assert_called_once_with(mock_video_path, format="mp4")
        mock_audio.export.assert_called_once_with(mock_mp3_path, format="mp3")

        # Verify cleanup was called
        mock_video_path.unlink.assert_called_once()
        mock_mp3_path.unlink.assert_called_once()

        assert result == fake_mp3_data


def test_extract_audio_cleanup_on_error():
    """Test that temp files are cleaned up even on error."""
    from src.services.video_processor import extract_audio_from_video

    fake_video_data = b"fake video data"

    with (
        patch("src.services.video_processor.tempfile") as mock_tempfile,
        patch("src.services.video_processor.AudioSegment") as mock_audio_segment,
        patch("src.services.video_processor.Path") as mock_path_class,
    ):
        # Setup temp file mock
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__ = MagicMock(return_value=mock_temp_file)
        mock_temp_file.__exit__ = MagicMock(return_value=False)
        mock_temp_file.name = "/tmp/test.mp4"
        mock_tempfile.NamedTemporaryFile.return_value = mock_temp_file

        # Setup path mock
        mock_video_path = MagicMock()
        mock_mp3_path = MagicMock()
        mock_video_path.with_suffix.return_value = mock_mp3_path
        mock_path_class.return_value = mock_video_path

        # Make pydub raise an error
        mock_audio_segment.from_file.side_effect = Exception("Codec error")

        try:
            extract_audio_from_video(fake_video_data, "mp4")
        except Exception:
            pass

        # Verify cleanup was still called
        mock_video_path.unlink.assert_called_once()
        mock_mp3_path.unlink.assert_called_once()
