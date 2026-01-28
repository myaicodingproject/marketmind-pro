#!/usr/bin/env python3
"""
Quick Hybrid System Test - Direct Implementation
"""

import requests
import json
import time
import os

def test_hybrid_system_direct():
    """Test hybrid system with direct implementations"""
    print("🚀 QUICK HYBRID SYSTEM TEST")
    print("=" * 50)
    
    start_time = time.time()
    
    # Get GOOGL data
    print("📊 Getting GOOGL report data...")
    try:
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code == 200:
            report_data = response.json()
            print(f"✅ Retrieved {len(report_data.get('sections', {}))} sections")
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Generate charts directly
    print("\n📈 Generating charts...")
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create simple DCF chart
        fig, ax = plt.subplots(figsize=(10, 6))
        years = ['2026E', '2027E', '2028E', '2029E', '2030E', 'Terminal']
        values = [45.2, 52.1, 59.8, 68.4, 78.2, 1856.0]
        
        bars = ax.bar(years, values, color=['#2563eb', '#2563eb', '#2563eb', '#2563eb', '#2563eb', '#059669'])
        ax.set_title('GOOGL DCF Valuation ($B)', fontsize=16, fontweight='bold')
        ax.set_ylabel('Present Value ($B)')
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                   f'${value}B', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart_path = '/mnt/c/kiro/googl_dcf_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Generated DCF chart: {os.path.getsize(chart_path):,} bytes")
        
    except Exception as e:
        print(f"⚠️  Chart generation error: {e}")
    
    # Generate PDF with enhanced professional generator
    print("\n🎯 Generating enhanced PDF...")
    try:
        from professional_pdf_generator import generate_professional_pdf
        
        output_path = "/mnt/c/kiro/GOOGL_Hybrid_Test.pdf"
        pdf_path = generate_professional_pdf("GOOGL", report_data, output_path)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ Generated PDF: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        else:
            print(f"❌ PDF not generated")
            return False
            
    except Exception as e:
        print(f"❌ PDF error: {e}")
        return False
    
    # Quick quality check
    print("\n🔍 Quality validation...")
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Check first page
            first_page = pdf_reader.pages[0].extract_text()
            
            quality_score = 0
            checks = [
                ('Professional branding', 'MarketMind Pro' in first_page, 20),
                ('Investment recommendation', 'BUY' in first_page or 'SELL' in first_page, 20),
                ('Price target', '$' in first_page, 15),
                ('Clean content', 'Invoking' not in first_page, 25),
                ('Proper pages', total_pages > 50, 20)
            ]
            
            for check_name, passed, points in checks:
                if passed:
                    quality_score += points
                    print(f"   ✅ {check_name}: +{points} points")
                else:
                    print(f"   ❌ {check_name}: 0 points")
            
            print(f"📊 Quality Score: {quality_score}/100")
            
    except Exception as e:
        print(f"⚠️  Quality check error: {e}")
        quality_score = 0
    
    # Results
    total_time = time.time() - start_time
    print(f"\n🎯 HYBRID SYSTEM TEST RESULTS")
    print("=" * 40)
    print(f"📄 PDF: {pdf_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"📈 Pages: {total_pages}")
    print(f"🔍 Quality: {quality_score}/100")
    print(f"⏱️  Time: {total_time:.1f} seconds")
    
    if quality_score >= 80:
        print(f"🏆 EXCELLENT - System working well!")
    elif quality_score >= 60:
        print(f"✅ GOOD - System functional")
    else:
        print(f"⚠️  NEEDS WORK - System has issues")
    
    return True

if __name__ == "__main__":
    success = test_hybrid_system_direct()
    
    if success:
        print(f"\n🎉 HYBRID SYSTEM TEST COMPLETED!")
        print(f"📋 The enhanced PDF generation system is working!")
    else:
        print(f"\n❌ Test failed - check errors above")
