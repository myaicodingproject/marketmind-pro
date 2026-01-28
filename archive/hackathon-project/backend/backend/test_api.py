#!/usr/bin/env python3
"""
Test script for MarketMind Pro API endpoints
"""
import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.access_token = None
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("Testing health check...")
        response = await self.client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    
    async def test_register_user(self):
        """Test user registration"""
        print("\nTesting user registration...")
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = await self.client.post("/api/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print(f"User created: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return response.status_code == 400  # User might already exist
    
    async def test_login_user(self):
        """Test user login"""
        print("\nTesting user login...")
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = await self.client.post("/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            print(f"Login successful, token received")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    async def test_get_current_user(self):
        """Test get current user endpoint"""
        print("\nTesting get current user...")
        if not self.access_token:
            print("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = await self.client.get("/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"User info: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    async def test_create_report(self):
        """Test report creation"""
        print("\nTesting report creation...")
        if not self.access_token:
            print("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        report_data = {
            "ticker": "AAPL",
            "report_type": "comprehensive"
        }
        response = await self.client.post("/api/reports/", json=report_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            report = response.json()
            print(f"Report created: {report['id']} - {report['title']}")
            return report["id"]
        else:
            print(f"Error: {response.text}")
            return None
    
    async def test_get_reports(self):
        """Test get reports endpoint"""
        print("\nTesting get reports...")
        if not self.access_token:
            print("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = await self.client.get("/api/reports/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            reports = response.json()
            print(f"Found {len(reports)} reports")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    async def test_get_companies(self):
        """Test get companies endpoint"""
        print("\nTesting get companies...")
        response = await self.client.get("/api/companies/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            companies = response.json()
            print(f"Found {len(companies)} companies")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("Starting API tests...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_register_user),
            ("User Login", self.test_login_user),
            ("Get Current User", self.test_get_current_user),
            ("Create Report", self.test_create_report),
            ("Get Reports", self.test_get_reports),
            ("Get Companies", self.test_get_companies),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = "PASS" if result else "FAIL"
            except Exception as e:
                print(f"Error in {test_name}: {str(e)}")
                results[test_name] = "ERROR"
        
        print("\n" + "=" * 50)
        print("TEST RESULTS:")
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
        
        await self.client.aclose()

async def main():
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())