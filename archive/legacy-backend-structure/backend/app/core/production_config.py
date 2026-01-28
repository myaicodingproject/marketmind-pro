"""
MarketMind Pro Production Configuration
Centralized configuration management for all components
"""

import os
from typing import List, Optional
from pydantic import BaseSettings
from .db_config import db_config

class Settings(BaseSettings):
    """Production settings with environment variable support"""
    
    # Application
    APP_NAME: str = "MarketMind Pro"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database - using centralized configuration
    @property
    def DATABASE_URL(self) -> str:
        return db_config.database_url
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 900  # 15 minutes
    
    # External APIs
    SEC_EDGAR_USER_AGENT: str = "MarketMind Pro research@marketmind.com"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/marketmind_production.log"
    
    # Report Generation
    MAX_CONCURRENT_REPORTS: int = 5
    REPORT_TIMEOUT_MINUTES: int = 30
    
    # Quality Gates
    MIN_CONTENT_LENGTH: int = 200
    MIN_QUALITY_SCORE: float = 75.0
    
    # File Storage
    REPORTS_DIR: str = "reports"
    DATA_DIR: str = "data"
    STATIC_DIR: str = "static"
    
    # WebSocket
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    WORKERS: int = 1

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 4
    
    # Production security
    CORS_ORIGINS: List[str] = [
        "https://marketmind.com",
        "https://app.marketmind.com"
    ]

class TestingSettings(Settings):
    DEBUG: bool = True
    
    @property
    def DATABASE_URL(self) -> str:
        # Override for testing to use test database
        return "sqlite:///./test.db"

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Export the appropriate settings
settings = get_settings()