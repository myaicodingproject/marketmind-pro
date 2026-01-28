# A4.3: Robust Queue System for Concurrent Users
# Handles 50+ concurrent report generations with Redis/Celery

import asyncio
import json
import uuid
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import redis.asyncio as redis
from celery import Celery
import logging

logger = logging.getLogger(__name__)

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class JobStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueueJob:
    job_id: str
    ticker: str
    user_id: str
    user_tier: UserTier
    status: JobStatus
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    stage: str = "queued"
    error_message: Optional[str] = None
    report_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class QueueManager:
    """Advanced queue manager with user tiers, load balancing, and monitoring"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.max_concurrent_jobs = 50
        self.tier_limits = {
            UserTier.FREE: {"concurrent": 1, "daily": 5},
            UserTier.PREMIUM: {"concurrent": 3, "daily": 50},
            UserTier.ENTERPRISE: {"concurrent": 10, "daily": 1000}
        }
        self.priority_weights = {
            UserTier.ENTERPRISE: 100,
            UserTier.PREMIUM: 50,
            UserTier.FREE: 10
        }
    
    async def enqueue_job(self, ticker: str, user_id: str, user_tier: UserTier) -> str:
        """Enqueue a new report generation job with capacity and tier checks"""
        
        # Check user limits
        if not await self._check_user_limits(user_id, user_tier):
            raise ValueError("User has exceeded tier limits")
        
        # Create job
        job_id = str(uuid.uuid4())
        priority = self._calculate_priority(user_tier)
        
        job = QueueJob(
            job_id=job_id,
            ticker=ticker,
            user_id=user_id,
            user_tier=user_tier,
            status=JobStatus.QUEUED,
            priority=priority,
            created_at=datetime.utcnow(),
            estimated_completion=self._estimate_completion_time()
        )
        
        # Store job data
        await self.redis.hset(f"job:{job_id}", mapping=self._job_to_dict(job))
        
        # Add to appropriate queue
        queue_name = f"queue:{user_tier.value}"
        await self.redis.zadd(queue_name, {job_id: priority})
        
        # Update user counters
        await self._update_user_counters(user_id)
        
        # Try to start processing immediately if capacity available
        await self._process_next_jobs()
        
        logger.info(f"Job {job_id} enqueued for user {user_id} (tier: {user_tier.value})")
        return job_id
    
    async def _check_user_limits(self, user_id: str, user_tier: UserTier) -> bool:
        """Check if user can submit new job based on tier limits"""
        limits = self.tier_limits[user_tier]
        
        # Check concurrent jobs
        active_jobs = await self.redis.scard(f"user_active:{user_id}")
        if active_jobs >= limits["concurrent"]:
            return False
        
        # Check daily limit
        today = datetime.utcnow().date().isoformat()
        daily_count = await self.redis.get(f"user_daily:{user_id}:{today}")
        if daily_count and int(daily_count) >= limits["daily"]:
            return False
        
        return True
    
    def _calculate_priority(self, user_tier: UserTier) -> int:
        """Calculate job priority based on user tier and current time"""
        base_priority = self.priority_weights[user_tier]
        time_bonus = int(datetime.utcnow().timestamp()) % 1000
        return base_priority + time_bonus
    
    async def _estimate_completion_time(self) -> datetime:
        """Estimate job completion time based on current queue"""
        active_count = await self.redis.scard("active_jobs")
        avg_processing_time = 8 * 60  # 8 minutes average
        
        if active_count < self.max_concurrent_jobs:
            return datetime.utcnow() + timedelta(seconds=avg_processing_time)
        else:
            queue_position = await self._get_total_queue_size()
            estimated_wait = (queue_position / self.max_concurrent_jobs) * avg_processing_time
            return datetime.utcnow() + timedelta(seconds=estimated_wait)
    
    async def _get_total_queue_size(self) -> int:
        """Get total number of queued jobs across all tiers"""
        total = 0
        for tier in UserTier:
            count = await self.redis.zcard(f"queue:{tier.value}")
            total += count
        return total
    
    async def _process_next_jobs(self):
        """Process next jobs from queues with priority ordering"""
        active_count = await self.redis.scard("active_jobs")
        
        while active_count < self.max_concurrent_jobs:
            job_id = await self._get_next_job()
            if not job_id:
                break
            
            await self._start_job_processing(job_id)
            active_count += 1
    
    async def _get_next_job(self) -> Optional[str]:
        """Get next job from priority queues (Enterprise > Premium > Free)"""
        for tier in [UserTier.ENTERPRISE, UserTier.PREMIUM, UserTier.FREE]:
            queue_name = f"queue:{tier.value}"
            result = await self.redis.zpopmax(queue_name)
            if result:
                return result[0][0].decode()
        return None
    
    async def _start_job_processing(self, job_id: str):
        """Start processing a job"""
        # Update job status
        await self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.PROCESSING.value,
            "started_at": datetime.utcnow().isoformat()
        })
        
        # Add to active jobs
        await self.redis.sadd("active_jobs", job_id)
        
        # Get job data for Celery task
        job_data = await self.redis.hgetall(f"job:{job_id}")
        
        # Start Celery task
        generate_report_task.delay(job_id, job_data)
        
        logger.info(f"Started processing job {job_id}")
    
    async def update_job_progress(self, job_id: str, progress: int, stage: str):
        """Update job progress and notify via WebSocket"""
        await self.redis.hset(f"job:{job_id}", mapping={
            "progress": str(progress),
            "stage": stage,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Publish progress update
        await self.redis.publish(f"progress:{job_id}", json.dumps({
            "job_id": job_id,
            "progress": progress,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    async def complete_job(self, job_id: str, report_url: str):
        """Mark job as completed and process next in queue"""
        job_data = await self.redis.hgetall(f"job:{job_id}")
        user_id = job_data[b"user_id"].decode()
        
        # Update job status
        await self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.COMPLETED.value,
            "completed_at": datetime.utcnow().isoformat(),
            "report_url": report_url,
            "progress": "100"
        })
        
        # Remove from active jobs
        await self.redis.srem("active_jobs", job_id)
        await self.redis.srem(f"user_active:{user_id}", job_id)
        
        # Publish completion notification
        await self.redis.publish(f"progress:{job_id}", json.dumps({
            "job_id": job_id,
            "status": "completed",
            "report_url": report_url,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Process next jobs
        await self._process_next_jobs()
        
        logger.info(f"Job {job_id} completed successfully")
    
    async def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed and process next in queue"""
        job_data = await self.redis.hgetall(f"job:{job_id}")
        user_id = job_data[b"user_id"].decode()
        
        await self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.FAILED.value,
            "error_message": error_message,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Remove from active jobs
        await self.redis.srem("active_jobs", job_id)
        await self.redis.srem(f"user_active:{user_id}", job_id)
        
        # Publish failure notification
        await self.redis.publish(f"progress:{job_id}", json.dumps({
            "job_id": job_id,
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        await self._process_next_jobs()
        logger.error(f"Job {job_id} failed: {error_message}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get current job status"""
        job_data = await self.redis.hgetall(f"job:{job_id}")
        if not job_data:
            return None
        
        return {k.decode(): v.decode() for k, v in job_data.items()}
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        active_count = await self.redis.scard("active_jobs")
        
        queue_counts = {}
        for tier in UserTier:
            queue_counts[tier.value] = await self.redis.zcard(f"queue:{tier.value}")
        
        # System resources
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return {
            "active_jobs": active_count,
            "max_concurrent": self.max_concurrent_jobs,
            "queue_counts": queue_counts,
            "total_queued": sum(queue_counts.values()),
            "system_resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        """Cancel a job if it belongs to the user"""
        job_data = await self.redis.hgetall(f"job:{job_id}")
        if not job_data or job_data[b"user_id"].decode() != user_id:
            return False
        
        status = job_data[b"status"].decode()
        if status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
            return False
        
        # Remove from queues and mark as cancelled
        user_tier = job_data[b"user_tier"].decode()
        await self.redis.zrem(f"queue:{user_tier}", job_id)
        await self.redis.srem("active_jobs", job_id)
        await self.redis.srem(f"user_active:{user_id}", job_id)
        
        await self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.CANCELLED.value,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        await self._process_next_jobs()
        return True
    
    async def _update_user_counters(self, user_id: str):
        """Update user job counters"""
        today = datetime.utcnow().date().isoformat()
        
        # Increment daily counter
        await self.redis.incr(f"user_daily:{user_id}:{today}")
        await self.redis.expire(f"user_daily:{user_id}:{today}", 86400)  # 24 hours
    
    def _job_to_dict(self, job: QueueJob) -> Dict[str, str]:
        """Convert job object to Redis-compatible dict"""
        job_dict = asdict(job)
        
        # Convert datetime objects to ISO strings
        for key, value in job_dict.items():
            if isinstance(value, datetime):
                job_dict[key] = value.isoformat()
            elif isinstance(value, Enum):
                job_dict[key] = value.value
            elif value is None:
                job_dict[key] = ""
            else:
                job_dict[key] = str(value)
        
        return job_dict

# Celery configuration
celery_app = Celery('marketmind_pro')
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_concurrency=10,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        'app.core.queue_system.generate_report_task': {'queue': 'reports'},
    }
)

@celery_app.task(bind=True, max_retries=3)
def generate_report_task(self, job_id: str, job_data: Dict):
    """Celery task for report generation with retry logic"""
    import asyncio
    from app.services.optimized_kiro_service import OptimizedKiroService
    
    async def _generate():
        queue_manager = QueueManager("redis://localhost:6379/0")
        kiro_service = OptimizedKiroService()
        
        try:
            ticker = job_data[b"ticker"].decode()
            user_id = job_data[b"user_id"].decode()
            
            # Update progress stages
            await queue_manager.update_job_progress(job_id, 10, "Initializing Kiro CLI")
            await queue_manager.update_job_progress(job_id, 20, "Fetching company data")
            await queue_manager.update_job_progress(job_id, 40, "Generating analysis")
            await queue_manager.update_job_progress(job_id, 70, "Creating visualizations")
            await queue_manager.update_job_progress(job_id, 90, "Finalizing report")
            
            # Generate report using optimized Kiro service
            report_data = await kiro_service.generate_comprehensive_report(ticker)
            
            # Generate PDF and get URL
            from app.services.pdf_generator import PDFGenerator
            pdf_generator = PDFGenerator()
            report_url = await pdf_generator.generate_report_pdf(report_data, job_id)
            
            await queue_manager.complete_job(job_id, report_url)
            
        except Exception as e:
            logger.error(f"Report generation failed for job {job_id}: {str(e)}")
            
            # Retry logic
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))
            else:
                await queue_manager.fail_job(job_id, str(e))
    
    try:
        asyncio.run(_generate())
    except Exception as e:
        logger.error(f"Critical error in report generation task: {str(e)}")
        raise