import logging
import time
import zeroconf
import pychromecast
from pychromecast.discovery import CastBrowser, SimpleCastListener


class CollectingCastListener(SimpleCastListener):
    def __init__(self):
        super().__init__()
        self.devices = []
        self.seen_services = set()
        self.browser = None  # Will be set by the discover function

    def add_service(self, _zconf, _type_, name):
        logging.debug("add_service called: %s", name)
        self.seen_services.add(name)

    def add_cast(self, uuid, service):
        super().add_cast(uuid, service)
        # Get the cast info from the browser's devices dictionary
        if self.browser and uuid in self.browser.devices:
            cast_info = self.browser.devices[uuid]
            # Create a mock cast object with cast_info

            class MockCast:
                def __init__(self, cast_info):
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
        logging.debug("remove_service called: %s", name)

    def update_service(self, _zconf, _type_, name):
        logging.debug("update_service called: %s", name)


def discover_all_chromecasts():
    """Discover and list all available Chromecast devices on the network."""
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


def broadcast_message_to_device(message, target_device_name=None, target_ip=None):
    """Broadcast a text-to-speech message to a specific Chromecast device."""
    logging.info("Discovering devices to find target for broadcast...")

    # Discover all devices first
    devices = discover_all_chromecasts()

    if not devices:
        logging.error("No Chromecast devices found for broadcasting")
        return False

    # Find the target device
    target_cast = None
    if target_ip:
        # Find by IP address
        target_cast = devices.get(target_ip)
        if target_cast:
            logging.info("Found target device by IP %s: %s",
                         target_ip, target_cast.cast_info.friendly_name)
    elif target_device_name:
        # Find by friendly name
        for cast in devices.values():
            if target_device_name.lower() in cast.cast_info.friendly_name.lower():
                target_cast = cast
                logging.info("Found target device by name '%s': %s (%s)",
                             target_device_name, cast.cast_info.friendly_name, cast.cast_info.host)
                break

    if not target_cast:
        logging.error("Target device not found. Available devices:")
        for cast in devices.values():
            logging.error("  - %s: %s", cast.cast_info.host,
                          cast.cast_info.friendly_name)
        return False

    # Create a new zeroconf instance for the broadcast
    zconf = zeroconf.Zeroconf()

    try:
        # Connect to the Chromecast device with zeroconf instance
        logging.info("Connecting to %s (%s)...",
                     target_cast.cast_info.friendly_name, target_cast.cast_info.host)
        chromecast = pychromecast.Chromecast(
            target_cast.cast_info, zconf=zconf)

        # Wait for the device to be ready
        chromecast.wait()
        logging.info("Connected successfully to %s",
                     target_cast.cast_info.friendly_name)

        # Start the default media receiver app
        mc = chromecast.media_controller

        # Use Text-to-Speech (TTS) to speak the message
        tts_url = f"http://translate.google.com/translate_tts?ie=UTF-8&q={message.replace(' ', '%20')}&tl=en&client=tw-ob"

        logging.info("Broadcasting message: '%s'", message)
        mc.play_media(tts_url, 'audio/mpeg')
        mc.block_until_active()

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


def broadcast_message_direct(message, host, port=8009, friendly_name="Chromecast Device"):
    """Broadcast a text-to-speech message directly to a known Chromecast device."""
    logging.info("Broadcasting directly to %s (%s)...", friendly_name, host)

    # Create a new zeroconf instance for the broadcast
    zconf = zeroconf.Zeroconf()

    try:
        # Create CastInfo for the known device
        from pychromecast.models import CastInfo, HostServiceInfo
        from uuid import uuid4
        import urllib.parse
        import time

        services = {HostServiceInfo(host, port)}
        cast_info = CastInfo(
            services=services,
            uuid=uuid4(),  # Generate a temporary UUID
            model_name="Unknown",
            friendly_name=friendly_name,
            host=host,
            port=port,
            cast_type=None,
            manufacturer=None
        )

        # Connect to the Chromecast device
        logging.info("Connecting to %s (%s:%d)...", friendly_name, host, port)
        chromecast = pychromecast.Chromecast(cast_info, zconf=zconf)

        # Wait for the device to be ready
        chromecast.wait()
        logging.info("Connected successfully to %s", friendly_name)

        # Set volume after connection is established
        chromecast.set_volume(0.7)

        # Start the default media receiver app
        mc = chromecast.media_controller

        # Use better TTS URL
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
            # logging.info("Quitting current app")
            chromecast.quit_app()
        except (AttributeError, ConnectionError):
            pass
        finally:
            zconf.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # Option 1: Discover all devices first (slower but comprehensive)
    # discover_all_chromecasts()
    # success = broadcast_message_to_device(
    #     "Hello World", target_ip="192.168.7.38")

    # Option 2: Direct broadcast to known device (faster)
    success = broadcast_message_direct(
        "Hello World", "192.168.7.38", friendly_name="Kitchen display")

    if success:
        logging.info("Broadcast completed successfully!")
    else:
        logging.error("Broadcast failed!")
