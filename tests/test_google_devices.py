"""
Unit tests for the main device discovery function in google_devices.py.
Ensures device discovery runs without raising exceptions, using mocks for pychromecast.
"""

from unittest.mock import patch, MagicMock

import pytest

from src.google_devices import main as discover_devices


def test_google_devices_discovery_runs():
    """
    Test that the device discovery function runs without raising exceptions.
    Mocks pychromecast.get_chromecasts to simulate no devices found.
    Also mocks stop_discovery to avoid AttributeError if browser is None.
    """
    with patch('src.google_devices.pychromecast.get_chromecasts') as mock_get, \
            patch('src.google_devices.pychromecast.discovery.stop_discovery') as mock_stop:
        # Use a MagicMock for browser
        mock_get.return_value = ([], MagicMock())
        mock_stop.return_value = None
        discover_devices()
