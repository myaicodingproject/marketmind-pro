#!/usr/bin/env python3
"""
Complete Ultra-Systematic Integration Test
Tests the entire pipeline: JSON → Ultra-Formatter → Frontend → PDF
"""

import requests
import json
import time
import os
from datetime import datetime

def test_complete_ultra_system():
    """Test the complete ultra-systematic formatting system"""
    
    print("🧪 ULTRA-SYSTEMATIC INTEGRATION TEST")
    print("=" * 50)
    
    # Step 1: Test Backend Health
    print("\n1️⃣ Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data['status']}")
            print(f"   Version: {health_data['version']}")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {str(e)}")
        return False
    
    # Step 2: Test Frontend Health
    print("\n2️⃣ Testing Frontend Health...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {str(e)}")
        return False
    
    # Step 3: Generate Test Report with Ultra-Formatting
    print("\n3️⃣ Generating Test Report with Ultra-Formatting...")
    test_ticker = "TSLA"
    
    try:
        # Start report generation
        response = requests.post(
            "http://localhost:8000/api/v1/reports/generate",
            json={
                "ticker": test_ticker,
                "include_pdf": True,
                "include_charts": True
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            report_id = result.get('report_id')
            print(f"✅ Report generation started: {report_id}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Report generation request failed: {str(e)}")
        return False
    
    # Step 4: Monitor Progress
    print("\n4️⃣ Monitoring Report Generation Progress...")
    max_wait_time = 600  # 10 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"http://localhost:8000/api/v1/reports/progress/{report_id}")
            if response.status_code == 200:
                progress = response.json()
                stage = progress.get('stage', 'unknown')
                progress_pct = progress.get('progress', 0)
                message = progress.get('message', '')
                
                print(f"   📊 {stage}: {progress_pct}% - {message}")
                
                if stage == 'completed':
                    print("✅ Report generation completed!")
                    break
                elif stage == 'failed':
                    print("❌ Report generation failed!")
                    return False
                    
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"❌ Progress check failed: {str(e)}")
            time.sleep(10)
            continue
    else:
        print("❌ Report generation timed out!")
        return False
    
    # Step 5: Validate Ultra-Formatted Report
    print("\n5️⃣ Validating Ultra-Formatted Report...")
    try:
        response = requests.get(f"http://localhost:8000/api/v1/reports/{report_id}")
        if response.status_code == 200:
            report = response.json()
            
            # Check for ultra-formatting indicators
            formatting_applied = report.get('formatting_applied', False)
            html_content = report.get('html_content', '')
            pdf_content = report.get('pdf_content', '')
            
            print(f"✅ Report retrieved successfully")
            print(f"   Ticker: {report.get('ticker')}")
            print(f"   Sections: {len(report.get('sections', {}))}")
            print(f"   Words: {report.get('statistics', {}).get('total_words', 0):,}")
            print(f"   Ultra-Formatting Applied: {formatting_applied}")
            print(f"   HTML Content Length: {len(html_content):,} chars")
            print(f"   PDF Content Length: {len(pdf_content):,} chars")
            
            # Validate formatting quality
            if formatting_applied and html_content and pdf_content:
                print("✅ Ultra-systematic formatting validated!")
            else:
                print("❌ Ultra-systematic formatting missing!")
                return False
                
        else:
            print(f"❌ Report retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Report validation failed: {str(e)}")
        return False
    
    # Step 6: Test PDF Generation
    print("\n6️⃣ Testing Ultra-Styled PDF Generation...")
    try:
        pdf_filename = report.get('pdf_filename')
        if pdf_filename and os.path.exists(pdf_filename):
            pdf_size = os.path.getsize(pdf_filename)
            print(f"✅ Ultra-PDF generated: {pdf_filename}")
            print(f"   Size: {pdf_size:,} bytes")
            
            if pdf_size > 50000:  # At least 50KB for a real report
                print("✅ Ultra-PDF size validation passed!")
            else:
                print("❌ Ultra-PDF too small - may be incomplete")
                return False
        else:
            print("❌ Ultra-PDF file not found")
            return False
            
    except Exception as e:
        print(f"❌ PDF validation failed: {str(e)}")
        return False
    
    # Step 7: Test Frontend Report Viewer Page
    print("\n7️⃣ Testing Frontend Report Viewer Page...")
    try:
        response = requests.get(f"http://localhost:3000/report/{report_id}")
        if response.status_code == 200:
            print("✅ Report viewer page accessible")
        else:
            print(f"❌ Report viewer page error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Report viewer page test failed: {str(e)}")
        return False
    
    # Step 8: Final Validation Summary
    print("\n8️⃣ Final Validation Summary...")
    print("✅ Backend Health: PASSED")
    print("✅ Frontend Health: PASSED") 
    print("✅ Report Generation: PASSED")
    print("✅ Ultra-Formatting: PASSED")
    print("✅ PDF Generation: PASSED")
    print("✅ Frontend Integration: PASSED")
    
    print(f"\n🎉 ULTRA-SYSTEMATIC INTEGRATION TEST: SUCCESS!")
    print(f"   Report ID: {report_id}")
    print(f"   Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = test_complete_ultra_system()
    if success:
        print("\n🚀 System ready for production!")
        exit(0)
    else:
        print("\n💥 System integration failed!")
        exit(1)
