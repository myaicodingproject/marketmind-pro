#!/usr/bin/env python3
"""
Simple OpenAI Integration Test
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_openai_connection():
    """Test basic OpenAI connection"""
    
    print("🧪 TESTING OPENAI CONNECTION")
    print("=" * 40)
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test basic connection
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, test connection"}],
            max_tokens=10
        )
        
        print("✅ OpenAI connection successful!")
        print(f"   Model: gpt-4o-mini")
        print(f"   Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

async def test_content_enhancement():
    """Test content enhancement functionality"""
    
    print("\n📝 TESTING CONTENT ENHANCEMENT")
    print("-" * 40)
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test content with issues
        test_content = """
        Searching for symbols matching: "generate_report"
        + 7: + 8: Alphabet Inc. (GOOGL) stands as the dominant force
        > # Executive Summary
        • Revenue: $339.7 billion
        git/objects/04: IO error
        """
        
        # Enhance content
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Clean this financial report content. Remove debug messages, line numbers, and system errors. Make it professional."
                },
                {
                    "role": "user",
                    "content": f"Clean this content: {test_content}"
                }
            ],
            max_tokens=200
        )
        
        enhanced_content = response.choices[0].message.content
        
        print("✅ Content enhancement successful!")
        print(f"   Original issues: Debug messages, line numbers, system errors")
        print(f"   Enhanced content: {enhanced_content[:150]}...")
        
        # Check if issues were fixed
        issues_fixed = (
            'Searching for symbols' not in enhanced_content and
            '+ 7:' not in enhanced_content and
            'git/objects' not in enhanced_content
        )
        
        print(f"   Issues fixed: {'✅' if issues_fixed else '❌'}")
        
        return issues_fixed
        
    except Exception as e:
        print(f"❌ Content enhancement failed: {e}")
        return False

async def test_pdf_enhancement():
    """Test PDF enhancement with existing system"""
    
    print("\n🎯 TESTING PDF ENHANCEMENT")
    print("-" * 40)
    
    try:
        import requests
        from professional_pdf_generator import generate_professional_pdf
        from openai import AsyncOpenAI
        
        # Get GOOGL report
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code != 200:
            print(f"❌ Could not get GOOGL report: {response.status_code}")
            return False
        
        report_data = response.json()
        print("✅ Retrieved GOOGL report data")
        
        # Enhance first section with OpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        sections = report_data.get('sections', {})
        if not sections:
            print("❌ No sections found in report")
            return False
        
        first_section_key = list(sections.keys())[0]
        first_section = sections[first_section_key]
        original_content = first_section.get('content', '')
        
        # Enhance the content
        enhancement_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Clean and enhance this financial report content:
                    1. Remove debug messages and system artifacts
                    2. Fix formatting and spacing
                    3. Ensure professional tone
                    4. Preserve all financial data"""
                },
                {
                    "role": "user",
                    "content": f"Enhance this section: {original_content[:1000]}"
                }
            ],
            max_tokens=500
        )
        
        enhanced_content = enhancement_response.choices[0].message.content
        
        # Update report with enhanced content
        enhanced_report = report_data.copy()
        enhanced_report['sections'][first_section_key]['content'] = enhanced_content
        
        print("✅ Content enhanced with OpenAI")
        
        # Generate PDF with enhanced content
        output_path = "/mnt/c/kiro/GOOGL_OpenAI_Enhanced.pdf"
        pdf_path = generate_professional_pdf("GOOGL", enhanced_report, output_path)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ Enhanced PDF generated!")
            print(f"   Path: {pdf_path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return True
        else:
            print("❌ PDF not generated")
            return False
            
    except Exception as e:
        print(f"❌ PDF enhancement failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    
    print("🚀 OPENAI HYBRID SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: OpenAI Connection
    connection_ok = await test_openai_connection()
    
    # Test 2: Content Enhancement
    enhancement_ok = await test_content_enhancement()
    
    # Test 3: PDF Enhancement
    pdf_ok = await test_pdf_enhancement()
    
    # Results
    print(f"\n🎯 TEST RESULTS")
    print("=" * 30)
    print(f"OpenAI Connection: {'✅ PASSED' if connection_ok else '❌ FAILED'}")
    print(f"Content Enhancement: {'✅ PASSED' if enhancement_ok else '❌ FAILED'}")
    print(f"PDF Enhancement: {'✅ PASSED' if pdf_ok else '❌ FAILED'}")
    
    overall_success = connection_ok and enhancement_ok and pdf_ok
    
    if overall_success:
        print(f"\n🏆 OPENAI HYBRID SYSTEM WORKING!")
        print(f"📋 Ready to enhance PDF quality with AI")
    else:
        print(f"\n⚠️  Some tests failed - check details above")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
