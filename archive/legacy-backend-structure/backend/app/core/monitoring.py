"""
Performance Monitoring and Metrics Collection
Real-time system monitoring with comprehensive metrics
"""
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    active_connections: int

@dataclass
class ApplicationMetrics:
    timestamp: float
    request_count: int
    error_count: int
    avg_response_time: float
    active_users: int
    queue_size: int
    cache_hit_rate: float

class MetricsCollector:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics = deque(maxlen=max_history)
        self.app_metrics = deque(maxlen=max_history)
        self.custom_metrics = defaultdict(deque)
        self.alerts = []
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "response_time": 5.0
        }
        
    async def start_monitoring(self):
        """Start continuous monitoring"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_app_metrics())
        logger.info("Performance monitoring started")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_usage = (disk.used / disk.total) * 100
                
                # Network I/O
                network = psutil.net_io_counters()
                network_io = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
                
                # Active connections
                connections = len(psutil.net_connections())
                
                metrics = SystemMetrics(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_usage=disk_usage,
                    network_io=network_io,
                    active_connections=connections
                )
                
                self.system_metrics.append(metrics)
                
                # Check thresholds
                await self._check_system_thresholds(metrics)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            await asyncio.sleep(30)  # Collect every 30 seconds
    
    async def _collect_app_metrics(self):
        """Collect application-level metrics"""
        while True:
            try:
                # These would be populated by the API Gateway
                from app.core.gateway import gateway
                
                gateway_metrics = gateway.get_system_metrics()
                
                metrics = ApplicationMetrics(
                    timestamp=time.time(),
                    request_count=gateway_metrics.get("request_count", 0),
                    error_count=gateway_metrics.get("error_count", 0),
                    avg_response_time=gateway_metrics.get("avg_response_time", 0),
                    active_users=len(gateway_metrics.get("active_sessions", {})),
                    queue_size=0,  # Would get from queue service
                    cache_hit_rate=0.0  # Would get from cache service
                )
                
                self.app_metrics.append(metrics)
                
                # Check application thresholds
                await self._check_app_thresholds(metrics)
                
            except Exception as e:
                logger.error(f"Error collecting app metrics: {e}")
            
            await asyncio.sleep(60)  # Collect every minute
    
    async def _check_system_thresholds(self, metrics: SystemMetrics):
        """Check system metrics against thresholds"""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds["cpu_percent"]:
            alerts.append({
                "type": "system",
                "metric": "cpu_percent",
                "value": metrics.cpu_percent,
                "threshold": self.thresholds["cpu_percent"],
                "severity": "high" if metrics.cpu_percent > 90 else "medium"
            })
        
        if metrics.memory_percent > self.thresholds["memory_percent"]:
            alerts.append({
                "type": "system",
                "metric": "memory_percent",
                "value": metrics.memory_percent,
                "threshold": self.thresholds["memory_percent"],
                "severity": "high" if metrics.memory_percent > 95 else "medium"
            })
        
        if metrics.disk_usage > self.thresholds["disk_usage"]:
            alerts.append({
                "type": "system",
                "metric": "disk_usage",
                "value": metrics.disk_usage,
                "threshold": self.thresholds["disk_usage"],
                "severity": "critical" if metrics.disk_usage > 95 else "high"
            })
        
        for alert in alerts:
            alert["timestamp"] = time.time()
            self.alerts.append(alert)
            logger.warning(f"System alert: {alert}")
    
    async def _check_app_thresholds(self, metrics: ApplicationMetrics):
        """Check application metrics against thresholds"""
        alerts = []
        
        # Error rate check
        if metrics.request_count > 0:
            error_rate = (metrics.error_count / metrics.request_count) * 100
            if error_rate > self.thresholds["error_rate"]:
                alerts.append({
                    "type": "application",
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": self.thresholds["error_rate"],
                    "severity": "high" if error_rate > 10 else "medium"
                })
        
        # Response time check
        if metrics.avg_response_time > self.thresholds["response_time"]:
            alerts.append({
                "type": "application",
                "metric": "response_time",
                "value": metrics.avg_response_time,
                "threshold": self.thresholds["response_time"],
                "severity": "high" if metrics.avg_response_time > 10 else "medium"
            })
        
        for alert in alerts:
            alert["timestamp"] = time.time()
            self.alerts.append(alert)
            logger.warning(f"Application alert: {alert}")
    
    def record_custom_metric(self, name: str, value: float, metadata: Dict[str, Any] = None):
        """Record custom application metric"""
        metric_data = {
            "timestamp": time.time(),
            "value": value,
            "metadata": metadata or {}
        }
        
        self.custom_metrics[name].append(metric_data)
        
        # Keep only recent metrics
        if len(self.custom_metrics[name]) > self.max_history:
            self.custom_metrics[name].popleft()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system state"""
        current_system = self.system_metrics[-1] if self.system_metrics else None
        current_app = self.app_metrics[-1] if self.app_metrics else None
        
        return {
            "timestamp": time.time(),
            "system": asdict(current_system) if current_system else None,
            "application": asdict(current_app) if current_app else None,
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "custom_metrics": {
                name: list(metrics)[-5:]  # Last 5 values for each custom metric
                for name, metrics in self.custom_metrics.items()
            }
        }
    
    def get_historical_data(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get historical metrics data"""
        current_time = time.time()
        
        # Filter system metrics
        system_data = [
            asdict(m) for m in self.system_metrics
            if current_time - m.timestamp <= time_window
        ]
        
        # Filter app metrics
        app_data = [
            asdict(m) for m in self.app_metrics
            if current_time - m.timestamp <= time_window
        ]
        
        # Filter alerts
        recent_alerts = [
            alert for alert in self.alerts
            if current_time - alert["timestamp"] <= time_window
        ]
        
        return {
            "time_window": time_window,
            "system_metrics": system_data,
            "application_metrics": app_data,
            "alerts": recent_alerts,
            "summary": self._calculate_summary(system_data, app_data)
        }
    
    def _calculate_summary(self, system_data: List[Dict], app_data: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not system_data or not app_data:
            return {}
        
        # System averages
        avg_cpu = sum(m["cpu_percent"] for m in system_data) / len(system_data)
        avg_memory = sum(m["memory_percent"] for m in system_data) / len(system_data)
        
        # Application averages
        total_requests = sum(m["request_count"] for m in app_data)
        total_errors = sum(m["error_count"] for m in app_data)
        avg_response_time = sum(m["avg_response_time"] for m in app_data) / len(app_data)
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time
        }

class HealthChecker:
    def __init__(self):
        self.health_checks = {}
        self.last_results = {}
    
    def register_health_check(self, name: str, check_func, interval: int = 60):
        """Register a health check function"""
        self.health_checks[name] = {
            "func": check_func,
            "interval": interval,
            "last_run": 0
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        current_time = time.time()
        
        for name, check_config in self.health_checks.items():
            # Check if it's time to run this health check
            if current_time - check_config["last_run"] >= check_config["interval"]:
                try:
                    result = await check_config["func"]()
                    results[name] = {
                        "status": "healthy",
                        "result": result,
                        "timestamp": current_time
                    }
                except Exception as e:
                    results[name] = {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": current_time
                    }
                
                check_config["last_run"] = current_time
                self.last_results[name] = results[name]
            else:
                # Use cached result
                results[name] = self.last_results.get(name, {
                    "status": "unknown",
                    "timestamp": current_time
                })
        
        return results

# Global monitoring instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()