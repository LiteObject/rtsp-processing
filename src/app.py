"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import logging
import time
from src.services import RTSPProcessingService

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    """
    Main service loop for image capture, analysis, and broadcast using RTSPProcessingService.
    """
    service = RTSPProcessingService()
    logging.info("Starting image capture and analysis system...")
    while True:
        try:
            service.process_frame()
        except (IOError, ValueError) as e:
            logging.exception("Error in main loop: %s", e)
        except RuntimeError as e:
            logging.exception("Runtime error in main loop: %s", e)
        time.sleep(service.config.CAPTURE_INTERVAL if hasattr(
            service, 'config') and hasattr(service.config, 'CAPTURE_INTERVAL') else 10)


if __name__ == "__main__":
    main()
