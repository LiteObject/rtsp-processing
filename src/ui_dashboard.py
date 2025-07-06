"""
Real-time Streamlit dashboard for RTSP processing monitoring.
"""
import streamlit as st
import time
import os
import glob
import sys
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


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="RTSP Monitor",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🎥 Real-time RTSP Processing Monitor")

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
        last_activity = events[0]['timestamp'].strftime(
            "%H:%M:%S") if events else "None"
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
                                    img_path, caption=f"{filename}\n{timestamp.strftime('%H:%M:%S')}")
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
                    timestamp_str = event['timestamp'].strftime('%H:%M:%S')

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
            st.info("No events yet. Start the RTSP processing to see live updates.")

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
