"""
test_app.py

Unit tests for the main application loop in src/app.py, 
focusing on the threaded/queue-based architecture and shutdown logic.
"""

from unittest.mock import patch, MagicMock
from src.app import main


class TestApp:
    """
    Test suite for the main threaded/queue-based application loop in app.py.
    """

    @patch('src.app.time.sleep')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.Queue')
    @patch('src.app.threading.Thread')
    @patch('src.app.RTSPProcessingService')
    def test_main_threaded_loop_keyboard_interrupt(self, mock_service_class, mock_thread, mock_queue, mock_capture, mock_sleep):
        """
        Test that the main loop handles KeyboardInterrupt correctly, shuts down the worker thread,
        and sends the shutdown signal to the queue after capturing an image.
        """
        # Setup
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_capture.return_value = "images/test.jpg"
        mock_q = MagicMock()
        mock_queue.return_value = mock_q
        # Simulate KeyboardInterrupt after first loop

        def side_effect(*args, **kwargs):
            raise KeyboardInterrupt()
        mock_sleep.side_effect = side_effect
        # Patch thread to not actually start
        mock_thread.return_value.start.return_value = None
        mock_thread.return_value.join.return_value = None

        # Execute
        main()
        mock_capture.assert_called_once()
        mock_q.put.assert_any_call("images/test.jpg")
        mock_service_class.assert_called_once()
        # Check shutdown logic
        mock_q.put.assert_any_call(None)
        mock_thread.return_value.join.assert_called_once()

    @patch('src.app.time.sleep')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.Queue')
    @patch('src.app.threading.Thread')
    @patch('src.app.RTSPProcessingService')
    def test_main_threaded_loop_handles_no_image(self, mock_service_class, mock_thread, mock_queue, mock_capture, mock_sleep):
        """
        Test that the main loop handles the case where no image is captured (capture returns None),
        and still shuts down the worker thread and sends the shutdown signal to the queue.
        """
        # Setup
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_capture.return_value = None  # Simulate failed capture
        mock_q = MagicMock()
        mock_queue.return_value = mock_q
        # Simulate KeyboardInterrupt after first loop

        def side_effect(*args, **kwargs):
            raise KeyboardInterrupt()
        mock_sleep.side_effect = side_effect
        mock_thread.return_value.start.return_value = None
        mock_thread.return_value.join.return_value = None

        # Execute
        main()
        mock_capture.assert_called_once()
        # Only shutdown signal should be sent to the queue
        mock_q.put.assert_called_once_with(None)
        mock_service_class.assert_called_once()
        mock_thread.return_value.join.assert_called_once()
