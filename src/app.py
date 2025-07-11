"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
import threading
from logging.handlers import RotatingFileHandler

from .config import Config
from .health_checks import run_health_checks
from .image_capture import capture_frame_from_rtsp
from .services import AsyncRTSPProcessingService

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

    # Check if RTSP URL is configured
    if not service.config.RTSP_URL:
        logging.error("RTSP URL is not configured. Exiting...")
        return

    active_tasks = set()
    max_concurrent_tasks = 5

    try:
        while True:
            # Clean up completed tasks
            active_tasks = {task for task in active_tasks if not task.done()}

            success, frame = capture_frame_from_rtsp(service.config.RTSP_URL)
            if success and frame is not None:
                # Limit concurrent tasks to prevent memory buildup
                if len(active_tasks) < max_concurrent_tasks:
                    task = asyncio.create_task(
                        service.process_frame_async(frame))
                    active_tasks.add(task)
                else:
                    logging.debug(
                        "Max concurrent tasks reached, skipping frame")
                # Explicit frame cleanup
                del frame

            await asyncio.sleep(service.config.CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        # Cancel remaining tasks
        for task in active_tasks:
            if not task.done():
                task.cancel()
        # Wait for cancellation to complete
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
        # Clean up service resources
        service.cleanup()


async def main_async_with_shutdown(shutdown_event: threading.Event) -> None:
    """
    Main async service loop with shutdown event support.
    """
    # Run health checks before starting
    health_results = await run_health_checks()
    if not all(health_results.values()):
        logging.warning("Some health checks failed, but continuing...")

    service = AsyncRTSPProcessingService()
    logging.info("Starting async image capture and analysis system...")

    # Check if RTSP URL is configured
    if not service.config.RTSP_URL:
        logging.error("RTSP URL is not configured. Exiting...")
        return

    active_tasks = set()
    max_concurrent_tasks = 5

    try:
        while not shutdown_event.is_set():
            # Clean up completed tasks
            active_tasks = {task for task in active_tasks if not task.done()}

            success, frame = capture_frame_from_rtsp(service.config.RTSP_URL)
            if success and frame is not None:
                # Limit concurrent tasks to prevent memory buildup
                if len(active_tasks) < max_concurrent_tasks:
                    task = asyncio.create_task(
                        service.process_frame_async(frame))
                    active_tasks.add(task)
                else:
                    logging.debug(
                        "Max concurrent tasks reached, skipping frame")
                # Explicit frame cleanup
                del frame

            await asyncio.sleep(service.config.CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        # Cancel remaining tasks
        for task in active_tasks:
            if not task.done():
                task.cancel()
        # Wait for cancellation to complete
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
        # Clean up service resources
        service.cleanup()
        logging.info("Background processing shutdown complete")


def main() -> None:
    """Main entry point with UI option."""

    parser = argparse.ArgumentParser(description='RTSP Processing System')
    parser.add_argument('--ui', action='store_true',
                        help='Launch with Streamlit GUI only (no background processing)')
    parser.add_argument('--with-ui', action='store_true',
                        help='Launch background processing WITH Streamlit GUI')
    args = parser.parse_args()

    if args.with_ui:
        # Run both background processing and UI
        logging.info("Starting RTSP processing with UI dashboard...")

        # Start background processing in a separate thread (non-daemon for graceful shutdown)
        shutdown_event = threading.Event()

        def run_background():
            try:
                asyncio.run(main_async_with_shutdown(shutdown_event))
            except (KeyboardInterrupt, asyncio.CancelledError):
                logging.info("Background processing interrupted")
            except RuntimeError as e:
                logging.error("Background processing runtime error: %s", e)

        background_thread = threading.Thread(
            target=run_background, daemon=False)
        background_thread.start()

        # Give background service a moment to start
        import time
        time.sleep(2)

        try:
            # Get the root directory (parent of src)
            root_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))

            # Change to root directory and run streamlit with proper module path
            os.chdir(root_dir)
            logging.info("Launching UI dashboard at http://localhost:8501")
            subprocess.run([sys.executable, '-m', 'streamlit',
                           'run', 'src/ui_dashboard.py'], check=False)
        except KeyboardInterrupt:
            logging.info("UI interrupted, shutting down gracefully...")
        finally:
            # Signal background thread to shutdown and wait for it
            logging.info("Signaling background processing to shut down...")
            shutdown_event.set()

            # Ensure graceful shutdown of background thread
            logging.info("Waiting for background processing to complete...")
            if background_thread.is_alive():
                # Give the background thread a reasonable time to finish
                background_thread.join(timeout=10.0)
                if background_thread.is_alive():
                    logging.warning(
                        "Background thread did not shut down within timeout")

    elif args.ui:
        # UI only (original behavior)
        logging.info(
            "Launching UI dashboard only (no background processing)...")

        # Get the root directory (parent of src)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Change to root directory and run streamlit with proper module path
        os.chdir(root_dir)
        subprocess.run([sys.executable, '-m', 'streamlit',
                       'run', 'src/ui_dashboard.py'], check=False)
    else:
        # Background processing only (original behavior)
        asyncio.run(main_async())


if __name__ == "__main__":
    main()
