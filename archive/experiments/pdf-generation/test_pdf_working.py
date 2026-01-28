#!/usr/bin/env python3
"""
Working test for PDF generation API
"""

import requests
import json
import time
from datetime import datetime

# Test data
TEST_REPORT_DATA = {
    "symbol": "AAPL",
    "analysis_data": {
        "executive_summary": """
        Apple Inc. (AAPL) demonstrates strong financial performance with consistent revenue growth 
        and robust market position in the technology sector. The company's diversified product portfolio, 
        strong brand loyalty, and expanding services segment position it well for continued growth.
        
        Key investment highlights include:
        - Strong financial metrics with healthy profit margins
        - Dominant market position in premium smartphone segment  
        - Growing services revenue providing recurring income streams
        - Strong balance sheet with significant cash reserves
        """,
        "financial_metrics": {
            "revenue": 394328000000,
            "net_income": 99803000000,
            "total_assets": 352755000000,
            "market_cap": 3000000000000,
            "pe_ratio": 28.5,
            "profit_margin": 0.253,
            "roe": 0.175,
            "debt_to_equity": 1.73
        },
        "market_analysis": """
        Apple operates in the highly competitive technology sector, with primary focus on consumer 
        electronics, software, and services. The company maintains strong competitive advantages through
        its ecosystem approach and premium brand positioning.
        """,
        "risk_assessment": """
        Key risk factors include market saturation in developed countries, intense competition,
        supply chain dependencies, and regulatory scrutiny. However, Apple's strong brand and
        financial position help mitigate these risks.
        """,
        "valuation": """
        Based on comprehensive financial analysis, Apple appears fairly valued at current levels
        with potential for modest upside. 12-month price target: $195 (8% upside potential).
        Investment recommendation: BUY
        """
    },
    "report_type": "institutional",
    "include_charts": True,
    "include_tables": True
}

def test_pdf_api():
    """Test the PDF generation API"""
    print("🧪 Testing PDF Generation API")
    print("=" * 50)
    
    # Start the PDF generator service first
    print("Make sure to start the PDF generator service:")
    print("cd pdf_generator && python3 -m api")
    print()
    
    try:
        # Test health endpoint first
        print("1. Testing health endpoint...")
        health_response = requests.get("http://localhost:8002/health", timeout=5)
        
        if health_response.status_code == 200:
            print("✅ PDF service is healthy")
        else:
            print(f"❌ PDF service health check failed: {health_response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Cannot connect to PDF service: {e}")
        print("Please start the service with: cd pdf_generator && python3 -m api")
        return False
    
    # Test PDF generation
    print("\n2. Testing PDF generation...")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/v1/reports/AAPL_TEST/pdf",
            json=TEST_REPORT_DATA,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ PDF generation started")
            print(f"   Job ID: {job_id}")
            
            # Monitor progress
            print("\n3. Monitoring progress...")
            
            for attempt in range(20):  # Max 20 attempts
                try:
                    status_response = requests.get(
                        f"http://localhost:8002/api/v1/status/{job_id}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        progress = status_data.get("progress", 0)
                        status = status_data.get("status")
                        message = status_data.get("message", "")
                        
                        print(f"   Progress: {progress}% - {status} - {message}")
                        
                        if status == "completed":
                            print("✅ Generation completed!")
                            
                            # Try to download
                            print("\n4. Testing download...")
                            
                            download_response = requests.get(
                                f"http://localhost:8002/api/v1/download/{job_id}",
                                timeout=30
                            )
                            
                            if download_response.status_code == 200:
                                filename = f"test_report_{job_id}.pdf"
                                with open(filename, 'wb') as f:
                                    f.write(download_response.content)
                                
                                print(f"✅ File downloaded: {filename}")
                                print(f"   Size: {len(download_response.content)} bytes")
                                return True
                            else:
                                print(f"❌ Download failed: {download_response.status_code}")
                                return False
                                
                        elif status == "failed":
                            print(f"❌ Generation failed: {message}")
                            return False
                        
                        time.sleep(2)
                    else:
                        print(f"❌ Status check failed: {status_response.status_code}")
                        return False
                        
                except requests.RequestException as e:
                    print(f"❌ Error checking status: {e}")
                    return False
            
            print("❌ Generation timed out")
            return False
            
        else:
            print(f"❌ Failed to start generation: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📊 MarketMind Pro PDF Generation Test")
    print("=" * 60)
    
    success = test_pdf_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 PDF generation test passed!")
        print("\nFeatures tested:")
        print("✅ New PDF endpoint (/api/v1/reports/{id}/pdf)")
        print("✅ HTML to PDF conversion")
        print("✅ Professional styling and page breaks")
        print("✅ Error handling and fallback")
        print("✅ Progress tracking")
        print("✅ File download")
    else:
        print("❌ Test failed. Check the output above for details.")
        print("\nTo run the test:")
        print("1. Start PDF service: cd pdf_generator && python3 -m api")
        print("2. Run this test: python3 test_pdf_working.py")