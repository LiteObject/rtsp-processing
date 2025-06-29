"""
config.py

Centralized configuration management for the RTSP processing system.
Loads and validates environment variables and provides a config object.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration object for the RTSP processing system.
    Loads values from environment variables and provides defaults/validation.
    """
    # RTSP Settings
    RTSP_URL = os.getenv("RTSP_URL")
    CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "10"))

    # Google Hub Settings
    GOOGLE_DEVICE_IP = os.getenv("GOOGLE_DEVICE_IP")
    BROADCAST_VOLUME = float(os.getenv("BROADCAST_VOLUME", "1.0"))

    # LLM Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    # Storage Settings
    IMAGES_DIR = os.getenv("IMAGES_DIR", "images")
    MAX_IMAGES = int(os.getenv("MAX_IMAGES", "100"))
    BROADCAST_MESSAGE_TEMPLATE = os.getenv(
        "BROADCAST_MESSAGE_TEMPLATE", "Person detected: {desc}")
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")

    @classmethod
    def validate(cls):
        """
        Validates that all required configuration values are set.
        Raises a ValueError if any required configuration is missing.
        """
        missing = []
        if not cls.RTSP_URL:
            missing.append("RTSP_URL")
        if not cls.GOOGLE_DEVICE_IP:
            missing.append("GOOGLE_DEVICE_IP")
        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}")
