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
    
    # Timeout and Retry Settings
    RTSP_TIMEOUT = int(os.getenv("RTSP_TIMEOUT", "10"))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
    CHROMECAST_TIMEOUT = int(os.getenv("CHROMECAST_TIMEOUT", "15"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # Magic Numbers
    CV_BUFFER_SIZE = 1
    SLEEP_INTERVAL = 1
    TIMEOUT_MULTIPLIER = 1000
    
    # Security Settings
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    # Directory Settings
    IMAGES_DIR = os.getenv("IMAGES_DIR", "images")

    @classmethod
    def validate(cls):
        """
        Validates that all required configuration values are set.
        Raises a ValueError if any required configuration is missing.
        """
        errors = []
        
        # Required fields
        if not cls.RTSP_URL:
            errors.append("RTSP_URL is required")
        elif not cls.RTSP_URL.startswith(('rtsp://', 'http://', 'https://')):
            errors.append("RTSP_URL must be a valid URL")
            
        if not cls.GOOGLE_DEVICE_IP:
            errors.append("GOOGLE_DEVICE_IP is required")
            
        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required for OpenAI provider")
            
        # Numeric range validation
        if not 0.0 <= cls.BROADCAST_VOLUME <= 1.0:
            errors.append("BROADCAST_VOLUME must be between 0.0 and 1.0")
            
        if not 0.0 <= cls.LLM_TEMPERATURE <= 2.0:
            errors.append("LLM_TEMPERATURE must be between 0.0 and 2.0")
            
        if cls.CAPTURE_INTERVAL <= 0:
            errors.append("CAPTURE_INTERVAL must be positive")
            
        if cls.MAX_IMAGES <= 0:
            errors.append("MAX_IMAGES must be positive")
            
        # File path validation
        if not os.path.exists(cls.YOLO_MODEL_PATH):
            errors.append(f"YOLO model file not found: {cls.YOLO_MODEL_PATH}")
            
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
