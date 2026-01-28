#!/usr/bin/env python3
"""
Simple test for basic API functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_docs_endpoint():
    """Test docs endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Docs endpoint - Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing docs endpoint: {e}")
        return False

def main():
    print("Testing MarketMind Pro API...")
    print("=" * 40)
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Endpoint", test_health_endpoint),
        ("Docs Endpoint", test_docs_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"Error in {test_name}: {str(e)}")
            results[test_name] = "ERROR"
    
    print("\n" + "=" * 40)
    print("TEST RESULTS:")
    for test_name, result in results.items():
        print(f"{test_name}: {result}")

if __name__ == "__main__":
    main()