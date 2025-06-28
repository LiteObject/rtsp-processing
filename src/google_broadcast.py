"""
google_broadcast.py

Broadcasts a text-to-speech message to a Google Hub or compatible Chromecast device.
"""

import time
import logging
import urllib.parse
import pychromecast


def send_message_to_google_hub(message, device_ip, volume=1.0):
    """
    Sends a text-to-speech message to a Google Hub (or compatible Chromecast device) 
    at the specified IP address.

    Args:
        message (str): The message to broadcast as speech.
        device_ip (str): The IP address of the target Google device.
        volume (float): Volume level (0.0 to 1.0). Default is 1.0.

    Returns:
        bool: True if message was broadcast, False otherwise.
    """
    # Discover Chromecast devices
    chromecasts, browser = pychromecast.get_chromecasts()

    # Find the specific device by IP address
    target_device = next(
        (cc for cc in chromecasts if cc.cast_info.host == device_ip), None)
    if not target_device:
        logging.error("No Google device found with IP address: %s", device_ip)
        pychromecast.discovery.stop_discovery(browser)
        return False

    try:
        # Connect to the specific Google device
        target_device.wait()
        # Set volume to specified level
        target_device.set_volume(volume)

        class MediaStatusListener:
            """
            Listener for media status updates from the Chromecast device.
            Tracks when the message starts and finishes playing.
            """

            def __init__(self):
                """Initializes the MediaStatusListener."""
                self.message_played = False

            def new_media_status(self, status):
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

        listener = MediaStatusListener()
        target_device.media_controller.register_status_listener(listener)

        # URL encode the message for TTS
        tts_url = (
            "https://translate.google.com/translate_tts?ie=UTF-8&q="
            f"{urllib.parse.quote(message)}&tl=en&client=tw-ob"
        )
        target_device.media_controller.play_media(tts_url, "audio/mp3")
        target_device.media_controller.block_until_active()
        target_device.media_controller.play()

        # Wait for the message to finish playing
        while not listener.message_played:
            time.sleep(1)

        target_device.media_controller.unregister_status_listener(listener)
        return True
    except pychromecast.error.ChromecastConnectionError as e:
        logging.error("Failed to connect to Chromecast device: %s", e)
        return False
    except pychromecast.error.PyChromecastError as e:
        logging.error("Chromecast error occurred: %s", e)
        return False
    except (ValueError, AttributeError, TypeError) as e:
        logging.error("An unexpected error occurred: %s", e)
        return False
    finally:
        # Stop the discovery service
        pychromecast.discovery.stop_discovery(browser)


def main():
    """
    Example usage of send_message_to_google_hub.
    """
    send_message_to_google_hub(
        "Hello friends! How are you?", "192.168.7.38"
    )


if __name__ == "__main__":
    main()
