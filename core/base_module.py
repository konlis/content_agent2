"""
Core Base Module for Content Agent
Provides the foundation for all feature modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class ModuleInfo:
    """Module metadata information"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    optional_dependencies: List[str] = None
    author: str = "Content Agent Team"

class BaseModule(ABC):
    """
    Base class for all Content Agent modules
    Provides common functionality and enforces module interface
    """
    
    def __init__(self, container):
        self.container = container
        self.config = container.get('config')
        self.logger = logger.bind(module=self.__class__.__name__)
        self.event_bus = container.get('event_bus')
        self._initialized = False
        
    @abstractmethod
    def get_module_info(self) -> ModuleInfo:
        """Return module information and dependencies"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize module - return True if successful"""
        pass
    
    @abstractmethod
    def register_routes(self, app):
        """Register FastAPI routes for this module"""
        pass
    
    @abstractmethod
    def register_ui_components(self) -> Dict[str, Any]:
        """Register Streamlit UI components for this module"""
        pass
    
    async def cleanup(self):
        """Cleanup resources when module is unloaded"""
        self._initialized = False
    
    def emit_event(self, event_name: str, data: Dict[str, Any]):
        """Emit event to other modules"""
        try:
            self.event_bus.emit(f"{self.get_module_info().name}.{event_name}", data)
        except Exception as e:
            self.logger.error(f"Failed to emit event {event_name}: {e}")
    
    def subscribe_to_event(self, event_name: str, callback):
        """Subscribe to events from other modules"""
        try:
            self.event_bus.subscribe(event_name, callback)
        except Exception as e:
            self.logger.error(f"Failed to subscribe to event {event_name}: {e}")
    
    def is_initialized(self) -> bool:
        """Check if module is properly initialized"""
        return self._initialized
    
    def get_service(self, service_name: str):
        """Get a service from the DI container"""
        return self.container.get(service_name)
    
    def register_service(self, service_name: str, service_instance):
        """Register a service in the DI container"""
        self.container.register(service_name, service_instance)
    
    async def health_check(self) -> Dict[str, Any]:
        """Basic health check for the module"""
        return {
            "module": self.get_module_info().name,
            "status": "healthy" if self._initialized else "not_initialized",
            "version": self.get_module_info().version
        }
