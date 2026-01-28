from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/marketmind_pro"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = ""
    SEC_EDGAR_USER_AGENT: str = "MarketMind Pro support@marketmind.com"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-jwt-secret-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Cache Settings
    CACHE_TTL_SECONDS: int = 900  # 15 minutes
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()