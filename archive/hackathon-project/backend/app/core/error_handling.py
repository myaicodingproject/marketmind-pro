"""
Error Handling and Logging Coordination
Centralized error handling with structured logging and monitoring
"""
import logging
import traceback
import time
import json
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import asyncio

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    SYSTEM = "system"

@dataclass
class ErrorContext:
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    service_name: Optional[str] = None

class ErrorHandler:
    def __init__(self):
        self.error_log = []
        self.error_counts = {}
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,
            ErrorSeverity.HIGH: 5,
            ErrorSeverity.MEDIUM: 20,
            ErrorSeverity.LOW: 100
        }
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger("marketmind_errors")
        logger.setLevel(logging.INFO)
        
        # Create formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for errors
        file_handler = logging.FileHandler('logs/errors.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def handle_error(
        self,
        error: Exception,
        severity: ErrorSeverity,
        category: ErrorCategory,
        context: Dict[str, Any] = None,
        user_id: str = None,
        request_id: str = None,
        service_name: str = None
    ) -> ErrorContext:
        """Handle and log error with context"""
        error_id = f"ERR_{int(time.time() * 1000)}"
        
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=time.time(),
            severity=severity,
            category=category,
            message=str(error),
            details=context or {},
            user_id=user_id,
            request_id=request_id,
            stack_trace=traceback.format_exc(),
            service_name=service_name
        )
        
        # Log error
        self._log_error(error_context)
        
        # Store for monitoring
        self.error_log.append(error_context)
        
        # Update error counts
        key = f"{category.value}_{severity.value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Check for alerts
        self._check_alert_thresholds(error_context)
        
        return error_context
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        log_data = {
            "error_id": error_context.error_id,
            "severity": error_context.severity.value,
            "category": error_context.category.value,
            "message": error_context.message,
            "user_id": error_context.user_id,
            "service_name": error_context.service_name,
            "details": error_context.details
        }
        
        log_message = json.dumps(log_data)
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _check_alert_thresholds(self, error_context: ErrorContext):
        """Check if error count exceeds alert thresholds"""
        key = f"{error_context.category.value}_{error_context.severity.value}"
        count = self.error_counts.get(key, 0)
        threshold = self.alert_thresholds.get(error_context.severity, 100)
        
        if count >= threshold:
            self._send_alert(error_context, count)
    
    def _send_alert(self, error_context: ErrorContext, count: int):
        """Send alert for high error rates"""
        alert_message = f"Alert: {count} {error_context.severity.value} errors in {error_context.category.value}"
        self.logger.critical(f"ALERT: {alert_message}")
        
        # Here you would integrate with alerting systems like PagerDuty, Slack, etc.
        # For now, we'll just log the alert
    
    def get_error_metrics(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get error metrics for monitoring"""
        current_time = time.time()
        recent_errors = [
            error for error in self.error_log
            if current_time - error.timestamp <= time_window
        ]
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = len([
                e for e in recent_errors if e.severity == severity
            ])
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = len([
                e for e in recent_errors if e.category == category
            ])
        
        # Error rate
        total_errors = len(recent_errors)
        error_rate = total_errors / (time_window / 60)  # errors per minute
        
        return {
            "total_errors": total_errors,
            "error_rate_per_minute": error_rate,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "recent_errors": [asdict(e) for e in recent_errors[-10:]]  # Last 10 errors
        }
    
    @contextmanager
    def error_context(
        self,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        **context
    ):
        """Context manager for error handling"""
        try:
            yield
        except Exception as e:
            self.handle_error(
                error=e,
                severity=severity,
                category=category,
                context={"operation": operation, **context}
            )
            raise

class LoggingCoordinator:
    def __init__(self):
        self.loggers = {}
        self.log_levels = {}
        self.performance_logs = []
        
    def get_logger(self, name: str, level: str = "INFO") -> logging.Logger:
        """Get or create logger with specified level"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(getattr(logging, level.upper()))
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            self.loggers[name] = logger
            self.log_levels[name] = level
        
        return self.loggers[name]
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        success: bool,
        metadata: Dict[str, Any] = None
    ):
        """Log performance metrics"""
        perf_log = {
            "timestamp": time.time(),
            "operation": operation,
            "duration": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        self.performance_logs.append(perf_log)
        
        # Log to performance logger
        perf_logger = self.get_logger("performance")
        perf_logger.info(json.dumps(perf_log))
    
    def get_performance_metrics(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get performance metrics"""
        current_time = time.time()
        recent_logs = [
            log for log in self.performance_logs
            if current_time - log["timestamp"] <= time_window
        ]
        
        if not recent_logs:
            return {"total_operations": 0}
        
        # Calculate metrics
        total_ops = len(recent_logs)
        successful_ops = len([log for log in recent_logs if log["success"]])
        success_rate = (successful_ops / total_ops) * 100
        
        durations = [log["duration"] for log in recent_logs]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "max_duration": max_duration,
            "min_duration": min_duration,
            "operations_per_minute": total_ops / (time_window / 60)
        }

# Global instances
error_handler = ErrorHandler()
logging_coordinator = LoggingCoordinator()