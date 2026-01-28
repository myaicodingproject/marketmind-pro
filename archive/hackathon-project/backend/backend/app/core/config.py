"""
Configuration Settings for MarketMind Pro
Includes Kiro CLI integration and process management settings
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field

class Settings(BaseModel):
    """Application settings"""
    
    # Application
    app_name: str = "MarketMind Pro"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/marketmind_pro")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])
    
    # Security
    secret_key: str = Field(default="your-secret-key-here")
    jwt_secret_key: str = Field(default="your-jwt-secret-here")
    
    # Kiro CLI Integration
    kiro_cli_path: str = Field(default="kiro-cli")
    kiro_workspace_path: str = Field(default="/tmp/kiro_workspace")
    
    # Process Management
    max_concurrent_processes: int = Field(default=3)
    max_process_memory_mb: int = Field(default=2048)
    process_timeout_seconds: int = Field(default=300)
    max_queue_size: int = Field(default=100)
    max_workers: int = Field(default=3)
    
    # User Quotas
    max_user_concurrent: int = Field(default=2)
    max_user_hourly: int = Field(default=10)
    max_user_daily: int = Field(default=50)
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default=None)
    SEC_EDGAR_USER_AGENT: Optional[str] = Field(default=None)
    
    # AWS (for file storage)
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket_name: Optional[str] = Field(default=None)
    
    # Report Generation (Legacy)
    max_concurrent_reports: int = Field(default=3)
    report_timeout_minutes: int = Field(default=30)
    
    def __init__(self, **kwargs):
        # Load from environment variables
        env_values = {}
        for field_name, field_info in self.__fields__.items():
            env_name = field_name.upper()
            env_value = os.getenv(env_name)
            if env_value is not None:
                # Convert to appropriate type
                if field_info.type_ == int:
                    try:
                        env_values[field_name] = int(env_value)
                    except ValueError:
                        pass
                elif field_info.type_ == bool:
                    env_values[field_name] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif field_info.type_ == List[str]:
                    env_values[field_name] = [s.strip() for s in env_value.split(',')]
                else:
                    env_values[field_name] = env_value
        
        # Merge with provided kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)

settings = Settings()