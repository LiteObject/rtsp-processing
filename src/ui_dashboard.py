"""
Real-time Streamlit dashboard for RTSP processing monitoring.
"""
import glob
import os
import re
import sys
import time
from datetime import datetime

import streamlit as st

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


@st.cache_data(ttl=1)  # Reduced cache time for more responsive updates
def get_cached_events():
    """Get events with caching to improve performance."""
    return broadcaster.get_recent_events(100)


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


def show_system_status():
    """Show system status indicators."""
    col1, col2, col3 = st.columns(3)

    with col1:
        # Check recent events for activity
        events = broadcaster.get_recent_events(10)
        recent_events = []
        for e in events:
            try:
                ts = e['timestamp']
                # Handle both datetime objects and ISO strings
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                time_diff = (datetime.now() - ts).total_seconds()
                if time_diff < 300:  # 5 minutes
                    recent_events.append(e)
            except (TypeError, ValueError, KeyError):
                continue

        if recent_events:
            st.success("🟢 Event System: Active")
        else:
            st.warning("🟡 Event System: Idle")

    with col2:
        # Check background service
        background_active = check_background_service_status()
        if background_active:
            st.success("🟢 Background Service: Running")
        else:
            st.error("🔴 Background Service: Not Detected")

    with col3:
        # Show last detection status
        detection_events = [e for e in events if e.get('type') == 'detection']
        if detection_events:
            # Get the most recent, not first
            last_detection = detection_events[-1]
            status = last_detection.get('data', {}).get('status', 'unknown')
            if status in ['person_detected', 'person_confirmed']:
                st.info("👤 Last Detection: Person")
            else:
                st.info("👁️ Last Detection: No Person")
        else:
            st.info("❓ Last Detection: Unknown")


def format_event_for_display(event):
    """Format an event for user-friendly display."""
    timestamp = format_datetime_friendly(event['timestamp'])
    event_type = event['type']
    data = event.get('data', {})

    if event_type == 'detection':
        status = data.get('status', 'unknown')
        method = data.get('method', 'Unknown')
        if status == 'person_detected':
            return f"👤 **Person Detected** via {method} at {timestamp}"
        elif status == 'person_confirmed':
            return f"✅ **Person Confirmed** via {method} at {timestamp}"
        else:
            return f"👁️ No person detected via {method} at {timestamp}"

    elif event_type == 'image':
        filepath = data.get('filepath', 'Unknown')
        filename = os.path.basename(filepath) if filepath else 'Unknown'
        return f"📸 **Image Captured**: {filename} at {timestamp}"

    elif event_type == 'analysis':
        description = data.get('description', 'No description')
        return f"🧠 **AI Analysis**: {description} at {timestamp}"

    elif event_type == 'notification':
        success = data.get('success', False)
        message = data.get('message', 'No message')
        target = data.get('target', 'Unknown')
        status_icon = "✅" if success else "❌"
        return f"{status_icon} **Notification** to {target}: {message} at {timestamp}"

    else:
        return f"ℹ️ **{event_type.title()}** at {timestamp}"


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="RTSP Monitor",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🎥 Real-time RTSP Processing Monitor")

    # Show system status
    show_system_status()

    st.markdown("---")  # Separator line

    background_active = check_background_service_status()
    if not background_active:
        st.warning(
            "⚠️ Background processing not detected - Run `python -m src.app --with-ui` for full functionality")

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
    if 'last_event_count' not in st.session_state:
        st.session_state.last_event_count = 0
    if 'last_event_timestamp' not in st.session_state:
        st.session_state.last_event_timestamp = None

    # Control panel
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col2:
        auto_refresh_enabled = st.checkbox(
            "Auto-refresh (event-driven)", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh_enabled

    # Event-driven auto-refresh
    if st.session_state.auto_refresh:
        # Get fresh events (bypass cache for this check)
        current_events = broadcaster.get_recent_events(100)
        current_event_count = len(current_events)

        # Check both count and latest event timestamp for changes
        latest_event_timestamp = current_events[-1]['timestamp'] if current_events else None

        # Initialize session state on first run
        if st.session_state.last_event_count == 0 and st.session_state.last_event_timestamp is None:
            st.session_state.last_event_count = current_event_count
            st.session_state.last_event_timestamp = latest_event_timestamp
            st.info(
                f"🔄 Dashboard initialized with {current_event_count} events")

        # Detect new events by count OR timestamp change
        has_new_events = (
            current_event_count != st.session_state.last_event_count or
            latest_event_timestamp != st.session_state.last_event_timestamp
        )

        if has_new_events:
            # New events detected - update state and refresh after a delay
            st.success(
                f"🔄 New events detected! Refreshing... ({current_event_count} total events)")
            # Show what changed for debugging
            if current_event_count != st.session_state.last_event_count:
                st.info(
                    f"Event count changed: {st.session_state.last_event_count} → {current_event_count}")
            if latest_event_timestamp != st.session_state.last_event_timestamp:
                st.info(f"Latest event timestamp changed")

            # Update session state BEFORE refresh to prevent infinite loop
            st.session_state.last_event_count = current_event_count
            st.session_state.last_event_timestamp = latest_event_timestamp

            # Clear cache to ensure fresh data on next load
            st.cache_data.clear()
            # Small delay to show the message, then refresh
            st.html("""
            <script>
            setTimeout(function() {
                window.location.reload();
            }, 1500);  // 1.5 second delay to show the message and prevent rapid reloads
            </script>
            """)
        else:
            # No new events - show monitoring status and check periodically
            st.caption(
                f"🔄 Monitoring for new events... ({current_event_count} total events)")
            st.html("""
            <script>
            setTimeout(function() {
                window.location.reload();
            }, 3000);  // Check every 3 seconds when no new events (reduced frequency)
            </script>
            """)

    # Get recent events
    events = get_cached_events()

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
            events[-1]['timestamp']) if events else "None"
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
                                # is_detected = "_Detected" in filename

                                # if is_detected:
                                #     st.success(f"✅ Person Detected")

                                st.image(
                                    img_path, caption=f"{filename}\n{format_datetime_friendly(timestamp)}")
                            except (OSError, IOError) as e:
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
                    formatted_event = format_event_for_display(event)

                    # Use different styling based on event type
                    if event['type'] == 'detection':
                        status = event['data'].get('status', 'unknown')
                        if status in ['person_detected', 'person_confirmed']:
                            st.success(formatted_event)
                        else:
                            st.info(formatted_event)
                    elif event['type'] == 'notification':
                        success = event['data'].get('success', False)
                        if success:
                            st.success(formatted_event)
                        else:
                            st.error(formatted_event)
                    elif event['type'] == 'image':
                        st.info(formatted_event)
                    elif event['type'] == 'analysis':
                        st.info(formatted_event)
                    else:
                        st.text(formatted_event)
        else:
            if check_background_service_status():
                st.info(
                    "No events yet. Waiting for RTSP processing to generate events.")
            else:
                st.warning(
                    "No events detected. Start background processing with: `python -m src.app --with-ui`")


if __name__ == "__main__":
    main()
