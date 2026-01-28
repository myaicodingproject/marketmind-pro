#!/usr/bin/env python3
"""
Test enhanced service directly
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append('/mnt/c/kiro')

async def test_enhanced_service():
    """Test enhanced service functionality"""
    try:
        from enhanced_service import enhanced_service
        from enhanced_models import SectionType
        
        print("🔍 Testing Enhanced Service...")
        
        # Initialize the service
        await enhanced_service.initialize()
        print("✅ Enhanced service initialized")
        
        # Create a test enhanced report
        report_id = await enhanced_service.create_enhanced_report("TEST")
        print(f"✅ Created enhanced report: {report_id}")
        
        # Try to process a section
        await enhanced_service.process_raw_section(
            report_id, 
            SectionType.EXECUTIVE_SUMMARY, 
            "This is test content for executive summary.",
            2,  # target_pages
            30  # processing_time
        )
        print("✅ Processed raw section")
        
        # Try to get the report
        report = await enhanced_service.get_enhanced_report(report_id)
        if report:
            print(f"✅ Retrieved enhanced report: {report.ticker}")
            print(f"   Status: {report.status}")
            print(f"   Sections: {len(report.sections)}")
        else:
            print("❌ Could not retrieve enhanced report")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set OpenAI API key
    os.environ['OPENAI_API_KEY'] = "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"
    
    success = asyncio.run(test_enhanced_service())
    if success:
        print("\n🎉 Enhanced service is working correctly!")
    else:
        print("\n⚠️ Enhanced service has issues.")
