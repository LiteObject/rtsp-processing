"""
Unit tests for the capture_image_from_rtsp function in image_capture.py.
Tests RTSP image capture logic using mocks for OpenCV and filesystem operations.
"""

from unittest.mock import MagicMock, patch
import os
import pytest

from src.image_capture import capture_image_from_rtsp


@patch('src.image_capture.cv2')
def test_capture_image_success(mock_cv2, tmp_path):
    """
    Test that capture_image_from_rtsp returns a valid image path when the stream and frame are captured successfully.
    Mocks VideoCapture, imwrite, and filesystem operations.
    """
    # Mock VideoCapture and its methods
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, 'frame')
    mock_cv2.VideoCapture.return_value = mock_cap
    mock_cv2.imwrite.return_value = True
    mock_cv2.destroyAllWindows.return_value = None

    # Patch os.makedirs to avoid actual file system changes
    with patch('src.image_capture.os.makedirs') as mock_makedirs:
        image_path = capture_image_from_rtsp('rtsp://test')
        assert image_path is not None
        # Platform-independent path check
        assert os.path.basename(image_path).startswith('capture_')
        assert os.path.dirname(image_path) == 'images'
        mock_cap.release.assert_called_once()
        mock_cv2.imwrite.assert_called_once()
        mock_cv2.destroyAllWindows.assert_called_once()


@patch('src.image_capture.cv2')
def test_capture_image_stream_fail(mock_cv2):
    """
    Test that capture_image_from_rtsp returns None if the RTSP stream cannot be opened.
    """
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_cv2.VideoCapture.return_value = mock_cap
    result = capture_image_from_rtsp('rtsp://bad')
    assert result is None


@patch('src.image_capture.cv2')
def test_capture_image_read_fail(mock_cv2):
    """
    Test that capture_image_from_rtsp returns None if a frame cannot be read from the stream.
    """
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)
    mock_cv2.VideoCapture.return_value = mock_cap
    result = capture_image_from_rtsp('rtsp://bad')
    assert result is None
