#!/usr/bin/env python3
"""
Quick Start Script for MarketMind Pro Parallel Report Generation
Simple interface to generate institutional-grade reports in 3-5 minutes
"""

import asyncio
import sys
from datetime import datetime

async def quick_generate(ticker: str):
    """Quick report generation with minimal output"""
    
    print(f"🚀 MarketMind Pro - Generating Report for {ticker}")
    print("⏳ Starting 8 concurrent subagents...")
    
    try:
        # Import and run the system
        from marketmind_parallel_system import generate_report
        
        start_time = datetime.now()
        report = await generate_report(ticker)
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Extract key results
        perf = report.get('performance_summary', {})
        metadata = report.get('metadata', {})
        
        print(f"\n✅ Report Generated Successfully!")
        print(f"⏱️  Time: {total_time:.1f}s (Target: ≤300s)")
        print(f"📊 Quality: {perf.get('quality_score_percentage', 0):.1f}%")
        print(f"🎓 Grade: {perf.get('performance_grade', 'N/A')}")
        print(f"📄 Pages: ~{metadata.get('estimated_pages', 0)}")
        print(f"💰 Value: Equivalent to $5,000+ Wall Street report")
        
        # Show section breakdown
        sections = report.get('sections', {})
        print(f"\n📋 Sections Generated: {len(sections)}/8")
        for name in sections.keys():
            print(f"  ✅ {name.replace('_', ' ').title()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation Failed: {e}")
        return False

async def main():
    """Main execution"""
    
    if len(sys.argv) != 2:
        print("Usage: python run_parallel_report.py <TICKER>")
        print("Example: python run_parallel_report.py AAPL")
        return
    
    ticker = sys.argv[1].upper()
    success = await quick_generate(ticker)
    
    if success:
        print(f"\n🎉 MarketMind Pro report for {ticker} completed!")
        print("📁 Check the 'reports' directory for output files")
    else:
        print(f"\n❌ Failed to generate report for {ticker}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())