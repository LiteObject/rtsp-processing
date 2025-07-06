"""
Service layer for business logic orchestration.
"""
import cv2
import logging
import os
import time
from typing import Dict, Any

from .config import Config
from .computer_vision import person_detected_yolov8_frame
from .image_analysis import analyze_image_async
from .notification_dispatcher import NotificationDispatcher, NotificationTarget
from .event_broadcaster import broadcaster


class AsyncRTSPProcessingService:
    """Main service for RTSP processing workflow."""

    def __init__(self):
        Config.validate()
        self.logger = logging.getLogger(__name__)
        self.config = Config
        
        # Initialize notification dispatcher
        target_map = {
            "local_speaker": NotificationTarget.LOCAL_SPEAKER,
            "google_hub": NotificationTarget.GOOGLE_HUB,
            "both": NotificationTarget.BOTH
        }
        self.notification_target = target_map.get(self.config.NOTIFICATION_TARGET, NotificationTarget.BOTH)
        self.dispatcher = NotificationDispatcher(
            google_device_ip=self.config.GOOGLE_DEVICE_IP,
            google_device_name=self.config.GOOGLE_DEVICE_NAME
        )

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
                broadcaster.emit('detection', {'status': 'no_person', 'method': 'YOLO'})
                return False

            # Save frame to disk only when person detected
            os.makedirs(self.config.IMAGES_DIR, exist_ok=True)
            image_name = f"capture_{int(time.time())}.jpg"
            image_path = os.path.join(self.config.IMAGES_DIR, image_name)
            cv2.imwrite(image_path, frame)
            logging.info("Image saved: %s", os.path.basename(image_path))
            broadcaster.emit('image', {'path': image_path, 'status': 'saved'})

            # Async LLM analysis
            logging.debug("Starting LLM analysis for: %s",
                          os.path.basename(image_path))
            result = await analyze_image_async(
                image_path,
                provider=self.config.DEFAULT_LLM_PROVIDER
            )
            logging.debug("LLM analysis result: %s", result)

            if result["person_present"]:
                broadcaster.emit('detection', {
                    'status': 'person_confirmed', 
                    'description': result.get('description', 'Unknown')
                })
                await self._handle_person_detected_async(image_path, result)
                return True
            else:
                self.logger.info("Person not confirmed by LLM")
                broadcaster.emit('detection', {'status': 'person_not_confirmed', 'method': 'LLM'})
                # Clean up image if no person confirmed
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                return False

        except (OSError, IOError, ValueError, RuntimeError) as e:
            self.logger.exception("Error processing frame: %s", e)
            return False

    async def _handle_person_detected_async(self, image_path: str, result: Dict[str, Any]) -> None:
        """Handle person detection event."""
        # Rename image file
        base, ext = os.path.splitext(image_path)
        detected_path = f"{base}_Detected{ext}"
        os.rename(image_path, detected_path)

        # Send notification
        description = result.get("description", "Person detection unknown")
        message = self.config.BROADCAST_MESSAGE_TEMPLATE.format(
            desc=description)

        success = self.dispatcher.dispatch(message, self.notification_target)
        
        broadcaster.emit('notification', {
            'success': success,
            'message': message,
            'target': str(self.notification_target)
        })

        if success:
            self.logger.info("Notification sent: %s", message)
        else:
            self.logger.error("Failed to send notification")
