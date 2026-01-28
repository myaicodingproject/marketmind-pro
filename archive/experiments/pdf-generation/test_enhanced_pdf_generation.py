#!/usr/bin/env python3
"""
Enhanced PDF Generation Test Suite
Tests the new Puppeteer-based PDF generation with professional styling
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

import httpx
import requests

# Test configuration
BACKEND_URL = "http://localhost:8000"
PDF_SERVICE_URL = "http://localhost:8002"

# Sample report data for testing
SAMPLE_REPORT_DATA = {
    "symbol": "AAPL",
    "analysis_data": {
        "executive_summary": """
        Apple Inc. (AAPL) demonstrates strong fundamentals with consistent revenue growth and market leadership in consumer technology. 
        
        Recommendation: BUY with a 12-month price target of $200.00
        
        Key Investment Thesis:
        • Strong ecosystem and brand loyalty driving recurring revenue
        • Expanding services segment with high margins
        • Innovation in emerging technologies (AR/VR, AI)
        • Robust balance sheet with significant cash reserves
        """,
        "financial_metrics": {
            "revenue": 394328000000,
            "net_income": 99803000000,
            "eps": 6.16,
            "pe_ratio": 28.5,
            "price_target": 200.00,
            "current_price": 175.50,
            "market_cap": 2800000000000,
            "debt_to_equity": 1.73,
            "roe": 26.4,
            "gross_margin": 43.3
        },
        "market_analysis": """
        The smartphone market continues to show resilience despite global economic headwinds. Apple maintains a premium position with strong pricing power.
        
        Market Dynamics:
        Apple's ecosystem approach creates significant switching costs for consumers. The company's focus on services revenue provides more predictable cash flows.
        
        Competitive Position:
        Apple maintains technological leadership in key areas including chip design, software integration, and user experience. The brand commands premium pricing across all product categories.
        
        Growth Drivers:
        Emerging markets present significant expansion opportunities. The services segment continues to grow at double-digit rates, improving overall margin profile.
        """,
        "risk_assessment": """
        Risk: Regulatory scrutiny in key markets could impact App Store revenue streams.
        
        High risk factors include supply chain disruptions and geopolitical tensions affecting manufacturing operations.
        
        Low risk factors include strong brand loyalty and diversified revenue streams providing stability during market downturns.
        
        Mitigation strategies include geographic diversification of manufacturing and continued investment in R&D to maintain competitive advantages.
        """,
        "valuation": """
        Price Target: $200.00 based on DCF analysis and peer comparison.
        
        Fair Value: Our analysis suggests a fair value range of $185-205 per share.
        
        Valuation Methodology:
        • DCF model assumes 8% revenue CAGR over next 5 years
        • P/E multiple of 25x applied to 2025E earnings
        • Sum-of-parts analysis values services segment at premium multiple
        
        Upside/Downside Analysis:
        Bull case: $220 (successful AR/VR launch, services acceleration)
        Base case: $200 (steady growth, margin expansion)
        Bear case: $160 (economic downturn, margin compression)
        """,
        "competitive_analysis": """
        Apple competes primarily with Samsung in premium smartphones and faces increasing competition from Chinese manufacturers in emerging markets.
        
        Key differentiators include integrated hardware/software ecosystem, premium brand positioning, and superior customer service experience.
        """
    },
    "report_type": "institutional",
    "output_format": "pdf",
    "include_charts": True,
    "include_tables": True
}

class PDFGenerationTester:
    def __init__(self):
        self.test_results = []
        
    async def test_pdf_service_health(self):
        """Test if PDF service is running and healthy"""
        print("🔍 Testing PDF service health...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{PDF_SERVICE_URL}/health", timeout=10.0)
                if response.status_code == 200:
                    print("✅ PDF service is healthy")
                    return True
                else:
                    print(f"❌ PDF service health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to PDF service: {e}")
            return False
    
    async def test_backend_integration(self):
        """Test backend integration with PDF service"""
        print("\n🔍 Testing backend PDF endpoint integration...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/v1/reports/test-report-123/pdf",
                    json=SAMPLE_REPORT_DATA,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job_id = result.get('job_id')
                    print(f"✅ PDF generation started successfully, job_id: {job_id}")
                    return job_id
                else:
                    print(f"❌ Backend PDF endpoint failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Backend integration test failed: {e}")
            return None
    
    async def test_direct_pdf_generation(self):
        """Test direct PDF service generation"""
        print("\n🔍 Testing direct PDF service generation...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{PDF_SERVICE_URL}/api/v1/reports/direct-test-456/pdf",
                    json=SAMPLE_REPORT_DATA,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job_id = result.get('job_id')
                    print(f"✅ Direct PDF generation started, job_id: {job_id}")
                    return job_id
                else:
                    print(f"❌ Direct PDF generation failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"❌ Direct PDF generation test failed: {e}")
            return None
    
    async def monitor_job_progress(self, job_id: str, service_url: str = PDF_SERVICE_URL):
        """Monitor job progress until completion"""
        print(f"\n📊 Monitoring job progress: {job_id}")
        
        max_attempts = 30  # 30 seconds timeout
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{service_url}/api/v1/status/{job_id}",
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        status = response.json()
                        progress = status.get('progress', 0)
                        message = status.get('message', 'Processing...')
                        job_status = status.get('status', 'unknown')
                        
                        print(f"   Progress: {progress}% - {message}")
                        
                        if job_status == 'completed':
                            print("✅ Job completed successfully!")
                            return status
                        elif job_status == 'failed':
                            print(f"❌ Job failed: {message}")
                            return status
                        
                    await asyncio.sleep(1)
                    attempt += 1
                    
            except Exception as e:
                print(f"❌ Error monitoring job: {e}")
                break
        
        print("⏰ Job monitoring timed out")
        return None
    
    async def test_pdf_download(self, job_id: str, service_url: str = PDF_SERVICE_URL):
        """Test PDF download functionality"""
        print(f"\n📥 Testing PDF download for job: {job_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{service_url}/api/v1/download/{job_id}",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # Save the file
                    filename = f"test_report_{job_id}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = len(response.content)
                    print(f"✅ PDF downloaded successfully: {filename} ({file_size} bytes)")
                    return filename
                else:
                    print(f"❌ PDF download failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"❌ PDF download test failed: {e}")
            return None
    
    async def test_enhanced_features(self):
        """Test enhanced PDF features"""
        print("\n🎨 Testing enhanced PDF features...")
        
        enhanced_data = SAMPLE_REPORT_DATA.copy()
        enhanced_data['analysis_data']['charts'] = [
            {
                'title': 'Revenue Growth Trend',
                'type': 'line',
                'data': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
            }
        ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{PDF_SERVICE_URL}/api/v1/reports/enhanced-test-789/pdf",
                    json=enhanced_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job_id = result.get('job_id')
                    print(f"✅ Enhanced PDF generation started, job_id: {job_id}")
                    return job_id
                else:
                    print(f"❌ Enhanced PDF generation failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ Enhanced features test failed: {e}")
            return None
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Enhanced PDF Generation Test Suite")
        print("=" * 60)
        
        # Test 1: Service Health
        if not await self.test_pdf_service_health():
            print("\n❌ PDF service is not available. Please start the service first.")
            return False
        
        # Test 2: Backend Integration
        backend_job_id = await self.test_backend_integration()
        
        # Test 3: Direct PDF Generation
        direct_job_id = await self.test_direct_pdf_generation()
        
        # Test 4: Enhanced Features
        enhanced_job_id = await self.test_enhanced_features()
        
        # Monitor jobs and download results
        successful_downloads = 0
        
        for job_id, test_name in [
            (backend_job_id, "Backend Integration"),
            (direct_job_id, "Direct Generation"),
            (enhanced_job_id, "Enhanced Features")
        ]:
            if job_id:
                print(f"\n📊 Monitoring {test_name} job...")
                status = await self.monitor_job_progress(job_id)
                
                if status and status.get('status') == 'completed':
                    filename = await self.test_pdf_download(job_id)
                    if filename:
                        successful_downloads += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful PDF downloads: {successful_downloads}/3")
        
        if successful_downloads >= 2:
            print("🎉 Enhanced PDF generation system is working correctly!")
            return True
        else:
            print("⚠️  Some tests failed. Please check the logs above.")
            return False

def main():
    """Main test function"""
    tester = PDFGenerationTester()
    
    try:
        result = asyncio.run(tester.run_comprehensive_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()