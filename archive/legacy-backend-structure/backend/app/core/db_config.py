"""
Centralized Database Configuration
Single source of truth for all database settings
"""

import os
from typing import Optional
from urllib.parse import urlparse

class DatabaseConfig:
    """Centralized database configuration management"""
    
    def __init__(self):
        self._database_url: Optional[str] = None
        self._parsed_url: Optional[object] = None
    
    @property
    def database_url(self) -> str:
        """Get the standardized database URL"""
        if self._database_url is None:
            self._database_url = self._resolve_database_url()
        return self._database_url
    
    @property
    def async_database_url(self) -> str:
        """Get the async version of the database URL"""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        elif url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        return url
    
    @property
    def sync_database_url(self) -> str:
        """Get the sync version of the database URL"""
        url = self.database_url
        if "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql://")
        elif "sqlite+aiosqlite:///" in url:
            return url.replace("sqlite+aiosqlite:///", "sqlite:///")
        return url
    
    def _resolve_database_url(self) -> str:
        """Resolve database URL from environment variables with fallback priority"""
        
        # Priority order for database URL resolution
        url_sources = [
            os.getenv("DATABASE_URL"),
            os.getenv("POSTGRES_URL"), 
            os.getenv("DB_URL"),
            "postgresql://marketmind:password@localhost:5432/marketmind_pro"  # Default
        ]
        
        for url in url_sources:
            if url and url.strip():
                return self._validate_and_normalize_url(url.strip())
        
        # Fallback to SQLite if no PostgreSQL URL works
        return "sqlite:///./marketmind.db"
    
    def _validate_and_normalize_url(self, url: str) -> str:
        """Validate and normalize database URL"""
        try:
            parsed = urlparse(url)
            
            # Ensure we have a valid scheme
            if parsed.scheme not in ['postgresql', 'postgres', 'sqlite']:
                raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
            
            # Normalize postgres schemes
            if parsed.scheme == 'postgres':
                url = url.replace('postgres://', 'postgresql://')
            
            return url
            
        except Exception as e:
            print(f"Warning: Invalid database URL '{url}': {e}")
            return "sqlite:///./marketmind.db"
    
    def get_alembic_url(self) -> str:
        """Get URL specifically formatted for Alembic"""
        return self.sync_database_url
    
    def get_connection_params(self) -> dict:
        """Get connection parameters as dictionary"""
        url = self.database_url
        parsed = urlparse(url)
        
        if parsed.scheme.startswith('postgresql'):
            return {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 5432,
                'database': parsed.path.lstrip('/') if parsed.path else 'marketmind_pro',
                'username': parsed.username or 'marketmind',
                'password': parsed.password or 'password'
            }
        elif parsed.scheme.startswith('sqlite'):
            return {
                'database': parsed.path
            }
        
        return {}

# Global database configuration instance
db_config = DatabaseConfig()