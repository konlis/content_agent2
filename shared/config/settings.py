"""
Configuration management for Content Agent
Handles environment variables, settings, and configuration validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Application Info
    app_name: str = Field(default="Content Agent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    serpapi_key: Optional[str] = Field(None, env="SERPAPI_KEY")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/content_agent",
        env="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # WordPress Configuration
    wordpress_url: Optional[str] = Field(None, env="WORDPRESS_URL")
    wordpress_username: Optional[str] = Field(None, env="WORDPRESS_USERNAME")
    wordpress_app_password: Optional[str] = Field(None, env="WORDPRESS_APP_PASSWORD")
    wordpress_use_blocks: bool = Field(default=True, env="WORDPRESS_USE_BLOCKS")
    
    # Rate Limits & Cost Control
    daily_user_limit: int = Field(default=50, env="DAILY_USER_LIMIT")
    cost_per_user_limit: float = Field(default=10.0, env="COST_PER_USER_LIMIT")
    default_model_tier: str = Field(default="research", env="DEFAULT_MODEL_TIER")
    enable_local_fallback: bool = Field(default=True, env="ENABLE_LOCAL_FALLBACK")
    
    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/content_agent.log", env="LOG_FILE")
    
    # Model Configuration
    model_costs: dict = Field(default={
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015}
    })
    
    # Content Generation Settings
    default_content_length: int = Field(default=1000, env="DEFAULT_CONTENT_LENGTH")
    max_content_length: int = Field(default=5000, env="MAX_CONTENT_LENGTH")
    default_tone: str = Field(default="professional", env="DEFAULT_TONE")
    
    # Scraping Configuration
    scraping_delay: float = Field(default=1.0, env="SCRAPING_DELAY")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Scheduling Settings
    max_scheduled_posts: int = Field(default=100, env="MAX_SCHEDULED_POSTS")
    scheduling_timezone: str = Field(default="UTC", env="SCHEDULING_TIMEZONE")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level. Must be one of: {valid_levels}')
        return v.upper()
    
    @validator('default_model_tier')
    def validate_model_tier(cls, v):
        valid_tiers = ['research', 'draft', 'final']
        if v not in valid_tiers:
            raise ValueError(f'Invalid model tier. Must be one of: {valid_tiers}')
        return v
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'sqlite:///')):
            raise ValueError('Database URL must start with postgresql:// or sqlite:///')
        return v
    
    def get_model_for_tier(self, tier: str) -> str:
        """Get the model name for a given tier"""
        tier_models = {
            "research": "gpt-4o-mini",
            "draft": "claude-3-haiku", 
            "final": "gpt-4o"
        }
        return tier_models.get(tier, "gpt-4o-mini")
    
    def get_model_cost(self, model: str, token_type: str = "input") -> float:
        """Get cost per token for a model"""
        return self.model_costs.get(model, {}).get(token_type, 0.0)
    
    def is_api_key_configured(self, service: str) -> bool:
        """Check if API key is configured for a service"""
        key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "serpapi": self.serpapi_key
        }
        return key_mapping.get(service) is not None
    
    def get_wordpress_config(self) -> dict:
        """Get WordPress configuration as dict"""
        return {
            "url": self.wordpress_url,
            "username": self.wordpress_username,
            "app_password": self.wordpress_app_password,
            "use_blocks": self.wordpress_use_blocks
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "uploads",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
