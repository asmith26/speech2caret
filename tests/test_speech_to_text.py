from pathlib import Path

from speech2caret.recorder import Recorder
from speech2caret.speech_to_text import SpeechToText


def test__transcribe_returns_correctly(fake_audio_fp):
    test_fp = Path(__file__).parent / "data/jfk.flac"
    stt = SpeechToText()

    assert (
        stt.transcribe(test_fp)
        == " And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country."
    )
