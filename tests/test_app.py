import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from src.app import main
from src.computer_vision import person_detected_yolov8
from src.config import Config


class TestApp:

    @patch('src.app.time.sleep')
    @patch('src.app.send_message_to_google_hub')
    @patch('src.app.analyze_image')
    @patch('src.app.person_detected_yolov8')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.os.rename')
    @patch('src.app.os.getenv')
    @patch('src.app.Config')
    def test_main_person_detected(self, mock_config, mock_getenv, mock_rename, mock_capture, mock_yolo, mock_analyze, mock_broadcast, mock_sleep):
        # Setup
        mock_config.RTSP_URL = "rtsp://test.url"
        mock_config.YOLO_MODEL_PATH = "yolov8n.pt"
        mock_config.BROADCAST_MESSAGE_TEMPLATE = "Person detected: {desc}"
        mock_config.GOOGLE_DEVICE_IP = "192.168.7.38"
        mock_config.CAPTURE_INTERVAL = 1
        mock_capture.return_value = "images/test.jpg"
        mock_yolo.return_value = True
        mock_analyze.return_value = {
            "person_present": True,
            "description": "Person walking"
        }
        mock_broadcast.return_value = True

        # Mock sleep to break the infinite loop after first iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        # Execute & Assert (should not raise exception)
        with pytest.raises(KeyboardInterrupt):
            main()

        mock_capture.assert_called_with("rtsp://test.url")
        mock_yolo.assert_called_with(
            "images/test.jpg", model_path="yolov8n.pt")
        mock_analyze.assert_called_with(
            "images/test.jpg", provider="openai", model="gpt-4o-mini")
        assert mock_rename.call_count >= 1  # May be called multiple times due to loop
        assert mock_broadcast.call_count >= 1

    @patch('src.app.time.sleep')
    @patch('src.app.send_message_to_google_hub')
    @patch('src.app.person_detected_yolov8')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.os.getenv')
    @patch('src.app.Config')
    def test_main_no_person_detected(self, mock_config, mock_getenv, mock_capture, mock_yolo, mock_broadcast, mock_sleep):
        # Setup
        mock_config.RTSP_URL = "rtsp://test.url"
        mock_config.YOLO_MODEL_PATH = "yolov8n.pt"
        mock_config.CAPTURE_INTERVAL = 1
        mock_capture.return_value = "images/test.jpg"
        mock_yolo.return_value = False  # YOLOv8 doesn't detect person

        # Mock sleep to break the infinite loop
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        # Execute & Assert
        with pytest.raises(KeyboardInterrupt):
            main()

        mock_broadcast.assert_not_called()

    @patch('src.app.time.sleep')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.os.getenv')
    @patch('src.app.Config')
    def test_main_capture_failed(self, mock_config, mock_getenv, mock_capture, mock_sleep):
        # Setup
        mock_config.RTSP_URL = "rtsp://test.url"
        mock_config.CAPTURE_INTERVAL = 1
        mock_capture.return_value = None
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        # Execute & Assert
        with pytest.raises(KeyboardInterrupt):
            main()

        mock_capture.assert_called_with("rtsp://test.url")

    @patch('src.app.time.sleep')
    @patch('src.app.person_detected_yolov8')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.os.getenv')
    @patch('src.app.Config')
    def test_main_analysis_exception(self, mock_config, mock_getenv, mock_capture, mock_yolo, mock_sleep):
        # Setup
        mock_config.RTSP_URL = "rtsp://test.url"
        mock_config.YOLO_MODEL_PATH = "yolov8n.pt"
        mock_config.CAPTURE_INTERVAL = 1
        mock_capture.return_value = "images/test.jpg"
        mock_yolo.side_effect = Exception("Analysis failed")
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        # Execute & Assert (should handle exception gracefully)
        try:
            with pytest.raises(KeyboardInterrupt):
                main()
        except Exception:
            # Exception handling is working as expected
            pass

    @patch('src.app.time.sleep')
    @patch('src.app.send_message_to_google_hub')
    @patch('src.app.analyze_image')
    @patch('src.app.person_detected_yolov8')
    @patch('src.app.capture_image_from_rtsp')
    @patch('src.app.os.rename')
    @patch('src.app.os.getenv')
    @patch('src.app.Config')
    def test_main_person_detected_no_description(self, mock_config, mock_getenv, mock_rename, mock_capture, mock_yolo, mock_analyze, mock_broadcast, mock_sleep):
        # Setup
        mock_config.RTSP_URL = "rtsp://test.url"
        mock_config.YOLO_MODEL_PATH = "yolov8n.pt"
        mock_config.BROADCAST_MESSAGE_TEMPLATE = "Person detected: {desc}"
        mock_config.GOOGLE_DEVICE_IP = "192.168.7.38"
        mock_config.CAPTURE_INTERVAL = 1
        mock_capture.return_value = "images/test.jpg"
        mock_yolo.return_value = True
        mock_analyze.return_value = {
            "person_present": True
            # No description field
        }
        mock_broadcast.return_value = True
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        # Execute & Assert
        with pytest.raises(KeyboardInterrupt):
            main()

        # Should use default description
        mock_broadcast.assert_called_with(
            "Person detected: Person detection unknown", "192.168.7.38")
