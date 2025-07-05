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
            "# example:\n# keyboard_device_path": "/dev/input/by-path/pci-0000:00:1.0-usb-0:1:1.0-event-kbd",
            "# start_stop_key": "KEY_F11",
            "# resume_pause_key": "KEY_F12",
            "# audio_fp": "/tmp/tmp_audio.wav\n",  # nosec
            "keyboard_device_path": "",
            "start_stop_key": "",
            "resume_pause_key": "",
            "audio_fp": "/tmp/tmp_audio.wav",  # nosec
        }
        with open(CONFIG_FILE, "w") as f:
            f.write(
                "# This is the configuration file for speech2caret.\n"
                "# You can find an explanation of the options in the GitHub README.md: https://github.com/asmith26/speech2caret\n\n"
            )
            config.write(f)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config
