from pathlib import Path
from unittest.mock import MagicMock, patch

import evdev

from speech2caret.virtual_keyboard import VirtualKeyboard


def make_mock_device():
    mock_device = MagicMock(spec=evdev.InputDevice)
    mock_device.write = MagicMock()
    mock_device.syn = MagicMock()
    return mock_device


@patch("evdev.InputDevice", return_value=make_mock_device())
def test_type_simple_text(mock_input_device):
    vk = VirtualKeyboard(Path("/dev/input/event0"))
    vk.type_text("abc")

    expected_calls = [
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 1),),
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 0),),
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_B, 1),),
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_B, 0),),
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_C, 1),),
        ((evdev.ecodes.EV_KEY, evdev.ecodes.KEY_C, 0),),
    ]
    vk.device.write.assert_has_calls(expected_calls, any_order=False)
    vk.device.syn.call_count == 3


@patch("evdev.InputDevice", return_value=make_mock_device())
def test_type_uppercase(mock_input_device):
    vk = VirtualKeyboard(Path("/dev/input/event0"))
    vk.type_text("A")

    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 0)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)
    vk.device.syn.assert_called_once()


@patch("evdev.InputDevice", return_value=make_mock_device())
def test_type_special_chars(mock_input_device):
    vk = VirtualKeyboard(Path("/dev/input/event0"))
    vk.type_text("!?")

    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_1, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_1, 0)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)

    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_SLASH, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_SLASH, 0)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)

    vk.device.syn.call_count == 2


@patch("evdev.InputDevice", return_value=make_mock_device())
def test_type_digits(mock_input_device):
    vk = VirtualKeyboard(Path("/dev/input/event0"))
    vk.type_text("123")

    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_1, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_2, 1)
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_3, 1)
    vk.device.syn.call_count == 3


@patch("evdev.InputDevice", return_value=make_mock_device())
def test_whitespace_is_stripped(mock_input_device):
    vk = VirtualKeyboard(Path("/dev/input/event0"))
    vk.type_text("  a ")
    vk.device.write.assert_any_call(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 1)
    vk.device.syn.assert_called_once()
