import asyncio
import subprocess  # nosec
from pathlib import Path

from loguru import logger

from speech2caret.recorder import Recorder
from speech2caret.speech_to_text import SpeechToText
from speech2caret.virtual_keyboard import VirtualKeyboard


def play_audio(audio_fp: Path) -> None:
    if audio_fp.exists() and audio_fp.is_file():
        subprocess.run(["paplay", audio_fp])  # nosec


async def transcribe_and_type(recorder: Recorder, stt: SpeechToText, vkeyboard: VirtualKeyboard) -> None:
    try:
        text = await asyncio.to_thread(stt.transcribe, recorder.audio_fp)
        logger.info(f"Transcribed text: {text}")
        await asyncio.to_thread(vkeyboard.type_text, text)
    finally:
        # delete the temporary file (if successful, failed, or cancelled).
        recorder.delete_audio_file()
