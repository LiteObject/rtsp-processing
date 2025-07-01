"""
Context managers for proper resource cleanup.
"""
import cv2
import logging
from typing import Optional


class RTSPCapture:
    """Context manager for RTSP video capture with automatic cleanup."""
    
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.cap: Optional[cv2.VideoCapture] = None
    
    def __enter__(self) -> cv2.VideoCapture:
        self.cap = cv2.VideoCapture(self.rtsp_url)
        return self.cap
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()