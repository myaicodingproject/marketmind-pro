#!/usr/bin/env python3

import requests
import sys
import time

def quick_test():
    """Rapid system validation - essential checks only"""
    
    print("🚀 MarketMind Pro Quick Test")
    print("=" * 40)
    
    tests = [
        ("Backend Health", "http://localhost:8000/health"),
        ("Frontend Access", "http://localhost:3000"),
        ("API Docs", "http://localhost:8000/docs"),
    ]
    
    passed = 0
    
    for name, url in tests:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {name}")
                passed += 1
            else:
                print(f"❌ {name} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name} (Error: {str(e)[:50]}...)")
    
    print("=" * 40)
    if passed == len(tests):
        print("🎉 All quick tests passed!")
        return True
    else:
        print(f"⚠️  {len(tests) - passed}/{len(tests)} tests failed")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)