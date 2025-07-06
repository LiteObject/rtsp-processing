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
- `pyttsx3` - Cross-platform text-to-speech engine
- `opencv-python` - Image processing and RTSP capture
- `ultralytics` - YOLOv8 object detection
- `openai` - Vision API for image analysis
- `pychromecast` - Google Hub/Chromecast communication
- `streamlit` - Real-time web dashboard
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
- 📊 **Live Metrics** - Detection counts, image captures, activity status
- 📸 **Image Gallery** - Latest captures with person detection highlights
- 📋 **Event Stream** - Real-time detection events and notifications
- 📄 **System Logs** - Live log tail with color-coded severity
- 🔄 **Auto-refresh** - Updates every 2 seconds

Access at: http://localhost:8501

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
- **Concurrent Processing**: Multiple images analyzed simultaneously
- **Non-blocking Notifications**: Threaded dispatch prevents processing delays
- **TTS Optimization**: 33% faster speech (200 WPM vs 150 WPM)
- **Duplicate Filtering**: Intelligent suppression of repetitive messages
- **Resource Management**: Automatic cleanup prevents memory/disk leaks
- **Error Recovery**: Retry logic with exponential backoff
- **Health Monitoring**: Startup validation of all dependencies

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## Notes

### LLM Options
- **OpenAI**: Cloud-based, requires API key and internet connectivity
- **Ollama**: Local processing with `llama3.2-vision:latest`, zero API costs
- **RTSP stream** must be accessible from the application

### Architecture Benefits
- **Async/await**: Non-blocking I/O for better performance
- **Health checks**: Early detection of configuration issues
- **Input validation**: Comprehensive validation prevents runtime errors
- **Context managers**: Automatic resource cleanup
- **Structured logging**: Better debugging and monitoring

## License

This project is licensed under the [MIT License](LICENSE).
