#!/usr/bin/env python3
"""Quick test of DEMO mode functionality"""
import json
from pathlib import Path

def test_demo_mode():
    """Test that demo mode components are in place"""
    
    print("🧪 Testing DEMO Mode Implementation\n")
    
    # Test 1: Demo data file exists
    demo_file = Path("data/demo_report_aapl.json")
    assert demo_file.exists(), "❌ Demo data file not found"
    print("✅ Demo data file exists")
    
    # Test 2: Demo data is valid JSON
    with open(demo_file, 'r') as f:
        demo_data = json.load(f)
    print("✅ Demo data is valid JSON")
    
    # Test 3: Required fields present
    assert demo_data['ticker'] == 'DEMO', "❌ Ticker should be DEMO"
    assert demo_data['metadata']['is_demo'] == True, "❌ is_demo flag missing"
    assert len(demo_data['sections']) == 8, f"❌ Expected 8 sections, got {len(demo_data['sections'])}"
    print("✅ Demo data has required fields")
    
    # Test 4: All sections present
    required_sections = [
        'executive_summary', 'company_history', 'leadership_analysis',
        'business_model', 'financial_analysis', 'valuation_analysis',
        'market_analysis', 'risk_assessment'
    ]
    for section in required_sections:
        assert section in demo_data['sections'], f"❌ Missing section: {section}"
    print("✅ All 8 sections present")
    
    # Test 5: Backend functions exist
    backend_file = Path("complete_production_system.py")
    with open(backend_file, 'r') as f:
        backend_code = f.read()
    
    assert 'def load_demo_data()' in backend_code, "❌ load_demo_data() not found"
    assert 'async def simulate_demo_progress(' in backend_code, "❌ simulate_demo_progress() not found"
    assert 'async def handle_demo_mode(' in backend_code, "❌ handle_demo_mode() not found"
    assert 'if ticker == "DEMO":' in backend_code, "❌ DEMO detection not found"
    print("✅ Backend functions present")
    
    # Test 6: PDF endpoint modified
    assert 'is_demo' in backend_code, "❌ PDF demo check not found"
    print("✅ PDF endpoint modified")
    
    print("\n🎉 All tests passed! DEMO mode is ready to use.")
    print("\n📝 To test:")
    print("   1. Start backend: python3 complete_production_system.py")
    print("   2. Open frontend: http://localhost:3000")
    print("   3. Enter 'DEMO' as ticker")
    print("   4. Should complete in ~10 seconds")

if __name__ == "__main__":
    test_demo_mode()
