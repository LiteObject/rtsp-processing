"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import asyncio
import logging
import time

from .services import AsyncRTSPProcessingService
from .image_capture import capture_image_from_rtsp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def main_async() -> None:
    """
    Main async service loop for image capture, analysis, and broadcast.
    """
    service = AsyncRTSPProcessingService()
    logging.info("Starting async image capture and analysis system...")
    
    try:
        while True:
            image_path = capture_image_from_rtsp(service.config.RTSP_URL)
            if image_path:
                # Process frame asynchronously without blocking
                asyncio.create_task(service.process_frame_async(image_path))
            await asyncio.sleep(service.config.CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down...")


def main() -> None:
    """Sync wrapper for backward compatibility."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
