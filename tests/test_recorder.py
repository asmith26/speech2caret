import asyncio
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from speech2caret.recorder import Recorder


def test_delete_audio_file(fake_audio_fp):
    # Create a test audio file
    fake_audio_fp.write_bytes(b"spam")

    recorder = Recorder(audio_fp=fake_audio_fp)
    recorder.delete_audio_file()

    assert not fake_audio_fp.exists()


@pytest.mark.asyncio
async def test_recording_cycle(fake_audio_fp):
    recorder = Recorder(audio_fp=fake_audio_fp)

    # Fake audio data to simulate the callback
    dummy_data = np.random.randint(-32768, 32767, (4410, 2), dtype=np.int16)

    # Patch sounddevice.InputStream and its context manager
    with mock.patch("sounddevice.InputStream") as mock_stream_class:
        mock_stream = mock_stream_class.return_value
        mock_stream.__enter__.return_value = mock_stream
        mock_stream.__exit__.return_value = None

        # Simulate appending data during recording
        async def simulate_recording():
            recorder.callback(dummy_data, None, None, None)
            recorder.is_recording = False

        # Start recording and stop after a brief moment
        await asyncio.gather(recorder.start_recording(), simulate_recording())

        await recorder.stop_recording()

    assert fake_audio_fp.exists()

    import wave

    with wave.open(str(fake_audio_fp), "rb") as wf:
        assert wf.getnchannels() == recorder.channels
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == recorder.sample_rate
        assert wf.getnframes() > 0

        # Rewind and read frames
        wf.rewind()
        recorded_bytes = wf.readframes(wf.getnframes())
        recorded_array = np.frombuffer(recorded_bytes, dtype=np.int16).reshape(-1, 2)

        # Check if the recorded data matches the dummy_data
        # Note: since we're not using any actual audio hardware, this check is valid
        np.testing.assert_array_equal(recorded_array, dummy_data)
