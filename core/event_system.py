"""
Event System for Inter-Module Communication
Provides async event bus for decoupled module communication
"""

from typing import Dict, List, Callable, Any, Optional
import asyncio
from loguru import logger
from datetime import datetime
import uuid

class Event:
    """Represents an event with metadata"""
    
    def __init__(self, name: str, data: Dict[str, Any], source: str = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()

class EventBus:
    """
    Async event bus for inter-module communication
    Supports event subscription, emission, and middleware
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
        self._logger = logger.bind(component="EventBus")
        self._event_history: List[Event] = []
        self._max_history = 1000
        
    def subscribe(self, event_name: str, callback: Callable[[Event], Any]) -> str:
        """
        Subscribe to an event
        Returns subscription ID that can be used to unsubscribe
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        subscription_id = f"{event_name}_{len(self._subscribers[event_name])}"
        self._subscribers[event_name].append(callback)
        
        self._logger.debug(f"Subscribed to event: {event_name}")
        return subscription_id
    
    def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        """Unsubscribe from an event"""
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(callback)
                self._logger.debug(f"Unsubscribed from event: {event_name}")
                return True
            except ValueError:
                pass
        return False
    
    async def emit(self, event_name: str, data: Dict[str, Any], source: str = None) -> None:
        """Emit an event to all subscribers"""
        event = Event(event_name, data, source)
        
        # Add to history
        self._add_to_history(event)
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(event)
                else:
                    await asyncio.to_thread(middleware, event)
            except Exception as e:
                self._logger.error(f"Middleware error for event {event_name}: {e}")
        
        # Notify subscribers
        if event_name in self._subscribers:
            tasks = []
            for callback in self._subscribers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(event))
                    else:
                        tasks.append(asyncio.to_thread(callback, event))
                except Exception as e:
                    self._logger.error(f"Error preparing callback for event {event_name}: {e}")
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log any exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self._logger.error(f"Event handler error for {event_name}: {result}")
        
        self._logger.debug(f"Emitted event: {event_name} with {len(data)} data items")
    
    def add_middleware(self, middleware: Callable[[Event], Any]) -> None:
        """Add middleware that processes all events"""
        self._middleware.append(middleware)
        self._logger.debug("Added event middleware")
    
    def get_event_history(self, event_name: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by event name"""
        history = self._event_history[-limit:]
        
        if event_name:
            history = [event for event in history if event.name == event_name]
        
        return history
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
        self._logger.debug("Cleared event history")
    
    def get_subscribers_count(self, event_name: str) -> int:
        """Get number of subscribers for an event"""
        return len(self._subscribers.get(event_name, []))
    
    def list_events(self) -> List[str]:
        """List all events that have subscribers"""
        return list(self._subscribers.keys())
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size limit"""
        self._event_history.append(event)
        
        # Trim history if too large
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

# Event middleware examples
class LoggingMiddleware:
    """Middleware that logs all events"""
    
    def __init__(self):
        self.logger = logger.bind(component="EventMiddleware")
    
    async def __call__(self, event: Event):
        self.logger.info(f"Event: {event.name} from {event.source or 'unknown'}")

class EventValidationMiddleware:
    """Middleware that validates event data"""
    
    def __init__(self, validators: Dict[str, Callable]):
        self.validators = validators
        self.logger = logger.bind(component="EventValidation")
    
    async def __call__(self, event: Event):
        if event.name in self.validators:
            try:
                self.validators[event.name](event.data)
            except Exception as e:
                self.logger.error(f"Event validation failed for {event.name}: {e}")
                raise
