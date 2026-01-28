"""
API Gateway with Service Orchestration
Coordinates all backend services with health monitoring and circuit breakers
"""
import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from contextlib import asynccontextmanager

from app.services.kiro_service import KiroService
from app.services.pdf_generator import PDFGenerator
from app.services.report_queue import ReportQueue
from app.services.performance_optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class ServiceHealth:
    status: ServiceStatus
    response_time: float
    error_rate: float
    last_check: float
    consecutive_failures: int = 0

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.health_status: Dict[str, ServiceHealth] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.load_balancers: Dict[str, List[str]] = {}
    
    def register_service(self, name: str, service: Any, instances: List[str] = None):
        self.services[name] = service
        self.circuit_breakers[name] = CircuitBreaker()
        self.health_status[name] = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            response_time=0.0,
            error_rate=0.0,
            last_check=time.time()
        )
        if instances:
            self.load_balancers[name] = instances
    
    async def get_service(self, name: str):
        if name not in self.services:
            raise ValueError(f"Service {name} not registered")
        
        health = self.health_status[name]
        if health.status == ServiceStatus.UNHEALTHY:
            raise Exception(f"Service {name} is unhealthy")
        
        return self.services[name]

class APIGateway:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.metrics = {}
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
    async def initialize(self):
        """Initialize all services and register them"""
        # Initialize services
        kiro_service = KiroService()
        pdf_generator = PDFGenerator()
        report_queue = ReportQueue()
        performance_optimizer = PerformanceOptimizer()
        
        # Register services
        self.registry.register_service("kiro", kiro_service)
        self.registry.register_service("pdf", pdf_generator)
        self.registry.register_service("queue", report_queue)
        self.registry.register_service("optimizer", performance_optimizer)
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor())
        
        logger.info("API Gateway initialized with all services")
    
    async def _health_monitor(self):
        """Continuous health monitoring of all services"""
        while True:
            for service_name in self.registry.services:
                try:
                    start_time = time.time()
                    
                    # Perform health check
                    service = self.registry.services[service_name]
                    if hasattr(service, 'health_check'):
                        await service.health_check()
                    
                    response_time = time.time() - start_time
                    
                    # Update health status
                    health = self.registry.health_status[service_name]
                    health.response_time = response_time
                    health.last_check = time.time()
                    health.consecutive_failures = 0
                    
                    if response_time > 5.0:
                        health.status = ServiceStatus.DEGRADED
                    else:
                        health.status = ServiceStatus.HEALTHY
                        
                except Exception as e:
                    health = self.registry.health_status[service_name]
                    health.consecutive_failures += 1
                    
                    if health.consecutive_failures >= 3:
                        health.status = ServiceStatus.UNHEALTHY
                    
                    logger.error(f"Health check failed for {service_name}: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def orchestrate_report_generation(self, ticker: str, user_id: str) -> Dict[str, Any]:
        """Orchestrate complete report generation workflow"""
        self.request_count += 1
        start_time = time.time()
        
        try:
            # Step 1: Queue the request
            queue_service = await self.registry.get_service("queue")
            job_id = await self.registry.circuit_breakers["queue"].call(
                queue_service.enqueue_report, ticker, user_id
            )
            
            # Step 2: Generate report sections with Kiro
            kiro_service = await self.registry.get_service("kiro")
            report_data = await self.registry.circuit_breakers["kiro"].call(
                kiro_service.generate_comprehensive_report, ticker
            )
            
            # Step 3: Generate PDF
            pdf_service = await self.registry.get_service("pdf")
            pdf_path = await self.registry.circuit_breakers["pdf"].call(
                pdf_service.generate_report_pdf, report_data, ticker
            )
            
            # Step 4: Optimize performance metrics
            optimizer = await self.registry.get_service("optimizer")
            await optimizer.record_generation_metrics(
                ticker, time.time() - start_time, len(report_data)
            )
            
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            return {
                "job_id": job_id,
                "status": "completed",
                "report_data": report_data,
                "pdf_path": pdf_path,
                "generation_time": response_time
            }
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Report generation failed for {ticker}: {e}")
            
            # Attempt graceful degradation
            return await self._graceful_degradation(ticker, user_id, str(e))
    
    async def _graceful_degradation(self, ticker: str, user_id: str, error: str) -> Dict[str, Any]:
        """Provide degraded service when primary services fail"""
        try:
            # Try to provide basic report without advanced features
            basic_report = {
                "ticker": ticker,
                "status": "degraded",
                "error": error,
                "basic_data": {
                    "company_name": ticker,
                    "timestamp": time.time(),
                    "message": "Advanced analysis temporarily unavailable"
                }
            }
            
            return {
                "job_id": f"degraded_{int(time.time())}",
                "status": "degraded",
                "report_data": basic_report,
                "pdf_path": None,
                "generation_time": 0.1
            }
            
        except Exception as e:
            logger.error(f"Graceful degradation failed: {e}")
            raise Exception("All services unavailable")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        avg_response_time = sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "service_health": {
                name: {
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "last_check": health.last_check,
                    "consecutive_failures": health.consecutive_failures
                }
                for name, health in self.registry.health_status.items()
            },
            "circuit_breakers": {
                name: {
                    "state": cb.state,
                    "failure_count": cb.failure_count
                }
                for name, cb in self.registry.circuit_breakers.items()
            }
        }

# Global gateway instance
gateway = APIGateway()