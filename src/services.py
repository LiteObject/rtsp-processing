"""
Service layer for business logic orchestration.
"""
import asyncio
import logging
import os
from typing import Dict, Any

from .config import Config
from .computer_vision import person_detected_yolov8_frame
from .image_analysis import analyze_image_async
from .image_capture import capture_frame_from_rtsp
from .google_broadcast import send_message_to_google_hub


class AsyncRTSPProcessingService:
    """Main service for RTSP processing workflow."""

    def __init__(self):
        Config.validate()
        self.logger = logging.getLogger(__name__)
        self.config = Config

    async def process_frame_async(self, frame) -> bool:
        """Process single frame asynchronously."""
        # Input validation
        if frame is None:
            self.logger.error("Invalid frame provided")
            return False
        
        try:
            # Quick person detection with YOLOv8
            if not person_detected_yolov8_frame(frame, model_path=self.config.YOLO_MODEL_PATH):
                self.logger.info("No person detected (YOLOv8)")
                return False
            
            # Save frame to disk only when person detected
            import time
            import cv2
            os.makedirs(self.config.IMAGES_DIR, exist_ok=True)
            image_name = f"capture_{int(time.time())}.jpg"
            image_path = os.path.join(self.config.IMAGES_DIR, image_name)
            cv2.imwrite(image_path, frame)
            logging.info("Image saved: %s", os.path.basename(image_path))

            # Async LLM analysis
            logging.debug("Starting LLM analysis for: %s", os.path.basename(image_path))
            result = await analyze_image_async(
                image_path,
                provider=self.config.DEFAULT_LLM_PROVIDER
            )
            logging.debug("LLM analysis result: %s", result)

            if result["person_present"]:
                await self._handle_person_detected_async(image_path, result)
                return True
            else:
                self.logger.info("Person not confirmed by LLM")
                # Clean up image if no person confirmed
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                return False

        except Exception as e:
            self.logger.exception("Error processing frame: %s", e)
            return False

    async def _handle_person_detected_async(self, image_path: str, result: Dict[str, Any]) -> None:
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
            self.logger.debug("Broadcast sent to device: %s", self.config.GOOGLE_DEVICE_IP)
        else:
            self.logger.error("Failed to send broadcast")
            self.logger.debug("Broadcast failed for device: %s", self.config.GOOGLE_DEVICE_IP)
