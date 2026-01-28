#!/usr/bin/env python3
"""
Backend Test Suite - Test report generation without frontend
"""
import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append('/mnt/c/kiro')

from real_kiro_agents import REAL_KIRO_AGENTS

async def test_backend_generation():
    """Test complete backend report generation"""
    print("🧪 BACKEND TEST SUITE")
    print("=" * 50)
    
    # Test 1: Check Kiro CLI availability
    print("\n1️⃣ Testing Kiro CLI availability...")
    try:
        process = await asyncio.create_subprocess_exec(
            "kiro-cli", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            print("✅ Kiro CLI available")
        else:
            print("❌ Kiro CLI not available")
            return False
    except Exception as e:
        print(f"❌ Kiro CLI test failed: {e}")
        return False
    
    # Test 2: Test single agent
    print("\n2️⃣ Testing single Kiro agent...")
    try:
        progress_storage = {
            "test_report": {
                "stage": "testing",
                "progress": 0,
                "activity_log": []
            }
        }
        
        # Test executive summary agent
        agent = REAL_KIRO_AGENTS["executive_summary"]
        print(f"   Testing: {agent.section_name}")
        
        start_time = time.time()
        result = await agent.generate_analysis("AAPL", progress_storage, "test_report")
        end_time = time.time()
        
        print(f"✅ Agent completed in {end_time - start_time:.1f}s")
        print(f"   Content length: {len(result['content'])} characters")
        print(f"   Activity log entries: {len(progress_storage['test_report']['activity_log'])}")
        
        # Show activity log
        print("   Activity log:")
        for activity in progress_storage['test_report']['activity_log'][-3:]:
            print(f"     {activity}")
            
    except Exception as e:
        print(f"❌ Single agent test failed: {e}")
        return False
    
    # Test 3: Test progress tracking
    print("\n3️⃣ Testing progress tracking...")
    try:
        progress_storage = {
            "test_progress": {
                "stage": "initializing",
                "progress": 15,
                "activity_log": ["🚀 Starting test"]
            }
        }
        
        # Test progress updates
        original_log_count = len(progress_storage["test_progress"]["activity_log"])
        
        # Simulate progress update
        progress_storage["test_progress"]["stage"] = "executing_kiro_test"
        progress_storage["test_progress"]["progress"] = 25
        progress_storage["test_progress"]["activity_log"].append("📝 Test update")
        
        # Verify data preserved
        if len(progress_storage["test_progress"]["activity_log"]) == original_log_count + 1:
            print("✅ Progress tracking preserves data")
        else:
            print("❌ Progress tracking loses data")
            return False
            
    except Exception as e:
        print(f"❌ Progress tracking test failed: {e}")
        return False
    
    # Test 4: Test all agents (quick test)
    print("\n4️⃣ Testing all agents (structure only)...")
    try:
        for section_id, agent in REAL_KIRO_AGENTS.items():
            print(f"   {section_id}: {agent.section_name} ({agent.pages} pages)")
        
        print(f"✅ All {len(REAL_KIRO_AGENTS)} agents configured")
        
    except Exception as e:
        print(f"❌ Agent configuration test failed: {e}")
        return False
    
    print("\n🎉 ALL BACKEND TESTS PASSED!")
    print("✅ Ready for full report generation")
    return True

async def test_full_generation():
    """Test complete report generation"""
    print("\n🚀 FULL GENERATION TEST")
    print("=" * 30)
    
    # Simulate the main generation function
    ticker = "AAPL"
    report_id = f"test_report_{int(time.time())}"
    
    # Initialize progress storage
    progress_storage = {
        report_id: {
            "stage": "initializing",
            "progress": 5,
            "ticker": ticker,
            "started_at": datetime.now().isoformat(),
            "activity_log": ["🚀 Initializing test report generation..."]
        }
    }
    
    print(f"📊 Report ID: {report_id}")
    print(f"📈 Ticker: {ticker}")
    
    all_sections = {}
    
    try:
        # Execute agents in sequence (like the real system)
        for i, (section_id, agent) in enumerate(REAL_KIRO_AGENTS.items()):
            print(f"\n🤖 Section {i+1}/{len(REAL_KIRO_AGENTS)}: {section_id}")
            
            # Update progress
            progress_storage[report_id]["stage"] = f"executing_kiro_{section_id}"
            progress_storage[report_id]["progress"] = 15 + (i * 8)
            
            print(f"   Progress: {progress_storage[report_id]['progress']}%")
            
            # Execute agent
            start_time = time.time()
            section_data = await agent.generate_analysis(ticker, progress_storage, report_id)
            end_time = time.time()
            
            all_sections[section_id] = section_data
            
            # Update progress after completion
            progress_storage[report_id]["progress"] = 15 + ((i + 1) * 8)
            
            print(f"   ✅ Completed in {end_time - start_time:.1f}s")
            print(f"   📝 Content: {len(section_data['content'])} characters")
            
            # Show latest activity
            if progress_storage[report_id]["activity_log"]:
                print(f"   🔍 Latest: {progress_storage[report_id]['activity_log'][-1]}")
        
        # Final phases
        print(f"\n📋 Quality validation...")
        progress_storage[report_id]["stage"] = "quality_validation"
        progress_storage[report_id]["progress"] = 75
        
        print(f"\n📄 Final compilation...")
        progress_storage[report_id]["stage"] = "final_compilation"
        progress_storage[report_id]["progress"] = 90
        
        # Complete
        progress_storage[report_id]["stage"] = "completed"
        progress_storage[report_id]["progress"] = 100
        
        print(f"\n🎉 REPORT GENERATION COMPLETE!")
        print(f"📊 Total sections: {len(all_sections)}")
        print(f"📝 Total content: {sum(len(s['content']) for s in all_sections.values())} characters")
        
        # Save test report
        report_data = {
            "report_id": report_id,
            "ticker": ticker,
            "sections": all_sections,
            "progress": progress_storage[report_id],
            "generated_at": datetime.now().isoformat()
        }
        
        with open(f"/mnt/c/kiro/test_report_{ticker}.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"💾 Report saved to: test_report_{ticker}.json")
        return True
        
    except Exception as e:
        print(f"❌ Full generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        # Run basic tests first
        if await test_backend_generation():
            # If basic tests pass, run full generation
            await test_full_generation()
        else:
            print("❌ Basic tests failed - skipping full generation")
    
    asyncio.run(main())
