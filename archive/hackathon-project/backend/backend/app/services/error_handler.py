"""
Error Handling and Retry Logic for Kiro Integration
Provides robust error handling, retry mechanisms, and graceful degradation
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class KiroIntegrationError(Exception):
    """Base exception for Kiro integration errors"""
    pass

class KiroTimeoutError(KiroIntegrationError):
    """Raised when Kiro execution times out"""
    pass

class KiroValidationError(KiroIntegrationError):
    """Raised when Kiro validation fails"""
    pass

class KiroResourceError(KiroIntegrationError):
    """Raised when system resources are insufficient"""
    pass

class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class ErrorHandler:
    """Centralized error handling for Kiro integration"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self.circuit_breakers = {}
    
    def classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate handling"""
        
        error_str = str(error).lower()
        
        if isinstance(error, asyncio.TimeoutError) or 'timeout' in error_str:
            return 'timeout'
        elif 'connection' in error_str or 'network' in error_str:
            return 'network'
        elif 'memory' in error_str or 'resource' in error_str:
            return 'resource'
        elif 'permission' in error_str or 'access' in error_str:
            return 'permission'
        elif 'not found' in error_str or 'missing' in error_str:
            return 'missing_resource'
        elif isinstance(error, (ValueError, TypeError)):
            return 'validation'
        else:
            return 'unknown'
    
    def should_retry(self, error: Exception, attempt: int, max_attempts: int) -> bool:
        """Determine if an error should trigger a retry"""
        
        error_type = self.classify_error(error)
        
        # Never retry these error types
        if error_type in ['permission', 'validation', 'missing_resource']:
            return False
        
        # Always retry these if attempts remain
        if error_type in ['timeout', 'network', 'resource'] and attempt < max_attempts:
            return True
        
        # For unknown errors, retry up to half max attempts
        if error_type == 'unknown' and attempt < (max_attempts // 2):
            return True
        
        return False
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay before retry"""
        
        delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        delay = min(delay, config.max_delay)
        
        if config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        retry_config: Optional[RetryConfig] = None,
        context: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        
        if retry_config is None:
            retry_config = RetryConfig()
        
        context = context or func.__name__
        last_error = None
        
        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                logger.debug(f"Executing {context}, attempt {attempt}/{retry_config.max_attempts}")
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success - reset error tracking
                if context in self.error_counts:
                    del self.error_counts[context]
                
                logger.info(f"Successfully executed {context} on attempt {attempt}")
                return result
                
            except Exception as e:
                last_error = e
                error_type = self.classify_error(e)
                
                # Track error
                self.error_counts[context] = self.error_counts.get(context, 0) + 1
                self.last_errors[context] = {
                    'error': str(e),
                    'type': error_type,
                    'timestamp': datetime.now(),
                    'attempt': attempt
                }
                
                logger.warning(
                    f"Attempt {attempt} failed for {context}: {error_type} - {str(e)}"
                )
                
                # Check if we should retry
                if not self.should_retry(e, attempt, retry_config.max_attempts):
                    logger.error(f"Not retrying {context} due to error type: {error_type}")
                    break
                
                if attempt < retry_config.max_attempts:
                    delay = self.calculate_delay(attempt, retry_config)
                    logger.info(f"Retrying {context} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max attempts reached for {context}")
        
        # All attempts failed
        logger.error(f"All retry attempts failed for {context}")
        raise last_error

class CircuitBreaker:
    """Circuit breaker pattern for failing services"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise KiroIntegrationError("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                self._on_success()
                return result
                
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

class GracefulDegradation:
    """Provides fallback mechanisms when primary systems fail"""
    
    @staticmethod
    def get_fallback_report_section(section_name: str, ticker: str) -> Dict[str, Any]:
        """Generate fallback content when Kiro execution fails"""
        
        fallback_content = {
            'company-overview-investment-thesis': f"""
# {ticker} - Company Overview & Investment Thesis

## Executive Summary
Analysis for {ticker} is currently unavailable due to system limitations. 
Please try again later or contact support for assistance.

## Investment Thesis
- Comprehensive analysis requires additional data processing
- Manual review recommended for investment decisions
- Technical analysis tools may provide alternative insights

## Recommendation
HOLD - Pending comprehensive analysis completion

## Risk Factors
- Analysis incomplete due to technical limitations
- Market conditions may have changed since last update
- Manual verification of all data points recommended
            """,
            
            'financial-analysis-key-metrics': f"""
# {ticker} - Financial Analysis & Key Metrics

## Financial Performance Summary
Financial data for {ticker} is currently being processed.

**Status**: Analysis in progress
**Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Key Metrics
- Revenue data: Processing...
- Profitability metrics: Processing...
- Growth indicators: Processing...

## Recommendation
Please check back in a few minutes for complete financial analysis.
            """,
            
            'valuation-analysis-price-target': f"""
# {ticker} - Valuation Analysis & Price Target

## Valuation Summary
Valuation models for {ticker} are currently being calculated.

**Current Status**: Model execution in progress
**Expected Completion**: Within 5-10 minutes

## Price Target
- Target calculation: In progress
- Valuation range: To be determined
- Risk assessment: Pending

## Next Steps
- Monitor for analysis completion
- Review alternative data sources
- Consider manual valuation methods
            """,
            
            'risk-assessment-summary': f"""
# {ticker} - Risk Assessment & Summary

## Risk Analysis Status
Comprehensive risk assessment for {ticker} is currently unavailable.

## General Risk Considerations
- Market volatility risk
- Sector-specific risks
- Regulatory environment changes
- Economic conditions impact

## Recommendation
- Conduct manual risk assessment
- Review recent news and filings
- Consult additional research sources
- Consider position sizing carefully

## Summary
Analysis completion pending. Exercise caution with investment decisions.
            """
        }
        
        return {
            'content': fallback_content.get(section_name, f"Fallback content for {section_name} not available"),
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'message': 'Generated fallback content due to system limitations'
        }
    
    @staticmethod
    def get_partial_report(completed_sections: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Generate partial report when some sections fail"""
        
        total_sections = 4
        completed_count = len([s for s in completed_sections.values() if s.get('status') == 'success'])
        
        return {
            'ticker': ticker,
            'status': 'partial',
            'completion_rate': (completed_count / total_sections) * 100,
            'completed_sections': completed_count,
            'total_sections': total_sections,
            'sections': completed_sections,
            'message': f'Partial report generated. {completed_count}/{total_sections} sections completed.',
            'timestamp': datetime.now().isoformat(),
            'recommendations': [
                'Review completed sections for available insights',
                'Retry failed sections individually',
                'Consider alternative data sources for missing analysis',
                'Contact support if issues persist'
            ]
        }

# Global instances
error_handler = ErrorHandler()

# Decorator for automatic retry
def with_retry(retry_config: Optional[RetryConfig] = None, context: Optional[str] = None):
    """Decorator to add retry logic to functions"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await error_handler.execute_with_retry(
                func, *args, retry_config=retry_config, context=context, **kwargs
            )
        return wrapper
    return decorator

# Circuit breaker decorator
def with_circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """Decorator to add circuit breaker pattern"""
    
    def decorator(func):
        breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        return breaker(func)
    return decorator