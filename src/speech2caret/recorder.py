import asyncio
import wave
from pathlib import Path
from typing import List

import numpy as np
import sounddevice
from _sounddevice import ffi
from loguru import logger


class Recorder:
    def __init__(self, audio_fp: Path):
        self.audio_fp = audio_fp
        self.channels = 2  # stereo
        self.sampwith = 2  # 2 bytes (16-bit audio)
        self.sample_rate = 44100
        self.audio_format = "int16"
        self.audio_data: List[np.ndarray] = []
        self.is_recording = False
        # Use an asyncio.Event to signal when recording should stop
        self._stop_event = asyncio.Event()

        self.delete_audio_file()  # Always start fresh

    def delete_audio_file(self) -> None:
        logger.info(f"Deleting audio file: {self.audio_fp}")
        self.audio_fp.unlink(missing_ok=True)

    def _callback(self, indata: np.ndarray, frames: int, time: ffi.CData, status: sounddevice.CallbackFlags) -> None:
        if status:
            logger.debug(status)
        self.audio_data.append(indata.copy())

    async def start_recording(self) -> None:
        self.is_recording = True
        # Clear the stop event flag, allowing the recording loop to run.
        self._stop_event.clear()

        # If we're starting a new recording, clear the old audio data.
        if not self.audio_fp.exists():
            self.audio_data = []

        with sounddevice.InputStream(
            samplerate=self.sample_rate, channels=self.channels, dtype=self.audio_format, callback=self._callback
        ):
            # Wait efficiently until the event is set to True with _stop_event.set() (instead of polling in a loop with `await asyncio.sleep(0.1)`)
            await self._stop_event.wait()

    def pause_recording(self) -> None:
        self.is_recording = False
        # Signal the event to stop the recording loop.
        self._stop_event.set()

    def save_recording(self) -> None:
        self.is_recording = False
        # Signal the event to stop the recording loop.
        self._stop_event.set()

        # Convert the list to a numpy array
        audio_data = np.concatenate(self.audio_data, axis=0)

        # Save the recorded data as a WAV file
        with wave.open(str(self.audio_fp), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sampwith)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
