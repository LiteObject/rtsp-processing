#!/usr/bin/env python3
"""
Test the log formatting function to ensure it works correctly.
"""
import re
from datetime import datetime


def format_log_line_with_friendly_time(log_line):
    """Convert log line timestamp to friendly 12-hour format."""
    # Pattern to match log timestamp: YYYY-MM-DD HH:MM:SS,mmm
    timestamp_pattern = r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}),(\d{3})'

    match = re.match(timestamp_pattern, log_line)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        milliseconds = match.group(3)

        try:
            # Parse the datetime
            dt = datetime.strptime(
                f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S")

            # Format to friendly 12-hour time
            friendly_time = dt.strftime("%b %d, %I:%M:%S %p")

            # Replace the original timestamp with friendly one
            return log_line.replace(f"{date_part} {time_part},{milliseconds}", friendly_time)
        except ValueError:
            # If parsing fails, return original line
            return log_line

    return log_line


# Test the function
if __name__ == "__main__":
    test_cases = [
        "2025-07-01 09:11:21,114 - INFO - Running health checks...",
        "2025-07-01 14:30:45,567 - ERROR - Connection failed",
        "2025-07-05 23:59:59,999 - WARNING - Low disk space",
        "Invalid log line without timestamp",
        "2025-12-25 00:00:01,001 - INFO - Merry Christmas!"
    ]

    print("Testing log line formatting:")
    print("=" * 80)

    for test_line in test_cases:
        formatted = format_log_line_with_friendly_time(test_line)
        print(f"Original:  {test_line}")
        print(f"Formatted: {formatted}")
        print("-" * 80)
