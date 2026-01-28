# Queue Persistence and Recovery System
# Handles system failures and ensures queue integrity

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import redis.asyncio as redis
from app.core.queue_system import QueueManager, JobStatus, UserTier

logger = logging.getLogger(__name__)

class QueueRecoveryManager:
    """Handles queue persistence, recovery, and cleanup operations"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.queue_manager = QueueManager(redis_url)
    
    async def backup_queue_state(self) -> Dict:
        """Create a backup of the current queue state"""
        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_jobs": [],
            "queued_jobs": {},
            "job_data": {}
        }
        
        # Backup active jobs
        active_jobs = await self.redis.smembers("active_jobs")
        backup_data["active_jobs"] = [job.decode() for job in active_jobs]
        
        # Backup queued jobs by tier
        for tier in UserTier:
            queue_name = f"queue:{tier.value}"
            queued_jobs = await self.redis.zrange(queue_name, 0, -1, withscores=True)
            backup_data["queued_jobs"][tier.value] = [
                {"job_id": job[0].decode(), "priority": job[1]} 
                for job in queued_jobs
            ]
        
        # Backup job data for all jobs
        all_job_ids = set(backup_data["active_jobs"])
        for tier_jobs in backup_data["queued_jobs"].values():
            all_job_ids.update([job["job_id"] for job in tier_jobs])
        
        for job_id in all_job_ids:
            job_data = await self.redis.hgetall(f"job:{job_id}")
            if job_data:
                backup_data["job_data"][job_id] = {
                    k.decode(): v.decode() for k, v in job_data.items()
                }
        
        # Store backup in Redis with expiration
        backup_key = f"queue_backup:{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        await self.redis.setex(backup_key, 86400 * 7, json.dumps(backup_data))  # 7 days
        
        logger.info(f"Queue state backed up to {backup_key}")
        return backup_data
    
    async def recover_from_backup(self, backup_key: str = None) -> bool:
        """Recover queue state from backup"""
        try:
            if not backup_key:
                # Find the most recent backup
                backup_keys = await self.redis.keys("queue_backup:*")
                if not backup_keys:
                    logger.error("No backup found for recovery")
                    return False
                backup_key = max(backup_keys).decode()
            
            backup_data_str = await self.redis.get(backup_key)
            if not backup_data_str:
                logger.error(f"Backup {backup_key} not found")
                return False
            
            backup_data = json.loads(backup_data_str)
            
            # Clear current queue state
            await self._clear_queue_state()
            
            # Restore job data
            for job_id, job_data in backup_data["job_data"].items():
                await self.redis.hset(f"job:{job_id}", mapping=job_data)
            
            # Restore queued jobs
            for tier, jobs in backup_data["queued_jobs"].items():
                queue_name = f"queue:{tier}"
                for job in jobs:
                    await self.redis.zadd(queue_name, {job["job_id"]: job["priority"]})
            
            # Restore active jobs (but mark them as failed for manual review)
            for job_id in backup_data["active_jobs"]:
                await self.redis.hset(f"job:{job_id}", mapping={
                    "status": JobStatus.FAILED.value,
                    "error_message": "System recovery - job was active during failure",
                    "completed_at": datetime.utcnow().isoformat()
                })
            
            logger.info(f"Queue state recovered from {backup_key}")
            return True
        
        except Exception as e:
            logger.error(f"Error recovering from backup: {str(e)}")
            return False
    
    async def _clear_queue_state(self):
        """Clear current queue state for recovery"""
        # Clear active jobs
        await self.redis.delete("active_jobs")
        
        # Clear queues
        for tier in UserTier:
            await self.redis.delete(f"queue:{tier.value}")
    
    async def cleanup_expired_jobs(self, max_age_hours: int = 24):
        """Clean up old completed/failed jobs"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cutoff_str = cutoff_time.isoformat()
        
        # Find all job keys
        job_keys = await self.redis.keys("job:*")
        cleaned_count = 0
        
        for job_key in job_keys:
            job_data = await self.redis.hgetall(job_key)
            if not job_data:
                continue
            
            status = job_data.get(b"status", b"").decode()
            completed_at = job_data.get(b"completed_at", b"").decode()
            
            # Clean up completed/failed jobs older than cutoff
            if status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
                if completed_at and completed_at < cutoff_str:
                    await self.redis.delete(job_key)
                    cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired jobs")
        return cleaned_count
    
    async def detect_stale_jobs(self, max_processing_hours: int = 2):
        """Detect and handle stale processing jobs"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_processing_hours)
        cutoff_str = cutoff_time.isoformat()
        
        active_jobs = await self.redis.smembers("active_jobs")
        stale_jobs = []
        
        for job_id_bytes in active_jobs:
            job_id = job_id_bytes.decode()
            job_data = await self.redis.hgetall(f"job:{job_id}")
            
            if not job_data:
                # Job data missing - remove from active
                await self.redis.srem("active_jobs", job_id)
                continue
            
            started_at = job_data.get(b"started_at", b"").decode()
            status = job_data.get(b"status", b"").decode()
            
            if status == JobStatus.PROCESSING.value and started_at < cutoff_str:
                stale_jobs.append(job_id)
        
        # Handle stale jobs
        for job_id in stale_jobs:
            await self.queue_manager.fail_job(
                job_id, 
                f"Job stale - processing for more than {max_processing_hours} hours"
            )
        
        logger.info(f"Detected and handled {len(stale_jobs)} stale jobs")
        return stale_jobs
    
    async def validate_queue_integrity(self) -> Dict:
        """Validate queue integrity and report issues"""
        issues = []
        
        # Check for orphaned active jobs
        active_jobs = await self.redis.smembers("active_jobs")
        for job_id_bytes in active_jobs:
            job_id = job_id_bytes.decode()
            job_exists = await self.redis.exists(f"job:{job_id}")
            if not job_exists:
                issues.append(f"Active job {job_id} has no job data")
                await self.redis.srem("active_jobs", job_id)
        
        # Check for jobs in queues without data
        for tier in UserTier:
            queue_name = f"queue:{tier.value}"
            queued_jobs = await self.redis.zrange(queue_name, 0, -1)
            
            for job_id_bytes in queued_jobs:
                job_id = job_id_bytes.decode()
                job_exists = await self.redis.exists(f"job:{job_id}")
                if not job_exists:
                    issues.append(f"Queued job {job_id} in {queue_name} has no job data")
                    await self.redis.zrem(queue_name, job_id)
        
        # Check for inconsistent job statuses
        job_keys = await self.redis.keys("job:*")
        for job_key in job_keys:
            job_id = job_key.decode().split(":")[-1]
            job_data = await self.redis.hgetall(job_key)
            
            if not job_data:
                continue
            
            status = job_data.get(b"status", b"").decode()
            
            # Check if processing job is in active set
            if status == JobStatus.PROCESSING.value:
                is_active = await self.redis.sismember("active_jobs", job_id)
                if not is_active:
                    issues.append(f"Processing job {job_id} not in active set")
                    await self.redis.sadd("active_jobs", job_id)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "issues_found": len(issues),
            "issues": issues,
            "status": "healthy" if not issues else "issues_detected"
        }
    
    async def get_recovery_status(self) -> Dict:
        """Get current recovery and health status"""
        # Get recent backups
        backup_keys = await self.redis.keys("queue_backup:*")
        recent_backups = sorted([key.decode() for key in backup_keys])[-5:]  # Last 5 backups
        
        # Get queue stats
        queue_stats = await self.queue_manager.get_queue_stats()
        
        # Check integrity
        integrity_report = await self.validate_queue_integrity()
        
        return {
            "recent_backups": recent_backups,
            "queue_stats": queue_stats,
            "integrity_report": integrity_report,
            "last_cleanup": await self.redis.get("last_cleanup_time"),
            "system_status": "operational"
        }

# Scheduled tasks for maintenance
async def scheduled_maintenance():
    """Run scheduled maintenance tasks"""
    recovery_manager = QueueRecoveryManager("redis://localhost:6379/0")
    
    # Daily backup
    await recovery_manager.backup_queue_state()
    
    # Clean up expired jobs
    await recovery_manager.cleanup_expired_jobs()
    
    # Detect stale jobs
    await recovery_manager.detect_stale_jobs()
    
    # Validate integrity
    await recovery_manager.validate_queue_integrity()
    
    # Update last maintenance time
    await recovery_manager.redis.set("last_cleanup_time", datetime.utcnow().isoformat())
    
    logger.info("Scheduled maintenance completed")