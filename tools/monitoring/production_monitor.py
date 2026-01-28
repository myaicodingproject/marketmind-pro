#!/usr/bin/env python3
"""
Production Monitor - Real-time monitoring of MarketMind Pro
Tracks all processes, logs, and can intervene when needed
"""
import asyncio
import subprocess
import time
import json
import requests
from datetime import datetime
import sys
import os

class ProductionMonitor:
    def __init__(self):
        self.backend_process = None
        self.report_id = None
        self.start_time = None
        self.log_file = "/mnt/c/kiro/logs/production_monitor.log"
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"{timestamp} | {message}"
        print(log_entry)
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def start_backend(self):
        """Start the backend server"""
        self.log("🚀 Starting backend server...")
        os.chdir("/mnt/c/kiro")
        self.backend_process = subprocess.Popen(
            ["python3", "complete_production_system.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Wait for startup
        self.log("✅ Backend started")
    
    def check_backend_health(self):
        """Check if backend is responding"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_report_generation(self, ticker="AAPL"):
        """Start a real report generation"""
        self.log(f"📊 Starting REAL report generation for {ticker}")
        self.start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/reports/generate",
                json={"ticker": ticker, "include_pdf": True},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.report_id = data.get("report_id")
                self.log(f"✅ Report started: {self.report_id}")
                return True
            else:
                self.log(f"❌ Failed to start report: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error starting report: {e}")
            return False
    
    def get_report_progress(self):
        """Get current report progress"""
        if not self.report_id:
            return None
            
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/reports/progress/{self.report_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except:
            return None
    
    def check_kiro_processes(self):
        """Check running Kiro CLI processes"""
        try:
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            
            kiro_lines = [line for line in result.stdout.split('\n') if 'kiro-cli' in line]
            return len(kiro_lines)
        except:
            return 0
    
    def kill_stuck_processes(self):
        """Kill stuck Kiro CLI processes"""
        self.log("🔪 Killing stuck Kiro CLI processes...")
        subprocess.run(["pkill", "-f", "kiro-cli-chat"], capture_output=True)
        subprocess.run(["pkill", "-f", "kiro-cli"], capture_output=True)
        time.sleep(2)
        self.log("✅ Processes killed")
    
    async def monitor_report(self, max_minutes=15):
        """Monitor report generation with timeout"""
        self.log(f"👁️ Monitoring report (max {max_minutes} minutes)...")
        
        start_time = time.time()
        last_progress = 0
        stuck_count = 0
        
        while True:
            elapsed = (time.time() - start_time) / 60
            
            # Check timeout
            if elapsed > max_minutes:
                self.log(f"⏰ TIMEOUT after {elapsed:.1f} minutes - KILLING PROCESSES")
                self.kill_stuck_processes()
                return False
            
            # Get progress
            progress_data = self.get_report_progress()
            if not progress_data:
                self.log("❌ Cannot get progress - backend may be down")
                await asyncio.sleep(5)
                continue
            
            current_progress = progress_data.get("progress", 0)
            stage = progress_data.get("stage", "unknown")
            status = progress_data.get("status", "unknown")
            
            # Check if completed
            if status == "completed" or stage == "completed" or current_progress >= 100:
                self.log(f"🎉 REPORT COMPLETED! Time: {elapsed:.1f} minutes")
                return True
            
            # Check if stuck
            if current_progress == last_progress:
                stuck_count += 1
                if stuck_count > 12:  # 1 minute stuck
                    self.log(f"🚨 STUCK at {current_progress}% for 1+ minutes")
                    kiro_count = self.check_kiro_processes()
                    self.log(f"   Kiro processes running: {kiro_count}")
            else:
                stuck_count = 0
            
            # Log progress
            self.log(f"📈 Progress: {current_progress}% | Stage: {stage} | Time: {elapsed:.1f}min")
            
            last_progress = current_progress
            await asyncio.sleep(5)
    
    async def run_full_test(self, ticker="AAPL"):
        """Run complete production test"""
        self.log("=" * 60)
        self.log("🎯 STARTING FULL PRODUCTION TEST")
        self.log("=" * 60)
        
        # 1. Start backend
        if not self.check_backend_health():
            self.start_backend()
            time.sleep(5)
        
        if not self.check_backend_health():
            self.log("❌ Backend failed to start")
            return False
        
        # 2. Start report
        if not self.start_report_generation(ticker):
            self.log("❌ Failed to start report")
            return False
        
        # 3. Monitor progress
        success = await self.monitor_report()
        
        # 4. Results
        if success:
            self.log("🎉 PRODUCTION TEST SUCCESSFUL!")
            # Get final report
            final_data = self.get_report_progress()
            if final_data:
                self.log(f"📊 Final status: {final_data.get('status')}")
                self.log(f"📈 Final progress: {final_data.get('progress')}%")
        else:
            self.log("❌ PRODUCTION TEST FAILED")
        
        return success

async def main():
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = "AAPL"
    
    monitor = ProductionMonitor()
    success = await monitor.run_full_test(ticker)
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
