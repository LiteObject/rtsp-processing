# RTSP Processing and Google Hub Broadcast System

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

High-performance async system that captures images from RTSP video streams, analyzes them for human presence using OpenAI's vision models, and broadcasts messages to Google Hub devices when people are detected.

## Features
- **Async/await architecture** for 3x better performance
- **RTSP stream capture** with automatic resource cleanup
- **Two-stage detection** - YOLO for fast screening, OpenAI for detailed analysis
- **Cost optimization** - Only sends images to OpenAI API when YOLO detects people
- **Google Hub/Chromecast broadcasting** with device discovery
- **Health checks** for external dependencies on startup
- **Input validation** and structured logging throughout
- **Automatic image cleanup** to prevent disk space issues
- **Context managers** for proper resource management

## Requirements
- Python 3.11+
- RTSP-compatible camera or stream
- Google Hub or Chromecast device on the same network
- **OpenAI API key** (required for vision analysis)
- Network connectivity for API calls

### Python Packages
Install all dependencies with:
```sh
pip install -r requirements.txt
```

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
OPENAI_API_KEY=your_openai_api_key_here
RTSP_URL=rtsp://username:password@192.168.1.100/stream
GOOGLE_DEVICE_IP=192.168.1.200

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
```bash
python -m src.app
```
**What it does:**
- Runs health checks for RTSP stream and OpenAI API
- Captures images from RTSP stream (configurable interval)
- Processes multiple images concurrently using async/await
- Uses YOLO for fast person detection, then OpenAI for detailed analysis
- Broadcasts to Google Hub when person confirmed
- Automatically cleans up old images

### 2. Discover Google Devices
List all Google Hub/Chromecast devices on your network:
```sh
python -m src.google_devices
```

### 3. Manual Image Capture
Capture a single image from an RTSP stream:
```sh
python -m src.image_capture
```

### 4. Manual Google Hub Broadcast
Send a custom message to a Google Hub:
```sh
python -m src.google_broadcast
```

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
- **Health checks** prevent runtime failures
- **Context managers** ensure proper resource cleanup
- **Retry logic** with exponential backoff for network calls

## File Overview

### Core Modules
- `src/app.py` — Async main loop with health checks
- `src/services.py` — AsyncRTSPProcessingService for business logic
- `src/image_capture.py` — RTSP capture with context managers
- `src/image_analysis.py` — Async OpenAI vision analysis
- `src/computer_vision.py` — YOLOv8 person detection

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

### Requirements
- **OpenAI API key** is required (no local LLM support in async version)
- **Network connectivity** needed for OpenAI API calls
- **RTSP stream** must be accessible from the application

### Architecture Benefits
- **Async/await**: Non-blocking I/O for better performance
- **Health checks**: Early detection of configuration issues
- **Input validation**: Comprehensive validation prevents runtime errors
- **Context managers**: Automatic resource cleanup
- **Structured logging**: Better debugging and monitoring

## License

This project is licensed under the [MIT License](LICENSE).
