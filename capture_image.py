import logging
import os
import time

import cv2


def capture_image_from_rtsp(rtsp_url):
    """
    Captures a single image from the RTSP stream and saves it to the images folder.

    Args:
        rtsp_url (str): The RTSP URL of the camera.

    Returns:
        str: The path of the saved image file, or None if capture failed.
    """
    # Open the RTSP stream
    cap = cv2.VideoCapture(rtsp_url)

    # Check if the stream was opened successfully
    if not cap.isOpened():
        logging.error("Could not open RTSP stream: %s", rtsp_url)
        return None

    # Read a frame from the stream
    ret, frame = cap.read()

    if not ret:
        logging.error("Failed to capture frame from RTSP stream: %s", rtsp_url)
        cap.release()
        return None

    # Save the frame as an image in the images folder
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    image_name = f"capture_{int(time.time())}.jpg"
    image_path = os.path.join(images_dir, image_name)
    cv2.imwrite(image_path, frame)
    print(f"Saved {image_path}")

    # Release the stream and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    return image_path


# Example usage
if __name__ == "__main__":
    RTSP_URL = "rtsp://mvxfamily:P_9Pup3U!KY5-fc@192.168.7.254/stream2"
    image_path = capture_image_from_rtsp(RTSP_URL)
    if image_path:
        print(f"Image captured and saved as {image_path}")
