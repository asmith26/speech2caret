from pathlib import Path

import pytest

from speech2caret.main import validate_inputs


def test_validate_inputs_happy_path(tmp_path: Path) -> None:
    """
    Tests that validate_inputs runs without error when all inputs are valid.
    """
    fake_device = tmp_path / "event0"
    fake_device.touch()  # Ensure the file exists
    try:
        validate_inputs(fake_device, "a", "b", Path("test.wav"))
    except SystemExit:
        pytest.fail("validate_inputs raised SystemExit unexpectedly on valid inputs.")


def test_validate_inputs_keyboard_path_not_set(caplog, tmp_path: Path) -> None:
    """
    Tests that validate_inputs exits if keyboard_device_path is not set (i.e., defaults to Path('.')).
    """
    with pytest.raises(SystemExit) as e:
        validate_inputs(Path("."), "a", "b", Path("test.wav"))

    assert e.value.code == 1
    assert "keyboard_device_path not set" in caplog.text


def test_validate_inputs_keyboard_path_does_not_exist(caplog, tmp_path: Path) -> None:
    """
    Tests that validate_inputs exits if the keyboard_device_path does not point to an existing file.
    """
    nonexistent_device = tmp_path / "nonexistent_device"

    with pytest.raises(SystemExit) as e:
        validate_inputs(nonexistent_device, "a", "b", Path("test.wav"))

    assert e.value.code == 1
    assert "Keyboard device does not exist" in caplog.text


def test_validate_inputs_start_stop_key_not_set(caplog, tmp_path: Path) -> None:
    """
    Tests that validate_inputs exits if start_stop_key is an empty string.
    """
    fake_device = tmp_path / "event0"
    fake_device.touch()  # Ensure the file exists

    with pytest.raises(SystemExit) as e:
        validate_inputs(fake_device, "", "b", Path("test.wav"))

    assert e.value.code == 1
    assert "start_stop_key not set" in caplog.text


def test_validate_inputs_resume_pause_key_not_set(caplog, tmp_path: Path) -> None:
    """
    Tests that validate_inputs exits if resume_pause_key is an empty string.
    """
    fake_device = tmp_path / "event0"
    fake_device.touch()  # Ensure the file exists

    with pytest.raises(SystemExit) as e:
        validate_inputs(fake_device, "a", "", Path("test.wav"))

    assert e.value.code == 1
    assert "resume_pause_key not set" in caplog.text


def test_validate_inputs_audio_fp_wrong_extension(caplog, tmp_path: Path) -> None:
    """
    Tests that validate_inputs exits if the audio file path does not end with '.wav'.
    """
    fake_device = tmp_path / "event0"
    fake_device.touch()  # Ensure the file exists

    with pytest.raises(SystemExit) as e:
        validate_inputs(fake_device, "a", "b", tmp_path / "audio.mp3")

    assert e.value.code == 1
    assert "Audio file path must have a .wav extension" in caplog.text
