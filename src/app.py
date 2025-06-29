"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import logging
import os
import time

from dotenv import load_dotenv

from src.computer_vision import person_detected_yolov8
# Ensure the current directory is in sys.path for local imports
from src.config import Config
from src.google_broadcast import send_message_to_google_hub
from src.image_analysis import ImageAnalysisResult, analyze_image
from src.image_capture import capture_image_from_rtsp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    """
    Main service loop for image capture, analysis, and broadcast.
    """
    Config.validate()
    logging.info("Starting image capture and analysis system...")
    while True:
        try:
            image_path = capture_image_from_rtsp(Config.RTSP_URL)
            if not image_path:
                logging.warning("Image capture failed (could not save image).")
            elif person_detected_yolov8(image_path, model_path=Config.YOLO_MODEL_PATH):
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
                    message = Config.BROADCAST_MESSAGE_TEMPLATE.format(
                        desc=desc)
                    send_message_to_google_hub(
                        message, Config.GOOGLE_DEVICE_IP)
                else:
                    logging.info(
                        "No person detected in the image (LLM analysis).")
            else:
                logging.info(
                    "No person detected in the image (YOLOv8 pre-filter).")
        except (IOError, ValueError) as e:
            logging.exception("Error in main loop: %s", e)
        except RuntimeError as e:
            logging.exception("Runtime error in main loop: %s", e)
        time.sleep(Config.CAPTURE_INTERVAL)


if __name__ == "__main__":
    main()
