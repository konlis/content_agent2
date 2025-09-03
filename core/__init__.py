"""
Core module initialization
"""

from .base_module import BaseModule, ModuleInfo
from .dependency_injection import Container
from .event_system import EventBus, Event
from .module_registry import ModuleRegistry

__all__ = [
    'BaseModule',
    'ModuleInfo', 
    'Container',
    'EventBus',
    'Event',
    'ModuleRegistry'
]
