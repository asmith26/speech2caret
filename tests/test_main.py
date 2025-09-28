from unittest.mock import patch, MagicMock

from speech2caret import main


@patch("speech2caret.main.get_config")
@patch("asyncio.run")
def test_main(mock_asyncio_run, mock_get_config):
    """
    GIVEN the main function
    WHEN it is called
    THEN it should call get_config and asyncio.run with listen_keyboard_events
    """
    # Arrange
    mock_config = MagicMock()
    mock_get_config.return_value = mock_config

    # Act
    main.main()

    # Assert
    mock_get_config.assert_called_once()
    mock_asyncio_run.assert_called_once()
    # Check that listen_keyboard_events was passed to asyncio.run
    args, kwargs = mock_asyncio_run.call_args
    assert "listen_keyboard_events" in str(args[0])


@patch("speech2caret.main.get_config")
@patch("asyncio.run", side_effect=KeyboardInterrupt)
@patch("sys.exit")
def test_main_keyboard_interrupt(mock_sys_exit, mock_asyncio_run, mock_get_config):
    """
    GIVEN the main function
    WHEN asyncio.run raises KeyboardInterrupt
    THEN sys.exit should be called
    """
    # Arrange
    mock_config = MagicMock()
    mock_get_config.return_value = mock_config

    # Act
    main.main()

    # Assert
    mock_get_config.assert_called_once()
    mock_asyncio_run.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)
