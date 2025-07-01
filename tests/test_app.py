"""
test_app.py

Unit tests for the main application loop in src/app.py, 
focusing on the threaded/queue-based architecture and shutdown logic.
"""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.app import main_async


class TestApp:
    """
    Test suite for the main threaded/queue-based application loop in app.py.
    """

    @patch('src.app.asyncio.sleep')
    @patch('src.app.capture_frame_from_rtsp')
    @patch('src.app.AsyncRTSPProcessingService')
    @patch('src.app.run_health_checks')
    def test_main_async_loop_keyboard_interrupt(self, mock_health_checks, mock_service_class, mock_capture, mock_sleep):
        """
        Test that the async main loop handles KeyboardInterrupt correctly.
        """
        # Setup
        mock_health_checks.return_value = {
            "rtsp_stream": True, "openai_api": True}
        mock_service = MagicMock()
        mock_service.config.RTSP_URL = "rtsp://test"
        mock_service.config.CAPTURE_INTERVAL = 1
        mock_service.process_frame_async = AsyncMock()
        mock_service_class.return_value = mock_service
        mock_capture.return_value = (True, "fake_frame")

        # Simulate KeyboardInterrupt after first loop
        async def side_effect(*args, **kwargs):
            raise KeyboardInterrupt()
        mock_sleep.side_effect = side_effect

        # Execute
        asyncio.run(main_async())
        mock_capture.assert_called_once()
        mock_service_class.assert_called_once()

    @patch('src.app.asyncio.sleep')
    @patch('src.app.capture_frame_from_rtsp')
    @patch('src.app.AsyncRTSPProcessingService')
    @patch('src.app.run_health_checks')
    def test_main_async_loop_handles_no_image(self, mock_health_checks, mock_service_class, mock_capture, mock_sleep):
        """
        Test that the async main loop handles the case where no image is captured.
        """
        # Setup
        mock_health_checks.return_value = {
            "rtsp_stream": True, "openai_api": True}
        mock_service = MagicMock()
        mock_service.config.RTSP_URL = "rtsp://test"
        mock_service.config.CAPTURE_INTERVAL = 1
        mock_service.process_frame_async = AsyncMock()
        mock_service_class.return_value = mock_service
        mock_capture.return_value = (False, None)  # Simulate failed capture

        # Simulate KeyboardInterrupt after first loop
        async def side_effect(*args, **kwargs):
            raise KeyboardInterrupt()
        mock_sleep.side_effect = side_effect

        # Execute
        asyncio.run(main_async())
        mock_capture.assert_called_once()
        mock_service.process_frame_async.assert_not_called()
        mock_service_class.assert_called_once()
