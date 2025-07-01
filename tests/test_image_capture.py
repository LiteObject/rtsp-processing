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
    @patch('src.image_capture.cv2.imwrite')
    @patch('src.image_capture.os.makedirs')
    @patch('src.image_capture.time.time')
    def test_capture_image_success(self, mock_time, mock_makedirs, mock_imwrite, mock_video_capture):
        """
        Test that capture_image_from_rtsp saves an image successfully when the stream opens and frame is read.
        """
        # Setup
        mock_time.return_value = 1234567890
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_video_capture.return_value = mock_cap
        mock_imwrite.return_value = True

        # Execute
        result = capture_frame_from_rtsp("rtsp://test.url")

        # Assert
        assert result.endswith("capture_1234567890.jpg")
        mock_video_capture.assert_called_once_with("rtsp://test.url")
        mock_cap.isOpened.assert_called_once()
        mock_cap.read.assert_called_once()
        mock_cap.release.assert_called_once()
        mock_makedirs.assert_called_once_with("images", exist_ok=True)
        mock_imwrite.assert_called_once()

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
        result = capture_image_from_rtsp("rtsp://invalid.url")

        # Assert
        assert result is None
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
        result = capture_image_from_rtsp("rtsp://test.url")

        # Assert
        assert result is None
        mock_cap.release.assert_called_once()

    @patch('src.image_capture.cv2.VideoCapture')
    @patch('src.image_capture.cv2.imwrite')
    @patch('src.image_capture.os.makedirs')
    @patch('src.image_capture.time.time')
    def test_capture_image_custom_timestamp(self, mock_time, _, mock_imwrite, mock_video_capture):
        """
        Test that capture_image_from_rtsp uses the correct timestamp in the saved image filename.
        """
        # Setup
        mock_time.return_value = 9876543210
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_video_capture.return_value = mock_cap
        mock_imwrite.return_value = True

        # Execute
        result = capture_image_from_rtsp("rtsp://test.url")

        # Assert
        assert result.endswith("capture_9876543210.jpg")
