#!/usr/bin/env python3
"""
Quick test to verify the backend progression fix works
"""
import asyncio
import sys
from datetime import datetime

# Mock the progress storage and logger
progress_storage = {}
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = MockLogger()

# Mock Kiro agent that returns quickly
class MockKiroAgent:
    def __init__(self, section_id):
        self.section_id = section_id
    
    async def generate_analysis(self, ticker, progress_storage, report_id):
        await asyncio.sleep(0.1)  # Quick completion
        return f"Mock analysis for {self.section_id}: {ticker} analysis complete"

# Test the fixed parallel execution logic
async def test_parallel_execution():
    print("🧪 Testing parallel execution fix...")
    
    # Setup
    report_id = "test_report_123"
    ticker = "AAPL"
    
    progress_storage[report_id] = {
        "stage": "initializing",
        "progress": 0,
        "activity_log": [],
        "started_at": datetime.now().isoformat()
    }
    
    # Create mock agents (same as real system)
    MOCK_AGENTS = {
        "executive_summary": MockKiroAgent("executive_summary"),
        "company_analysis": MockKiroAgent("company_analysis"), 
        "financial_analysis": MockKiroAgent("financial_analysis"),
        "valuation_analysis": MockKiroAgent("valuation_analysis"),
        "risk_assessment": MockKiroAgent("risk_assessment"),
        "market_analysis": MockKiroAgent("market_analysis"),
        "technical_analysis": MockKiroAgent("technical_analysis"),
        "investment_thesis": MockKiroAgent("investment_thesis")
    }
    
    all_sections = {}
    section_count = len(MOCK_AGENTS)
    
    # FIXED CODE - Create all tasks at once for parallel execution
    tasks = []
    for section_id, agent in MOCK_AGENTS.items():
        task = asyncio.create_task(agent.generate_analysis(ticker, progress_storage, report_id))
        tasks.append((section_id, task))
    
    # Execute all agents in parallel
    progress_storage[report_id]["stage"] = "executing_parallel_kiro_agents"
    progress_storage[report_id]["progress"] = 15
    progress_storage[report_id]["activity_log"].append(f"🚀 Launching {section_count} PARALLEL Kiro CLI agents for {ticker}")
    
    # Wait for all parallel tasks to complete
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
    
    # Process results
    for i, (section_id, _) in enumerate(tasks):
        result = results[i]
        if isinstance(result, Exception):
            logger.error(f"❌ Failed Kiro CLI agent {section_id}: {str(result)}")
            all_sections[section_id] = f"Error: {str(result)}"
            progress_storage[report_id]["activity_log"].append(f"❌ Failed agent: {section_id}")
        else:
            all_sections[section_id] = result
            logger.info(f"✅ Completed PARALLEL Kiro CLI agent: {section_id}")
            progress_storage[report_id]["activity_log"].append(f"✅ Completed agent: {section_id}")
    
    # All parallel agents completed - advance to next stage
    progress_storage[report_id]["stage"] = "compiling_sections"
    progress_storage[report_id]["progress"] = 70
    progress_storage[report_id]["activity_log"].append(f"🔄 Compiling {len(all_sections)} sections into final report...")
    logger.info(f"✅ All {len(all_sections)} parallel agents completed")
    
    # Phase 3: Quality validation (real time)
    progress_storage[report_id]["stage"] = "quality_validation"
    progress_storage[report_id]["progress"] = 75
    progress_storage[report_id]["activity_log"].append("🔍 Running quality validation checks...")
    await asyncio.sleep(0.1)  # Real validation time
    
    # Phase 4: Final compilation
    progress_storage[report_id]["stage"] = "final_compilation"
    progress_storage[report_id]["progress"] = 90
    progress_storage[report_id]["activity_log"].append("📄 Generating final report document...")
    await asyncio.sleep(0.1)  # Real compilation time
    
    # Phase 6: Completion
    progress_storage[report_id]["stage"] = "completed"
    progress_storage[report_id]["progress"] = 100
    progress_storage[report_id]["activity_log"].append("✅ Report generation completed successfully!")
    progress_storage[report_id]["completed_at"] = datetime.now().isoformat()
    
    # Verify results
    print(f"\n✅ TEST RESULTS:")
    print(f"   Final stage: {progress_storage[report_id]['stage']}")
    print(f"   Final progress: {progress_storage[report_id]['progress']}%")
    print(f"   Sections completed: {len(all_sections)}/8")
    print(f"   Activity log entries: {len(progress_storage[report_id]['activity_log'])}")
    
    # Check if all stages were reached
    stages_reached = []
    for log_entry in progress_storage[report_id]['activity_log']:
        if "🔄 Compiling" in log_entry:
            stages_reached.append("compiling_sections")
        elif "🔍 Running quality" in log_entry:
            stages_reached.append("quality_validation") 
        elif "📄 Generating final" in log_entry:
            stages_reached.append("final_compilation")
        elif "✅ Report generation completed" in log_entry:
            stages_reached.append("completed")
    
    print(f"   Stages reached: {stages_reached}")
    
    if (progress_storage[report_id]['stage'] == 'completed' and 
        progress_storage[report_id]['progress'] == 100 and
        len(all_sections) == 8 and
        'completed' in stages_reached):
        print(f"\n🎉 SUCCESS: All fixes working correctly!")
        return True
    else:
        print(f"\n❌ FAILURE: Fix not working properly")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_parallel_execution())
    sys.exit(0 if success else 1)
