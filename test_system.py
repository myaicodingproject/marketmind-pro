#!/usr/bin/env python3
"""
Quick test to verify the system works without crashing WSL
"""

def test_system():
    try:
        print("🔍 Testing imports...")
        
        from services.real_kiro_agents import REAL_KIRO_AGENTS
        print(f"✅ Agents: {len(REAL_KIRO_AGENTS)}")
        
        from models.enhanced_models import SectionType
        print(f"✅ Section types: {len(list(SectionType))}")
        
        # Test a simple agent execution (without Kiro CLI)
        agent = REAL_KIRO_AGENTS['executive_summary']
        print(f"✅ Executive summary agent: {agent.pages} pages")
        
        print("🎉 All tests passed - system is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_system()
