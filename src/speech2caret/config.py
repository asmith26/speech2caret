import configparser
import sys
from pathlib import Path

from loguru import logger

CONFIG_DIR = Path.home() / ".config/speech2caret"
CONFIG_FILE = CONFIG_DIR / "config.ini"


class Config:
    def __init__(self, config_parser: configparser.ConfigParser):
        self.keyboard_device_path: Path = Path(config_parser["speech2caret"]["keyboard_device_path"])
        self.start_stop_key: str = config_parser["speech2caret"]["start_stop_key"]
        self.resume_pause_key: str = config_parser["speech2caret"]["resume_pause_key"]
        self.start_recording_audio_path: Path = Path(config_parser["speech2caret"]["start_recording_audio_path"])
        self.stop_recording_audio_path: Path = Path(config_parser["speech2caret"]["stop_recording_audio_path"])
        self.resume_recording_audio_path: Path = Path(config_parser["speech2caret"]["resume_recording_audio_path"])
        self.pause_recording_audio_path: Path = Path(config_parser["speech2caret"]["pause_recording_audio_path"])

        config_help_message = (
            "Edit the config file (see https://github.com/asmith26/speech2caret/tree/main#configuration)"
        )

        if self.keyboard_device_path == Path("."):
            logger.error(f"Keyboard device not set. {config_help_message}.")
            sys.exit(1)
        if not self.keyboard_device_path.exists():
            logger.error(f"Keyboard device does not exist: {self.keyboard_device_path}")
            sys.exit(1)
        if not self.start_stop_key:
            logger.error(f"start_stop_key not set. {config_help_message}.")
            sys.exit(1)
        if not self.resume_pause_key:
            logger.error(f"resume_pause_key not set. {config_help_message}.")
            sys.exit(1)


def get_config() -> Config:
    """Get user configuration.

    If the config file doesn't exist, it will be created.
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    config_parser = configparser.ConfigParser()

    # Create a default config file
    if not CONFIG_FILE.is_file():
        config_parser["speech2caret"] = {
            "# example:\n# keyboard_device_path": "/dev/input/by-path/pci-0000:00:1.0-usb-0:1:1.0-event-kbd",
            "# start_stop_key": "KEY_F11",
            "# resume_pause_key": "KEY_F12",
            "# start_recording_audio_path (optional)": "/path/to/sound.mp3",
            "# stop_recording_audio_path (optional)": "/path/to/another_sound.mp3",
            "# resume_recording_audio_path (optional)": "/path/to/another_sound.mp3",
            "# pause_recording_audio_path (optional)": "/path/to/another_sound.mp3",
            "keyboard_device_path": "",
            "start_stop_key": "",
            "resume_pause_key": "",
            "start_recording_audio_path": "",
            "stop_recording_audio_path": "",
            "resume_recording_audio_path": "",
            "pause_recording_audio_path": "",
        }
        with open(CONFIG_FILE, "w") as f:
            f.write(
                "# This is the configuration file for speech2caret.\n"
                "# You can find an explanation of the options in the GitHub README.md: https://github.com/asmith26/speech2caret\n\n"
            )
            config_parser.write(f)

    config_parser.read(CONFIG_FILE)

    # Convert to Config object
    config = Config(config_parser)
    return config
