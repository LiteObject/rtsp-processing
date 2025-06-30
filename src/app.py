"""
app.py

Main application loop for capturing images from an RTSP stream, analyzing them for human presence,
and broadcasting a message to a Google Hub device if a person is detected.
"""

import logging
import time
import threading
from queue import Queue
from src.services import RTSPProcessingService
from src.image_capture import capture_image_from_rtsp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def worker(service: 'RTSPProcessingService', q: Queue) -> None:
    """
    Worker thread function for processing images from the queue.
    Each image path is processed by the RTSPProcessingService.

    Args:
        service (RTSPProcessingService): The service instance to process frames.
        q (Queue): Queue from which image paths are received.
    """
    while True:
        image_path = q.get()
        if image_path is None:
            break
        try:
            service.process_frame(image_path=image_path)
        except (FileNotFoundError, ValueError, RuntimeError, OSError) as e:
            logging.exception("Worker error: %s", e)
        q.task_done()


def main() -> None:
    """
    Main service loop for image capture, analysis, and broadcast using RTSPProcessingService.
    Uses a worker thread for non-blocking frame processing.
    """
    service = RTSPProcessingService()
    q = Queue()
    num_workers = 1  # Increase for more parallelism
    threads = [threading.Thread(target=worker, args=(service, q), daemon=True)
               for _ in range(num_workers)]
    for t in threads:
        t.start()
    logging.info("Starting image capture and analysis system (threaded)...")
    try:
        while True:
            image_path = capture_image_from_rtsp(service.config.RTSP_URL)
            if image_path:
                q.put(image_path)
            time.sleep(service.config.CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        for _ in threads:
            q.put(None)
        for t in threads:
            t.join()


if __name__ == "__main__":
    main()
