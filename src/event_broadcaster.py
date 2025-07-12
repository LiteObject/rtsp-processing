"""
Event broadcasting system for real-time UI updates.
"""
import collections
import threading
import json
import os
from typing import Dict, Any, List
from datetime import datetime


class EventBroadcaster:
    """Thread-safe event broadcaster for real-time UI updates."""

    def __init__(self, max_events: int = 100, persist_file: str = "events.json",
                 batch_interval: float = 2.0):
        self.events = collections.deque(maxlen=max_events)
        self._lock = threading.Lock()
        self.persist_file = persist_file
        self.max_events = max_events
        self._last_load_time = 0
        self._batch_interval = batch_interval
        self._persist_timer = None
        self._dirty = False
        self._load_persisted_events()

    def _load_persisted_events(self):
        """Load persisted events from file if newer than last load."""
        if not os.path.exists(self.persist_file):
            return

        try:
            # Check if file is newer than our last load
            file_mtime = os.path.getmtime(self.persist_file)
            if file_mtime <= self._last_load_time:
                return  # No need to reload

            with open(self.persist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear current events and load fresh from file
            self.events.clear()
            for event_data in data.get('events', []):
                # Parse timestamp back to datetime
                event_data['timestamp'] = datetime.fromisoformat(
                    event_data['timestamp'])
                self.events.append(event_data)

            self._last_load_time = file_mtime
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            # If file is corrupted or invalid, start fresh
            pass

    def _persist_events(self):
        """Persist current events to file."""
        try:
            events_data = []
            for event in self.events:
                # Convert datetime to ISO string for JSON serialization
                event_copy = event.copy()
                event_copy['timestamp'] = event['timestamp'].isoformat()
                events_data.append(event_copy)

            data = {
                'events': events_data,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.persist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError):
            # If persistence fails, continue without it
            pass

    def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event with timestamp."""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'data': data
        }
        with self._lock:
            self.events.append(event)
            self._dirty = True
            self._schedule_persist()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events without memory churn."""
        # Reload from file to get latest events from other processes
        with self._lock:
            self._load_persisted_events()
            return list(self.events)[-limit:] if limit < len(self.events) else list(self.events)

    def _schedule_persist(self):
        """Schedule persistence after a delay to batch multiple events."""
        if self._persist_timer and self._persist_timer.is_alive():
            self._persist_timer.cancel()

        self._persist_timer = threading.Timer(
            self._batch_interval, self._persist_if_dirty)
        self._persist_timer.start()

    def _persist_if_dirty(self):
        """Persist events only if there are changes."""
        with self._lock:
            if self._dirty:
                self._persist_events()
                self._dirty = False

    def cleanup(self):
        """Clean up timer resources."""
        if self._persist_timer and self._persist_timer.is_alive():
            self._persist_timer.cancel()
        # Persist any remaining dirty events before cleanup
        if self._dirty:
            self._persist_events()


# Global broadcaster instance
broadcaster = EventBroadcaster()
