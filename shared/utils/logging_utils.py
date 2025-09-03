"""
Centralized Logging Utilities
Standardized logging patterns for Content Agent services
"""

from loguru import logger
from typing import Dict, Any, Optional
import traceback

class ServiceLogger:
    """Centralized service logger with standardized patterns"""
    
    def __init__(self, service_name: str):
        self.logger = logger.bind(service=service_name)
    
    def service_start(self, operation: str, **context):
        """Log service operation start"""
        context_str = " ".join([f"{k}={v}" for k, v in context.items()])
        self.logger.info(f"Starting {operation} {context_str}".strip())
    
    def service_success(self, operation: str, **context):
        """Log service operation success"""
        context_str = " ".join([f"{k}={v}" for k, v in context.items()])
        self.logger.info(f"Successfully completed {operation} {context_str}".strip())
    
    def service_error(self, operation: str, error: Exception, **context):
        """Log service operation error with standardized format"""
        context_str = " ".join([f"{k}={v}" for k, v in context.items()])
        error_msg = f"Failed to {operation} {context_str}".strip()
        
        # Log with full error details
        self.logger.error(f"{error_msg}: {str(error)}")
        
        # Log traceback for debugging
        self.logger.debug(f"Traceback for {operation}: {traceback.format_exc()}")
    
    def service_warning(self, operation: str, warning: str, **context):
        """Log service operation warning"""
        context_str = " ".join([f"{k}={v}" for k, v in context.items()])
        self.logger.warning(f"Warning in {operation} {context_str}: {warning}".strip())
    
    def health_check(self, status: bool, details: str = ""):
        """Log health check results"""
        if status:
            self.logger.info(f"Health check passed: {details}".strip())
        else:
            self.logger.error(f"Health check failed: {details}".strip())
    
    def performance_metric(self, operation: str, duration_ms: float, **context):
        """Log performance metrics"""
        context_str = " ".join([f"{k}={v}" for k, v in context.items()])
        self.logger.info(f"Performance: {operation} took {duration_ms:.2f}ms {context_str}".strip())

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def handle_service_error(operation: str, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Standardized error handling for services"""
        error_info = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": logger._core.now().isoformat()
        }
        
        # Log the error
        logger.error(f"Service error in {operation}: {error}")
        
        return error_info
    
    @staticmethod
    def is_recoverable_error(error: Exception) -> bool:
        """Determine if an error is recoverable"""
        recoverable_types = (
            ConnectionError,
            TimeoutError,
            OSError,
            ValueError,
            KeyError,
            IndexError
        )
        
        return isinstance(error, recoverable_types)
    
    @staticmethod
    def get_error_context(error: Exception) -> Dict[str, Any]:
        """Extract useful context from an error"""
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }

# Convenience functions for quick logging
def log_service_start(service_name: str, operation: str, **context):
    """Quick logging for service start"""
    ServiceLogger(service_name).service_start(operation, **context)

def log_service_success(service_name: str, operation: str, **context):
    """Quick logging for service success"""
    ServiceLogger(service_name).service_success(operation, **context)

def log_service_error(service_name: str, operation: str, error: Exception, **context):
    """Quick logging for service error"""
    ServiceLogger(service_name).service_error(operation, error, **context)

def log_health_check(service_name: str, status: bool, details: str = ""):
    """Quick logging for health checks"""
    ServiceLogger(service_name).health_check(status, details)
