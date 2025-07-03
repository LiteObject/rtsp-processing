"""
google_broadcast.py

Broadcasts a text-to-speech message to a Google Hub or compatible Chromecast device.
"""

import logging
import time
import urllib.parse
from uuid import uuid4

import pychromecast
import zeroconf
from pychromecast.discovery import CastBrowser, SimpleCastListener
from pychromecast.models import CastInfo, HostServiceInfo


class CollectingCastListener(SimpleCastListener):
    """
    Custom listener for collecting Chromecast devices during discovery.

    Extends SimpleCastListener to track discovered devices and provide
    access to device information through the browser's device registry.
    """

    def __init__(self):
        """Initialize the listener with empty device list and service tracking."""
        super().__init__()
        self.devices = []
        self.seen_services = set()
        self.browser = None  # Will be set by the discover function

    def add_service(self, _zconf, _type_, name):
        """
        Called when a new mDNS service is discovered.

        Args:
            _zconf: Zeroconf instance (unused)
            _type_: Service type (unused) 
            name (str): Service name
        """
        logging.debug("add_service called: %s", name)
        self.seen_services.add(name)

    def add_cast(self, uuid, service):
        """
        Called when a new Chromecast device is discovered and resolved.

        Creates a MockCast object for the discovered device and adds it
        to the devices list if not already present.

        Args:
            uuid (str): Unique identifier for the device
            service: Service information (unused)
        """
        super().add_cast(uuid, service)
        # Get the cast info from the browser's devices dictionary
        if self.browser and uuid in self.browser.devices:
            cast_info = self.browser.devices[uuid]
            # Create a mock cast object with cast_info

            class MockCast:
                """
                Mock Chromecast object that holds cast_info and uuid.

                Provides a lightweight representation of a discovered device
                without establishing a full connection.
                """

                def __init__(self, cast_info):
                    """
                    Initialize mock cast with device information.

                    Args:
                        cast_info: CastInfo object containing device details
                    """
                    self.cast_info = cast_info
                    self.uuid = uuid

            cast = MockCast(cast_info)
            if cast not in self.devices:
                logging.debug("Device resolved and added: %s (%s)",
                              cast_info.friendly_name, cast_info.host)
                self.devices.append(cast)
        else:
            logging.debug(
                "add_cast called but cast not found in browser.devices for uuid: %s, service: %s", uuid, service)

    def remove_service(self, _zconf, _type_, name):
        """
        Called when an mDNS service is removed from the network.

        Args:
            _zconf: Zeroconf instance (unused)
            _type_: Service type (unused)
            name (str): Service name
        """
        logging.debug("remove_service called: %s", name)

    def update_service(self, _zconf, _type_, name):
        """
        Called when an mDNS service is updated.

        Args:
            _zconf: Zeroconf instance (unused)
            _type_: Service type (unused)
            name (str): Service name
        """
        logging.debug("update_service called: %s", name)


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


def discover_all_chromecasts():
    """
    Discover and list all available Chromecast devices on the network.

    Uses CastBrowser with a custom listener to discover Google Cast devices.
    Waits 15 seconds for comprehensive device discovery, which is optimized
    for Windows environments where mDNS discovery can be slower.

    Returns:
        dict: Dictionary mapping device IP addresses to MockCast objects.
              Format: {ip_address: MockCast_object}

    Note:
        If no devices are found, provides troubleshooting tips for common
        network configuration issues, especially on Windows systems.
    """
    logging.info("Starting device discovery with CastBrowser...")

    listener = CollectingCastListener()
    zconf = zeroconf.Zeroconf()
    browser = CastBrowser(listener, zconf)

    # Set the browser reference so the listener can access devices
    listener.browser = browser

    try:
        browser.start_discovery()
        # Increase timeout for more robust discovery, especially on Windows
        discovery_timeout = 15
        logging.info("Waiting %d seconds for device discovery...",
                     discovery_timeout)
        time.sleep(discovery_timeout)
    finally:
        browser.stop_discovery()
        zconf.close()

    chromecasts = listener.devices

    if chromecasts:
        logging.info("Found %d device(s):", len(chromecasts))
        for cast in chromecasts:
            logging.info("  - %s: %s (%s)",
                         cast.cast_info.host,
                         cast.cast_info.friendly_name,
                         cast.cast_info.model_name)
    else:
        logging.warning("No Chromecast devices found on the network.\n"
                        "Troubleshooting tips:\n"
                        "- Ensure your computer and Google devices are on the same WiFi network.\n"
                        "- Disable VPNs and check firewall settings.\n"
                        "- On Windows, mDNS/zeroconf may be blocked by network configuration.\n"
                        "- Try running as administrator or on a different OS if possible.\n"
                        "- Use 'python -m pip show pychromecast zeroconf' to verify package versions.")

    return {cast.cast_info.host: cast for cast in chromecasts}


def send_message_to_google_hub(message: str, device_ip: str, volume: float = 1.0, port: int = 8009, friendly_name: str = "Google Hub Device") -> bool:
    """
    Sends a text-to-speech message directly to a Google Hub or compatible Chromecast device.
    Uses direct connection approach for better reliability.

    Args:
        message (str): The message to broadcast as speech.
        device_ip (str): The IP address of the target Google device.
        volume (float): Volume level (0.0 to 1.0). Default is 1.0.
        port (int): Port number for the Chromecast device. Default is 8009.
        friendly_name (str): Friendly name for the device (for logging). Default is "Google Hub Device".

    Returns:
        bool: True if message was broadcast successfully, False otherwise.
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

    logging.info("Broadcasting directly to %s (%s)...",
                 friendly_name, device_ip)

    # Create a new zeroconf instance for the broadcast
    zconf = zeroconf.Zeroconf()

    try:
        # Create CastInfo for the known device
        services = {HostServiceInfo(device_ip, port)}
        cast_info = CastInfo(
            services=services,
            uuid=uuid4(),  # Generate a temporary UUID
            model_name="Unknown",
            friendly_name=friendly_name,
            host=device_ip,
            port=port,
            cast_type=None,
            manufacturer=None
        )

        # Connect to the Chromecast device
        logging.info("Connecting to %s (%s:%d)...",
                     friendly_name, device_ip, port)
        chromecast = pychromecast.Chromecast(cast_info, zconf=zconf)

        # Wait for the device to be ready
        chromecast.wait()
        logging.info("Connected successfully to %s", friendly_name)

        # Set volume after connection is established
        chromecast.set_volume(volume)

        # Start the default media receiver app
        mc = chromecast.media_controller

        # Use better TTS URL with improved parameters
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(message)}&tl=en&client=tw-ob&ttsspeed=0.24&total=1&idx=0"

        logging.info("Broadcasting message: '%s'", message)
        mc.play_media(tts_url, 'audio/mpeg')
        mc.block_until_active()

        # Wait for playback to complete
        time.sleep(3)
        timeout = 30
        start_time = time.time()
        while mc.status.player_state in ['BUFFERING', 'PLAYING'] and (time.time() - start_time) < timeout:
            time.sleep(0.5)

        logging.info("Message broadcast successfully!")
        return True

    except (ConnectionError, OSError, pychromecast.error.ChromecastConnectionError) as e:
        logging.error("Failed to broadcast message: %s", e)
        return False
    finally:
        try:
            chromecast.quit_app()
        except (AttributeError, ConnectionError):
            pass
        finally:
            zconf.close()


def main() -> None:
    """
    Example usage and testing of google_broadcast functionality.

    Demonstrates how to:
    1. Discover all available Chromecast devices on the network
    2. Send a text-to-speech message to a specific device by IP address

    This function serves as both documentation and a testing entry point
    for the module's core functionality.
    """
    # Setup logging to see debug messages
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # First, discover all available devices (optional)
    discover_all_chromecasts()

    # Then try to send message using direct broadcast
    success = send_message_to_google_hub(
        "Hello World", "192.168.7.38", friendly_name="Kitchen display"
    )

    if success:
        logging.info("Broadcast completed successfully!")
    else:
        logging.error("Broadcast failed!")


if __name__ == "__main__":
    main()
