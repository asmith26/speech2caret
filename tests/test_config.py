import pytest
import configparser
from unittest import mock
from speech2caret.config import get_config, CONFIG_FILE

@pytest.fixture
def mock_config_dir(tmp_path):
    with mock.patch("speech2caret.config.CONFIG_DIR", tmp_path), mock.patch("speech2caret.config.CONFIG_FILE", tmp_path / "config.ini"):
        yield tmp_path

def test_get_config_creates_file(mock_config_dir):
    config_file = CONFIG_FILE
    assert not config_file.exists()

    config = get_config()

    assert config_file.exists()
    assert isinstance(config, configparser.ConfigParser)
    assert "speech2caret" in config
    assert config["speech2caret"].get("keyboard_device_path") == ""
    assert config["speech2caret"].get("start_stop_key") == ""
    assert config["speech2caret"].get("resume_pause_key") == ""
    assert config["speech2caret"].get("audio_fp") == "/tmp/tmp_audio.wav"

def test_get_config_reads_existing_file(mock_config_dir):
    # Pre-create config file with known values
    config = configparser.ConfigParser()
    config["speech2caret"] = {
        "keyboard_device_path": "/dev/test",
        "start_stop_key": "KEY_F1",
        "resume_pause_key": "KEY_F2",
        "audio_fp": "/tmp/test.wav",
    }
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

    loaded_config = get_config()
    assert loaded_config["speech2caret"].get("keyboard_device_path") == "/dev/test"
    assert loaded_config["speech2caret"].get("start_stop_key") == "KEY_F1"
    assert loaded_config["speech2caret"].get("resume_pause_key") == "KEY_F2"
    assert loaded_config["speech2caret"].get("audio_fp") == "/tmp/test.wav"
