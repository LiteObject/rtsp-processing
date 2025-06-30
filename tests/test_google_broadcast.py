"""
test_google_broadcast.py

Unit tests for the Google Hub broadcast utility in src/google_broadcast.py.
"""
from unittest.mock import Mock, patch

import pychromecast
from src.google_broadcast import send_message_to_google_hub


class TestGoogleBroadcast:
    """
    Test suite for send_message_to_google_hub, covering success, device not found, no devices,
    custom volume, and connection error scenarios.
    """

    @patch('src.google_broadcast.pychromecast.get_chromecasts')
    @patch('src.google_broadcast.pychromecast.discovery.stop_discovery')
    def test_send_message_success(self, mock_stop_discovery, mock_get_chromecasts):
        """
        Test that send_message_to_google_hub returns True and interacts with the device and media controller
        as expected when the device is found and message is played successfully.
        """
        # Setup
        mock_device = Mock()
        mock_device.cast_info.host = "192.168.1.100"
        mock_device.wait.return_value = None
        mock_device.set_volume.return_value = None

        mock_media_controller = Mock()
        mock_device.media_controller = mock_media_controller

        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([mock_device], mock_browser)

        # Mock the listener to simulate message completion
        def mock_register_listener(listener):
            listener.message_played = True
        mock_media_controller.register_status_listener.side_effect = mock_register_listener

        # Execute
        result = send_message_to_google_hub("Test message", "192.168.1.100")

        # Assert
        assert result is True
        mock_device.wait.assert_called_once()
        mock_device.set_volume.assert_called_once_with(1.0)
        mock_media_controller.play_media.assert_called_once()
        mock_stop_discovery.assert_called_once_with(mock_browser)

    @patch('src.google_broadcast.pychromecast.get_chromecasts')
    @patch('src.google_broadcast.pychromecast.discovery.stop_discovery')
    def test_send_message_device_not_found(self, mock_stop_discovery, mock_get_chromecasts):
        """
        Test that send_message_to_google_hub returns False when the target device is not found.
        """
        # Setup
        mock_device = Mock()
        mock_device.cast_info.host = "192.168.1.200"  # Different IP
        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([mock_device], mock_browser)

        # Execute
        result = send_message_to_google_hub("Test message", "192.168.1.100")

        # Assert
        assert result is False
        mock_stop_discovery.assert_called_once_with(mock_browser)

    @patch('src.google_broadcast.pychromecast.get_chromecasts')
    @patch('src.google_broadcast.pychromecast.discovery.stop_discovery')
    def test_send_message_no_devices(self, mock_stop_discovery, mock_get_chromecasts):
        """
        Test that send_message_to_google_hub returns False when no devices are discovered.
        """
        # Setup
        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([], mock_browser)

        # Execute
        result = send_message_to_google_hub("Test message", "192.168.1.100")

        # Assert
        assert result is False
        mock_stop_discovery.assert_called_once_with(mock_browser)

    @patch('src.google_broadcast.pychromecast.get_chromecasts')
    @patch('src.google_broadcast.pychromecast.discovery.stop_discovery')
    def test_send_message_custom_volume(self, mock_stop_discovery, mock_get_chromecasts):
        """
        Test that send_message_to_google_hub sets the custom volume when provided.
        """
        # Setup
        mock_device = Mock()
        mock_device.cast_info.host = "192.168.1.100"
        mock_device.wait.return_value = None
        mock_device.set_volume.return_value = None

        mock_media_controller = Mock()
        mock_device.media_controller = mock_media_controller

        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([mock_device], mock_browser)

        # Mock the listener
        def mock_register_listener(listener):
            listener.message_played = True
        mock_media_controller.register_status_listener.side_effect = mock_register_listener

        # Execute
        result = send_message_to_google_hub(
            "Test message", "192.168.1.100", volume=0.5)

        # Assert
        assert result is True
        mock_device.set_volume.assert_called_once_with(0.5)
        mock_stop_discovery.assert_called_once_with(mock_browser)

    @patch('src.google_broadcast.pychromecast.get_chromecasts')
    @patch('src.google_broadcast.pychromecast.discovery.stop_discovery')
    def test_send_message_connection_error(self, mock_stop_discovery, mock_get_chromecasts):
        """
        Test that send_message_to_google_hub handles connection errors gracefully and returns False.
        """
        # Setup
        mock_device = Mock()
        mock_device.cast_info.host = "192.168.1.100"
        mock_device.wait.side_effect = Exception("Connection failed")

        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([mock_device], mock_browser)

        # Execute
        result = None
        try:
            result = send_message_to_google_hub(
                "Test message", "192.168.1.100")
        except pychromecast.error.ChromecastConnectionError as e:
            assert False, f"send_message_to_google_hub should handle the exception, but raised: {e}"
        # Assert
        assert result is False
        mock_stop_discovery.assert_called_once_with(mock_browser)
