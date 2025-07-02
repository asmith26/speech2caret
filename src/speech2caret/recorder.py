import asyncio
import wave
from pathlib import Path
from typing import List

import numpy as np
import sounddevice as sd
from _sounddevice import ffi


class Recorder:
    def __init__(self, audio_fp: Path):
        self.audio_fp = audio_fp
        self.sample_rate = 44100
        self.channels = 2
        self.audio_format = "int16"
        self.audio_data: List[np.ndarray] = []
        self.is_recording = False

        self.delete_audio_file()  # Start fresh

    def delete_audio_file(self) -> None:
        print(f"Deleting audio file: {self.audio_fp}")
        self.audio_fp.unlink(missing_ok=True)

    def callback(self, indata: np.ndarray, frames: int, time: ffi.CData, status: sd.CallbackFlags) -> None:
        if status:
            print(status, flush=True)
        self.audio_data.append(indata.copy())

    async def start_recording(self) -> None:
        self.is_recording = True
        self.audio_data = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, channels=self.channels, dtype=self.audio_format, callback=self.callback
        )
        with self.stream:
            while self.is_recording:
                await asyncio.sleep(0.1)

    async def stop_recording(self) -> None:
        self.recording = False
        await asyncio.sleep(0.1)

        # Convert the list to a numpy array
        audio_data = np.concatenate(self.audio_data, axis=0)

        # Check if file exists already
        if self.audio_fp.exists():
            # Read existing data
            with wave.open(str(self.audio_fp), "rb") as wf:
                existing_frames = wf.readframes(wf.getnframes())
                nchannels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()

            # Make sure format matches
            if nchannels != self.channels:
                raise ValueError(f"Channel count mismatch: expected {self.channels}, got {nchannels}")
            if sampwidth != 2:  # 16‑bit
                raise ValueError(f"Sample width mismatch: expected 2 (16‑bit), got {sampwidth}")
            if framerate != self.sample_rate:
                raise ValueError(f"Sample rate mismatch: expected {self.sample_rate}, got {framerate}")

            # Combine old and new
            combined_audio = existing_frames + audio_data.tobytes()

        else:
            # If file does not exist, just use the new audio data
            combined_audio = audio_data.tobytes()

        # Save the recorded data as a WAV file
        with wave.open(str(self.audio_fp), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 2 bytes (16 bits)
            wf.setframerate(self.sample_rate)
            wf.writeframes(combined_audio)
