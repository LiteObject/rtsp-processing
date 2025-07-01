"""
image_capture.py

This module provides functionality to capture a single 
image from an RTSP stream and save it to disk.
"""

import logging
import os
import time

import cv2
from .config import Config
from .context_managers import RTSPCapture
import glob


def capture_image_from_rtsp(rtsp_url: str) -> str | None:
    """
    Captures a single image from the RTSP stream and saves it to the images folder.

    Args:
        rtsp_url (str): The RTSP URL of the camera.

    Returns:
        str: The path of the saved image file, or None if capture failed.
    """
    # Input validation
    if not isinstance(rtsp_url, str) or not rtsp_url.strip():
        logging.error("Invalid RTSP URL provided")
        return None
    
    if not rtsp_url.startswith(('rtsp://', 'http://', 'https://')):
        logging.error("RTSP URL must start with rtsp://, http://, or https://")
        return None
    
    with RTSPCapture(rtsp_url) as cap:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, Config.CV_BUFFER_SIZE)
        # Note: CAP_PROP_TIMEOUT not available in all OpenCV versions
        try:
            cap.set(cv2.CAP_PROP_TIMEOUT, Config.RTSP_TIMEOUT * Config.TIMEOUT_MULTIPLIER)
        except AttributeError:
            pass
        
        if not cap.isOpened():
            logging.error("Could not open RTSP stream: [URL REDACTED]")
            return None

        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame from RTSP stream")
            return None

        os.makedirs(Config.IMAGES_DIR, exist_ok=True)
        image_name = f"capture_{int(time.time())}.jpg"
        saved_image_path = os.path.join(Config.IMAGES_DIR, image_name)
        cv2.imwrite(saved_image_path, frame)
        logging.info("Image saved: %s", os.path.basename(saved_image_path))
        
        # Cleanup old images to prevent disk space issues
        _cleanup_old_images()
        return saved_image_path


def _cleanup_old_images() -> None:
    """Remove old images to prevent disk space issues."""
    try:
        image_files = glob.glob(os.path.join(Config.IMAGES_DIR, "capture_*.jpg"))
        if len(image_files) > Config.MAX_IMAGES:
            # Sort by modification time and remove oldest
            image_files.sort(key=os.path.getmtime)
            for old_file in image_files[:-Config.MAX_IMAGES]:
                os.remove(old_file)
    except OSError:
        pass  # Ignore cleanup errors


def main() -> None:
    """Example usage of capture_image_from_rtsp."""
    rtsp_url = "rtsp://<USERNAME>:<PASSWORD>@192.168.7.25/stream2"
    image_path = capture_image_from_rtsp(rtsp_url)
    if image_path:
        print(f"Image captured and saved as {image_path}")


if __name__ == "__main__":
    main()
