#!/usr/bin/env python3
"""
System Monitor for MarketMind Pro
Monitors and manages Kiro CLI processes to prevent accumulation
"""

import psutil
import time
import logging
import requests
import json
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor system resources and Kiro CLI processes"""
    
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
        self.max_processes = 10  # Maximum allowed Kiro processes
        self.max_memory_percent = 80  # Maximum memory usage
        self.max_cpu_percent = 90  # Maximum CPU usage
        
    def get_kiro_processes(self) -> List[Dict]:
        """Get all Kiro CLI processes"""
        kiro_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_percent', 'cpu_percent', 'create_time']):
            try:
                if proc.info['name'] and 'kiro-cli' in proc.info['name']:
                    kiro_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': proc.info['cmdline'],
                        'memory_percent': proc.info['memory_percent'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'create_time': proc.info['create_time'],
                        'age_seconds': time.time() - proc.info['create_time']
                    })
                elif proc.info['cmdline'] and any('kiro-cli' in str(cmd) for cmd in proc.info['cmdline']):
                    kiro_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': proc.info['cmdline'],
                        'memory_percent': proc.info['memory_percent'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'create_time': proc.info['create_time'],
                        'age_seconds': time.time() - proc.info['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return kiro_processes
    
    def get_system_stats(self) -> Dict:
        """Get system resource statistics"""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            'cpu_percent': cpu_percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_api_processes(self) -> Dict:
        """Check processes via API"""
        try:
            response = requests.get(f"{self.api_base}/api/v1/system/processes", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_via_api(self) -> Dict:
        """Trigger cleanup via API"""
        try:
            response = requests.post(f"{self.api_base}/api/v1/system/cleanup", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def kill_old_processes(self, max_age_seconds: int = 600) -> int:
        """Kill processes older than max_age_seconds"""
        killed_count = 0
        kiro_processes = self.get_kiro_processes()
        
        for proc_info in kiro_processes:
            if proc_info['age_seconds'] > max_age_seconds:
                try:
                    proc = psutil.Process(proc_info['pid'])
                    proc.kill()
                    logger.info(f"🔪 Killed old process PID {proc_info['pid']} (age: {proc_info['age_seconds']:.1f}s)")
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"Could not kill process {proc_info['pid']}: {e}")
        
        return killed_count
    
    def monitor_and_cleanup(self):
        """Main monitoring loop with automatic cleanup"""
        logger.info("🔍 Starting system monitoring...")
        
        while True:
            try:
                # Get current stats
                system_stats = self.get_system_stats()
                kiro_processes = self.get_kiro_processes()
                api_processes = self.check_api_processes()
                
                process_count = len(kiro_processes)
                memory_percent = system_stats['memory_percent']
                cpu_percent = system_stats['cpu_percent']
                
                logger.info(f"📊 System Status: {process_count} Kiro processes, {memory_percent:.1f}% memory, {cpu_percent:.1f}% CPU")
                
                # Check for cleanup conditions
                cleanup_needed = False
                cleanup_reason = []
                
                if process_count > self.max_processes:
                    cleanup_needed = True
                    cleanup_reason.append(f"Too many processes ({process_count} > {self.max_processes})")
                
                if memory_percent > self.max_memory_percent:
                    cleanup_needed = True
                    cleanup_reason.append(f"High memory usage ({memory_percent:.1f}% > {self.max_memory_percent}%)")
                
                if cpu_percent > self.max_cpu_percent:
                    cleanup_needed = True
                    cleanup_reason.append(f"High CPU usage ({cpu_percent:.1f}% > {self.max_cpu_percent}%)")
                
                # Perform cleanup if needed
                if cleanup_needed:
                    logger.warning(f"🚨 Cleanup triggered: {', '.join(cleanup_reason)}")
                    
                    # Try API cleanup first
                    api_result = self.cleanup_via_api()
                    if "error" not in api_result:
                        logger.info(f"✅ API cleanup successful: {api_result}")
                    else:
                        logger.warning(f"⚠️ API cleanup failed: {api_result['error']}")
                        
                        # Fallback to direct process killing
                        killed = self.kill_old_processes(max_age_seconds=300)  # Kill processes older than 5 minutes
                        logger.info(f"🔪 Direct cleanup killed {killed} processes")
                
                # Kill very old processes regardless
                killed_old = self.kill_old_processes(max_age_seconds=900)  # Kill processes older than 15 minutes
                if killed_old > 0:
                    logger.info(f"🧹 Cleaned up {killed_old} old processes")
                
                # Log detailed process info if many processes
                if process_count > 5:
                    logger.info("📋 Active Kiro processes:")
                    for proc in kiro_processes[:10]:  # Show first 10
                        logger.info(f"  PID {proc['pid']}: {proc['age_seconds']:.1f}s old, {proc['memory_percent']:.1f}% memory")
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {str(e)}")
                time.sleep(30)
    
    def emergency_cleanup(self):
        """Emergency cleanup of all Kiro processes - DISABLED to preserve kiro sessions"""
        logger.info("🚨 Emergency cleanup DISABLED - preserving kiro processes")
        logger.info("✅ Kiro processes preserved")
        return 0

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MarketMind Pro System Monitor")
    parser.add_argument("--api-base", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--emergency", action="store_true", help="Emergency cleanup and exit")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(api_base=args.api_base)
    
    if args.emergency:
        monitor.emergency_cleanup()
        return
    
    if args.once:
        system_stats = monitor.get_system_stats()
        kiro_processes = monitor.get_kiro_processes()
        
        print(f"System Stats: {json.dumps(system_stats, indent=2)}")
        print(f"Kiro Processes: {len(kiro_processes)}")
        for proc in kiro_processes:
            print(f"  PID {proc['pid']}: {proc['age_seconds']:.1f}s old")
        return
    
    # Start monitoring
    monitor.monitor_and_cleanup()

if __name__ == "__main__":
    main()
