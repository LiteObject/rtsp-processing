"""
google_devices.py

Utility to discover Google Chromecast and compatible devices on the local network.
"""

import logging

import pychromecast


def discover_google_devices():
    """
    Discovers Google Chromecast and compatible devices on the local 
    network and prints their details.

    Returns:
        None
    """
    logging.info("Searching for Google devices on the network...")
    chromecasts, browser = pychromecast.get_chromecasts()
    if not chromecasts:
        logging.info("No Google devices found.")
    else:
        for device in chromecasts:
            logging.info("Device Name: %s", device.name)
            logging.info("IP Address: %s", device.cast_info.host)
            logging.info("Model: %s", device.model_name)
            logging.info("UUID: %s", device.uuid)
            logging.info("%s", "-" * 40)
    pychromecast.discovery.stop_discovery(browser)


def main():
    """
    Example usage of discover_google_devices.
    """
    discover_google_devices()


if __name__ == "__main__":
    main()
