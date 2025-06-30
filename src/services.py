"""
Service layer for business logic orchestration.
"""
import asyncio
import logging
import os
from typing import Dict, Any

from .config import Config
from .computer_vision import person_detected_yolov8
from .image_analysis import analyze_image_async
from .image_capture import capture_image_from_rtsp
from .google_broadcast import send_message_to_google_hub


class AsyncRTSPProcessingService:
    """Main service for RTSP processing workflow."""

    def __init__(self):
        Config.validate()
        self.logger = logging.getLogger(__name__)
        self.config = Config

    async def process_frame_async(self, image_path: str) -> bool:
        """Process single frame asynchronously."""
        try:
            # Quick person detection with YOLOv8
            if not person_detected_yolov8(image_path, model_path=self.config.YOLO_MODEL_PATH):
                self.logger.info("No person detected (YOLOv8)")
                # Clean up image if no person detected
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                return False

            # Async LLM analysis
            result = await analyze_image_async(
                image_path,
                provider=self.config.DEFAULT_LLM_PROVIDER
            )

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
        else:
            self.logger.error("Failed to send broadcast")
