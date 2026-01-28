#!/usr/bin/env python3
"""
Hybrid PDF Generation API Demo
Demonstrates how to use the new Phase 2 integration layer
"""

import asyncio
import aiohttp
import json
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
HYBRID_ENDPOINT = f"{BASE_URL}/hybrid"

async def demo_hybrid_api():
    """Demonstrate the hybrid PDF generation API"""
    
    print("🚀 MarketMind Pro - Hybrid PDF Generation Demo")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Check system health
        print("\n1️⃣ Checking System Health...")
        try:
            async with session.get(f"{HYBRID_ENDPOINT}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ System Status: {health_data['status']}")
                    print(f"📊 Services: {health_data['services']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # 2. Get system capabilities
        print("\n2️⃣ Getting System Capabilities...")
        try:
            async with session.get(f"{HYBRID_ENDPOINT}/capabilities") as response:
                if response.status == 200:
                    capabilities = await response.json()
                    print("✅ Available Enhancement Levels:")
                    for level in capabilities['enhancement_levels']:
                        print(f"   • {level['level']}: {level['description']}")
                        print(f"     Features: {', '.join(level['features'])}")
                else:
                    print(f"❌ Capabilities check failed: {response.status}")
        except Exception as e:
            print(f"❌ Capabilities error: {e}")
        
        # 3. Generate hybrid reports
        print("\n3️⃣ Generating Hybrid Reports...")
        
        test_requests = [
            {
                "symbol": "AAPL",
                "enhancement_level": "kiro_only",
                "include_charts": True,
                "priority": "normal"
            },
            {
                "symbol": "GOOGL", 
                "enhancement_level": "standard",
                "include_charts": True,
                "priority": "normal"
            },
            {
                "symbol": "MSFT",
                "enhancement_level": "premium", 
                "include_charts": True,
                "priority": "high"
            }
        ]
        
        for i, request_data in enumerate(test_requests, 1):
            print(f"\n   📊 Test {i}: {request_data['symbol']} ({request_data['enhancement_level']})")
            
            try:
                # Note: In production, you would need JWT authentication
                # headers = {"Authorization": f"Bearer {jwt_token}"}
                
                async with session.post(
                    f"{HYBRID_ENDPOINT}/generate",
                    json=request_data,
                    # headers=headers  # Uncomment for production
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result['success']:
                            print(f"   ✅ Generated: {result['pdf_path']}")
                            print(f"   📈 Quality: {result['quality_score']}")
                            print(f"   ⏱️  Time: {result['generation_time']}")
                        else:
                            print(f"   ❌ Generation failed: {result.get('error')}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ API Error {response.status}: {error_text}")
                        
            except Exception as e:
                print(f"   ❌ Request error: {e}")
        
        # 4. Download example (if files exist)
        print("\n4️⃣ Testing Download Functionality...")
        
        reports_dir = Path("reports")
        if reports_dir.exists():
            pdf_files = list(reports_dir.glob("MarketMind_Hybrid_*.pdf"))
            if pdf_files:
                latest_file = max(pdf_files, key=lambda p: p.stat().st_mtime)
                symbol = latest_file.name.split('_')[2]  # Extract symbol from filename
                
                print(f"   📄 Testing download for {symbol}...")
                try:
                    async with session.get(f"{HYBRID_ENDPOINT}/download/{symbol}") as response:
                        if response.status == 200:
                            print(f"   ✅ Download successful: {response.headers.get('content-length', 'Unknown')} bytes")
                        else:
                            print(f"   ❌ Download failed: {response.status}")
                except Exception as e:
                    print(f"   ❌ Download error: {e}")
            else:
                print("   ℹ️  No hybrid PDF files found for download test")
        else:
            print("   ℹ️  Reports directory not found")

def demo_direct_service():
    """Demonstrate direct service usage (without API)"""
    
    print("\n\n🔧 Direct Service Usage Demo")
    print("=" * 35)
    
    try:
        import sys
        sys.path.append('.')
        
        from app.services.enhanced_pdf_generator import EnhancedPDFGenerator
        from app.schemas.hybrid_models import EnhancementLevel
        
        async def run_direct_demo():
            generator = EnhancedPDFGenerator()
            
            print("✅ EnhancedPDFGenerator initialized")
            
            # Generate a report directly
            result = await generator.generate_hybrid_report(
                symbol="DEMO",
                enhancement_level=EnhancementLevel.STANDARD.value,
                include_charts=True
            )
            
            if result["success"]:
                print(f"✅ Direct generation successful:")
                print(f"   📄 PDF: {result['pdf_path']}")
                print(f"   📈 Quality: {result['quality_score']}")
            else:
                print(f"❌ Direct generation failed: {result.get('error')}")
        
        asyncio.run(run_direct_demo())
        
    except ImportError as e:
        print(f"ℹ️  Direct service demo skipped (import error): {e}")
    except Exception as e:
        print(f"❌ Direct service demo error: {e}")

async def main():
    """Run the complete demo"""
    
    # API Demo (requires running server)
    await demo_hybrid_api()
    
    # Direct Service Demo
    demo_direct_service()
    
    print(f"\n🎉 Demo Complete!")
    print("=" * 20)
    print("📚 Next Steps:")
    print("   1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("   2. Set up JWT authentication for production use")
    print("   3. Configure real Kiro CLI integration")
    print("   4. Add OpenAI enhancement processing")
    print("   5. Set up monitoring and alerting")

if __name__ == "__main__":
    asyncio.run(main())