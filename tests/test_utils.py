from pathlib import Path
from unittest import mock

import pytest

from speech2caret.utils import play_audio, transcribe_and_type


class TestPlayAudio:
    @mock.patch("subprocess.run")
    def test_calls_paplay(self, mock_subprocess_run, tmp_path):
        """Test that play_audio calls paplay with the correct file path."""
        audio_file = tmp_path / "test.wav"
        audio_file.touch()

        play_audio(audio_file)

        mock_subprocess_run.assert_called_once_with(["paplay", audio_file])

    @mock.patch("subprocess.run")
    def test_file_does_not_exist(self, mock_subprocess_run):
        """Test that play_audio does not call paplay if the file does not exist."""
        audio_fp = Path("/path/to/nonexistent/file.wav")
        play_audio(audio_fp)
        mock_subprocess_run.assert_not_called()

    @mock.patch("subprocess.run")
    def test_is_directory(self, mock_subprocess_run, tmp_path):
        """Test that play_audio does not call paplay if the path is a directory."""
        play_audio(tmp_path)
        mock_subprocess_run.assert_not_called()


@pytest.mark.asyncio
class TestTranscribeAndType:
    async def test_happy_path(self):
        """Test the normal execution of transcribe_and_type."""
        mock_recorder = mock.Mock()
        mock_recorder.audio_fp = "/path/to/audio.wav"
        mock_recorder.delete_audio_file = mock.Mock()

        mock_stt = mock.Mock()
        mock_stt.transcribe.return_value = "hello world"

        mock_vkeyboard = mock.Mock()
        mock_vkeyboard.type_text = mock.Mock()

        await transcribe_and_type(mock_recorder, mock_stt, mock_vkeyboard)

        mock_stt.transcribe.assert_called_once_with("/path/to/audio.wav")
        mock_vkeyboard.type_text.assert_called_once_with("hello world")
        mock_recorder.delete_audio_file.assert_called_once()

    async def test_transcription_fails(self):
        """Test that delete_audio_file is called even if transcription fails."""
        mock_recorder = mock.Mock()
        mock_recorder.audio_fp = "/path/to/audio.wav"
        mock_recorder.delete_audio_file = mock.Mock()

        mock_stt = mock.Mock()
        mock_stt.transcribe.side_effect = Exception("Transcription failed")

        mock_vkeyboard = mock.Mock()
        mock_vkeyboard.type_text = mock.Mock()

        with pytest.raises(Exception, match="Transcription failed"):
            await transcribe_and_type(mock_recorder, mock_stt, mock_vkeyboard)

        mock_vkeyboard.type_text.assert_not_called()
        mock_recorder.delete_audio_file.assert_called_once()

    async def test_typing_fails(self):
        """Test that delete_audio_file is called even if typing fails."""
        mock_recorder = mock.Mock()
        mock_recorder.audio_fp = "/path/to/audio.wav"
        mock_recorder.delete_audio_file = mock.Mock()

        mock_stt = mock.Mock()
        mock_stt.transcribe.return_value = "hello world"

        mock_vkeyboard = mock.Mock()
        mock_vkeyboard.type_text.side_effect = Exception("Typing failed")

        with pytest.raises(Exception, match="Typing failed"):
            await transcribe_and_type(mock_recorder, mock_stt, mock_vkeyboard)

        mock_stt.transcribe.assert_called_once_with("/path/to/audio.wav")
        mock_recorder.delete_audio_file.assert_called_once()
