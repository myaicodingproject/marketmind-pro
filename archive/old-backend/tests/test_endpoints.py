#!/usr/bin/env python3
"""
Test script to verify all key endpoints are working correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, expected_status=200, data=None):
    """Test an endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"{method} {endpoint}: {response.status_code}")
        
        if response.status_code == expected_status:
            print("  ✅ SUCCESS")
            return True, response.json() if response.content else None
        else:
            print(f"  ❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        return False, None

def main():
    print("Testing MarketMind Pro Backend Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Health Check:")
    success, data = test_endpoint("GET", "/health")
    if success and data:
        print(f"  Version: {data.get('version', 'Unknown')}")
        print(f"  Status: {data.get('status', 'Unknown')}")
    
    # Test existing report retrieval
    print("\n2. Report Retrieval (Existing Report):")
    report_id = "prod_report_AAPL_1769439480"
    success, data = test_endpoint("GET", f"/api/v1/reports/{report_id}")
    if success and data:
        print(f"  Report ID: {data.get('report_id', 'Unknown')}")
        print(f"  Ticker: {data.get('ticker', 'Unknown')}")
        print(f"  Sections: {len(data.get('sections', {}))}")
    
    # Test non-existent report
    print("\n3. Report Retrieval (Non-existent):")
    success, data = test_endpoint("GET", "/api/v1/reports/nonexistent_123", expected_status=404)
    
    # Test progress endpoint
    print("\n4. Progress Endpoint:")
    success, data = test_endpoint("GET", f"/api/v1/reports/progress/{report_id}", expected_status=404)
    
    # Test PDF endpoint
    print("\n5. PDF Generation:")
    success, data = test_endpoint("GET", f"/api/v1/reports/{report_id}/pdf")
    
    # Test system status
    print("\n6. System Status:")
    success, data = test_endpoint("GET", "/api/v1/system/status")
    if success and data:
        print(f"  Active Processes: {data.get('active_processes', 'Unknown')}")
        print(f"  Memory Usage: {data.get('memory_usage', 'Unknown')}")
    
    print("\n" + "=" * 50)
    print("Endpoint testing complete!")

if __name__ == "__main__":
    main()
