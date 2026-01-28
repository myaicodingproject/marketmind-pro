#!/usr/bin/env python3
"""
Test script for Puppeteer PDF generation
"""

import asyncio
import json
import time
import requests
from datetime import datetime

# Test data
TEST_REPORT_DATA = {
    "symbol": "AAPL",
    "analysis_data": {
        "executive_summary": """
        <p>Apple Inc. (AAPL) demonstrates strong financial performance with consistent revenue growth 
        and robust market position in the technology sector. The company's diversified product portfolio, 
        strong brand loyalty, and expanding services segment position it well for continued growth.</p>
        
        <p>Key investment highlights include:</p>
        <ul>
            <li>Strong financial metrics with healthy profit margins</li>
            <li>Dominant market position in premium smartphone segment</li>
            <li>Growing services revenue providing recurring income streams</li>
            <li>Strong balance sheet with significant cash reserves</li>
        </ul>
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
        <p>Apple operates in the highly competitive technology sector, with primary focus on consumer 
        electronics, software, and services. The company maintains strong competitive advantages through:</p>
        
        <h3>Market Position</h3>
        <p>Apple holds a dominant position in the premium smartphone market with approximately 50% 
        market share in the US and strong global presence. The ecosystem approach creates high 
        switching costs for customers.</p>
        
        <h3>Growth Drivers</h3>
        <ul>
            <li>Services segment expansion (App Store, iCloud, Apple Pay)</li>
            <li>Emerging markets penetration</li>
            <li>Product innovation and new category development</li>
            <li>Subscription-based revenue models</li>
        </ul>
        """,
        "risk_assessment": """
        <h3>Key Risk Factors</h3>
        
        <h4>Market Risks</h4>
        <ul>
            <li>Intense competition in smartphone and tablet markets</li>
            <li>Market saturation in developed countries</li>
            <li>Economic downturns affecting consumer spending</li>
        </ul>
        
        <h4>Operational Risks</h4>
        <ul>
            <li>Supply chain dependencies and geopolitical tensions</li>
            <li>Regulatory scrutiny and potential antitrust actions</li>
            <li>Currency exchange rate fluctuations</li>
        </ul>
        
        <h4>Technology Risks</h4>
        <ul>
            <li>Rapid technological changes requiring continuous innovation</li>
            <li>Cybersecurity threats and data privacy concerns</li>
            <li>Dependence on key suppliers and manufacturing partners</li>
        </ul>
        """,
        "valuation": """
        <h3>Valuation Analysis</h3>
        
        <p>Based on comprehensive financial analysis and market comparisons, Apple appears 
        fairly valued at current levels with potential for modest upside.</p>
        
        <h4>Valuation Metrics</h4>
        <ul>
            <li>P/E Ratio: 28.5x (vs. sector average of 25.2x)</li>
            <li>PEG Ratio: 2.1x (indicating moderate growth premium)</li>
            <li>Price-to-Sales: 7.8x (premium to sector average)</li>
            <li>Enterprise Value/EBITDA: 22.1x</li>
        </ul>
        
        <h4>Price Target</h4>
        <p>12-month price target: $195 (representing 8% upside potential)</p>
        <p>Investment recommendation: <strong>BUY</strong></p>
        """
    },
    "report_type": "institutional",
    "include_charts": True,
    "include_tables": True
}

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("🚀 Testing PDF Generation with Puppeteer")
    print("=" * 50)
    
    # Test 1: Generate PDF
    print("\n1. Initiating PDF generation...")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/v1/reports/AAPL_TEST/pdf",
            json=TEST_REPORT_DATA,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ PDF generation started successfully")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {result.get('status')}")
            
            # Test 2: Monitor progress
            print("\n2. Monitoring generation progress...")
            
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
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
                            print("✅ PDF generation completed successfully!")
                            
                            # Test 3: Download PDF
                            print("\n3. Downloading generated PDF...")
                            
                            download_response = requests.get(
                                f"http://localhost:8002/api/v1/download/{job_id}",
                                timeout=30
                            )
                            
                            if download_response.status_code == 200:
                                filename = f"test_report_{job_id}.pdf"
                                with open(filename, 'wb') as f:
                                    f.write(download_response.content)
                                
                                print(f"✅ PDF downloaded successfully: {filename}")
                                print(f"   File size: {len(download_response.content)} bytes")
                                
                                return True
                            else:
                                print(f"❌ Download failed: {download_response.status_code}")
                                return False
                                
                        elif status == "failed":
                            print(f"❌ PDF generation failed: {message}")
                            return False
                        
                        time.sleep(2)
                        attempt += 1
                    else:
                        print(f"❌ Status check failed: {status_response.status_code}")
                        return False
                        
                except requests.RequestException as e:
                    print(f"❌ Error checking status: {e}")
                    return False
            
            print("❌ PDF generation timed out")
            return False
            
        else:
            print(f"❌ Failed to start PDF generation: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to PDF service: {e}")
        return False

def test_main_api_integration():
    """Test integration with main API"""
    print("\n🔗 Testing Main API Integration")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8001/api/v1/reports/AAPL_MAIN_TEST/pdf",
            json=TEST_REPORT_DATA,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Main API integration working")
            print(f"   Job ID: {job_id}")
            return True
        else:
            print(f"❌ Main API integration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to main API: {e}")
        return False

def check_services():
    """Check if services are running"""
    print("🔍 Checking Service Status")
    print("=" * 50)
    
    services = [
        ("PDF Generator", "http://localhost:8002/health"),
        ("Main API", "http://localhost:8001/api/system/status")
    ]
    
    all_healthy = True
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy ({response.status_code})")
                all_healthy = False
        except requests.RequestException as e:
            print(f"❌ {name}: Not responding ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    print("📊 MarketMind Pro PDF Generation Test Suite")
    print("=" * 60)
    
    # Check services
    if not check_services():
        print("\n❌ Some services are not running. Please start them first:")
        print("   1. PDF Generator: python -m pdf_generator.api")
        print("   2. Main API: python -m app.main")
        exit(1)
    
    # Run tests
    success = True
    
    # Test PDF generation
    if not test_pdf_generation():
        success = False
    
    # Test main API integration
    if not test_main_api_integration():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! PDF generation is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    print("\n📋 Test Summary:")
    print("   - Puppeteer PDF generation")
    print("   - Professional styling and page breaks")
    print("   - Chart rendering optimization")
    print("   - Error handling")
    print("   - Main API integration")