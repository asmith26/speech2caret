import tempfile
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger


@pytest.fixture
def fake_audio_fp():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """
    Override the default caplog fixture to capture loguru's output.
    """
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level="INFO",
    )
    yield caplog
    logger.remove(handler_id)
