"""
Robust Process Management for Kiro CLI Execution
Prevents memory leaks, manages resources, and ensures system stability
"""
import asyncio
import psutil
import signal
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
import weakref
import gc

logger = logging.getLogger(__name__)

class ProcessStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class ProcessMetrics:
    """Process resource usage metrics"""
    cpu_percent: float
    memory_mb: float
    start_time: float
    duration: float
    status: ProcessStatus

class ProcessManager:
    """Robust process manager for Kiro CLI execution"""
    
    def __init__(self, max_concurrent: int = 3, max_memory_mb: int = 2048, timeout_seconds: int = 300):
        self.max_concurrent = max_concurrent
        self.max_memory_mb = max_memory_mb
        self.timeout_seconds = timeout_seconds
        
        # Process tracking
        self._active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self._process_metrics: Dict[str, ProcessMetrics] = {}
        self._process_queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Weak references for cleanup
        self._process_refs = weakref.WeakSet()
        
    async def start(self):
        """Start the process manager"""
        logger.info("Starting Kiro Process Manager")
        self._health_check_task = asyncio.create_task(self._health_monitor())
        self._cleanup_task = asyncio.create_task(self._cleanup_monitor())
        
    async def stop(self):
        """Stop the process manager and cleanup"""
        logger.info("Stopping Kiro Process Manager")
        
        # Cancel monitoring tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
        # Terminate all active processes
        await self._terminate_all_processes()
        
        # Force garbage collection
        gc.collect()
        
    @asynccontextmanager
    async def managed_process(self, process_id: str, command: List[str], **kwargs):
        """Context manager for safe process execution"""
        process = None
        try:
            async with self._semaphore:  # Limit concurrent processes
                # Check resource availability
                await self._check_resources()
                
                # Create process
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    **kwargs
                )
                
                # Track process
                self._active_processes[process_id] = process
                self._process_refs.add(process)
                
                # Initialize metrics
                self._process_metrics[process_id] = ProcessMetrics(
                    cpu_percent=0.0,
                    memory_mb=0.0,
                    start_time=time.time(),
                    duration=0.0,
                    status=ProcessStatus.RUNNING
                )
                
                logger.info(f"Started process {process_id} (PID: {process.pid})")
                yield process
                
        except Exception as e:
            logger.error(f"Error in managed process {process_id}: {e}")
            if process_id in self._process_metrics:
                self._process_metrics[process_id].status = ProcessStatus.FAILED
            raise
        finally:
            # Cleanup process
            if process and process.returncode is None:
                await self._terminate_process(process_id, process)
            
            # Remove from tracking
            self._active_processes.pop(process_id, None)
            
            # Update metrics
            if process_id in self._process_metrics:
                metrics = self._process_metrics[process_id]
                metrics.duration = time.time() - metrics.start_time
                if metrics.status == ProcessStatus.RUNNING:
                    metrics.status = ProcessStatus.COMPLETED
                    
    async def execute_with_timeout(self, process_id: str, command: List[str], 
                                 timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Execute command with timeout and resource monitoring"""
        timeout = timeout or self.timeout_seconds
        
        try:
            async with self.managed_process(process_id, command, **kwargs) as process:
                # Wait for completion with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=timeout
                    )
                    
                    return {
                        "success": True,
                        "stdout": stdout.decode('utf-8', errors='replace'),
                        "stderr": stderr.decode('utf-8', errors='replace'),
                        "returncode": process.returncode,
                        "metrics": self._process_metrics.get(process_id)
                    }
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Process {process_id} timed out after {timeout}s")
                    self._process_metrics[process_id].status = ProcessStatus.TIMEOUT
                    await self._terminate_process(process_id, process)
                    
                    return {
                        "success": False,
                        "error": f"Process timed out after {timeout} seconds",
                        "metrics": self._process_metrics.get(process_id)
                    }
                    
        except Exception as e:
            logger.error(f"Process execution error for {process_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "metrics": self._process_metrics.get(process_id)
            }
            
    async def _check_resources(self):
        """Check system resources before starting new process"""
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            raise RuntimeError(f"System memory usage too high: {memory.percent}%")
            
        # Check active process memory
        total_process_memory = sum(
            metrics.memory_mb for metrics in self._process_metrics.values()
            if metrics.status == ProcessStatus.RUNNING
        )
        
        if total_process_memory > self.max_memory_mb:
            raise RuntimeError(f"Process memory limit exceeded: {total_process_memory}MB")
            
    async def _health_monitor(self):
        """Monitor process health and resource usage"""
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                for process_id, process in list(self._active_processes.items()):
                    try:
                        # Get process info
                        proc_info = psutil.Process(process.pid)
                        
                        # Update metrics
                        if process_id in self._process_metrics:
                            metrics = self._process_metrics[process_id]
                            metrics.cpu_percent = proc_info.cpu_percent()
                            metrics.memory_mb = proc_info.memory_info().rss / 1024 / 1024
                            
                            # Check for resource violations
                            if metrics.memory_mb > 512:  # 512MB per process limit
                                logger.warning(f"Process {process_id} using excessive memory: {metrics.memory_mb}MB")
                                await self._terminate_process(process_id, process)
                                
                    except (psutil.NoSuchProcess, ProcessLookupError):
                        # Process already terminated
                        self._active_processes.pop(process_id, None)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                
    async def _cleanup_monitor(self):
        """Periodic cleanup of completed processes and memory"""
        while True:
            try:
                await asyncio.sleep(30)  # Cleanup every 30 seconds
                
                # Remove old metrics (keep last 100)
                if len(self._process_metrics) > 100:
                    sorted_metrics = sorted(
                        self._process_metrics.items(),
                        key=lambda x: x[1].start_time
                    )
                    
                    # Keep only the most recent 50
                    to_remove = sorted_metrics[:-50]
                    for process_id, _ in to_remove:
                        self._process_metrics.pop(process_id, None)
                        
                # Force garbage collection
                gc.collect()
                
                logger.debug(f"Cleanup: {len(self._active_processes)} active, {len(self._process_metrics)} tracked")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup monitor error: {e}")
                
    async def _terminate_process(self, process_id: str, process: asyncio.subprocess.Process):
        """Safely terminate a process"""
        try:
            if process.returncode is None:
                # Try graceful termination first
                process.terminate()
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    # Force kill if graceful termination fails
                    process.kill()
                    await process.wait()
                    
                logger.info(f"Terminated process {process_id}")
                
        except Exception as e:
            logger.error(f"Error terminating process {process_id}: {e}")
            
    async def _terminate_all_processes(self):
        """Terminate all active processes"""
        for process_id, process in list(self._active_processes.items()):
            await self._terminate_process(process_id, process)
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get current process metrics"""
        return {
            "active_processes": len(self._active_processes),
            "total_tracked": len(self._process_metrics),
            "system_memory_percent": psutil.virtual_memory().percent,
            "system_cpu_percent": psutil.cpu_percent(),
            "process_details": {
                pid: {
                    "status": metrics.status.value,
                    "memory_mb": metrics.memory_mb,
                    "cpu_percent": metrics.cpu_percent,
                    "duration": metrics.duration
                }
                for pid, metrics in self._process_metrics.items()
                if metrics.status == ProcessStatus.RUNNING
            }
        }
        
    async def restart_failed_processes(self):
        """Restart any failed processes (if configured for auto-restart)"""
        # This would be implemented based on specific restart policies
        pass

# Global process manager instance
process_manager = ProcessManager()