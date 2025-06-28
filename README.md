# RTSP Processing and Google Hub Broadcast System

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

This project captures images from an RTSP video stream, analyzes them for human presence using LLMs (Ollama or OpenAI), and broadcasts a message to a Google Hub (or compatible Chromecast device) if a person is detected.

## Features
- Capture images from RTSP streams (e.g., IP cameras)
- Analyze images for human presence using local (Ollama) or cloud (OpenAI) vision models
- Broadcast text-to-speech messages to Google Hub/Chromecast devices
- Modular, robust, and production-ready Python code
- Logging and error handling throughout

## Requirements
- Python 3.8+
- RTSP-compatible camera or stream
- Google Hub or Chromecast device on the same network
- [Ollama](https://ollama.com/) (for local LLMs) or OpenAI API key (for cloud LLMs)

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

## Environment Variables
Copy `.env.example` to `.env` and set your OpenAI API key if using OpenAI:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### 1. Capture and Analyze Images, Broadcast if Person Detected
Run the main application:
```sh
python -m src.app
```
- Captures an image from the RTSP stream every 10 seconds
- Analyzes the image for human presence
- Broadcasts a message to the configured Google Hub if a person is detected

### 2. Discover Google Devices
List all Google Hub/Chromecast devices on your network:
```sh
python -m src.google_devices
```

### 3. Manual Image Capture
Capture a single image from an RTSP stream:
```sh
python -m src.capture_image
```

### 4. Manual Google Hub Broadcast
Send a custom message to a Google Hub:
```sh
python -m src.google_broadcast
```

## File Overview
- `src/app.py` — Main loop for capture, analysis, and broadcast
- `src/capture_image.py` — Captures a single image from RTSP
- `src/process_image.py` — Analyzes images using LLMs (Ollama/OpenAI)
- `src/llm_factory.py` — Factory for LLM model selection
- `src/google_broadcast.py` — Broadcasts TTS messages to Google Hub/Chromecast
- `src/google_devices.py` — Discovers Google devices on the network
- `requirements.txt` — Python dependencies
- `.env.example` — Example environment config

## Configuration
- Edit `GOOGLE_DEVICE_IP` in `app.py` and `google_broadcast.py` to match your Google Hub's IP address.
- Edit the RTSP URL in `app.py` and other scripts to match your camera.
- Change LLM model names in `process_image.py` and `llm_factory.py` as needed.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## Notes
- Ollama must be running and the vision model (e.g., `llama3.2-vision`) must be pulled locally for local inference.
- OpenAI API key is required for cloud-based analysis.
- All logs are output to the console; you can configure logging as needed.

## License

This project is licensed under the [MIT License](LICENSE).
