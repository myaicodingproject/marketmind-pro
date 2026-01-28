"""
Queue Management System for Multiple Users
Handles concurrent report generation requests with fair scheduling and resource allocation
"""
import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import heapq
import uuid

logger = logging.getLogger(__name__)

class QueuePriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0

class RequestStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueueRequest:
    """Represents a queued request"""
    request_id: str
    user_id: str
    ticker: str
    request_type: str
    priority: QueuePriority
    created_at: float
    estimated_duration: int  # seconds
    callback: Optional[Callable] = None
    status: RequestStatus = RequestStatus.QUEUED
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at

class UserQuota:
    """Manages per-user quotas and rate limiting"""
    
    def __init__(self, max_concurrent: int = 2, max_hourly: int = 10, max_daily: int = 50):
        self.max_concurrent = max_concurrent
        self.max_hourly = max_hourly
        self.max_daily = max_daily
        
        self.concurrent_count = 0
        self.hourly_requests: List[float] = []
        self.daily_requests: List[float] = []
        
    def can_process(self) -> bool:
        """Check if user can process another request"""
        now = time.time()
        
        # Clean old requests
        self.hourly_requests = [t for t in self.hourly_requests if now - t < 3600]
        self.daily_requests = [t for t in self.daily_requests if now - t < 86400]
        
        return (
            self.concurrent_count < self.max_concurrent and
            len(self.hourly_requests) < self.max_hourly and
            len(self.daily_requests) < self.max_daily
        )
        
    def start_request(self):
        """Mark request as started"""
        now = time.time()
        self.concurrent_count += 1
        self.hourly_requests.append(now)
        self.daily_requests.append(now)
        
    def complete_request(self):
        """Mark request as completed"""
        self.concurrent_count = max(0, self.concurrent_count - 1)

class QueueManager:
    """Manages request queue with fair scheduling and resource allocation"""
    
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        
        # Queue management
        self._request_queue: List[QueueRequest] = []
        self._active_requests: Dict[str, QueueRequest] = {}
        self._completed_requests: Dict[str, QueueRequest] = {}
        
        # User management
        self._user_quotas: Dict[str, UserQuota] = defaultdict(UserQuota)
        self._user_last_request: Dict[str, float] = {}
        
        # Worker management
        self._workers: List[asyncio.Task] = []
        self._worker_semaphore = asyncio.Semaphore(max_workers)
        self._queue_lock = asyncio.Lock()
        
        # Monitoring
        self._stats = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "average_wait_time": 0.0,
            "average_processing_time": 0.0
        }
        
    async def start(self):
        """Start the queue manager"""
        logger.info("Starting Queue Manager")
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
            
    async def stop(self):
        """Stop the queue manager"""
        logger.info("Stopping Queue Manager")
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
            
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        # Cancel remaining requests
        async with self._queue_lock:
            for request in self._request_queue:
                request.status = RequestStatus.CANCELLED
                
    async def submit_request(self, user_id: str, ticker: str, request_type: str, 
                           priority: QueuePriority = QueuePriority.NORMAL,
                           estimated_duration: int = 180,
                           callback: Optional[Callable] = None) -> str:
        """Submit a new request to the queue"""
        
        # Check user quota
        user_quota = self._user_quotas[user_id]
        if not user_quota.can_process():
            raise RuntimeError("User quota exceeded. Please try again later.")
            
        # Check queue size
        if len(self._request_queue) >= self.max_queue_size:
            raise RuntimeError("Queue is full. Please try again later.")
            
        # Create request
        request_id = f"{user_id}_{ticker}_{uuid.uuid4().hex[:8]}"
        request = QueueRequest(
            request_id=request_id,
            user_id=user_id,
            ticker=ticker,
            request_type=request_type,
            priority=priority,
            created_at=time.time(),
            estimated_duration=estimated_duration,
            callback=callback
        )
        
        # Add to queue
        async with self._queue_lock:
            heapq.heappush(self._request_queue, request)
            self._stats["total_requests"] += 1
            
        logger.info(f"Queued request {request_id} for user {user_id}")
        return request_id
        
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a request"""
        
        # Check active requests
        if request_id in self._active_requests:
            request = self._active_requests[request_id]
            return self._request_to_dict(request)
            
        # Check completed requests
        if request_id in self._completed_requests:
            request = self._completed_requests[request_id]
            return self._request_to_dict(request)
            
        # Check queue
        async with self._queue_lock:
            for request in self._request_queue:
                if request.request_id == request_id:
                    return self._request_to_dict(request)
                    
        return None
        
    async def cancel_request(self, request_id: str, user_id: str) -> bool:
        """Cancel a request"""
        
        # Check if user owns the request
        async with self._queue_lock:
            for i, request in enumerate(self._request_queue):
                if request.request_id == request_id and request.user_id == user_id:
                    request.status = RequestStatus.CANCELLED
                    del self._request_queue[i]
                    heapq.heapify(self._request_queue)
                    return True
                    
        return False
        
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        
        async with self._queue_lock:
            queue_by_priority = defaultdict(int)
            for request in self._request_queue:
                queue_by_priority[request.priority.name] += 1
                
        return {
            "queue_length": len(self._request_queue),
            "active_requests": len(self._active_requests),
            "available_workers": self._worker_semaphore._value,
            "queue_by_priority": dict(queue_by_priority),
            "stats": self._stats.copy()
        }
        
    async def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get user-specific status"""
        
        user_quota = self._user_quotas[user_id]
        
        # Count user requests in queue and active
        user_queued = sum(1 for r in self._request_queue if r.user_id == user_id)
        user_active = sum(1 for r in self._active_requests.values() if r.user_id == user_id)
        
        return {
            "user_id": user_id,
            "queued_requests": user_queued,
            "active_requests": user_active,
            "concurrent_limit": user_quota.max_concurrent,
            "hourly_requests": len(user_quota.hourly_requests),
            "hourly_limit": user_quota.max_hourly,
            "daily_requests": len(user_quota.daily_requests),
            "daily_limit": user_quota.max_daily,
            "can_submit": user_quota.can_process()
        }
        
    async def _worker(self, worker_id: str):
        """Worker task that processes requests from the queue"""
        
        logger.info(f"Started worker {worker_id}")
        
        while True:
            try:
                # Get next request
                request = await self._get_next_request()
                if not request:
                    await asyncio.sleep(1)
                    continue
                    
                # Process request
                await self._process_request(worker_id, request)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)  # Back off on error
                
        logger.info(f"Stopped worker {worker_id}")
        
    async def _get_next_request(self) -> Optional[QueueRequest]:
        """Get the next request to process"""
        
        async with self._queue_lock:
            while self._request_queue:
                request = heapq.heappop(self._request_queue)
                
                # Skip cancelled requests
                if request.status == RequestStatus.CANCELLED:
                    continue
                    
                # Check user quota
                user_quota = self._user_quotas[request.user_id]
                if not user_quota.can_process():
                    # Put back in queue with lower priority
                    request.priority = QueuePriority.LOW
                    heapq.heappush(self._request_queue, request)
                    continue
                    
                # Mark as processing
                request.status = RequestStatus.PROCESSING
                request.started_at = time.time()
                self._active_requests[request.request_id] = request
                
                # Update user quota
                user_quota.start_request()
                
                return request
                
        return None
        
    async def _process_request(self, worker_id: str, request: QueueRequest):
        """Process a single request"""
        
        try:
            logger.info(f"Worker {worker_id} processing {request.request_id}")
            
            # Import here to avoid circular imports
            from app.services.kiro_process_service import kiro_process_service
            
            # Execute the request based on type
            if request.request_type == "comprehensive_report":
                # Mock company data for now
                company_data = {
                    "ticker": request.ticker,
                    "company_name": f"{request.ticker} Inc.",
                    "sector": "Technology",  # Would be fetched from data service
                }
                
                result = await kiro_process_service.generate_comprehensive_report(
                    request.ticker, company_data
                )
                
                request.result = result
                request.status = RequestStatus.COMPLETED
                
            else:
                raise ValueError(f"Unknown request type: {request.request_type}")
                
            # Update stats
            processing_time = time.time() - request.started_at
            self._update_stats(processing_time, success=True)
            
            logger.info(f"Completed {request.request_id} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing {request.request_id}: {e}")
            request.error = str(e)
            request.status = RequestStatus.FAILED
            self._update_stats(0, success=False)
            
        finally:
            # Cleanup
            request.completed_at = time.time()
            
            # Move to completed
            self._active_requests.pop(request.request_id, None)
            self._completed_requests[request.request_id] = request
            
            # Update user quota
            user_quota = self._user_quotas[request.user_id]
            user_quota.complete_request()
            
            # Call callback if provided
            if request.callback:
                try:
                    await request.callback(request)
                except Exception as e:
                    logger.error(f"Callback error for {request.request_id}: {e}")
                    
            # Cleanup old completed requests (keep last 1000)
            if len(self._completed_requests) > 1000:
                oldest_requests = sorted(
                    self._completed_requests.items(),
                    key=lambda x: x[1].completed_at or 0
                )[:500]  # Remove oldest 500
                
                for request_id, _ in oldest_requests:
                    self._completed_requests.pop(request_id, None)
                    
    def _update_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        
        if success:
            self._stats["completed_requests"] += 1
            
            # Update average processing time
            total_completed = self._stats["completed_requests"]
            current_avg = self._stats["average_processing_time"]
            self._stats["average_processing_time"] = (
                (current_avg * (total_completed - 1) + processing_time) / total_completed
            )
        else:
            self._stats["failed_requests"] += 1
            
    def _request_to_dict(self, request: QueueRequest) -> Dict[str, Any]:
        """Convert request to dictionary"""
        
        return {
            "request_id": request.request_id,
            "user_id": request.user_id,
            "ticker": request.ticker,
            "request_type": request.request_type,
            "priority": request.priority.name,
            "status": request.status.value,
            "created_at": request.created_at,
            "started_at": request.started_at,
            "completed_at": request.completed_at,
            "estimated_duration": request.estimated_duration,
            "actual_duration": (
                (request.completed_at or time.time()) - request.started_at
                if request.started_at else None
            ),
            "result": request.result,
            "error": request.error
        }

# Global queue manager instance
queue_manager = QueueManager()