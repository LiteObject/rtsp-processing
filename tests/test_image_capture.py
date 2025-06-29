import pytest
from unittest.mock import Mock, patch, MagicMock
import cv2
import os
from src.image_capture import capture_image_from_rtsp


class TestImageCapture:
    
    @patch('src.image_capture.cv2.VideoCapture')
    @patch('src.image_capture.cv2.imwrite')
    @patch('src.image_capture.os.makedirs')
    @patch('src.image_capture.time.time')
    def test_capture_image_success(self, mock_time, mock_makedirs, mock_imwrite, mock_video_capture):
        # Setup
        mock_time.return_value = 1234567890
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_video_capture.return_value = mock_cap
        mock_imwrite.return_value = True
        
        # Execute
        result = capture_image_from_rtsp("rtsp://test.url")
        
        # Assert
        assert result == os.path.join("images", "capture_1234567890.jpg")
        mock_video_capture.assert_called_once_with("rtsp://test.url")
        mock_cap.isOpened.assert_called_once()
        mock_cap.read.assert_called_once()
        mock_cap.release.assert_called_once()
        mock_makedirs.assert_called_once_with("images", exist_ok=True)
        mock_imwrite.assert_called_once()

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_stream_not_opened(self, mock_video_capture):
        # Setup
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        # Execute
        result = capture_image_from_rtsp("rtsp://invalid.url")
        
        # Assert
        assert result is None
        mock_cap.release.assert_not_called()

    @patch('src.image_capture.cv2.VideoCapture')
    def test_capture_image_read_failed(self, mock_video_capture):
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
    def test_capture_image_custom_timestamp(self, mock_time, mock_makedirs, mock_imwrite, mock_video_capture):
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
        expected_path = os.path.join("images", "capture_9876543210.jpg")
        assert result == expected_path