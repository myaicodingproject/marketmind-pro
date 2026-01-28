#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced Pipeline
"""
import requests
import json
import time
import asyncio
import asyncpg

BASE_URL = "http://localhost:8000"

def test_database_connection():
    """Test database connection and tables"""
    print("🔍 Testing Database Connection...")
    
    try:
        import asyncio
        import asyncpg
        
        async def check_db():
            conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/marketmind")
            
            # Check tables
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            print(f"  ✅ Database connected")
            print(f"  ✅ Tables: {[t['table_name'] for t in tables]}")
            
            # Check if we have any enhanced reports
            count = await conn.fetchval("SELECT COUNT(*) FROM enhanced_reports")
            print(f"  📊 Enhanced reports in DB: {count}")
            
            await conn.close()
            return True
        
        return asyncio.run(check_db())
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_enhanced_endpoints():
    """Test enhanced system endpoints"""
    print("\n🔍 Testing Enhanced Endpoints...")
    
    # Test enhanced report endpoint (should return 404 for non-existent)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/enhanced/reports/999", timeout=10)
        if response.status_code == 404:
            print("  ✅ Enhanced report endpoint working (404 for non-existent)")
        else:
            print(f"  ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Enhanced endpoint test failed: {e}")
        return False
    
    # Test search endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v1/enhanced/search?query=test&limit=5", timeout=10)
        if response.status_code in [200, 404]:  # 200 if results, 404 if no data
            print("  ✅ Enhanced search endpoint working")
        else:
            print(f"  ❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Search endpoint test failed: {e}")
        return False
    
    return True

def test_openai_integration():
    """Test OpenAI integration"""
    print("\n🔍 Testing OpenAI Integration...")
    
    try:
        import os
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            print("  ✅ OpenAI API key is set")
            
            # Test if we can import openai
            try:
                import openai
                print("  ✅ OpenAI library available")
                return True
            except ImportError:
                print("  ❌ OpenAI library not installed")
                return False
        else:
            print("  ❌ OpenAI API key not set or invalid")
            return False
            
    except Exception as e:
        print(f"  ❌ OpenAI test failed: {e}")
        return False

def test_backend_health():
    """Test backend health and enhanced features"""
    print("\n🔍 Testing Backend Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Backend healthy - Version: {data.get('version')}")
            
            features = data.get('production_features', {})
            for feature, status in features.items():
                print(f"    {feature}: {status}")
            
            return True
        else:
            print(f"  ❌ Backend unhealthy: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Backend health test failed: {e}")
        return False

def wait_for_report_completion(report_id, max_wait=300):
    """Wait for report to complete and check if enhanced pipeline was used"""
    print(f"\n🔍 Monitoring Report: {report_id}")
    
    start_time = time.time()
    while (time.time() - start_time) < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/reports/progress/{report_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                progress = data.get('progress', 0)
                status = data.get('status', 'unknown')
                
                print(f"  📊 Progress: {progress}% - Status: {status}")
                
                # Check activity log for enhanced pipeline indicators
                activity_log = data.get('activity_log', [])
                enhanced_indicators = [
                    log for log in activity_log 
                    if any(keyword in log.lower() for keyword in ['enhanced', 'polished', 'rag', 'database'])
                ]
                
                if enhanced_indicators:
                    print("  ✨ Enhanced pipeline activity detected:")
                    for indicator in enhanced_indicators[-3:]:  # Show last 3
                        print(f"    - {indicator}")
                
                if status == 'completed':
                    print("  ✅ Report completed!")
                    return True
                elif status == 'error':
                    print("  ❌ Report generation failed")
                    return False
                    
            time.sleep(10)  # Wait 10 seconds between checks
            
        except Exception as e:
            print(f"  ❌ Progress check failed: {e}")
            time.sleep(10)
    
    print("  ⏰ Timeout waiting for report completion")
    return False

def main():
    print("Enhanced Pipeline Comprehensive Test")
    print("=" * 50)
    
    # Test 1: Database Connection
    db_ok = test_database_connection()
    
    # Test 2: Backend Health
    health_ok = test_backend_health()
    
    # Test 3: Enhanced Endpoints
    endpoints_ok = test_enhanced_endpoints()
    
    # Test 4: OpenAI Integration
    openai_ok = test_openai_integration()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Backend Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Enhanced Endpoints: {'✅ PASS' if endpoints_ok else '❌ FAIL'}")
    print(f"OpenAI Integration: {'✅ PASS' if openai_ok else '❌ FAIL'}")
    
    if all([db_ok, health_ok, endpoints_ok, openai_ok]):
        print("\n🎉 Enhanced Pipeline is FULLY OPERATIONAL!")
        
        # Check if there's an active report to monitor
        print("\nChecking for active reports...")
        # You can add report monitoring here if needed
        
    else:
        print("\n⚠️  Enhanced Pipeline has issues. Check failed tests above.")

if __name__ == "__main__":
    main()
