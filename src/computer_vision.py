"""
computer_vision.py

This module provides computer vision utilities, including YOLOv8-based person detection.
"""
import threading

from ultralytics import YOLO

# Singleton YOLOv8 model loader


class YOLOv8ModelSingleton:
    """
    Singleton class for loading and providing access to a YOLOv8 model instance.
    Ensures that the model is loaded only once per process, even in multithreaded environments.
    """
    _instances = {}
    _lock = threading.Lock()

    def __init__(self, model_path='yolov8n.pt'):
        if not hasattr(self, '_model'):
            self._model = YOLO(model_path)

    def __new__(cls, model_path='yolov8n.pt'):
        """
        Create or return the singleton instance of the YOLOv8 model.

        Args:
            model_path (str): Path to the YOLOv8 model weights file.

        Returns:
            YOLOv8ModelSingleton: The singleton instance containing the loaded model.
        """
        if model_path not in cls._instances:
            with cls._lock:
                if model_path not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[model_path] = instance
        return cls._instances[model_path]

    @property
    def model(self):
        """
        Returns the loaded YOLOv8 model instance.

        Returns:
            YOLO: The loaded YOLOv8 model.
        """
        return self._model


def person_detected_yolov8_frame(frame, model_path='yolov8n.pt') -> bool:
    """
    Detects whether a person is present in the given cv2 frame using YOLOv8.

    Args:
        frame: cv2 image array.
        model_path (str): Path to the YOLOv8 model weights file.

    Returns:
        bool: True if a person is detected in the frame, False otherwise.
    """
    model = YOLOv8ModelSingleton(model_path).model
    results = model(frame)
    for _result in results:
        for box in _result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            if class_name == 'person':
                return True
    return False


def person_detected_yolov8(image_path, model_path='yolov8n.pt') -> bool:
    """
    Detects whether a person is present in the given image using YOLOv8.

    Args:
        image_path (str): Path to the image file to analyze.
        model_path (str): Path to the YOLOv8 model weights file.

    Returns:
        bool: True if a person is detected in the image, False otherwise.
    """
    model = YOLOv8ModelSingleton(model_path).model
    results = model(image_path)
    for _result in results:
        for box in _result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            if class_name == 'person':
                return True
    return False
