#!/usr/bin/env python3
"""
Test OpenAI Integration and Hybrid PDF Enhancement
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add app to path
sys.path.append('/mnt/c/kiro')

async def test_openai_integration():
    """Test OpenAI integration and hybrid PDF enhancement"""
    
    print("🧪 TESTING OPENAI HYBRID PDF ENHANCEMENT")
    print("=" * 60)
    
    try:
        from app.services.hybrid_system import HybridPDFSystem
        
        # Initialize system
        system = HybridPDFSystem()
        print(f"✅ Hybrid system initialized")
        print(f"   Model: {system.model}")
        print(f"   Enhancement enabled: {system.enhancement_enabled}")
        
        # Test content enhancement
        test_content = """
        Searching for symbols matching: "generate_report"
        + 7: + 8: Alphabet Inc. (GOOGL) stands as the dominant force
        > # Executive Summary
        • Revenue: $339.7 billion (+13.3% YoY)
        • Net Income: $88.3 billion
        git/objects/04: IO error for operation
        """
        
        print(f"\n📝 Testing content enhancement...")
        enhanced_section = await system._enhance_section("Executive Summary", test_content)
        
        print(f"✅ Content enhanced successfully!")
        print(f"   Issues fixed: {enhanced_section.issues_fixed}")
        print(f"   Quality score: {enhanced_section.quality_score}/100")
        print(f"   Content preview: {enhanced_section.content[:200]}...")
        
        # Test with GOOGL report data
        print(f"\n📊 Testing with GOOGL report data...")
        
        import requests
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code == 200:
            report_data = response.json()
            
            # Enhance first section
            first_section_key = list(report_data.get('sections', {}).keys())[0]
            first_section = report_data['sections'][first_section_key]
            
            enhanced = await system._enhance_section(
                first_section.get('title', first_section_key),
                first_section.get('content', '')[:1000]  # Limit for testing
            )
            
            print(f"✅ GOOGL section enhanced!")
            print(f"   Section: {enhanced.title}")
            print(f"   Issues fixed: {len(enhanced.issues_fixed)}")
            print(f"   Quality score: {enhanced.quality_score}/100")
            
        else:
            print(f"⚠️  Could not get GOOGL report data: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_pdf_generation():
    """Test complete enhanced PDF generation"""
    
    print(f"\n🎯 TESTING ENHANCED PDF GENERATION")
    print("-" * 40)
    
    try:
        from app.services.enhanced_pdf_generator import EnhancedPDFGenerator
        
        generator = EnhancedPDFGenerator()
        
        # Generate enhanced PDF
        pdf_path = await generator.generate_enhanced_pdf(
            ticker="GOOGL",
            report_id="prod_report_GOOGL_1769350746"
        )
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ Enhanced PDF generated!")
            print(f"   Path: {pdf_path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Quick quality check
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                first_page = pdf_reader.pages[0].extract_text()
                
                # Check for improvements
                no_debug_text = 'Searching for symbols' not in first_page
                no_line_numbers = '+ 7:' not in first_page and '+ 8:' not in first_page
                has_content = len(first_page) > 100
                
                quality_checks = [no_debug_text, no_line_numbers, has_content]
                quality_score = (sum(quality_checks) / len(quality_checks)) * 100
                
                print(f"📊 Quality Assessment:")
                print(f"   Pages: {total_pages}")
                print(f"   No debug text: {'✅' if no_debug_text else '❌'}")
                print(f"   No line numbers: {'✅' if no_line_numbers else '❌'}")
                print(f"   Has content: {'✅' if has_content else '❌'}")
                print(f"   Quality score: {quality_score:.1f}/100")
                
                return quality_score >= 80
        else:
            print(f"❌ PDF not generated")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all hybrid system tests"""
    
    print("🚀 HYBRID SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: OpenAI Integration
    openai_success = await test_openai_integration()
    
    # Test 2: Enhanced PDF Generation
    pdf_success = await test_enhanced_pdf_generation()
    
    # Results
    print(f"\n🎯 HYBRID SYSTEM TEST RESULTS")
    print("=" * 40)
    print(f"✅ OpenAI Integration: {'PASSED' if openai_success else 'FAILED'}")
    print(f"✅ Enhanced PDF Generation: {'PASSED' if pdf_success else 'FAILED'}")
    
    overall_success = openai_success and pdf_success
    
    if overall_success:
        print(f"\n🏆 HYBRID SYSTEM FULLY OPERATIONAL!")
        print(f"📋 Ready for production use")
        print(f"🎯 Enhanced PDF generation with OpenAI working perfectly")
    else:
        print(f"\n⚠️  HYBRID SYSTEM NEEDS ATTENTION")
        print(f"📋 Check errors above for details")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
