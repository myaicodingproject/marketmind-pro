#!/usr/bin/env python3
"""
Process Manager for Kiro CLI - Prevents Process Accumulation
Handles proper lifecycle management of Kiro CLI processes
"""

import asyncio
import subprocess
import psutil
import signal
import logging
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import threading
import atexit
import weakref

logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages Kiro CLI processes with proper cleanup"""
    
    def __init__(self):
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.process_metadata: Dict[str, Dict] = {}
        self.cleanup_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        
        # Register cleanup handlers
        atexit.register(self.cleanup_all_processes)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._background_cleanup, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("🔧 ProcessManager initialized with cleanup handlers")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, initiating cleanup...")
        self.shutdown_event.set()
        self.cleanup_all_processes()
    
    async def execute_kiro_process(self, process_id: str, prompt: str, timeout: int = 480) -> str:
        """Execute Kiro CLI with proper process management"""
        
        try:
            # Clean up any existing process with same ID
            await self.cleanup_process(process_id)
            
            # Create new process
            cmd = ["kiro-cli", "chat"]
            logger.info(f"🚀 Starting Kiro process {process_id}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/mnt/c/kiro"
            )
            
            # Register process
            self.active_processes[process_id] = process
            self.process_metadata[process_id] = {
                'pid': process.pid,
                'started_at': datetime.now(),
                'timeout': timeout,
                'status': 'running'
            }
            
            logger.info(f"📝 Registered process {process_id} with PID {process.pid}")
            
            # Execute with timeout and cleanup
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=prompt.encode()),
                    timeout=timeout
                )
                
                # Mark as completed
                self.process_metadata[process_id]['status'] = 'completed'
                self.process_metadata[process_id]['completed_at'] = datetime.now()
                
                if process.returncode != 0:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    raise Exception(f"Kiro CLI failed: {error_msg}")
                
                result = stdout.decode()
                logger.info(f"✅ Process {process_id} completed successfully")
                
                # Immediate cleanup after success
                await self.cleanup_process(process_id)
                
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Process {process_id} timed out after {timeout}s")
                await self.cleanup_process(process_id, force=True)
                raise Exception(f"Process timeout after {timeout} seconds")
                
        except Exception as e:
            logger.error(f"❌ Process {process_id} failed: {str(e)}")
            await self.cleanup_process(process_id, force=True)
            raise
    
    async def cleanup_process(self, process_id: str, force: bool = False):
        """Clean up a specific process"""
        
        with self.cleanup_lock:
            if process_id not in self.active_processes:
                return
            
            process = self.active_processes[process_id]
            metadata = self.process_metadata.get(process_id, {})
            
            try:
                if process.returncode is None:  # Process still running
                    if force:
                        logger.info(f"🔪 Force killing process {process_id} (PID: {process.pid})")
                        process.kill()
                    else:
                        logger.info(f"🛑 Terminating process {process_id} (PID: {process.pid})")
                        process.terminate()
                    
                    # Wait for termination
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning(f"⚡ Force killing unresponsive process {process_id}")
                        process.kill()
                        await process.wait()
                
                # Clean up system-level process if still exists
                await self._cleanup_system_process(metadata.get('pid'))
                
                logger.info(f"🧹 Cleaned up process {process_id}")
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up process {process_id}: {str(e)}")
            
            finally:
                # Remove from tracking
                self.active_processes.pop(process_id, None)
                self.process_metadata.pop(process_id, None)
    
    async def _cleanup_system_process(self, pid: Optional[int]):
        """Clean up system-level process and children"""
        if not pid:
            return
            
        try:
            if psutil.pid_exists(pid):
                parent = psutil.Process(pid)
                
                # Kill all children first
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.kill()
                        logger.debug(f"🔪 Killed child process {child.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Kill parent
                try:
                    parent.kill()
                    logger.debug(f"🔪 Killed parent process {pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            logger.debug(f"System cleanup error for PID {pid}: {str(e)}")
    
    def cleanup_all_processes(self):
        """Clean up all active processes"""
        logger.info("🧹 Cleaning up all active processes...")
        
        with self.cleanup_lock:
            process_ids = list(self.active_processes.keys())
            
            for process_id in process_ids:
                try:
                    # Run cleanup synchronously for shutdown
                    asyncio.run(self.cleanup_process(process_id, force=True))
                except Exception as e:
                    logger.error(f"Error cleaning up {process_id}: {str(e)}")
        
        # Don't clean up system-wide processes to preserve user sessions
        logger.info("✅ All managed processes cleaned up (user sessions preserved)")
    
    def _cleanup_orphaned_kiro_processes(self):
        """Clean up any orphaned kiro-cli processes - DISABLED to preserve user sessions"""
        # Disabled to prevent killing user's kiro-cli sessions
        logger.info("🔒 Orphaned process cleanup disabled to preserve user sessions")
        return
    
    def _background_cleanup(self):
        """Background thread for periodic cleanup"""
        while not self.shutdown_event.is_set():
            try:
                current_time = datetime.now()
                cleanup_candidates = []
                
                with self.cleanup_lock:
                    for process_id, metadata in self.process_metadata.items():
                        started_at = metadata.get('started_at')
                        timeout = metadata.get('timeout', 480)
                        
                        if started_at and (current_time - started_at).total_seconds() > timeout:
                            cleanup_candidates.append(process_id)
                
                # Clean up timed out processes
                for process_id in cleanup_candidates:
                    logger.warning(f"⏰ Background cleanup of timed out process {process_id}")
                    asyncio.run(self.cleanup_process(process_id, force=True))
                
                # Sleep for 30 seconds before next check
                self.shutdown_event.wait(30)
                
            except Exception as e:
                logger.error(f"Background cleanup error: {str(e)}")
                self.shutdown_event.wait(30)
    
    def get_active_processes(self) -> Dict[str, Dict]:
        """Get information about active processes"""
        with self.cleanup_lock:
            return dict(self.process_metadata)
    
    def get_process_count(self) -> int:
        """Get count of active processes"""
        return len(self.active_processes)

# Global process manager instance
process_manager = ProcessManager()

# Context manager for process execution
class ManagedKiroProcess:
    """Context manager for Kiro CLI process execution"""
    
    def __init__(self, process_id: str, timeout: int = 480):
        self.process_id = process_id
        self.timeout = timeout
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await process_manager.cleanup_process(self.process_id, force=True)
    
    async def execute(self, prompt: str) -> str:
        """Execute Kiro CLI with managed cleanup"""
        return await process_manager.execute_kiro_process(
            self.process_id, prompt, self.timeout
        )

# Utility functions
async def execute_managed_kiro(process_id: str, prompt: str, timeout: int = 480) -> str:
    """Execute Kiro CLI with automatic cleanup"""
    async with ManagedKiroProcess(process_id, timeout) as manager:
        return await manager.execute(prompt)

def cleanup_all_kiro_processes():
    """Emergency cleanup function"""
    process_manager.cleanup_all_processes()

if __name__ == "__main__":
    # Test the process manager
    async def test():
        result = await execute_managed_kiro("test", "What is 2+2?", timeout=60)
        print(f"Result: {result}")
    
    asyncio.run(test())
