"""
Test script for MarketMind Pro JWT Authentication System
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_auth_system():
    """Test the complete authentication flow"""
    async with httpx.AsyncClient() as client:
        print("🔐 Testing MarketMind Pro Authentication System")
        print("=" * 50)
        
        # Test 1: Register a new user
        print("1. Testing user registration...")
        register_data = {
            "email": "test@marketmind.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print("✅ User registration successful")
                print(f"   Token: {access_token[:20]}...")
            else:
                print(f"❌ Registration failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return
        
        # Test 2: Login with the user
        print("\n2. Testing user login...")
        login_data = {
            "email": "test@marketmind.com",
            "password": "testpassword123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                user_info = token_data["user"]
                print("✅ User login successful")
                print(f"   User ID: {user_info['id']}")
                print(f"   Email: {user_info['email']}")
            else:
                print(f"❌ Login failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # Test 3: Access protected endpoint
        print("\n3. Testing protected endpoint access...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(f"{BASE_URL}/api/reports/", headers=headers)
            if response.status_code == 200:
                reports = response.json()
                print("✅ Protected endpoint access successful")
                print(f"   Reports count: {len(reports)}")
            else:
                print(f"❌ Protected endpoint failed: {response.text}")
        except Exception as e:
            print(f"❌ Protected endpoint error: {e}")
        
        # Test 4: Access endpoint without token
        print("\n4. Testing endpoint without authentication...")
        try:
            response = await client.get(f"{BASE_URL}/api/reports/")
            if response.status_code == 401:
                print("✅ Unauthenticated access properly blocked")
            else:
                print(f"❌ Unauthenticated access should be blocked: {response.status_code}")
        except Exception as e:
            print(f"❌ Unauthenticated test error: {e}")
        
        # Test 5: Test report generation with authentication
        print("\n5. Testing report generation with authentication...")
        report_data = {
            "ticker": "AAPL",
            "report_type": "comprehensive"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/reports/generate", 
                json=report_data, 
                headers=headers
            )
            if response.status_code == 200:
                report_response = response.json()
                print("✅ Authenticated report generation successful")
                print(f"   Report ID: {report_response['id']}")
            else:
                print(f"❌ Report generation failed: {response.text}")
        except Exception as e:
            print(f"❌ Report generation error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Authentication system test completed!")

if __name__ == "__main__":
    asyncio.run(test_auth_system())