# README Updates for Recent Changes

## New Sections to Add:

### Real-time Event Broadcasting (Add after "Configuration" section)
```markdown
## Event Broadcasting System

The system includes a sophisticated cross-process event broadcasting system for real-time UI updates:

### Features
- **Cross-Process Sync**: Events from background service instantly appear in UI dashboard
- **Persistent Storage**: Events stored in `events.json` for reliability
- **Thread-Safe**: Concurrent access from multiple processes handled safely
- **Auto-Cleanup**: Events automatically pruned to prevent file growth (max 100 events)
- **Real-time Updates**: UI dashboard reflects live activity immediately

### Event Types
- **Detection Events**: YOLO detections, LLM confirmations, person status
- **Image Events**: Image captures and file operations
- **Notification Events**: TTS and Google Hub broadcast results

### Usage
Events are automatically broadcasted - no manual intervention needed:
```python
# Events are emitted automatically by the service
# UI dashboard automatically displays them in real-time
```

The event system ensures the UI dashboard always shows current activity, even when background processing runs in a separate process.
```

### Updated Dashboard Features (Replace existing section)
```markdown
**Dashboard Features:**
- 📊 **Live Metrics** - Real-time detection counts, image captures, persons confirmed
- 📸 **Image Gallery** - Latest captures with person detection highlights  
- 📋 **Event Stream** - Live detection events and notifications with friendly 12-hour timestamps
- 📄 **System Logs** - Live log tail with user-friendly time formatting
- 🔄 **Auto-refresh** - Updates every 2 seconds with cross-process event synchronization
- 🎯 **Accurate Counters** - Metrics reflect actual background service activity
```

### Troubleshooting Section (Add before "Contributing")
```markdown
## Troubleshooting

### UI Dashboard Issues

**Dashboard shows zero counts despite background processing:**
- Ensure you're using `--with-ui` flag: `python -m src.app --with-ui`
- Check that `events.json` exists in the project root after processing starts
- Verify background service is running by checking logs: `tail -f logs/rtsp_processing.log`
- Events should appear in real-time as the service processes frames

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
```

### Updated Dependencies (Replace in requirements section)
```markdown
**Key dependencies:**
- `zeroconf>=0.47.0` - Async device discovery and networking
- `pyttsx3` - Cross-platform text-to-speech engine
- `opencv-python` - Image processing and RTSP capture
- `ultralytics` - YOLOv8 object detection
- `openai` - Vision API for image analysis
- `pychromecast` - Google Hub/Chromecast communication with async support
- `streamlit` - Real-time web dashboard with live event updates
```
