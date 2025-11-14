import configparser
from pathlib import Path
from unittest import mock

import pytest

from speech2caret.config import Config, get_config


@pytest.fixture
def mock_config_dir(tmp_path):
    with (
        mock.patch("speech2caret.config.CONFIG_DIR", tmp_path),
        mock.patch("speech2caret.config.CONFIG_FILE", tmp_path / "config.ini"),
    ):
        yield tmp_path


@pytest.fixture
def mock_valid_config_parser():
    parser = configparser.ConfigParser()
    parser["main"] = {
        "keyboard_device_path": "/dev/null",
        "start_stop_key": "KEY_A",
        "resume_pause_key": "KEY_B",
    }
    parser["audio"] = {
        "start_recording_audio_path": "",
        "stop_recording_audio_path": "",
        "resume_recording_audio_path": "",
        "pause_recording_audio_path": "",
    }
    parser["word_replacements"] = {}
    return parser


class TestGetConfig:
    def test_creates_file_and_exits_when_invalid(self, mock_config_dir):
        """
        Test that get_config creates a config file if one doesn't exist,
        and then exits because the default config is invalid.
        """
        config_file = mock_config_dir / "config.ini"
        assert not config_file.exists()

        with pytest.raises(SystemExit) as e:
            get_config()

        assert e.value.code == 1
        assert config_file.exists()

    def test_reads_existing_valid_file(self, mock_config_dir):
        """Test that get_config reads an existing and valid config file."""
        config_file = mock_config_dir / "config.ini"
        config = configparser.ConfigParser()
        config["main"] = {
            "keyboard_device_path": "/dev/null",  # /dev/null should exist
            "start_stop_key": "KEY_F1",
            "resume_pause_key": "KEY_F2",
        }
        config["audio"] = {
            "start_recording_audio_path": "",
            "stop_recording_audio_path": "",
            "resume_recording_audio_path": "",
            "pause_recording_audio_path": "",
        }
        config["word_replacements"] = {}
        with open(config_file, "w") as f:
            config.write(f)

        loaded_config = get_config()
        assert loaded_config.keyboard_device_path == Path("/dev/null")
        assert loaded_config.start_recording_audio_path == Path("")
        assert loaded_config.word_replacements == {}


class TestConfigInit:
    def test_valid_config(self, mock_valid_config_parser):
        """Test that a valid config is parsed correctly."""
        config = Config(mock_valid_config_parser)
        assert config.keyboard_device_path == Path("/dev/null")
        assert config.start_stop_key == "KEY_A"
        assert config.resume_pause_key == "KEY_B"
        assert config.start_recording_audio_path == Path(".")
        assert config.stop_recording_audio_path == Path(".")
        assert config.resume_recording_audio_path == Path(".")
        assert config.pause_recording_audio_path == Path(".")
        assert config.word_replacements == {}


    def test_with_audio_paths(self, mock_valid_config_parser):
        """Test that audio paths are parsed correctly."""
        mock_valid_config_parser["audio"]["start_recording_audio_path"] = "/path/to/start.wav"
        mock_valid_config_parser["audio"]["stop_recording_audio_path"] = "/path/to/stop.wav"
        mock_valid_config_parser["audio"]["resume_recording_audio_path"] = "/path/to/resume.wav"
        mock_valid_config_parser["audio"]["pause_recording_audio_path"] = "/path/to/pause.wav"

        config = Config(mock_valid_config_parser)

        assert config.start_recording_audio_path == Path("/path/to/start.wav")
        assert config.stop_recording_audio_path == Path("/path/to/stop.wav")
        assert config.resume_recording_audio_path == Path("/path/to/resume.wav")
        assert config.pause_recording_audio_path == Path("/path/to/pause.wav")

    def test_no_keyboard_device_path(self, mock_valid_config_parser):
        """Test that SystemExit is raised when keyboard_device_path is missing."""
        mock_valid_config_parser["main"]["keyboard_device_path"] = ""
        with pytest.raises(SystemExit) as e:
            Config(mock_valid_config_parser)
        assert e.value.code == 1

    def test_nonexistent_keyboard_device_path(self, mock_valid_config_parser):
        """Test that SystemExit is raised when keyboard_device_path does not exist."""
        mock_valid_config_parser["main"]["keyboard_device_path"] = "/dev/nonexistent"
        with pytest.raises(SystemExit) as e:
            Config(mock_valid_config_parser)
        assert e.value.code == 1

    def test_no_start_stop_key(self, mock_valid_config_parser):
        """Test that SystemExit is raised when start_stop_key is missing."""
        mock_valid_config_parser["main"]["start_stop_key"] = ""
        with pytest.raises(SystemExit) as e:
            Config(mock_valid_config_parser)
        assert e.value.code == 1

    def test_no_resume_pause_key(self, mock_valid_config_parser):
        """Test that SystemExit is raised when resume_pause_key is missing."""
        mock_valid_config_parser["main"]["resume_pause_key"] = ""
        with pytest.raises(SystemExit) as e:
            Config(mock_valid_config_parser)
        assert e.value.code == 1
