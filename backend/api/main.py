"""
FastAPI Backend Main Application
Creates and configures the FastAPI app with module routes
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import time
from loguru import logger

from shared.config.settings import get_settings

def create_app(container, module_registry) -> FastAPI:
    """
    Create and configure FastAPI application
    """
    settings = get_settings()
    
    # Create FastAPI instance
    app = FastAPI(
        title="Content Agent API",
        description="AI-Powered Content Generation Platform",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:8501"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Store container and module registry in app state
    app.state.container = container
    app.state.module_registry = module_registry
    
    # Register core routes
    @app.get("/")
    async def root():
        return {
            "message": "Content Agent API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "modules": {}
        }
        
        # Check module health
        if module_registry:
            module_health = await module_registry.health_check_all()
            health_data["modules"] = module_health
        
        return health_data
    
    @app.get("/modules")
    async def list_modules():
        """List all loaded modules"""
        if not module_registry:
            return {"modules": []}
        
        modules_info = {}
        for name, module in module_registry.get_all_modules().items():
            modules_info[name] = {
                "name": module.get_module_info().name,
                "version": module.get_module_info().version,
                "description": module.get_module_info().description,
                "initialized": module.is_initialized()
            }
        
        return {"modules": modules_info}
    
    # Register module routes
    if module_registry:
        for module_name, module in module_registry.get_all_modules().items():
            try:
                module.register_routes(app)
                logger.info(f"Registered routes for module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to register routes for {module_name}: {e}")
    
    return app

# Dependency to get container
def get_container():
    """Dependency to get DI container"""
    # This would be injected properly in a real request context
    pass

# Dependency to get specific services
def get_service(service_name: str):
    """Dependency to get a specific service"""
    # This would use the container to get services
    pass
