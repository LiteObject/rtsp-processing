"""
Health checks for external dependencies.
"""
import asyncio
import logging
import cv2
import aiohttp
from typing import Dict

from .config import Config


async def check_openai_api() -> bool:
    """Check if OpenAI API is accessible."""
    if not Config.OPENAI_API_KEY:
        logging.warning("OpenAI API key not configured")
        return False
    
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        headers = {"Authorization": f"Bearer {Config.OPENAI_API_KEY}"}
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://api.openai.com/v1/models", headers=headers) as response:
                return response.status == 200
    except Exception as e:
        logging.error("OpenAI API health check failed: %s", e)
        return False


def check_rtsp_stream() -> bool:
    """Check if RTSP stream is accessible."""
    if not Config.RTSP_URL:
        logging.warning("RTSP URL not configured")
        return False
    
    try:
        cap = cv2.VideoCapture(Config.RTSP_URL)
        is_opened = cap.isOpened()
        cap.release()
        return is_opened
    except Exception as e:
        logging.error("RTSP stream health check failed: %s", e)
        return False


def check_chromecast_device() -> bool:
    """Check if Chromecast device is reachable."""
    if not Config.GOOGLE_DEVICE_IP:
        logging.warning("Google device IP not configured")
        return False
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((Config.GOOGLE_DEVICE_IP, 8009))  # Chromecast port
        sock.close()
        return result == 0
    except Exception as e:
        logging.error("Chromecast health check failed: %s", e)
        return False


async def run_health_checks() -> Dict[str, bool]:
    """Run all health checks and return results."""
    logging.info("Running health checks...")
    
    results = {
        "rtsp_stream": check_rtsp_stream(),
        "openai_api": await check_openai_api(),
        "chromecast_device": check_chromecast_device()
    }
    
    for service, status in results.items():
        if status:
            logging.info("✓ %s: healthy", service)
        else:
            logging.warning("✗ %s: unhealthy", service)
    
    return results