from typing import Dict

import torch
from transformers import pipeline  # type: ignore

from speech2caret.recorder import Recorder


class SpeechToText:
    def __init__(self, recorder: Recorder):
        self.recorder = recorder
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base.en",
            assistant_model="openai/whisper-tiny.en",
            device="cpu",
            torch_dtype=torch.float32,
            chunk_length_s=30,  # split audio into 30 s pieces (allowing for longer audio)
            ignore_warning=True,  # ignore warnings about chunk length todo explore this further
        )

    def transcribe(self) -> str:
        result = self.pipe(str(self.recorder.audio_fp), batch_size=1)
        return result["text"]  # type: ignore
