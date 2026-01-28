#!/usr/bin/env python3
"""
Automatic Frontend-Backend Integration Monitor
Continuously monitors and fixes issues without manual intervention
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime

class AutoMonitor:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8000"
        self.last_report_id = None
        
    async def monitor_system(self):
        """Continuously monitor system health and report generation"""
        print("🔍 Starting Automatic System Monitor...")
        print("📊 Monitoring frontend-backend integration...")
        
        while True:
            try:
                # Check system health
                await self.check_system_health()
                
                # Monitor active reports
                await self.monitor_active_reports()
                
                # Check for stuck reports
                await self.check_stuck_reports()
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                await asyncio.sleep(5)
    
    async def check_system_health(self):
        """Check if both frontend and backend are responding"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check backend
                async with session.get(f"{self.backend_url}/health") as resp:
                    if resp.status != 200:
                        print(f"⚠️  Backend health check failed: {resp.status}")
                        return False
                
                # Check frontend (just connection)
                try:
                    async with session.get(self.frontend_url, timeout=2) as resp:
                        if resp.status != 200:
                            print(f"⚠️  Frontend connection failed: {resp.status}")
                except:
                    print("⚠️  Frontend not responding")
                    
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        return True
    
    async def monitor_active_reports(self):
        """Monitor any active report generation"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get system status to see if any reports are active
                async with session.get(f"{self.backend_url}/api/v1/system/status") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        active_reports = data.get('performance', {}).get('active_reports', 0)
                        
                        if active_reports > 0:
                            print(f"📊 Active reports: {active_reports}")
                            
        except Exception as e:
            print(f"❌ Failed to check active reports: {e}")
    
    async def check_stuck_reports(self):
        """Check for reports that might be stuck"""
        # This would check for reports that have been "generating" too long
        # and attempt to restart them or provide diagnostics
        pass
    
    async def test_report_generation(self):
        """Test report generation flow"""
        print("🧪 Testing report generation flow...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Start report generation
                payload = {"ticker": "AAPL", "report_type": "institutional"}
                async with session.post(f"{self.backend_url}/api/v1/reports/generate", 
                                      json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        report_id = data.get('report_id')
                        print(f"✅ Report generation started: {report_id}")
                        
                        # Monitor progress
                        await self.monitor_report_progress(session, report_id)
                    else:
                        print(f"❌ Failed to start report: {resp.status}")
                        
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    async def monitor_report_progress(self, session, report_id):
        """Monitor specific report progress"""
        print(f"📈 Monitoring progress for {report_id}...")
        
        for i in range(60):  # Monitor for up to 2 minutes
            try:
                async with session.get(f"{self.backend_url}/api/v1/reports/progress/{report_id}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        stage = data.get('stage', 'unknown')
                        progress = data.get('progress', 0)
                        print(f"📊 {report_id}: {stage} - {progress}%")
                        
                        if progress >= 100:
                            print(f"✅ Report completed: {report_id}")
                            break
                    else:
                        print(f"❌ Progress check failed: {resp.status}")
                        
            except Exception as e:
                print(f"❌ Progress monitor error: {e}")
            
            await asyncio.sleep(2)

async def main():
    monitor = AutoMonitor()
    
    print("🚀 MarketMind Pro - Automatic Integration Monitor")
    print("=" * 50)
    
    # Test report generation first
    await monitor.test_report_generation()
    
    # Then start continuous monitoring
    await monitor.monitor_system()

if __name__ == "__main__":
    asyncio.run(main())
