#!/usr/bin/env python3
"""
Test the background service detection logic.
"""
from unittest.mock import Mock
import sys
import os
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit to avoid import error
sys.modules['streamlit'] = Mock()


def test_background_detection():
    """Test the background service detection."""
    try:
        from src.ui_dashboard import check_background_service_status

        print("Testing background service detection...")
        print("=" * 50)

        # Test the function
        status = check_background_service_status()
        print(f"Background service detected: {status}")

        # Check log file details
        log_file = "logs/rtsp_processing.log"
        if os.path.exists(log_file):
            last_modified = os.path.getmtime(log_file)
            time_since_modified = time.time() - last_modified
            print(f"Log file exists: YES")
            print(f"Last modified: {time_since_modified:.1f} seconds ago")

            # Show last few lines
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-3:]
                print(f"Last 3 log entries:")
                for i, line in enumerate(lines, 1):
                    print(f"  {i}: {line.strip()}")
            except Exception as e:
                print(f"Error reading log: {e}")
        else:
            print("Log file exists: NO")

        # Check events
        try:
            from src.ui_dashboard import broadcaster
            events = broadcaster.get_recent_events(5)
            print(f"Recent events in broadcaster: {len(events)}")
            for i, event in enumerate(events[-3:], 1):
                print(f"  Event {i}: {event['type']} at {event['timestamp']}")
        except Exception as e:
            print(f"Error checking events: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_background_detection()

    print("\n" + "=" * 50)
    print("If background service is running but not detected:")
    print("1. Make sure you ran: python -m src.app --with-ui")
    print("2. Wait a few moments for the service to start logging")
    print("3. The UI refreshes every 2 seconds")
    print("4. Check the debug info in the UI expander")
