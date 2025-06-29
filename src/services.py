"""
Service layer for business logic orchestration.
"""
import logging
import os
from typing import Optional

from .config import config
from .computer_vision import person_detected
from .image_analysis import analyze_image, ImageAnalysisResult
from .image_capture import capture_image_from_rtsp
from .google_broadcast import send_message_to_google_hub


class RTSPProcessingService:
    """Main service for RTSP processing workflow."""
    
    def __init__(self):
        config.validate()
        self.logger = logging.getLogger(__name__)
    
    def process_frame(self) -> bool:
        """Process single frame from RTSP stream."""
        try:
            # Capture image
            image_path = capture_image_from_rtsp(config.rtsp_url)
            if not image_path:
                self.logger.warning("Failed to capture image")
                return False
            
            # Quick person detection with YOLOv8
            if not person_detected(image_path):
                self.logger.info("No person detected (YOLOv8)")
                return False
            
            # Detailed analysis with LLM
            result = analyze_image(
                image_path,
                provider=config.default_llm_provider,
                model=config.default_llm_model,
                temperature=config.llm_temperature
            )
            
            if result["person_present"]:
                self._handle_person_detected(image_path, result)
                return True
            else:
                self.logger.info("Person not confirmed by LLM")
                return False
                
        except Exception as e:
            self.logger.exception(f"Error processing frame: {e}")
            return False
    
    def _handle_person_detected(self, image_path: str, result: ImageAnalysisResult):
        """Handle person detection event."""
        # Rename image file
        base, ext = os.path.splitext(image_path)
        detected_path = f"{base}_Detected{ext}"
        os.rename(image_path, detected_path)
        
        # Send broadcast
        description = result.get("description", "Person detection unknown")
        message = f"Person detected: {description}"
        
        success = send_message_to_google_hub(
            message, 
            config.google_device_ip,
            volume=config.broadcast_volume
        )
        
        if success:
            self.logger.info(f"Broadcast sent: {message}")
        else:
            self.logger.error("Failed to send broadcast")