"""
notification_dispatcher.py

Cross-platform notification dispatcher for local speakers and Google Hub devices.
"""

import logging
import platform
from abc import ABC, abstractmethod
from enum import Enum


class NotificationTarget(Enum):
    """Enumeration of possible notification targets."""
    LOCAL_SPEAKER = "local_speaker"
    GOOGLE_HUB = "google_hub"
    BOTH = "both"


class NotificationProvider(ABC):
    """Abstract base class for notification providers."""
    @abstractmethod
    def send_notification(self, message: str) -> bool:
        """Send a notification with the given message.
        Args:
            message (str): The message to send.
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        pass


class LocalSpeakerProvider(NotificationProvider):
    """Cross-platform local speaker TTS provider."""

    def __init__(self):
        """Initialize the local speaker provider and TTS engine."""
        self.engine = None
        self._init_tts_engine()

    def _init_tts_engine(self):
        """Initialize the appropriate TTS engine for the current platform."""
        try:
            if platform.system() == "Windows":
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
                logging.info("Initialized Windows TTS engine")
            elif platform.system() == "Darwin":  # macOS
                import pyttsx3
                self.engine = pyttsx3.init()
                logging.info("Initialized macOS TTS engine")
            else:  # Linux
                import pyttsx3
                self.engine = pyttsx3.init()
                logging.info("Initialized Linux TTS engine")
        except ImportError:
            logging.error(
                "pyttsx3 not available, falling back to system commands")
            self.engine = None

    def send_notification(self, message: str) -> bool:
        """Send TTS notification to local speakers.
        Args:
            message (str): The message to speak.
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        try:
            if self.engine:
                self.engine.say(message)
                self.engine.runAndWait()
                logging.info("Local TTS notification sent: %s", message)
                return True
            else:
                # Fallback to system commands
                return self._fallback_tts(message)
        except (RuntimeError, AttributeError, ImportError) as e:
            logging.error("Failed to send local notification: %s", e)
            return False

    def _fallback_tts(self, message: str) -> bool:
        """Fallback TTS using system commands.
        Args:
            message (str): The message to speak.
        Returns:
            bool: True if the fallback notification was sent successfully, False otherwise.
        """
        import subprocess
        try:
            system = platform.system()
            if system == "Windows":
                # PowerShell TTS
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{message}\')"'
                subprocess.run(cmd, shell=True, check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["say", message], check=True)
            else:  # Linux
                subprocess.run(["espeak", message], check=True)

            logging.info("Fallback TTS notification sent: %s", message)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logging.error("Fallback TTS failed: %s", e)
            return False


class GoogleHubProvider(NotificationProvider):
    """Google Hub/Chromecast TTS provider."""

    def __init__(self, device_ip: str, friendly_name: str = "Google Device"):
        """Initialize the Google Hub provider.
        Args:
            device_ip (str): The IP address of the Google Hub device.
            friendly_name (str): The friendly name of the device.
        """
        self.device_ip = device_ip
        self.friendly_name = friendly_name

    def send_notification(self, message: str) -> bool:
        """Send TTS notification to Google Hub.
        Args:
            message (str): The message to broadcast.
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        try:
            from .google_broadcast import send_message_to_google_hub
            success = send_message_to_google_hub(
                message, self.device_ip, friendly_name=self.friendly_name)
            if success:
                logging.info("Google Hub notification sent: %s", message)
            return success
        except ImportError as e:
            logging.error("Failed to import google_broadcast: %s", e)
            return False
        except AttributeError as e:
            logging.error(
                "broadcast_message_direct not found or failed: %s", e)
            return False
        except Exception as e:
            logging.error("Unexpected error in Google Hub notification: %s", e)
            return False


class NotificationDispatcher:
    """Main notification dispatcher that routes messages to configured targets."""

    def __init__(self, google_device_ip: str = None, google_device_name: str = "Google Device"):
        """Initialize the notification dispatcher and configure providers.
        Args:
            google_device_ip (str, optional): The IP address of the Google Hub device.
            google_device_name (str, optional): The friendly name of the Google Hub device.
        """
        self.providers = {
            NotificationTarget.LOCAL_SPEAKER: LocalSpeakerProvider()
        }

        if google_device_ip:
            self.providers[NotificationTarget.GOOGLE_HUB] = GoogleHubProvider(
                google_device_ip, google_device_name
            )

    def dispatch(self, message: str, targets: NotificationTarget = NotificationTarget.LOCAL_SPEAKER) -> bool:
        """Dispatch notification to specified targets.
        Args:
            message (str): The message to send.
            targets (NotificationTarget): The target(s) to send the notification to.
        Returns:
            bool: True if all notifications were sent successfully, False otherwise.
        """
        if not message.strip():
            logging.error("Empty message provided")
            return False

        if targets == NotificationTarget.BOTH:
            results = []
            for target in [NotificationTarget.LOCAL_SPEAKER, NotificationTarget.GOOGLE_HUB]:
                if target in self.providers:
                    results.append(
                        self.providers[target].send_notification(message))
            return all(results) if results else False

        if targets not in self.providers:
            logging.error("Target %s not configured", targets)
            return False

        return self.providers[targets].send_notification(message)

    def test_all_providers(self):
        """Test all configured notification providers.
        Returns:
            dict: A dictionary mapping NotificationTarget to the result of sending a test notification.
        """
        test_message = "Notification system test"
        results = {}

        for target, provider in self.providers.items():
            logging.info("Testing %s...", target.value)
            results[target] = provider.send_notification(test_message)

        return results


def main():
    """Test the notification dispatcher by sending test notifications to all providers."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize dispatcher with Google Hub
    dispatcher = NotificationDispatcher(
        google_device_ip="192.168.7.38",
        google_device_name="Kitchen display"
    )

    # Test all providers
    results = dispatcher.test_all_providers()

    for target, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {target.value}: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    main()
