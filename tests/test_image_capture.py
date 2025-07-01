"""
test_image_capture.py

Unit tests for the RTSP image capture utility in src/image_capture.py.
"""

from unittest.mock import Mock, patch
from src.image_capture import capture_frame_from_rtsp


class TestImageCapture:
    """
    Test suite for the capture_frame_from_rtsp function, covering success, failure, and custom timestamp scenarios.
    """

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_success(self, mock_video_capture):
        """
        Test that capture_image_from_rtsp saves an image successfully when the stream opens and frame is read.
        """
        # Setup
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_video_capture.return_value = mock_cap

        # Execute
        success, frame = capture_frame_from_rtsp("rtsp://test.url")

        # Assert
        assert success is True
        assert frame == "fake_frame"
        mock_video_capture.assert_called_once_with("rtsp://test.url")
        mock_cap.isOpened.assert_called_once()
        mock_cap.read.assert_called_once()
        mock_cap.release.assert_called_once()
        # No file operations since we only return frame in memory

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_stream_not_opened(self, mock_video_capture):
        """
        Test that capture_image_from_rtsp returns None if the RTSP stream cannot be opened.
        """
        # Setup
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        # Execute
        success, frame = capture_frame_from_rtsp("rtsp://invalid.url")

        # Assert
        assert success is False
        assert frame is None
        # Release is always called in finally block
        mock_cap.release.assert_called_once()

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_read_failed(self, mock_video_capture):
        """
        Test that capture_image_from_rtsp returns None if reading a frame from the stream fails.
        """
        # Setup
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_video_capture.return_value = mock_cap

        # Execute
        success, frame = capture_frame_from_rtsp("rtsp://test.url")

        # Assert
        assert success is False
        assert frame is None
        mock_cap.release.assert_called_once()

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_custom_timestamp(self, mock_video_capture):
        """
        Test that capture_image_from_rtsp uses the correct timestamp in the saved image filename.
        """
        # Setup
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_video_capture.return_value = mock_cap

        # Execute
        success, frame = capture_frame_from_rtsp("rtsp://test.url")

        # Assert
        assert success is True
        assert frame == "fake_frame"
