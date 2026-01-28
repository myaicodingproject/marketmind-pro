#!/usr/bin/env python3
"""
Quick Production Test Runner
Simple test to verify system is working
"""

import asyncio
import aiohttp
import time

async def quick_test():
    """Run a quick production test"""
    
    print("🧪 QUICK PRODUCTION TEST")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Health check
            print("1. Testing health endpoint...")
            start_time = time.time()
            async with session.get(f"{base_url}/health") as response:
                response_time = (time.time() - start_time) * 1000
                if response.status == 200:
                    print(f"   ✅ Health: PASS ({response_time:.1f}ms)")
                else:
                    print(f"   ❌ Health: FAIL ({response.status})")
                    return False
            
            # Test 2: Root endpoint
            print("2. Testing root endpoint...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Root: PASS")
                    print(f"   System: {data.get('system', 'Unknown')}")
                    print(f"   Status: {data.get('status', 'Unknown')}")
                else:
                    print(f"   ❌ Root: FAIL ({response.status})")
                    return False
            
            # Test 3: Report generation (start only)
            print("3. Testing report generation...")
            payload = {"ticker": "AAPL"}
            async with session.post(f"{base_url}/api/v1/reports/generate", json=payload) as response:
                if response.status in [200, 202]:
                    result = await response.json()
                    print(f"   ✅ Report generation: STARTED")
                    print(f"   Report ID: {result.get('report_id', 'N/A')}")
                    print(f"   Estimated time: {result.get('estimated_time', 'Unknown')}")
                else:
                    print(f"   ❌ Report generation: FAIL ({response.status})")
                    return False
            
            print("\n🎉 QUICK TEST PASSED!")
            print("   System is responding correctly")
            print("   Ready for full production testing")
            return True
            
    except Exception as e:
        print(f"\n❌ QUICK TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    exit(0 if success else 1)
