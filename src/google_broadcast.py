"""
google_broadcast.py

Broadcasts a text-to-speech message to a Google Hub or compatible Chromecast device.
"""

import logging
import time
import urllib.parse

import pychromecast

from .config import Config


class MediaStatusListener:
    """
    Listener for media status updates from the Chromecast device.
    Tracks when the message starts and finishes playing.
    """

    def __init__(self) -> None:
        """Initializes the MediaStatusListener."""
        self.message_played = False

    def new_media_status(self, status) -> None:
        """
        Callback for new media status events.

        Args:
            status: The media status object from pychromecast.
        """
        if status.player_state == "PLAYING":
            logging.info("Message is now playing.")
        elif status.player_state == "IDLE":
            logging.info("Message playback has finished.")
            self.message_played = True


def send_message_to_google_hub(message: str, device_ip: str, volume: float = 1.0) -> bool:
    """
    Sends a text-to-speech message to a Google Hub (or compatible Chromecast device) 
    with input validation at the specified IP address.

    Args:
        message (str): The message to broadcast as speech.
        device_ip (str): The IP address of the target Google device.
        volume (float): Volume level (0.0 to 1.0). Default is 1.0.

    Returns:
        bool: True if message was broadcast, False otherwise.
    """

    # Input validation
    if not isinstance(message, str) or not message.strip():
        logging.error("Invalid message provided")
        return False

    if not isinstance(device_ip, str) or not device_ip.strip():
        logging.error("Invalid device IP provided")
        return False

    if not isinstance(volume, (int, float)) or not 0.0 <= volume <= 1.0:
        logging.error("Volume must be between 0.0 and 1.0")
        return False

    for attempt in range(Config.MAX_RETRIES):
        try:
            chromecasts, browser = pychromecast.get_chromecasts(
                timeout=Config.CHROMECAST_TIMEOUT)
            target_device = next(
                (cc for cc in chromecasts if cc.cast_info.host == device_ip), None)
            if not target_device:
                if attempt < Config.MAX_RETRIES - 1:
                    logging.warning("Device not found (attempt %d/%d)",
                                    attempt + 1, Config.MAX_RETRIES)
                    time.sleep(Config.RETRY_DELAY)
                    continue
                logging.error(
                    "No Google device found with IP address: %s", device_ip)
                return False

            target_device.wait(timeout=Config.CHROMECAST_TIMEOUT)
            target_device.set_volume(volume)
            break
        except (ConnectionError, TimeoutError, pychromecast.error.PyChromecastError) as e:
            if attempt < Config.MAX_RETRIES - 1:
                logging.warning(
                    "Chromecast connection failed (attempt %d/%d): %s", attempt + 1, Config.MAX_RETRIES, e)
                time.sleep(Config.RETRY_DELAY * (2 ** attempt))
                continue
            else:
                logging.error(
                    "Failed to connect after %d attempts", Config.MAX_RETRIES)
                return False
        finally:
            try:
                pychromecast.discovery.stop_discovery(browser)
            except (OSError, ValueError):
                pass

    try:

        listener = MediaStatusListener()
        target_device.media_controller.register_status_listener(listener)
        try:
            tts_url = (
                "https://translate.google.com/translate_tts?ie=UTF-8&q="
                f"{urllib.parse.quote(message)}&tl=en&client=tw-ob"
            )
            target_device.media_controller.play_media(tts_url, "audio/mp3")
            target_device.media_controller.block_until_active()
            target_device.media_controller.play()

            while not listener.message_played:
                time.sleep(Config.SLEEP_INTERVAL)
            return True
        finally:
            target_device.media_controller.unregister_status_listener(listener)
    except pychromecast.error.ChromecastConnectionError as e:
        logging.error("Failed to connect to Chromecast device: %s", e)
        return False
    except pychromecast.error.PyChromecastError as e:
        logging.error("Chromecast error occurred: %s", e)
        return False
    except (ValueError, AttributeError, TypeError) as e:
        logging.error("An unexpected error occurred: %s", e)
        return False
    except pychromecast.error.ChromecastConnectionError as e:
        logging.error("Failed to connect to Chromecast device: %s", e)
        return False
    except pychromecast.error.PyChromecastError as e:
        logging.error("Chromecast error occurred: %s", e)
        return False
    except (ValueError, AttributeError, TypeError) as e:
        logging.error("An unexpected error occurred: %s", e)
        return False


def main() -> None:
    """
    Example usage of send_message_to_google_hub.
    """
    send_message_to_google_hub(
        "Hello friend! How are you?", "192.168.7.38"
    )


if __name__ == "__main__":
    main()
