"""
Test client for MarketMind Pro PDF Generator
Demonstrates complete report generation workflow
"""

import requests
import json
import time
from datetime import datetime

class PDFGeneratorClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
    
    def test_institutional_report(self, symbol="AAPL"):
        """Test complete institutional report generation"""
        print(f"🚀 Testing institutional report generation for {symbol}...")
        
        # Sample analysis data
        analysis_data = {
            "current_price": "150.25",
            "market_cap": "2.45T",
            "pe_ratio": "28.5",
            "week_52_low": "124.17",
            "week_52_high": "198.23",
            "investment_thesis": "Strong fundamentals with consistent innovation and market leadership position",
            "key_finding_1": "Revenue growth accelerating with 15% YoY increase",
            "key_finding_2": "Technical breakout above key resistance levels",
            "key_finding_3": "Institutional ownership increasing by 8% this quarter",
            "performance_data": [2.5, 8.3, 15.7, 22.1, 45.6],
            "revenue_data": [95.2, 98.7, 102.3, 108.1, 112.5],
            "current_ratio": "2.1",
            "debt_equity": "0.45",
            "roe": "18.5%",
            "roa": "12.3%",
            "gross_margin": "42.1%",
            "margin_expansion": "2.3",
            "net_income_growth": "15.7",
            "rsi": "58.3",
            "macd": "0.85",
            "bb_position": "Upper Half",
            "volume_trend": "Increasing",
            "support": "145.20",
            "volatility_30d": "18.5%",
            "volatility_90d": "22.1%",
            "beta": "1.15",
            "sector": "Technology",
            "sector_growth": "12.5%",
            "market_share": "8.3%",
            "recommendation": "BUY",
            "price_target": "175.00",
            "time_horizon": "12 months"
        }
        
        # Test async generation
        print("📊 Starting async report generation...")
        response = requests.post(f"{self.base_url}/api/v1/generate-report", json={
            "symbol": symbol,
            "analysis_data": analysis_data,
            "report_type": "institutional",
            "include_charts": True,
            "include_tables": True
        })
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job created: {job_id}")
            
            # Monitor progress
            self._monitor_job_progress(job_id)
            
        else:
            print(f"❌ Failed to create job: {response.text}")
    
    def test_quick_generation(self, symbol="MSFT"):
        """Test quick synchronous generation"""
        print(f"⚡ Testing quick report generation for {symbol}...")
        
        analysis_data = {
            "current_price": "378.85",
            "market_cap": "2.81T",
            "pe_ratio": "32.1",
            "recommendation": "STRONG BUY",
            "price_target": "420.00"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/quick-generate", json={
            "symbol": symbol,
            "analysis_data": analysis_data,
            "report_type": "institutional"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Quick report generated: {result['file_path']}")
            return result
        else:
            print(f"❌ Quick generation failed: {response.text}")
            return None
    
    def _monitor_job_progress(self, job_id):
        """Monitor job progress until completion"""
        while True:
            response = requests.get(f"{self.base_url}/api/v1/status/{job_id}")
            
            if response.status_code == 200:
                status = response.json()
                print(f"🔄 [{status['status'].upper()}] {status['progress']}% - {status['message']}")
                
                if status["status"] == "completed":
                    print(f"✅ Report completed! File: {status['file_path']}")
                    
                    # Test download
                    download_response = requests.get(f"{self.base_url}/api/v1/download/{job_id}")
                    if download_response.status_code == 200:
                        filename = f"downloaded_report_{job_id}.pdf"
                        with open(filename, "wb") as f:
                            f.write(download_response.content)
                        print(f"📥 Downloaded report: {filename}")
                    break
                    
                elif status["status"] == "failed":
                    print(f"❌ Report generation failed: {status['message']}")
                    break
                    
            else:
                print(f"❌ Failed to get status: {response.text}")
                break
            
            time.sleep(2)
    
    def test_health_check(self):
        """Test service health"""
        print("🏥 Testing health check...")
        response = requests.get(f"{self.base_url}/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Service healthy: {health}")
        else:
            print(f"❌ Health check failed: {response.text}")

def main():
    """Run comprehensive tests"""
    print("🧪 MarketMind Pro PDF Generator - Test Suite")
    print("=" * 50)
    
    client = PDFGeneratorClient()
    
    # Health check
    client.test_health_check()
    print()
    
    # Quick generation test
    client.test_quick_generation("MSFT")
    print()
    
    # Full institutional report test
    client.test_institutional_report("AAPL")
    print()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()