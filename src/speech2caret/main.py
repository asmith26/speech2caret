import argparse
import asyncio
from pathlib import Path

from speech2caret.config import get_config


def validate_inputs(keyboard_device_path: Path, start_stop_key: str, resume_pause_key: str, audio_fp: Path) -> None:
    """Validate and return the inputs for the main function."""
    if not keyboard_device_path:
        raise ValueError("keyboard_device_path not set")
    if not keyboard_device_path.exists():
        raise ValueError(f"Keyboard device does not exist: {keyboard_device_path}")
    if not start_stop_key:
        raise ValueError("start_stop_key not set")
    if not resume_pause_key:
        raise ValueError("resume_pause_key not set")
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


def main() -> None:
    """Use your speech to write the current caret position!"""
    config = get_config()
    parser = argparse.ArgumentParser(description="Use your speech to write to the current caret position.")
    parser.add_argument(
        "--keyboard-device-path",
        type=Path,
        default=config.get("speech2caret", "keyboard_device_path", fallback=None),
        help="Path to the keyboard device.",
    )
    parser.add_argument(
        "--start-stop-key",
        type=str,
        default=config.get("speech2caret", "start_stop_key", fallback=None),
        help="Key to start/stop recording.",
    )
    parser.add_argument(
        "--resume-pause-key",
        type=str,
        default=config.get("speech2caret", "resume_pause_key", fallback=None),
        help="Key to resume/pause recording.",
    )
    parser.add_argument(
        "--audio-fp",
        type=Path,
        default=config.get("speech2caret", "audio_fp", fallback="/tmp/tmp_audio.wav"),
        help="Path to save the temporary audio file.",
    )
    args = parser.parse_args()

    validate_inputs(args.keyboard_device_path, args.start_stop_key, args.resume_pause_key, args.audio_fp)
    asyncio.run(
        listen_keyboard_events(
            args.keyboard_device_path,
            args.start_stop_key,
            args.resume_pause_key,
            args.audio_fp,
        )
    )

if __name__ == "__main__":
    main()
