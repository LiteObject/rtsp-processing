"""
Real-time Streamlit dashboard for RTSP processing monitoring.
"""
import streamlit as st
import time
import os
import glob
import sys
import re
from datetime import datetime

# Add the parent directory to Python path for absolute imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative import first (when running as module)
    from .event_broadcaster import broadcaster
except ImportError:
    # Fall back to absolute import (when running as script)
    from src.event_broadcaster import broadcaster


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


def format_datetime_friendly(dt):
    """Convert datetime object to friendly 12-hour format."""
    if dt is None:
        return "None"
    # Format to friendly 12-hour time (e.g., "6:45:30 PM")
    return dt.strftime("%I:%M:%S %p").lstrip('0')


def check_background_service_status():
    """Check if background processing service appears to be running."""
    # Method 1: Check for recent events (within last 2 minutes - reduced for faster detection)
    events = broadcaster.get_recent_events(10)
    if events:
        recent_events = [e for e in events if (
            datetime.now() - e['timestamp']).total_seconds() < 120]  # 2 minutes
        if len(recent_events) > 0:
            return True

    # Method 2: Check for recent log file activity (within last 1 minute)
    log_file = "logs/rtsp_processing.log"
    if os.path.exists(log_file):
        try:
            # Check if log file was modified recently
            last_modified = os.path.getmtime(log_file)
            time_since_modified = time.time() - last_modified
            if time_since_modified < 60:  # 1 minute
                return True

            # Method 3: Check for recent log entries
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-5:]  # Last 5 lines

            for line in lines:
                # Look for recent log entries
                timestamp_pattern = r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}),(\d{3})'
                match = re.match(timestamp_pattern, line)
                if match:
                    try:
                        date_part = match.group(1)
                        time_part = match.group(2)
                        log_dt = datetime.strptime(
                            f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S")

                        # Check if log entry is within last 1 minute
                        time_diff = (datetime.now() - log_dt).total_seconds()
                        if time_diff < 60:  # 1 minute
                            return True
                    except ValueError:
                        continue
        except (IOError, OSError, UnicodeDecodeError):
            pass

    return False


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="RTSP Monitor",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🎥 Real-time RTSP Processing Monitor")

    # Background service status indicator
    background_active = check_background_service_status()
    if background_active:
        st.success("🟢 Background processing is active")
    else:
        st.warning(
            "🟡 Background processing not detected - Run `python -m src.app --with-ui` for full functionality")

        # Show helpful debug info in an expander
        with st.expander("🔍 Debug Info - Click to expand"):
            st.write("**Checking for background service activity...**")

            # Check events
            events = broadcaster.get_recent_events(5)
            st.write(f"Recent events in broadcaster: {len(events)}")

            # Check log file
            log_file = "logs/rtsp_processing.log"
            if os.path.exists(log_file):
                last_modified = os.path.getmtime(log_file)
                time_since_modified = time.time() - last_modified
                st.write(
                    f"Log file last modified: {time_since_modified:.1f} seconds ago")

                # Show last few log lines
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-3:]
                    st.write("**Last 3 log entries:**")
                    for line in lines:
                        st.code(line.strip())
                except Exception:
                    st.write("Could not read log file")
            else:
                st.write("Log file does not exist")

            st.write("*Status updates every 2 seconds with auto-refresh*")

    # Auto-refresh toggle
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True

    # Control panel
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col2:
        st.session_state.auto_refresh = st.checkbox(
            "Auto-refresh", value=st.session_state.auto_refresh)

    # Get recent events
    events = broadcaster.get_recent_events(100)

    # Metrics row
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

    detections = [e for e in events if e['type'] == 'detection']
    images = [e for e in events if e['type'] == 'image']
    person_confirmed = [e for e in detections if e['data'].get(
        'status') == 'person_confirmed']

    with metrics_col1:
        st.metric("Total Detections", len(detections))
    with metrics_col2:
        st.metric("Images Captured", len(images))
    with metrics_col3:
        st.metric("Persons Confirmed", len(person_confirmed))
    with metrics_col4:
        last_activity = format_datetime_friendly(
            events[0]['timestamp']) if events else "None"
        st.metric("Last Activity", last_activity)

    # Main content area
    left_col, right_col = st.columns([2, 1])

    # Images section
    with left_col:
        st.subheader("📸 Latest Captures")

        # Get latest images from filesystem
        images_dir = "images"
        if os.path.exists(images_dir):
            image_files = glob.glob(f"{images_dir}/*.jpg")
            if image_files:
                latest_images = sorted(
                    image_files, key=os.path.getmtime, reverse=True)[:4]

                if latest_images:
                    img_cols = st.columns(2)
                    for i, img_path in enumerate(latest_images):
                        with img_cols[i % 2]:
                            try:
                                timestamp = datetime.fromtimestamp(
                                    os.path.getmtime(img_path))
                                filename = os.path.basename(img_path)
                                is_detected = "_Detected" in filename

                                if is_detected:
                                    st.success(f"✅ Person Detected")

                                st.image(
                                    img_path, caption=f"{filename}\n{format_datetime_friendly(timestamp)}")
                            except Exception as e:
                                st.error(f"Error loading image: {e}")
                else:
                    st.info("No images captured yet")
            else:
                st.info("No images found in images directory")
        else:
            st.info("Images directory not found")

    # Events and logs section
    with right_col:
        st.subheader("📋 Live Events")

        # Recent events
        if events:
            event_container = st.container()
            with event_container:
                for event in events[-15:]:  # Show last 15 events
                    timestamp_str = format_datetime_friendly(
                        event['timestamp'])

                    if event['type'] == 'detection':
                        status = event['data'].get('status', 'unknown')
                        if status == 'person_confirmed':
                            description = event['data'].get(
                                'description', 'Unknown')
                            st.success(
                                f"✅ {timestamp_str} - Person: {description}")
                        elif status == 'no_person':
                            method = event['data'].get('method', 'Unknown')
                            st.info(
                                f"ℹ️ {timestamp_str} - No person ({method})")
                        else:
                            st.text(f"🔍 {timestamp_str} - {status}")

                    elif event['type'] == 'image':
                        img_status = event['data'].get('status', 'unknown')
                        img_path = event['data'].get('path', 'unknown')
                        filename = os.path.basename(
                            img_path) if img_path != 'unknown' else 'unknown'
                        st.text(
                            f"📷 {timestamp_str} - {filename} ({img_status})")

                    elif event['type'] == 'notification':
                        success = event['data'].get('success', False)
                        message = event['data'].get('message', 'Unknown')
                        if success:
                            st.success(
                                f"📢 {timestamp_str} - Sent: {message[:30]}...")
                        else:
                            st.error(
                                f"❌ {timestamp_str} - Failed notification")
        else:
            if check_background_service_status():
                st.info(
                    "No events yet. Waiting for RTSP processing to generate events.")
            else:
                st.warning(
                    "No events detected. Start background processing with: `python -m src.app --with-ui`")

        # System logs section
        st.subheader("📄 System Logs")
        log_file = "logs/rtsp_processing.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # Last 10 lines

                log_container = st.container()
                with log_container:
                    for line in reversed(lines):
                        line = line.strip()
                        if not line:
                            continue

                        # Convert log line timestamp to friendly 12-hour format
                        line = format_log_line_with_friendly_time(line)

                        if "ERROR" in line:
                            st.error(line)
                        elif "WARNING" in line:
                            st.warning(line)
                        elif "Person detected" in line or "Notification sent" in line:
                            st.success(line)
                        else:
                            st.text(line)
            except Exception as e:
                st.error(f"Error reading log file: {e}")
        else:
            st.info("Log file not found")

    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()
