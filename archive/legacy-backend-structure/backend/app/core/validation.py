from typing import Optional, Dict, Any
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataValidator:
    """Validate and sanitize financial data"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate stock symbol format"""
        if not symbol or len(symbol) > 10:
            return False
        return re.match(r'^[A-Z]{1,5}$', symbol.upper()) is not None
    
    @staticmethod
    def sanitize_symbol(symbol: str) -> str:
        """Clean and format symbol"""
        return symbol.upper().strip()
    
    @staticmethod
    def validate_price_data(data: Dict[str, Any]) -> bool:
        """Validate price data structure"""
        required_fields = ['price', 'change', 'volume']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def sanitize_financial_value(value: Any) -> Optional[float]:
        """Sanitize financial values"""
        try:
            if value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

class ErrorHandler:
    """Handle and log errors consistently"""
    
    @staticmethod
    def log_api_error(source: str, symbol: str, error: Exception):
        """Log API errors with context"""
        logger.error(f"API Error [{source}] for {symbol}: {str(error)}")
    
    @staticmethod
    def log_cache_error(operation: str, key: str, error: Exception):
        """Log cache errors"""
        logger.error(f"Cache Error [{operation}] for {key}: {str(error)}")
    
    @staticmethod
    def log_validation_error(field: str, value: Any, error: str):
        """Log validation errors"""
        logger.warning(f"Validation Error [{field}]: {value} - {error}")

# Rate limiting decorator
import asyncio
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int = 60, window_minutes: int = 1):
        self.max_calls = max_calls
        self.window = timedelta(minutes=window_minutes)
        self.calls = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = datetime.now()
        # Clean old calls
        self.calls[key] = [call_time for call_time in self.calls[key] 
                          if now - call_time < self.window]
        
        if len(self.calls[key]) >= self.max_calls:
            return False
            
        self.calls[key].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(key_func=lambda *args, **kwargs: "default"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if not rate_limiter.is_allowed(key):
                raise Exception(f"Rate limit exceeded for {key}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator