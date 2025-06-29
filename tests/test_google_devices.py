import pytest
from unittest.mock import Mock, patch
from src.google_devices import discover_google_devices


class TestGoogleDevices:
    
    @patch('src.google_devices.pychromecast.get_chromecasts')
    @patch('src.google_devices.pychromecast.discovery.stop_discovery')
    def test_discover_google_devices_success(self, mock_stop_discovery, mock_get_chromecasts):
        # Setup
        mock_device1 = Mock()
        mock_device1.cast_info.friendly_name = "Living Room Hub"
        mock_device1.cast_info.host = "192.168.1.100"
        mock_device1.cast_info.port = 8009
        
        mock_device2 = Mock()
        mock_device2.cast_info.friendly_name = "Kitchen Display"
        mock_device2.cast_info.host = "192.168.1.101"
        mock_device2.cast_info.port = 8009
        
        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([mock_device1, mock_device2], mock_browser)
        
        # Execute
        devices = discover_google_devices()
        
        # Assert
        assert len(devices) == 2
        assert devices[0]["name"] == "Living Room Hub"
        assert devices[0]["ip"] == "192.168.1.100"
        assert devices[1]["name"] == "Kitchen Display"
        assert devices[1]["ip"] == "192.168.1.101"
        mock_stop_discovery.assert_called_once_with(mock_browser)

    @patch('src.google_devices.pychromecast.get_chromecasts')
    @patch('src.google_devices.pychromecast.discovery.stop_discovery')
    def test_discover_google_devices_empty(self, mock_stop_discovery, mock_get_chromecasts):
        # Setup
        mock_browser = Mock()
        mock_get_chromecasts.return_value = ([], mock_browser)
        
        # Execute
        devices = discover_google_devices()
        
        # Assert
        assert len(devices) == 0
        mock_stop_discovery.assert_called_once_with(mock_browser)