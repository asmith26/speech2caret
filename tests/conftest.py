import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def fake_audio_fp():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)
