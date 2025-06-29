"""
Unit tests for the send_message_to_google_hub function in google_broadcast.py.
Tests Chromecast device discovery and message broadcasting logic using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.google_broadcast import send_message_to_google_hub


@patch('src.google_broadcast.pychromecast')
def test_send_message_success(mock_pychromecast):
    """
    Test that send_message_to_google_hub returns True when a device is found and message is played.
    Mocks Chromecast discovery, device, and media controller behavior.
    """
    # Mock Chromecast discovery and device
    mock_cast = MagicMock()
    mock_cast.cast_info.host = '192.168.1.2'
    mock_cast.media_controller.register_status_listener.return_value = None
    mock_cast.media_controller.block_until_active.return_value = None
    mock_cast.media_controller.play.return_value = None
    mock_cast.media_controller.play_media.return_value = None
    mock_cast.media_controller.unregister_status_listener.return_value = None
    mock_cast.set_volume.return_value = None
    mock_cast.wait.return_value = None
    # Simulate message played
    # Patch MediaStatusListener at the module level, not as an attribute of the function
    with patch('src.google_broadcast.MediaStatusListener') as DummyListener:
        DummyListener.return_value.message_played = True
        mock_pychromecast.get_chromecasts.return_value = (
            [mock_cast], 'browser')
        mock_pychromecast.discovery.stop_discovery.return_value = None
        result = send_message_to_google_hub('hello', '192.168.1.2')
        assert result is True


@patch('src.google_broadcast.pychromecast')
def test_send_message_no_device(mock_pychromecast):
    """
    Test that send_message_to_google_hub returns False when no device is found.
    Mocks Chromecast discovery to return an empty list.
    """
    mock_pychromecast.get_chromecasts.return_value = ([], 'browser')
    mock_pychromecast.discovery.stop_discovery.return_value = None
    result = send_message_to_google_hub('hello', '192.168.1.2')
    assert result is False
