import asyncio
import sys
import tempfile
from pathlib import Path

from loguru import logger

from speech2caret import utils
from speech2caret.config import Config, get_config
from speech2caret.recorder import Recorder
from speech2caret.speech_to_text import SpeechToText
from speech2caret.virtual_keyboard import VirtualKeyboard


async def listen_keyboard_events(config: Config) -> None:  # pragma: no cover
    import evdev

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_audio_fp = Path(temp_dir) / "speech2caret.wav"
        recorder = Recorder(tmp_audio_fp)
        stt: SpeechToText = SpeechToText()
        vkeyboard = VirtualKeyboard(config.keyboard_device_path)

        logger.info(f"Listening on {config.keyboard_device_path}")
        logger.info(f"Start/Stop: {config.start_stop_key}")
        logger.info(f"Resume/Pause: {config.resume_pause_key}")
        logger.info(f"Start Recording audio path: {config.start_recording_audio_path}")
        logger.info(f"Stop Recording audio path: {config.stop_recording_audio_path}")
        logger.info(f"Resume Recording audio path: {config.resume_recording_audio_path}")
        logger.info(f"Pause Recording audio path: {config.pause_recording_audio_path}")
        logger.info(f"Temporary audio file: {tmp_audio_fp}\n")

        # This variable will hold the asyncio.Task for the transcription process.
        # It's used to check if a transcription is in progress and to cancel it if needed.
        transcribe_and_type_task = None

        try:
            async for event in vkeyboard.device.async_read_loop():
                # We only need to process key_down events
                if event.type == evdev.ecodes.EV_KEY:  # if input event is a keyboard key event
                    key_event: evdev.KeyEvent = evdev.categorize(event)  # type: ignore
                    if key_event.keystate == evdev.events.KeyEvent.key_down:
                        # === Start/Stop Recording ===
                        if key_event.keycode == config.start_stop_key:
                            if not recorder.is_recording and not recorder.is_paused:
                                # If there's an ongoing transcription task from a previous recording,
                                # cancel it (allows interrupting long transcriptions)
                                if transcribe_and_type_task and not transcribe_and_type_task.done():
                                    logger.info("Interrupting transcription...")
                                    transcribe_and_type_task.cancel()

                                logger.info("= Start recording ===")
                                utils.play_audio(config.start_recording_audio_path)
                                # Start the recording in a new asyncio task so it doesn't block the event loop.
                                asyncio.create_task(recorder.start_recording())

                            else:
                                logger.info("Stopping recording...")
                                utils.play_audio(config.stop_recording_audio_path)
                                recorder.save_recording()
                                # utils.play_sound(recorder.audio_fp)  # Play recording
                                # Start the transcribe_and_type in a new asyncio task so it doesn't block the event loop.
                                transcribe_and_type_task = asyncio.create_task(
                                    utils.transcribe_and_type(recorder, stt, vkeyboard)
                                )

                        # === Resume/Pause Recording ===
                        elif key_event.keycode == config.resume_pause_key:
                            if not recorder.is_recording and recorder.is_paused:
                                logger.info("Resuming recording...")
                                utils.play_audio(config.resume_recording_audio_path)
                                asyncio.create_task(recorder.start_recording(is_resume=True))

                            elif recorder.is_recording and not recorder.is_paused:
                                logger.info("Pausing recording...")
                                utils.play_audio(config.pause_recording_audio_path)
                                recorder.pause_recording()

                            elif not recorder.is_recording and not recorder.is_paused:
                                logger.warning("You must start recording before resume/pause")

        except Exception:
            logger.exception("An unexpected error occurred in the event loop.")


def main() -> None:  # pragma: no cover
    """Use your speech to write the current caret position!"""
    # Get/validate config
    config = get_config()

    # Start listening for keyboard events
    try:
        asyncio.run(listen_keyboard_events(config))
    except KeyboardInterrupt:
        logger.info("Successfully exited speech2caret. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
