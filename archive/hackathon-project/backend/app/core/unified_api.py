"""
Unified API Integration Layer
Main integration point that coordinates all backend services
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import time
from typing import Dict, Any, Optional
import logging

from app.core.gateway import gateway
from app.core.auth_middleware import auth_middleware
from app.core.error_handling import error_handler, logging_coordinator, ErrorSeverity, ErrorCategory
from app.core.monitoring import metrics_collector, health_checker

logger = logging_coordinator.get_logger("unified_api")

class UnifiedAPI:
    def __init__(self, app: FastAPI):
        self.app = app
        self.gateway = gateway
        self.auth = auth_middleware
        self.error_handler = error_handler
        self.metrics = metrics_collector
        self.health_checker = health_checker
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        self._setup_health_checks()
    
    def _setup_middleware(self):
        """Setup all middleware layers"""
        
        @self.app.middleware("http")
        async def unified_middleware(request: Request, call_next):
            start_time = time.time()
            request_id = f"req_{int(time.time() * 1000)}"
            
            try:
                # Authentication (for protected routes)
                user_context = None
                if not request.url.path.startswith("/health") and not request.url.path.startswith("/metrics"):
                    try:
                        user_context = await self.auth.authenticate_request(request)
                    except HTTPException as e:
                        if request.url.path.startswith("/api/"):
                            raise e
                        # Allow unauthenticated access to public routes
                
                # Add context to request
                request.state.user_context = user_context
                request.state.request_id = request_id
                
                # Process request
                response = await call_next(request)
                
                # Log performance
                duration = time.time() - start_time
                self.metrics.record_custom_metric(
                    "request_duration",
                    duration,
                    {
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "user_id": user_context.get("user_id") if user_context else None
                    }
                )
                
                logging_coordinator.log_performance(
                    operation=f"{request.method} {request.url.path}",
                    duration=duration,
                    success=response.status_code < 400,
                    metadata={
                        "status_code": response.status_code,
                        "user_id": user_context.get("user_id") if user_context else None
                    }
                )
                
                return response
                
            except Exception as e:
                # Handle errors
                duration = time.time() - start_time
                
                error_context = self.error_handler.handle_error(
                    error=e,
                    severity=ErrorSeverity.HIGH if isinstance(e, HTTPException) and e.status_code >= 500 else ErrorSeverity.MEDIUM,
                    category=ErrorCategory.AUTHENTICATION if isinstance(e, HTTPException) and e.status_code == 401 else ErrorCategory.SYSTEM,
                    context={
                        "path": request.url.path,
                        "method": request.method,
                        "duration": duration
                    },
                    user_id=user_context.get("user_id") if user_context else None,
                    request_id=request_id
                )
                
                # Return appropriate error response
                if isinstance(e, HTTPException):
                    return JSONResponse(
                        status_code=e.status_code,
                        content={
                            "error": e.detail,
                            "error_id": error_context.error_id,
                            "timestamp": error_context.timestamp
                        }
                    )
                else:
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": "Internal server error",
                            "error_id": error_context.error_id,
                            "timestamp": error_context.timestamp
                        }
                    )
    
    def _setup_routes(self):
        """Setup unified API routes"""
        
        @self.app.post("/api/reports/generate")
        async def generate_report(
            request: Request,
            ticker: str,
            report_type: str = "comprehensive"
        ):
            """Generate comprehensive stock report"""
            user_context = request.state.user_context
            if not user_context:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            try:
                # Check permissions
                if not self.auth.check_permission(user_context, "generate_reports"):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                # Orchestrate report generation
                result = await self.gateway.orchestrate_report_generation(
                    ticker=ticker,
                    user_id=user_context["user_id"]
                )
                
                return {
                    "success": True,
                    "data": result,
                    "user_id": user_context["user_id"],
                    "timestamp": time.time()
                }
                
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.BUSINESS_LOGIC,
                    context={"ticker": ticker, "report_type": report_type},
                    user_id=user_context["user_id"]
                )
                raise HTTPException(status_code=500, detail="Report generation failed")
        
        @self.app.get("/api/reports/{report_id}")
        async def get_report(request: Request, report_id: str):
            """Get report by ID"""
            user_context = request.state.user_context
            if not user_context:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Implementation would fetch report from database
            return {
                "report_id": report_id,
                "status": "completed",
                "user_id": user_context["user_id"]
            }
        
        @self.app.get("/api/system/metrics")
        async def get_system_metrics(request: Request):
            """Get system metrics (admin only)"""
            user_context = request.state.user_context
            if not user_context or not self.auth.check_permission(user_context, "admin"):
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {
                "gateway_metrics": self.gateway.get_system_metrics(),
                "performance_metrics": self.metrics.get_current_metrics(),
                "error_metrics": self.error_handler.get_error_metrics(),
                "timestamp": time.time()
            }
        
        @self.app.get("/health")
        async def health_check():
            """System health check"""
            health_results = await self.health_checker.run_health_checks()
            
            overall_status = "healthy"
            if any(result["status"] == "unhealthy" for result in health_results.values()):
                overall_status = "unhealthy"
            elif any(result["status"] == "degraded" for result in health_results.values()):
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "timestamp": time.time(),
                "services": health_results,
                "system_metrics": self.metrics.get_current_metrics()
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Prometheus-style metrics endpoint"""
            current_metrics = self.metrics.get_current_metrics()
            
            # Format as Prometheus metrics
            metrics_text = []
            
            if current_metrics.get("system"):
                system = current_metrics["system"]
                metrics_text.extend([
                    f"system_cpu_percent {system['cpu_percent']}",
                    f"system_memory_percent {system['memory_percent']}",
                    f"system_disk_usage {system['disk_usage']}",
                    f"system_active_connections {system['active_connections']}"
                ])
            
            if current_metrics.get("application"):
                app = current_metrics["application"]
                metrics_text.extend([
                    f"app_request_count {app['request_count']}",
                    f"app_error_count {app['error_count']}",
                    f"app_avg_response_time {app['avg_response_time']}",
                    f"app_active_users {app['active_users']}"
                ])
            
            return "\n".join(metrics_text)
    
    def _setup_health_checks(self):
        """Setup health check functions"""
        
        async def gateway_health():
            """Check gateway health"""
            metrics = self.gateway.get_system_metrics()
            if metrics["error_rate"] > 10:
                raise Exception(f"High error rate: {metrics['error_rate']}%")
            return {"error_rate": metrics["error_rate"]}
        
        async def database_health():
            """Check database connectivity"""
            # Implementation would check database connection
            return {"status": "connected"}
        
        async def external_services_health():
            """Check external service dependencies"""
            # Implementation would check external APIs
            return {"status": "available"}
        
        # Register health checks
        self.health_checker.register_health_check("gateway", gateway_health, 30)
        self.health_checker.register_health_check("database", database_health, 60)
        self.health_checker.register_health_check("external_services", external_services_health, 120)
    
    async def initialize(self):
        """Initialize all systems"""
        logger.info("Initializing Unified API system...")
        
        # Initialize gateway
        await self.gateway.initialize()
        
        # Start monitoring
        await self.metrics.start_monitoring()
        
        logger.info("Unified API system initialized successfully")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Unified API system...")
        
        # Perform cleanup tasks
        # Save metrics, close connections, etc.
        
        logger.info("Unified API system shutdown complete")

def create_unified_api(app: FastAPI) -> UnifiedAPI:
    """Factory function to create unified API"""
    return UnifiedAPI(app)