"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import logging
import os
import time

# Ensure the current directory is in sys.path for local imports
from dotenv import load_dotenv

from src.google_broadcast import send_message_to_google_hub
from src.image_analysis import ImageAnalysisResult, analyze_image, person_detected_yolov8
from src.image_capture import capture_image_from_rtsp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables from .env file
load_dotenv()

GOOGLE_DEVICE_IP = "192.168.7.38"  # Change to your Google Hub IP
BROADCAST_MESSAGE_TEMPLATE = "Person detected: {desc}"


def main(rtsp_url):
    """
    Continuously captures images from the RTSP stream every 10 seconds, analyzes them,
    and broadcasts a message if a human is detected.

    Args:
        rtsp_url (str): The RTSP URL of the camera.

    Returns:
        None
    """
    logging.info("Starting image capture and analysis system...")
    while True:
        try:
            image_path = capture_image_from_rtsp(rtsp_url)
            if image_path and person_detected_yolov8(image_path):
                result: ImageAnalysisResult = analyze_image(
                    image_path, provider="openai", model="gpt-4o-mini")
                if result["person_present"]:
                    # Add _Detected to the image filename
                    base, ext = os.path.splitext(image_path)
                    detected_path = f"{base}_Detected{ext}"
                    os.rename(image_path, detected_path)
                    image_path = detected_path
                    desc = result.get(
                        "description") or "Person detection unknown"
                    message = BROADCAST_MESSAGE_TEMPLATE.format(desc=desc)
                    send_message_to_google_hub(message, GOOGLE_DEVICE_IP)
                else:
                    logging.info("No person detected in the image.")
            else:
                logging.warning("Image capture failed.")
        except (IOError, ValueError) as e:
            logging.exception("Error in main loop: %s", e)
        except RuntimeError as e:
            logging.exception("Runtime error in main loop: %s", e)
        time.sleep(10)


if __name__ == "__main__":
    RTSP_URL = os.getenv("RTSP_URL")
    if not RTSP_URL:
        logging.error("RTSP_URL not set in environment variables.")
        exit(1)
    main(RTSP_URL)
