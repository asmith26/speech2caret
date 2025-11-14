import asyncio
import re
import subprocess  # nosec
from pathlib import Path

from loguru import logger

from speech2caret.config import Config
from speech2caret.recorder import Recorder
from speech2caret.speech_to_text import SpeechToText
from speech2caret.virtual_keyboard import VirtualKeyboard


def play_audio(audio_fp: Path) -> None:
    if audio_fp.exists() and audio_fp.is_file():
        subprocess.run(["paplay", audio_fp])  # nosec


def replace_words(text: str, word_replacements: dict[str, str]) -> str:
    """Replace words in a string with other words.

    Args:
        text: The string to process.
        word_replacements: A dictionary of words to replace and their replacements.

    Returns:
        The processed string.
    """
    for word, replacement in word_replacements.items():
        # Use \b for word boundaries, and re.IGNORECASE for case-insensitivity
        text = re.sub(r"\b" + re.escape(word) + r"\b", replacement, text, flags=re.IGNORECASE)
    return text


async def transcribe_and_type(
    recorder: Recorder, stt: SpeechToText, vkeyboard: VirtualKeyboard, config: Config
) -> None:
    try:
        text = await asyncio.to_thread(stt.transcribe, recorder.audio_fp)
        logger.info(f"Transcribed text: {text}")
        text = replace_words(text, config.word_replacements)
        logger.info(f"Post-processed text: {text}")
        await asyncio.to_thread(vkeyboard.type_text, text)
    finally:
        # delete the temporary file (if successful, failed, or cancelled).
        recorder.delete_audio_file()
