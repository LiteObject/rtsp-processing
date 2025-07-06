"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

from logging.handlers import RotatingFileHandler
import asyncio
import logging
import os

from .config import Config
from .services import AsyncRTSPProcessingService
from .image_capture import capture_frame_from_rtsp
from .health_checks import run_health_checks

# Ensure logs directory exists first
os.makedirs(Config.LOG_DIR, exist_ok=True)

# Configure logging with rolling file handler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        RotatingFileHandler(
            os.path.join(Config.LOG_DIR, 'rtsp_processing.log'),
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
    ]
)


async def main_async() -> None:
    """
    Main async service loop for image capture, analysis, and broadcast.
    """
    # Run health checks before starting
    health_results = await run_health_checks()
    if not all(health_results.values()):
        logging.warning("Some health checks failed, but continuing...")

    service = AsyncRTSPProcessingService()
    logging.info("Starting async image capture and analysis system...")

    try:
        while True:
            success, frame = capture_frame_from_rtsp(service.config.RTSP_URL)
            if success and frame is not None:
                # Process frame asynchronously without blocking
                asyncio.create_task(service.process_frame_async(frame))
            await asyncio.sleep(service.config.CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down...")


def main() -> None:
    """Main entry point with UI option."""
    import argparse
    parser = argparse.ArgumentParser(description='RTSP Processing System')
    parser.add_argument('--ui', action='store_true',
                        help='Launch with Streamlit GUI')
    args = parser.parse_args()

    if args.ui:
        import subprocess
        import sys
        import os

        # Get the root directory (parent of src)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Change to root directory and run streamlit with proper module path
        os.chdir(root_dir)
        subprocess.run([sys.executable, '-m', 'streamlit',
                       'run', 'src/ui_dashboard.py'])
    else:
        asyncio.run(main_async())


if __name__ == "__main__":
    main()
