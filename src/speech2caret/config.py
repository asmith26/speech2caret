import configparser
from pathlib import Path

APP_NAME = "speech2caret"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.ini"


def get_config() -> configparser.ConfigParser:
    """
    Get the application configuration.

    If the config file doesn't exist, it will be created.

    Returns
    -------
        The application configuration.
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.is_file():
        # Create a default config file
        config = configparser.ConfigParser()
        config["speech2caret"] = {
            "# Example: keyboard_device_path": "/dev/input/by-path/pci-0000:00:1.0-usb-0:1:1.0-event-kbd",
            "keyboard_device_path": "",
            "# Example: start_stop_key": "KEY_F11",
            "start_stop_key": "",
            "# Example: resume_pause_key": "KEY_F12",
            "resume_pause_key": "",
            "# Example: audio_fp": "/tmp/tmp_audio.wav",  # nosec
            "audio_fp": "/tmp/tmp_audio.wav",  # nosec
        }
        with open(CONFIG_FILE, "w") as f:
            f.write(
                "# This is the configuration file for speech2caret.\n"
                "# You can find an explanation of the options in the config.ini.example file in the project repository.\n"
            )
            config.write(f)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config
