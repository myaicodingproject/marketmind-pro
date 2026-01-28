#!/usr/bin/env python3
"""
Integration Test for Hybrid PDF Generation System - Phase 2
Tests the complete integration layer functionality
"""

import asyncio
import sys
import json
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.services.enhanced_pdf_generator import EnhancedPDFGenerator
from app.schemas.hybrid_models import HybridReportRequest, EnhancementLevel

async def test_hybrid_system():
    """Test the hybrid PDF generation system"""
    
    print("🚀 Testing Hybrid PDF Generation System - Phase 2")
    print("=" * 60)
    
    # Initialize generator
    try:
        generator = EnhancedPDFGenerator()
        print("✅ EnhancedPDFGenerator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return False
    
    # Test with different enhancement levels
    test_cases = [
        ("AAPL", EnhancementLevel.KIRO_ONLY),
        ("GOOGL", EnhancementLevel.STANDARD),
        ("MSFT", EnhancementLevel.PREMIUM)
    ]
    
    results = []
    
    for symbol, enhancement_level in test_cases:
        print(f"\n📊 Testing {symbol} with {enhancement_level.value} enhancement...")
        
        try:
            # Generate hybrid report
            result = await generator.generate_hybrid_report(
                symbol=symbol,
                enhancement_level=enhancement_level.value,
                include_charts=True
            )
            
            if result["success"]:
                print(f"✅ {symbol} report generated successfully")
                print(f"   📄 PDF Path: {result.get('pdf_path', 'N/A')}")
                print(f"   📈 Quality Score: {result.get('quality_score', 'N/A')}")
                print(f"   ⏱️  Generation Time: {result.get('generation_time', 'N/A')}")
                results.append(True)
            else:
                print(f"❌ {symbol} report generation failed: {result.get('error', 'Unknown error')}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Exception during {symbol} generation: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 30)
    success_count = sum(results)
    total_count = len(results)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All tests passed! Hybrid system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

async def test_api_models():
    """Test the API models and validation"""
    
    print("\n🔧 Testing API Models and Validation")
    print("=" * 40)
    
    try:
        # Test valid request
        valid_request = HybridReportRequest(
            symbol="AAPL",
            enhancement_level=EnhancementLevel.STANDARD,
            include_charts=True
        )
        print("✅ Valid request model created successfully")
        print(f"   Symbol: {valid_request.symbol}")
        print(f"   Enhancement: {valid_request.enhancement_level}")
        
        # Test invalid symbol
        try:
            invalid_request = HybridReportRequest(
                symbol="123",  # Invalid - contains numbers
                enhancement_level=EnhancementLevel.STANDARD
            )
            print("❌ Invalid symbol validation failed - should have been rejected")
            return False
        except ValueError as e:
            print("✅ Invalid symbol correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ API model testing failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist"""
    
    print("\n📁 Testing Directory Structure")
    print("=" * 35)
    
    required_dirs = [
        "app/services",
        "app/api", 
        "app/schemas",
        "reports"
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
            # Create missing directories
            path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 Created {dir_path}")
    
    return all_exist

async def main():
    """Run all integration tests"""
    
    print("🧪 Hybrid PDF Generation System - Integration Tests")
    print("=" * 55)
    
    # Test directory structure
    dir_test = test_directory_structure()
    
    # Test API models
    model_test = await test_api_models()
    
    # Test hybrid system (only if previous tests pass)
    if dir_test and model_test:
        system_test = await test_hybrid_system()
    else:
        print("⚠️  Skipping system tests due to prerequisite failures")
        system_test = False
    
    # Final summary
    print(f"\n🏁 Final Results")
    print("=" * 20)
    print(f"📁 Directory Structure: {'✅ PASS' if dir_test else '❌ FAIL'}")
    print(f"🔧 API Models: {'✅ PASS' if model_test else '❌ FAIL'}")
    print(f"🚀 Hybrid System: {'✅ PASS' if system_test else '❌ FAIL'}")
    
    overall_success = dir_test and model_test and system_test
    
    if overall_success:
        print("\n🎉 All integration tests passed! Phase 2 is ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)