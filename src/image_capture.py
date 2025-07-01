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


def capture_frame_from_rtsp(rtsp_url: str) -> tuple[bool, any]:
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
        return False, None

    if not rtsp_url.startswith(('rtsp://', 'http://', 'https://')):
        logging.error("RTSP URL must start with rtsp://, http://, or https://")
        return False, None

    with RTSPCapture(rtsp_url) as cap:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, Config.CV_BUFFER_SIZE)
        # Note: CAP_PROP_TIMEOUT not available in all OpenCV versions
        try:
            cap.set(cv2.CAP_PROP_TIMEOUT, Config.RTSP_TIMEOUT *
                    Config.TIMEOUT_MULTIPLIER)
        except AttributeError:
            pass

        if not cap.isOpened():
            logging.error("Could not open RTSP stream: [URL REDACTED]")
            return False, None

        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame from RTSP stream")
            return False, None

        return True, frame


def _cleanup_old_images() -> None:
    """Remove old images to prevent disk space issues."""
    try:
        image_files = glob.glob(os.path.join(
            Config.IMAGES_DIR, "capture_*.jpg"))
        logging.debug("Found %d image files", len(image_files))
        if len(image_files) > Config.MAX_IMAGES:
            # Sort by modification time and remove oldest
            image_files.sort(key=os.path.getmtime)
            files_to_remove = image_files[:-Config.MAX_IMAGES]
            logging.debug("Removing %d old image files", len(files_to_remove))
            for old_file in files_to_remove:
                os.remove(old_file)
                logging.debug("Removed: %s", os.path.basename(old_file))
    except OSError as e:
        logging.warning("Image cleanup failed: %s", e)


def main() -> None:
    """Example usage of capture_image_from_rtsp."""
    rtsp_url = "rtsp://<USERNAME>:<PASSWORD>@192.168.7.25/stream2"
    image_path = capture_image_from_rtsp(rtsp_url)
    if success and frame is not None:
        logging.info("Frame captured successfully: %dx%d", frame.shape[1], frame.shape[0])


if __name__ == "__main__":
    main()
