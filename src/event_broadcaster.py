"""
Event broadcasting system for real-time UI updates.
"""
import queue
import threading
from typing import Dict, Any
from datetime import datetime


class EventBroadcaster:
    """Thread-safe event broadcaster for real-time UI updates."""
    
    def __init__(self):
        self.events = queue.Queue(maxsize=100)
        self._lock = threading.Lock()
    
    def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event with timestamp."""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'data': data
        }
        try:
            self.events.put_nowait(event)
        except queue.Full:
            # Remove oldest event to make room
            try:
                self.events.get_nowait()
                self.events.put_nowait(event)
            except queue.Empty:
                pass
    
    def get_recent_events(self, limit: int = 50):
        """Get recent events without removing them from queue."""
        events = []
        temp_events = []
        
        with self._lock:
            # Drain queue
            while not self.events.empty() and len(events) < limit:
                try:
                    event = self.events.get_nowait()
                    events.append(event)
                    temp_events.append(event)
                except queue.Empty:
                    break
            
            # Put events back
            for event in reversed(temp_events):
                try:
                    self.events.put_nowait(event)
                except queue.Full:
                    break
        
        return list(reversed(events))


# Global broadcaster instance
broadcaster = EventBroadcaster()