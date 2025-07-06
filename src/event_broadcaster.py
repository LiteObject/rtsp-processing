"""
Event broadcasting system for real-time UI updates.
"""
import collections
import threading
from typing import Dict, Any, List
from datetime import datetime


class EventBroadcaster:
    """Thread-safe event broadcaster for real-time UI updates."""
    
    def __init__(self, max_events: int = 100):
        self.events = collections.deque(maxlen=max_events)
        self._lock = threading.Lock()
    
    def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event with timestamp."""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'data': data
        }
        with self._lock:
            self.events.append(event)
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events without memory churn."""
        with self._lock:
            return list(self.events)[-limit:] if limit < len(self.events) else list(self.events)


# Global broadcaster instance
broadcaster = EventBroadcaster()