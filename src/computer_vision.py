"""
computer_vision.py

This module provides computer vision utilities, including YOLOv8-based person detection.
"""
from ultralytics import YOLO
import threading

# Singleton YOLOv8 model loader


class YOLOv8ModelSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_path='yolov8n.pt'):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.model = YOLO(model_path)
        return cls._instance

    @property
    def model(self):
        return self._instance.model


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
