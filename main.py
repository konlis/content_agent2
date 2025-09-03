"""
Main Application Entry Point
Initializes and runs the Content Agent application
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import Container, EventBus, ModuleRegistry
from shared.config.settings import get_settings, create_directories
from shared.database.models import init_database
from loguru import logger

class ContentAgent:
    """
    Main application class for Content Agent
    Orchestrates backend, frontend, and module systems
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.container = Container()
        self.module_registry = None
        self.logger = logger.bind(component="ContentAgent")
        
        # Setup logging
        self._setup_logging()
        
        # Setup dependency injection
        self._setup_dependencies()
    
    def _setup_logging(self):
        """Configure application logging"""
        logger.remove()  # Remove default handler
        
        # Console logging
        logger.add(
            sys.stdout,
            level=self.settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
        # File logging
        create_directories()  # Ensure logs directory exists
        logger.add(
            self.settings.log_file,
            level=self.settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        self.logger.info("Logging configured")
    
    def _setup_dependencies(self):
        """Setup dependency injection container"""
        # Core services
        self.container.register('config', self.settings)
        self.container.register('event_bus', EventBus())
        self.container.register('logger', logger)
        
        # Database (placeholder - would setup real connections)
        # self.container.register('database', database_connection)
        # self.container.register('redis', redis_connection)
        
        self.logger.info("Dependencies configured")
    
    async def initialize(self):
        """Initialize the application"""
        try:
            self.logger.info("Initializing Content Agent...")
            
            # Create necessary directories
            create_directories()
            
            # Initialize database (placeholder)
            # init_database()
            
            # Initialize module registry
            self.module_registry = ModuleRegistry(self.container)
            self.container.register('module_registry', self.module_registry)
            
            # Load modules
            await self.module_registry.discover_and_load_modules()
            
            self.logger.info("Content Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Agent: {e}")
            return False
    
    async def start_backend(self):
        """Start the FastAPI backend server"""
        try:
            import uvicorn
            from backend.api.main import create_app
            
            # Create FastAPI app with loaded modules
            app = create_app(self.container, self.module_registry)
            
            # Run server
            config = uvicorn.Config(
                app=app,
                host="0.0.0.0",
                port=8000,
                log_level=self.settings.log_level.lower()
            )
            server = uvicorn.Server(config)
            
            self.logger.info("Starting FastAPI backend on http://0.0.0.0:8000")
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"Failed to start backend: {e}")
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        try:
            import subprocess
            import sys
            
            # Get the frontend app path
            frontend_path = project_root / "frontend" / "app.py"
            
            self.logger.info("Starting Streamlit frontend...")
            
            # Start Streamlit
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                str(frontend_path),
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ]
            
            subprocess.run(cmd)
            
        except Exception as e:
            self.logger.error(f"Failed to start frontend: {e}")
    
    async def run_async(self):
        """Run the application in async mode (backend only)"""
        if await self.initialize():
            await self.start_backend()
        else:
            self.logger.error("Failed to initialize, exiting...")
            sys.exit(1)
    
    def run(self, mode: str = "frontend"):
        """
        Run the application
        Modes: 'frontend' (Streamlit), 'backend' (FastAPI), 'both'
        """
        if mode == "frontend":
            # Run Streamlit frontend (blocking)
            asyncio.run(self.initialize())
            self.start_frontend()
            
        elif mode == "backend":
            # Run FastAPI backend (async)
            asyncio.run(self.run_async())
            
        elif mode == "both":
            # Run both (would need process management)
            self.logger.info("Running both frontend and backend...")
            # This would require proper process management
            # For now, just run frontend
            asyncio.run(self.initialize())
            self.start_frontend()
        
        else:
            self.logger.error(f"Unknown mode: {mode}")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Content Agent - AI-Powered Content Generation Platform")
    parser.add_argument(
        "--mode", 
        choices=["frontend", "backend", "both"], 
        default="frontend",
        help="Run mode: frontend (Streamlit), backend (FastAPI), or both"
    )
    
    args = parser.parse_args()
    
    # Create and run the application
    app = ContentAgent()
    app.run(mode=args.mode)

if __name__ == "__main__":
    main()
