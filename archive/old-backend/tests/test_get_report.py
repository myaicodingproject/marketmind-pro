#!/usr/bin/env python3
"""
Test script to verify the get_report endpoint is working correctly
and debug any potential issues
"""
import requests
import json
import time

def test_get_report():
    """Test the get_report endpoint with detailed debugging"""
    
    # Test with existing report
    report_id = "prod_report_AAPL_1769439480"
    url = f"http://localhost:8000/api/v1/reports/{report_id}"
    
    print(f"Testing GET {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Report retrieved")
            print(f"Report ID: {data.get('report_id')}")
            print(f"Ticker: {data.get('ticker')}")
            print(f"Title: {data.get('title')}")
            print(f"Sections: {list(data.get('sections', {}).keys())}")
            
            # Check each section
            sections = data.get('sections', {})
            for section_name, section_data in sections.items():
                content_length = len(section_data.get('content', ''))
                print(f"  - {section_name}: {content_length} characters")
            
            return True
            
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_nonexistent_report():
    """Test with non-existent report"""
    
    report_id = "nonexistent_report_123"
    url = f"http://localhost:8000/api/v1/reports/{report_id}"
    
    print(f"\nTesting GET {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ SUCCESS - Correctly returned 404 for non-existent report")
            return True
        else:
            print(f"❌ FAILED - Expected 404, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_backend_health():
    """Test backend health"""
    
    url = "http://localhost:8000/health"
    
    print(f"\nTesting GET {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"Version: {data.get('version')}")
            print(f"Status: {data.get('status')}")
            
            features = data.get('production_features', {})
            for feature, status in features.items():
                print(f"  {feature}: {status}")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("MarketMind Pro - Get Report Endpoint Testing")
    print("=" * 60)
    
    # Test backend health first
    health_ok = test_backend_health()
    
    if health_ok:
        # Test existing report
        existing_ok = test_get_report()
        
        # Test non-existent report
        nonexistent_ok = test_nonexistent_report()
        
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"Backend Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Existing Report: {'✅ PASS' if existing_ok else '❌ FAIL'}")
        print(f"Non-existent Report: {'✅ PASS' if nonexistent_ok else '❌ FAIL'}")
        
        if all([health_ok, existing_ok, nonexistent_ok]):
            print("\n🎉 All tests passed! The get_report endpoint is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Backend health check failed. Cannot proceed with endpoint testing.")
