import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

from loguru import logger

from speech2caret.config import get_config


def validate_inputs(keyboard_device_path: Path, start_stop_key: str, resume_pause_key: str) -> None:
    """Validate and return the inputs for the main function."""
    config_help = "Edit the config file (see https://github.com/asmith26/speech2caret/tree/main#configuration) or pass in CLI arguments (see `speech2caret --help`)"
    if keyboard_device_path == Path("."):
        logger.error(f"keyboard_device_path not set. {config_help}.")
        sys.exit(1)
    if not keyboard_device_path.exists():
        logger.error(f"Keyboard device does not exist: {keyboard_device_path}")
        sys.exit(1)
    if not start_stop_key:
        logger.error(f"start_stop_key not set. {config_help}.")
        sys.exit(1)
    if not resume_pause_key:
        logger.error(f"resume_pause_key not set. {config_help}.")
        sys.exit(1)


async def listen_keyboard_events(
    keyboard_device_path: Path,
    start_stop_key: str,
    resume_pause_key: str,
) -> None:  # pragma: no cover
    # Put import statements here to improve CLI performance.
    import evdev

    from speech2caret.recorder import Recorder
    from speech2caret.speech_to_text import SpeechToText
    from speech2caret.virtual_keyboard import VirtualKeyboard

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_audio_fp = Path(temp_dir) / "speech2caret.wav"
        recorder = Recorder(tmp_audio_fp)
        stt: SpeechToText = SpeechToText()
        vkeyboard = VirtualKeyboard(keyboard_device_path)

        logger.info(f"Listening on {keyboard_device_path}")
        logger.info(f"Start/Stop: {start_stop_key}")
        logger.info(f"Resume/Pause: {resume_pause_key}")
        logger.info(f"Temporary audio file: {tmp_audio_fp}")

        try:
            async for event in vkeyboard.device.async_read_loop():
                if event.type == evdev.ecodes.EV_KEY:  # if input event is a keyboard key event
                    key_event: evdev.KeyEvent = evdev.categorize(event)  # type: ignore
                    if key_event.keystate == evdev.events.KeyEvent.key_down:
                        if key_event.keycode == start_stop_key:
                            if not recorder.is_recording and not recorder.is_paused:
                                logger.info("=== Start recording ===")
                                asyncio.create_task(recorder.start_recording())
                            else:
                                logger.info("Stopping recording...")
                                recorder.save_recording()
                                text = stt.transcribe(recorder.audio_fp)
                                logger.info(f"Transcribed text: {text}")
                                vkeyboard.type_text(text)
                                recorder.delete_audio_file()

                        elif key_event.keycode == resume_pause_key:
                            if not recorder.is_recording and recorder.is_paused:
                                logger.info("Resuming recording...")
                                asyncio.create_task(recorder.start_recording(is_resume=True))
                            elif recorder.is_recording and not recorder.is_paused:
                                logger.info("Pausing recording...")
                                recorder.pause_recording()
                            elif not recorder.is_recording and not recorder.is_paused:
                                logger.warning("You must start recording before resume/pause")

        except Exception:
            logger.exception("An unexpected error occurred in the event loop.")


def main() -> None:  # pragma: no cover
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
    args = parser.parse_args()

    validate_inputs(args.keyboard_device_path, args.start_stop_key, args.resume_pause_key)
    try:
        asyncio.run(
            listen_keyboard_events(
                args.keyboard_device_path,
                args.start_stop_key,
                args.resume_pause_key,
            )
        )
    except KeyboardInterrupt:
        logger.info("Successfully exited speech2caret. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
