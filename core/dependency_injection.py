"""
Dependency Injection Container for Content Agent
Provides centralized service management and dependency resolution
"""

from typing import Dict, Any, Optional, TypeVar, Type, Callable
from loguru import logger
import inspect

T = TypeVar('T')

class Container:
    """
    Simple dependency injection container
    Manages service registration, resolution, and lifecycle
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._logger = logger.bind(component="DI_Container")
        
    def register(self, name: str, instance: Any) -> None:
        """Register a service instance"""
        self._services[name] = instance
        self._logger.debug(f"Registered service: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """Register a factory function for lazy initialization"""
        self._factories[name] = factory
        self._logger.debug(f"Registered factory: {name}")
    
    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """Register a singleton factory"""
        self._factories[name] = factory
        self._singletons[name] = None
        self._logger.debug(f"Registered singleton: {name}")
    
    def get(self, name: str) -> Any:
        """Get a service by name"""
        # Check if it's a direct service
        if name in self._services:
            return self._services[name]
        
        # Check if it's a singleton
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        
        # Check if it's a factory
        if name in self._factories:
            return self._factories[name]()
        
        raise ServiceNotFoundError(f"Service '{name}' not found")
    
    def has(self, name: str) -> bool:
        """Check if a service is registered"""
        return (name in self._services or 
                name in self._factories or 
                name in self._singletons)
    
    def remove(self, name: str) -> bool:
        """Remove a service from the container"""
        removed = False
        
        if name in self._services:
            del self._services[name]
            removed = True
        
        if name in self._factories:
            del self._factories[name]
            removed = True
        
        if name in self._singletons:
            del self._singletons[name]
            removed = True
        
        if removed:
            self._logger.debug(f"Removed service: {name}")
        
        return removed
    
    def list_services(self) -> Dict[str, str]:
        """List all registered services"""
        services = {}
        
        for name in self._services:
            services[name] = "instance"
        
        for name in self._factories:
            if name in self._singletons:
                services[name] = "singleton"
            else:
                services[name] = "factory"
        
        return services
    
    def auto_wire(self, cls: Type[T]) -> T:
        """
        Auto-wire constructor dependencies
        Experimental feature for automatic dependency injection
        """
        try:
            # Get constructor signature
            sig = inspect.signature(cls.__init__)
            kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Try to resolve dependency
                if self.has(param_name):
                    kwargs[param_name] = self.get(param_name)
                elif param.default != inspect.Parameter.empty:
                    # Use default value if available
                    continue
                else:
                    raise DependencyResolutionError(
                        f"Cannot resolve dependency '{param_name}' for {cls.__name__}"
                    )
            
            return cls(**kwargs)
        except Exception as e:
            self._logger.error(f"Auto-wire failed for {cls.__name__}: {e}")
            raise

class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found"""
    pass

class DependencyResolutionError(Exception):
    """Raised when dependency resolution fails"""
    pass
