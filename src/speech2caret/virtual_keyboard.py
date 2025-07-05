import time
from pathlib import Path

import evdev


class VirtualKeyboard:
    def __init__(self, keyboard_device_path: Path):
        self.device = evdev.InputDevice(keyboard_device_path)

    CHAR_MAP = {
        " ": "KEY_SPACE",
        ",": "KEY_COMMA",
        ".": "KEY_DOT",
        "-": "KEY_MINUS",
        "_": "KEY_MINUS",
        "/": "KEY_SLASH",
        ":": "KEY_SEMICOLON",
        ";": "KEY_SEMICOLON",
        "'": "KEY_APOSTROPHE",
        '"': "KEY_APOSTROPHE",
        "!": "KEY_1",
        "?": "KEY_SLASH",
        "£": "KEY_3",
    }

    def _send_key(self, key_event: str, shift: bool = False) -> None:
        if shift:
            self.device.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
        self.device.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[key_event], 1)
        self.device.write(evdev.ecodes.EV_KEY, evdev.ecodes.ecodes[key_event], 0)
        if shift:
            self.device.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)

        # Process the above write events
        self.device.syn()  # type: ignore
        time.sleep(0.01)  # this helps prevent the letters from getting jumbled up

    def type_text(self, text: str) -> None:
        for char in text:
            if char.isalpha():
                key = f"KEY_{char.upper()}"
                self._send_key(key, shift=char.isupper())
            elif char.isdigit():
                self._send_key(f"KEY_{char}")
            elif char in self.CHAR_MAP:
                shift = char in '!?:"_£'
                self._send_key(self.CHAR_MAP[char], shift)
