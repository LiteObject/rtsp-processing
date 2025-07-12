# RTSP Processing and Google Hub Broadcast System

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

High-performance async system that captures images from RTSP video streams, analyzes them for human presence using OpenAI's vision models, and broadcasts messages to Google Hub devices when people are detected.

## Features
- **Async/await architecture** for 3x better performance
- **RTSP stream capture** with automatic resource cleanup
- **Two-stage detection** - YOLO for fast screening, then LLM for detailed analysis
- **Cost optimization** - Only processes images with LLM when YOLO detects people
- **Flexible LLM support** - OpenAI API or local Ollama (llama3.2-vision) for zero cost
- **Advanced notification system** with threading, duplicate filtering, and optimized TTS
- **Cross-platform TTS** - Local speakers with pyttsx3 and system fallbacks
- **Google Hub/Chromecast broadcasting** with device discovery
- **Non-blocking notifications** - Threaded and async dispatch options
- **Intelligent duplicate filtering** - Prevents repetitive announcements
- **Health checks** for external dependencies on startup
- **Input validation** and structured logging throughout
- **Automatic image cleanup** to prevent disk space issues
- **Context managers** for proper resource management

## Requirements
- Python 3.11+
- RTSP-compatible camera or stream
- Google Hub or Chromecast device on the same network
- **Local speakers** for TTS notifications (optional)
- **LLM Provider** (choose one):
  - OpenAI API key for cloud analysis
  - [Ollama](https://ollama.com/) with `llama3.2-vision:latest` for local processing

### Python Packages
Install all dependencies with:
```sh
pip install -r requirements.txt
```

**Key dependencies:**
- `zeroconf>=0.47.0` - Async device discovery and networking
- `pyttsx3` - Cross-platform text-to-speech engine
- `opencv-python` - Image processing and RTSP capture
- `ultralytics` - YOLOv8 object detection
- `openai` - Vision API for image analysis
- `pychromecast` - Google Hub/Chromecast communication with async support
- `streamlit` - Real-time web dashboard with live event updates
- `streamlit` - Real-time web dashboard (optional UI)

### Running Unit Tests
Unit tests are provided in the `tests/` directory and use `pytest`.

To run all tests:
```sh
pytest
```

To run a specific test file:
```sh
pytest tests/test_process_image.py
```

Make sure all dependencies are installed before running tests.

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
# Required
RTSP_URL=rtsp://username:password@192.168.1.100/stream
GOOGLE_DEVICE_IP=192.168.1.200

# LLM Provider (choose one)
OPENAI_API_KEY=your_openai_api_key_here  # For cloud analysis
DEFAULT_LLM_PROVIDER=ollama              # For local processing

# Optional
IMAGES_DIR=images
MAX_IMAGES=100
CAPTURE_INTERVAL=10
LLM_TIMEOUT=30
```

### Config Class
All settings are centralized in `src/config.py` with validation and defaults.

## Event Broadcasting System

The system includes a sophisticated cross-process event broadcasting system for real-time UI updates:

### Features
- **Event-Driven UI Updates**: Dashboard refreshes immediately when new events occur
- **Cross-Process Sync**: Events from background service instantly appear in UI dashboard
- **Persistent Storage**: Events stored in `events.json` for reliability with batched writes
- **Performance Optimized**: Timer-based batched persistence (every 2 seconds) instead of per-event writes
- **Thread-Safe**: Concurrent access from multiple processes handled safely with proper locking
- **Graceful Shutdown**: Non-daemon threads with proper cleanup and shutdown handling
- **Auto-Cleanup**: Events automatically pruned to prevent file growth (max 100 events)
- **Real-time Updates**: UI dashboard reflects live activity with <1 second latency

### Event Types
- **Detection Events**: YOLO detections, LLM confirmations, person status
- **Image Events**: Image captures and file operations
- **Analysis Events**: AI descriptions and confidence scores
- **Notification Events**: TTS and Google Hub broadcast results

### Performance Improvements
- **3x faster event persistence** with batched writes
- **Reduced I/O load** with timer-based scheduling  
- **Better responsiveness** with event-driven UI refresh
- **Memory efficient** with automatic event pruning
- **Thread safety** with proper locking mechanisms
- **Notification Events**: TTS and Google Hub broadcast results

### Usage
Events are automatically broadcasted - no manual intervention needed:
```python
# Events are emitted automatically by the service
# UI dashboard automatically displays them in real-time
```

The event system ensures the UI dashboard always shows current activity, even when background processing runs in a separate process.

## Usage

### 1. Run Main Application

**Command Line (Headless)**
```bash
python -m src.app
```

**UI Dashboard Only (No Background Processing)**
```bash
python -m src.app --ui
```

**🔥 Background Processing + UI Dashboard (Recommended)**
```bash
python -m src.app --with-ui
```

**What it does:**
- Runs health checks for RTSP stream and OpenAI API
- Captures images from RTSP stream (configurable interval)
- Processes multiple images concurrently using async/await
- Uses YOLO for fast person detection, then OpenAI for detailed analysis
- Broadcasts to Google Hub when person confirmed
- Automatically cleans up old images
- **With UI**: Real-time dashboard at http://localhost:8501
- **`--with-ui`**: Runs both background processing AND UI in a single command

### 2. Notification System

The system includes an advanced notification dispatcher with multiple performance optimizations:

#### Basic Usage
```python
from src.notification_dispatcher import NotificationDispatcher, NotificationTarget

# Initialize with Google Hub (optional)
dispatcher = NotificationDispatcher(
    google_device_ip="192.168.1.200",
    google_device_name="Kitchen Display"
)

# Send notifications to different targets
dispatcher.dispatch("Person detected at front door", NotificationTarget.LOCAL_SPEAKER)
dispatcher.dispatch("Security alert", NotificationTarget.GOOGLE_HUB)
dispatcher.dispatch("Important message", NotificationTarget.BOTH)
```

#### Performance Features
```python
# Non-blocking notifications (recommended for real-time processing)
dispatcher.dispatch_threaded("Person walking by")  # Fire-and-forget

# Async notifications with result checking
future = dispatcher.dispatch_async("Motion detected")
# Continue processing...
success = future.result()  # Check result when needed

# Duplicate filtering (automatic)
dispatcher.dispatch("Same message")  # First time: sent
dispatcher.dispatch("Same message")  # Within 5 seconds: skipped
```

#### TTS Optimization
- **Faster speech rate**: 200 WPM (33% faster than default)
- **Cross-platform support**: Windows (pyttsx3), macOS (say), Linux (espeak)
- **Automatic fallbacks**: System commands if pyttsx3 unavailable
- **Voice optimization**: Uses best available voice on Windows

#### Test Notifications
```sh
python -m src.notification_dispatcher
```

### 3. Discover Google Devices
List all Google Hub/Chromecast devices on your network:
```sh
python -m src.google_devices
```

### 4. Manual Image Capture
Capture a single image from an RTSP stream:
```sh
python -m src.image_capture
```

### 5. Manual Google Hub Broadcast
Send a custom message to a Google Hub:
```sh
python -m src.google_broadcast
```

### 6. Real-time Web Dashboard
Launch the monitoring dashboard using any of these methods:

**Option 1: Through main app (recommended)**
```sh
python -m src.app --ui
```

**Option 2: Direct Streamlit (from project root)**
```sh
streamlit run src/ui_dashboard.py
```

**Option 3: Using standalone runner**
```sh
streamlit run run_ui.py
```

**Dashboard Features:**
- 📊 **Live Metrics** - Real-time detection counts, image captures, persons confirmed
- � **System Status** - Three-column status indicators showing event system, background service, and last detection
- �📸 **Image Gallery** - Latest captures with person detection highlights  
- 📋 **Event Stream** - Live detection events and notifications with enhanced formatting and icons
- 🔄 **Event-Driven Auto-refresh** - Updates immediately when new events occur, otherwise checks every 2 seconds
- 🎯 **Accurate Counters** - Metrics reflect actual background service activity
- ⚡ **Enhanced Performance** - Optimized caching and event-driven updates for <1 second latency

**Enhanced UI Features:**
- **Smart Auto-refresh**: Event-driven updates with immediate refresh on new activity
- **Visual Status Indicators**: Green/yellow/red status bars for system health monitoring
- **Better Event Formatting**: Rich text with icons, timestamps, and contextual styling
- **Error Handling**: Robust timestamp parsing for both datetime objects and ISO strings
- **Responsive Design**: Clean layout with improved user experience

Access at: http://localhost:8501 (or custom port if specified)

## System Architecture: Async Processing Flow

```mermaid
sequenceDiagram
    participant HealthCheck
    participant MainLoop
    participant RTSP
    participant YOLOv8
    participant OpenAI
    participant GoogleHub

    HealthCheck->>RTSP: Check stream connectivity
    HealthCheck->>OpenAI: Validate API access
    MainLoop->>RTSP: capture_image_from_rtsp()
    MainLoop->>MainLoop: asyncio.create_task(process_frame)
    
    par Async Processing
        MainLoop->>YOLOv8: person_detected_yolov8(image)
        alt Person detected
            MainLoop->>OpenAI: analyze_image_async(image)
            OpenAI-->>MainLoop: {person_present, description}
            MainLoop->>GoogleHub: send_message_to_google_hub()
        else No person
            MainLoop->>MainLoop: cleanup_image()
        end
    end
```

**Key Improvements:**
- **3x faster processing** with concurrent image analysis
- **Real-time web dashboard** with live monitoring
- **Health checks** prevent runtime failures
- **Context managers** ensure proper resource cleanup
- **Retry logic** with exponential backoff for network calls

## File Overview

### Core Modules
- `src/app.py` — Async main loop with health checks and UI launcher
- `src/services.py` — AsyncRTSPProcessingService for business logic
- `src/image_capture.py` — RTSP capture with context managers
- `src/image_analysis.py` — Async OpenAI vision analysis
- `src/computer_vision.py` — YOLOv8 person detection
- `src/notification_dispatcher.py` — Advanced notification system with threading and TTS
- `src/event_broadcaster.py` — Real-time event system for UI updates
- `src/ui_dashboard.py` — Streamlit web dashboard for monitoring

### Infrastructure
- `src/config.py` — Centralized configuration with validation
- `src/health_checks.py` — Startup dependency validation
- `src/context_managers.py` — Resource cleanup automation
- `src/google_broadcast.py` — Chromecast/Google Hub messaging
- `src/google_devices.py` — Network device discovery
- `src/llm_factory.py` — LangChain model factory (legacy)

### Configuration
- `requirements.txt` — Python dependencies (includes aiohttp)
- `.env.example` — Environment configuration template

## Performance & Monitoring

### Logging Levels
```bash
# Set logging level for debugging
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" -m src.app
```

### Key Metrics
- **Processing Speed**: 3x faster than synchronous version
- **Event Broadcasting**: Event-driven UI updates with <1 second latency
- **Concurrent Processing**: Multiple images analyzed simultaneously
- **Non-blocking Notifications**: Threaded dispatch prevents processing delays
- **TTS Optimization**: 33% faster speech (200 WPM vs 150 WPM)
- **Duplicate Filtering**: Intelligent suppression of repetitive messages
- **Resource Management**: Automatic cleanup prevents memory/disk leaks
- **Error Recovery**: Retry logic with exponential backoff
- **Health Monitoring**: Startup validation of all dependencies
- **UI Performance**: Batched event persistence with timer-based scheduling
- **Thread Safety**: Proper locking and graceful shutdown mechanisms

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## Troubleshooting

### UI Dashboard Issues

**Dashboard shows zero counts despite background processing:**
- Ensure you're using `--with-ui` flag: `python -m src.app --with-ui`
- Check that `events.json` exists in the project root after processing starts
- Verify background service is running by checking logs: `tail -f logs/rtsp_processing.log`
- Events should appear in real-time as the service processes frames

**Event-driven refresh not working:**
- Check browser console for JavaScript errors
- Verify the dashboard shows "🟢 Event System: Active" in the status bar
- Try manual refresh with the "🔄 Refresh" button
- Ensure auto-refresh is enabled with the checkbox

**System status indicators showing errors:**
- **🔴 Background Service: Not Detected** - Start background processing with `python -m src.app --with-ui`
- **🟡 Event System: Idle** - No recent events (last 5 minutes) - check RTSP stream connectivity
- **❓ Last Detection: Unknown** - No detection events recorded yet

**Time formatting inconsistency:**
- All timestamps now use friendly 12-hour format (e.g., "6:45:30 PM")
- System logs and Live Events use consistent formatting

### Google Hub Notification Issues

**"asyncio.run() cannot be called from a running event loop" error:**
- This has been resolved in recent versions
- Google Hub broadcasting now works from both sync and async contexts
- No manual intervention needed - the system auto-detects the context

**Google Hub not responding:**
- Verify device IP in `.env` file: `GOOGLE_DEVICE_IP=192.168.x.x`
- Ensure device and computer are on same WiFi network
- Test connection: `python -m src.google_broadcast`

### Performance Issues

**Slow processing or memory issues:**
- Check `MAX_IMAGES` setting in `.env` (default: 100)
- Verify `CAPTURE_INTERVAL` is appropriate (default: 10 seconds)
- Monitor log file size in `logs/` directory
- Ensure proper cleanup by checking for old images in `images/` directory

## License

This project is licensed under the [MIT License](LICENSE).
