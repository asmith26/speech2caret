import asyncio
from pathlib import Path
from typing import Tuple


def validate_inputs(keyboard_device_path: Path, start_stop_key: str, resume_pause_key: str, audio_fp: Path) -> None:
    """Validate and return the inputs for the main function."""
    if not keyboard_device_path.exists():
        raise ValueError(f"Keyboard device {keyboard_device_path} does not exist.")

    valid_keys = ["KEY_SCROLLLOCK", "KEY_PAUSE"]  # Add more valid keys as needed
    if start_stop_key not in valid_keys:
        raise ValueError(f"Invalid start/stop key: {start_stop_key}. Valid keys are: {valid_keys}")

    if resume_pause_key not in valid_keys:
        raise ValueError(f"Invalid resume/pause key: {resume_pause_key}. Valid keys are: {valid_keys}")

    if audio_fp.suffix != ".wav":
        raise ValueError("Audio file path must have a .wav extension.")


async def listen_keyboard_events(
    keyboard_device_path: Path, start_stop_key: str, resume_pause_key: str, audio_fp: Path
) -> None:
    # Put import statements here to improve CLI performance.
    import evdev

    from speech2caret.recorder import Recorder
    from speech2caret.speech_to_text import SpeechToText
    from speech2caret.virtual_keyboard import VirtualKeyboard

    recorder = Recorder(audio_fp)
    stt = SpeechToText()
    vkeyboard = VirtualKeyboard(keyboard_device_path)

    print(f"Listening on {keyboard_device_path}\nStart/Stop: {start_stop_key}\nResume/Pause: {resume_pause_key}")

    async for event in vkeyboard.device.async_read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event: evdev.KeyEvent = evdev.categorize(event)  # type: ignore
            if key_event.keystate == 1:
                if key_event.keycode == start_stop_key:
                    if not recorder.is_recording:
                        print("Start recording...")
                        asyncio.create_task(recorder.start_recording())
                    else:
                        print("Stopping recording...")
                        recorder.save_recording()
                        text = stt.transcribe(recorder.audio_fp)
                        print("Transcribed text:", text)
                        vkeyboard.type_text(text)
                        recorder.delete_audio_file()

                elif key_event.keycode == resume_pause_key:
                    if not recorder.is_recording:
                        print("Resuming recording...")
                        asyncio.create_task(recorder.start_recording())
                    else:
                        print("Pausing recording...")
                        recorder.pause_recording()


def main(
    keyboard_device_path: Path,
    start_stop_key: str,
    resume_pause_key: str,
    audio_fp: Path = Path("/tmp/tmp_audio.wav"),  # nosec
) -> None:
    """Use your speech to write the current caret position!

    Parameters
    ----------
    keyboard_device_path
        Path to the keyboard device (e.g., "/dev/input/eventX").
        You can find the path by running `ls /dev/input/` and looking for event devices.
    start_stop_key
        Keyboard key that when pressed starts/stops is_recording audio.
    resume_pause_key
        Keyboard key that when pressed resumes/pauses is_recording audio.
    audio_fp
        Path to the audio file where the recorded audio will be saved.
    """
    keyboard_device_path = Path(keyboard_device_path)
    audio_fp = Path(audio_fp)
    validate_inputs(keyboard_device_path, start_stop_key, resume_pause_key, audio_fp)
    asyncio.run(listen_keyboard_events(keyboard_device_path, start_stop_key, resume_pause_key, audio_fp))


if __name__ == "__main__":
    import os

    main(
        keyboard_device_path=Path(os.environ["KEYBOARD_DEVICE_PATH"]),
        start_stop_key=str(os.getenv("START_STOP_KEY")),
        resume_pause_key=str(os.getenv("RESUME_PAUSE_KEY")),
    )
