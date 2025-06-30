"""
google_devices.py

Utility to discover Google Chromecast and compatible devices on the local network.
"""

import logging

import pychromecast


def discover_google_devices() -> list[dict]:
    """
    Discovers Google Chromecast and compatible devices on the local 
    network and returns their details.

    Returns:
        list: List of device dictionaries with name, ip, model, and uuid
    """
    logging.info("Searching for Google devices on the network...")
    chromecasts, browser = pychromecast.get_chromecasts()
    devices = []
    
    if not chromecasts:
        logging.info("No Google devices found.")
    else:
        for device in chromecasts:
            device_info = {
                "name": device.cast_info.friendly_name,
                "ip": device.cast_info.host,
                "model": device.model_name,
                "uuid": device.uuid
            }
            devices.append(device_info)
            logging.info("Device Name: %s", device_info["name"])
            logging.info("IP Address: %s", device_info["ip"])
            logging.info("Model: %s", device_info["model"])
            logging.info("UUID: %s", device_info["uuid"])
            logging.info("%s", "-" * 40)
    
    pychromecast.discovery.stop_discovery(browser)
    return devices


def main() -> None:
    """
    Example usage of discover_google_devices.
    """
    discover_google_devices()


if __name__ == "__main__":
    main()
