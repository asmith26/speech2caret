from pathlib import Path

import torch
from transformers import pipeline


class SpeechToText:
    def __init__(self, model_name: str = "openai/whisper-base.en") -> None:
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            # assistant_model="openai/whisper-tiny.en",
            device="cpu",
            torch_dtype=torch.float32,
            chunk_length_s=30,  # split audio into 30 s pieces (allowing for longer audio)
            ignore_warning=True,  # ignore warnings about chunk length todo explore this further
        )

    def transcribe(self, audio_fp: Path) -> str:
        result = self.pipe(str(audio_fp), batch_size=1)
        return result["text"].strip()  # type: ignore
