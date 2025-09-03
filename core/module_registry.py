"""
Module Registry for Dynamic Module Loading
Handles discovery, loading, and management of feature modules
"""

import importlib
import os
import sys
from typing import Dict, List, Optional, Set
from pathlib import Path
from loguru import logger

from .base_module import BaseModule, ModuleInfo
from .dependency_injection import Container

class ModuleRegistry:
    """
    Manages dynamic loading and lifecycle of feature modules
    Handles dependencies, initialization order, and health monitoring
    """
    
    def __init__(self, container: Container):
        self.container = container
        self.modules: Dict[str, BaseModule] = {}
        self.module_order: List[str] = []
        self.failed_modules: Set[str] = set()
        self.logger = logger.bind(component="ModuleRegistry")
        
    async def discover_and_load_modules(self, modules_path: str = "modules") -> Dict[str, bool]:
        """
        Automatically discover and load all modules
        Returns dict of module_name -> success status
        """
        results = {}
        
        if not os.path.exists(modules_path):
            self.logger.warning(f"Modules directory not found: {modules_path}")
            return results
        
        # Discover available modules
        discovered_modules = self._discover_modules(modules_path)
        self.logger.info(f"Discovered {len(discovered_modules)} modules: {list(discovered_modules.keys())}")
        
        # Calculate load order based on dependencies
        load_order = self._calculate_load_order(discovered_modules)
        
        # Load modules in dependency order
        for module_name in load_order:
            try:
                success = await self.load_module(module_name)
                results[module_name] = success
                
                if success:
                    self.logger.info(f"Successfully loaded module: {module_name}")
                else:
                    self.logger.error(f"Failed to load module: {module_name}")
                    
            except Exception as e:
                self.logger.error(f"Error loading module {module_name}: {e}")
                results[module_name] = False
                self.failed_modules.add(module_name)
        
        return results
    
    async def load_module(self, module_name: str) -> bool:
        """Load a specific module by name"""
        try:
            # Import module
            module_path = f"modules.{module_name}.module"
            
            # Add current directory to Python path if needed
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            module_lib = importlib.import_module(module_path)
            
            # Find the module class (should follow naming convention)
            module_class_name = f"{''.join(word.capitalize() for word in module_name.split('_'))}Module"
            
            if not hasattr(module_lib, module_class_name):
                self.logger.error(f"Module class {module_class_name} not found in {module_path}")
                return False
            
            module_class = getattr(module_lib, module_class_name)
            
            # Create module instance
            module_instance = module_class(self.container)
            
            # Check dependencies
            if not await self._check_dependencies(module_instance):
                self.logger.error(f"Dependencies not satisfied for module: {module_name}")
                return False
            
            # Initialize module
            if await module_instance.initialize():
                self.modules[module_name] = module_instance
                module_instance._initialized = True
                
                # Register in container
                self.container.register(f"{module_name}_module", module_instance)
                
                self._update_load_order()
                return True
            else:
                self.logger.error(f"Module initialization failed: {module_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {e}")
            self.failed_modules.add(module_name)
            return False
    
    def _calculate_load_order(self, modules: Dict[str, ModuleInfo]) -> List[str]:
        """Calculate module load order based on dependencies"""
        ordered = []
        remaining = set(modules.keys())
        
        while remaining:
            # Find modules with no unresolved dependencies
            ready = []
            
            for module_name in remaining:
                module_info = modules[module_name]
                deps = module_info.dependencies or []
                
                # Check if all dependencies are already loaded or don't exist
                unresolved_deps = [dep for dep in deps if dep in remaining]
                
                if not unresolved_deps:
                    ready.append(module_name)
            
            if not ready:
                # Circular dependency or missing dependency
                self.logger.warning(f"Circular dependency detected or missing dependencies for: {remaining}")
                # Add remaining modules anyway (might fail at load time)
                ready = list(remaining)
            
            # Add ready modules to order and remove from remaining
            ordered.extend(ready)
            remaining -= set(ready)
        
        return ordered
    
    def _discover_modules(self, modules_path: str) -> Dict[str, ModuleInfo]:
        """Discover available modules in the modules directory"""
        discovered = {}
        
        for item in os.listdir(modules_path):
            module_dir = os.path.join(modules_path, item)
            
            if os.path.isdir(module_dir) and not item.startswith('_'):
                module_file = os.path.join(module_dir, 'module.py')
                
                if os.path.exists(module_file):
                    try:
                        # Try to get module info without full import
                        info = self._get_module_info_safe(item)
                        if info:
                            discovered[item] = info
                    except Exception as e:
                        self.logger.warning(f"Could not get info for module {item}: {e}")
        
        return discovered
    
    async def _check_dependencies(self, module: BaseModule) -> bool:
        """Check if module dependencies are satisfied"""
        info = module.get_module_info()
        
        for dep in info.dependencies:
            if dep not in self.modules:
                self.logger.error(f"Missing dependency '{dep}' for module '{info.name}'")
                return False
        return True
    
    def _update_load_order(self):
        """Update the module load order"""
        self.module_order = list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """Get a loaded module by name"""
        return self.modules.get(name)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """Get all loaded modules"""
        return self.modules.copy()
