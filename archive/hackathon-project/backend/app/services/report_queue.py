# A4.3: Report Queue System - CRITICAL Concurrent User Handling

import asyncio
import redis.asyncio as redis
from celery import Celery
from typing import Dict, Optional
import json
import uuid
from datetime import datetime, timedelta

class ReportQueue:
    def __init__(self, redis_url: str, max_concurrent: int = 50):
        self.redis = redis.from_url(redis_url)
        self.max_concurrent = max_concurrent
        self.active_jobs = {}
    
    async def enqueue_report(self, ticker: str, user_id: str) -> str:
        """Enqueue report generation with priority handling"""
        queue_id = str(uuid.uuid4())
        
        # Check queue capacity
        active_count = await self.redis.llen("active_reports")
        if active_count >= self.max_concurrent:
            await self.redis.lpush("pending_reports", json.dumps({
                "queue_id": queue_id,
                "ticker": ticker,
                "user_id": user_id,
                "queued_at": datetime.utcnow().isoformat()
            }))
            status = "queued"
        else:
            await self._start_processing(queue_id, ticker, user_id)
            status = "processing"
        
        # Store job metadata
        await self.redis.hset(f"job:{queue_id}", mapping={
            "ticker": ticker,
            "user_id": user_id,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "progress": "0"
        })
        
        return queue_id
    
    async def _start_processing(self, queue_id: str, ticker: str, user_id: str):
        """Start report processing"""
        await self.redis.lpush("active_reports", queue_id)
        await self.redis.hset(f"job:{queue_id}", "status", "processing")
        
        # Trigger Celery task
        generate_report_task.delay(queue_id, ticker, user_id)
    
    async def update_progress(self, queue_id: str, progress: int, stage: str):
        """Update job progress"""
        await self.redis.hset(f"job:{queue_id}", mapping={
            "progress": str(progress),
            "stage": stage,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Publish to WebSocket channel
        await self.redis.publish(f"progress:{queue_id}", json.dumps({
            "progress": progress,
            "stage": stage
        }))
    
    async def complete_job(self, queue_id: str, report_url: str):
        """Mark job as complete and process queue"""
        await self.redis.hset(f"job:{queue_id}", mapping={
            "status": "completed",
            "report_url": report_url,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Remove from active queue
        await self.redis.lrem("active_reports", 1, queue_id)
        
        # Process next queued job
        await self._process_next_queued()
    
    async def _process_next_queued(self):
        """Process next job in queue"""
        queued_job = await self.redis.rpop("pending_reports")
        if queued_job:
            job_data = json.loads(queued_job)
            await self._start_processing(
                job_data["queue_id"],
                job_data["ticker"], 
                job_data["user_id"]
            )
    
    async def get_job_status(self, queue_id: str) -> Optional[Dict]:
        """Get current job status"""
        job_data = await self.redis.hgetall(f"job:{queue_id}")
        if not job_data:
            return None
        
        return {k.decode(): v.decode() for k, v in job_data.items()}

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
)

@celery_app.task
def generate_report_task(queue_id: str, ticker: str, user_id: str):
    """Celery task for report generation"""
    import asyncio
    from app.services.kiro_engine import KiroEngine
    
    async def _generate():
        queue = ReportQueue("redis://localhost:6379/0")
        kiro = KiroEngine()
        
        try:
            await queue.update_progress(queue_id, 10, "Initializing")
            report_url = await kiro.generate_full_report(ticker, queue_id)
            await queue.complete_job(queue_id, report_url)
        except Exception as e:
            await queue.redis.hset(f"job:{queue_id}", "status", "failed")
            raise
    
    asyncio.run(_generate())