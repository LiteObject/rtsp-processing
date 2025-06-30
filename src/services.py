"""
Service layer for business logic orchestration.
"""
import logging
import os

from .config import Config
from .computer_vision import person_detected_yolov8
from .image_analysis import analyze_image, ImageAnalysisResult
from .image_capture import capture_image_from_rtsp
from .google_broadcast import send_message_to_google_hub


class RTSPProcessingService:
    """Main service for RTSP processing workflow."""

    def __init__(self):
        Config.validate()
        self.logger = logging.getLogger(__name__)
        self.config = Config

    def process_frame(self) -> bool:
        """Process single frame from RTSP stream."""
        try:
            # Capture image
            image_path = capture_image_from_rtsp(self.config.RTSP_URL)
            if not image_path:
                self.logger.warning("Failed to capture image")
                return False

            # Quick person detection with YOLOv8
            if not person_detected_yolov8(image_path, model_path=self.config.YOLO_MODEL_PATH):
                self.logger.info("No person detected (YOLOv8)")
                return False

            # Detailed analysis with LLM
            result = analyze_image(
                image_path,
                provider=self.config.DEFAULT_LLM_PROVIDER,
                model=self.config.DEFAULT_LLM_MODEL,
                temperature=self.config.LLM_TEMPERATURE
            )

            if result["person_present"]:
                self._handle_person_detected(image_path, result)
                return True
            else:
                self.logger.info("Person not confirmed by LLM")
                return False

        except (OSError, ValueError) as e:
            self.logger.exception("Error processing frame: %s", e)
            return False

    def _handle_person_detected(self, image_path: str, result: ImageAnalysisResult):
        """Handle person detection event."""
        # Rename image file
        base, ext = os.path.splitext(image_path)
        detected_path = f"{base}_Detected{ext}"
        os.rename(image_path, detected_path)

        # Send broadcast
        description = result.get("description", "Person detection unknown")
        message = self.config.BROADCAST_MESSAGE_TEMPLATE.format(
            desc=description)

        success = send_message_to_google_hub(
            message,
            self.config.GOOGLE_DEVICE_IP,
            volume=self.config.BROADCAST_VOLUME
        )

        if success:
            self.logger.info("Broadcast sent: %s", message)
        else:
            self.logger.error("Failed to send broadcast")
