import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config/speech2caret"
CONFIG_FILE = CONFIG_DIR / "config.ini"


def get_config() -> configparser.ConfigParser:
    """Get user configuration.

    If the config file doesn't exist, it will be created.
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    config = configparser.ConfigParser()

    # Create a default config file
    if not CONFIG_FILE.is_file():
        config["speech2caret"] = {
            "# example:\n# keyboard_device_path": "/dev/input/by-path/pci-0000:00:1.0-usb-0:1:1.0-event-kbd",
            "# start_stop_key": "KEY_F11",
            "# resume_pause_key": "KEY_F12",
            "keyboard_device_path": "",
            "start_stop_key": "",
            "resume_pause_key": "",
        }
        with open(CONFIG_FILE, "w") as f:
            f.write(
                "# This is the configuration file for speech2caret.\n"
                "# You can find an explanation of the options in the GitHub README.md: https://github.com/asmith26/speech2caret\n\n"
            )
            config.write(f)

    config.read(CONFIG_FILE)
    return config
