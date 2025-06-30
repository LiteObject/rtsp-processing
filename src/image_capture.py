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


def capture_image_from_rtsp(rtsp_url: str) -> str | None:
    """
    Captures a single image from the RTSP stream and saves it to the images folder.

    Args:
        rtsp_url (str): The RTSP URL of the camera.

    Returns:
        str: The path of the saved image file, or None if capture failed.
    """
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, Config.CV_BUFFER_SIZE)
    cap.set(cv2.CAP_PROP_TIMEOUT, Config.RTSP_TIMEOUT * Config.TIMEOUT_MULTIPLIER)
    try:
        if not cap.isOpened():
            logging.error("Could not open RTSP stream: [URL REDACTED]")
            return None

        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame from RTSP stream")
            return None

        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)
        image_name = f"capture_{int(time.time())}.jpg"
        saved_image_path = os.path.join(images_dir, image_name)
        cv2.imwrite(saved_image_path, frame)
        print(f"Saved {saved_image_path}")
        return saved_image_path
    finally:
        cap.release()
        cv2.destroyAllWindows()


def main() -> None:
    """Example usage of capture_image_from_rtsp."""
    rtsp_url = "rtsp://<USERNAME>:<PASSWORD>@192.168.7.25/stream2"
    image_path = capture_image_from_rtsp(rtsp_url)
    if image_path:
        print(f"Image captured and saved as {image_path}")


if __name__ == "__main__":
    main()
