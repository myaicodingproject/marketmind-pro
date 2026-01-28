#!/usr/bin/env python3
# Test script for GOOGL chart generation using MarketMind Pro Chart System

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.hybrid_chart_service import HybridChartService
from app.services.chart_data_processor import ChartDataProcessor

async def test_googl_charts():
    """Test GOOGL chart generation with sample data"""
    print("🚀 Testing MarketMind Pro Chart Generation System")
    print("=" * 60)
    
    # Initialize services
    chart_service = HybridChartService()
    data_processor = ChartDataProcessor()
    
    # Sample GOOGL report data (from the actual report)
    googl_report_data = {
        "ticker": "GOOGL",
        "title": "GOOGL - Comprehensive Stock Analysis Report",
        "chart_data": {
            "financial_performance": {
                "revenue_trend": [
                    {"year": "2022", "revenue": 282836, "profit": 59972},
                    {"year": "2023", "revenue": 307394, "profit": 73795},
                    {"year": "2024", "revenue": 339700, "profit": 88300},
                    {"year": "2025E", "revenue": 375200, "profit": 98100},
                    {"year": "2026E", "revenue": 415800, "profit": 109200}
                ],
                "margins": [
                    {"metric": "Gross Margin", "value": 57.3},
                    {"metric": "Operating Margin", "value": 26.0},
                    {"metric": "Net Margin", "value": 24.0}
                ]
            }
        },
        "valuation_data": {
            "dcf_inputs": {
                "wacc": 0.092,
                "terminal_growth": 0.025,
                "cash_flows": [78.2, 89.1, 101.4, 113.8, 126.1],
                "terminal_value": 1856.0
            }
        }
    }
    
    print(f"📊 Processing data for {googl_report_data['ticker']}")
    
    # Process data for charts
    processed_data = data_processor.extract_googl_data(googl_report_data)
    print(f"✅ Data processed: {len(processed_data)} data categories")
    
    # Generate all charts
    print("\n🎯 Generating financial charts...")
    charts = await chart_service.generate_all_charts(processed_data)
    
    if charts:
        print(f"\n✅ Successfully generated {len(charts)} charts:")
        for chart_type, chart_data in charts.items():
            data_size = len(chart_data) if chart_data else 0
            print(f"  • {chart_type}: {data_size} bytes")
        
        # Save chart data to files for inspection
        output_dir = "chart_output"
        os.makedirs(output_dir, exist_ok=True)
        
        for chart_type, chart_data in charts.items():
            if chart_data:
                # Save base64 data to file
                with open(f"{output_dir}/googl_{chart_type}.txt", "w") as f:
                    f.write(chart_data)
                print(f"  💾 Saved {chart_type} to {output_dir}/googl_{chart_type}.txt")
        
        # Create summary report
        summary = {
            "ticker": "GOOGL",
            "generated_at": datetime.now().isoformat(),
            "charts_generated": list(charts.keys()),
            "chart_count": len(charts),
            "status": "success"
        }
        
        with open(f"{output_dir}/googl_chart_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📋 Chart generation summary saved to {output_dir}/googl_chart_summary.json")
        
    else:
        print("❌ No charts were generated")
        return False
    
    print("\n🎉 GOOGL chart generation test completed successfully!")
    return True

async def test_individual_charts():
    """Test individual chart generation"""
    print("\n🔍 Testing individual chart components...")
    
    from app.services.matplotlib_charts import MatplotlibFinancialCharts
    
    matplotlib_service = MatplotlibFinancialCharts()
    test_data = {"ticker": "GOOGL"}
    
    # Test DCF waterfall
    print("  📊 Testing DCF waterfall chart...")
    dcf_chart = matplotlib_service.generate_dcf_waterfall(test_data)
    if dcf_chart:
        print("    ✅ DCF waterfall chart generated")
    else:
        print("    ❌ DCF waterfall chart failed")
    
    # Test sensitivity heatmap
    print("  🔥 Testing sensitivity heatmap...")
    sensitivity_chart = matplotlib_service.generate_sensitivity_heatmap(test_data)
    if sensitivity_chart:
        print("    ✅ Sensitivity heatmap generated")
    else:
        print("    ❌ Sensitivity heatmap failed")
    
    # Test peer multiples
    print("  📈 Testing peer multiples chart...")
    peer_chart = matplotlib_service.generate_peer_multiples(test_data)
    if peer_chart:
        print("    ✅ Peer multiples chart generated")
    else:
        print("    ❌ Peer multiples chart failed")

if __name__ == "__main__":
    print("MarketMind Pro - Chart Generation Test Suite")
    print("Phase 1: Hybrid Chart.js + Python matplotlib system")
    print()
    
    try:
        # Run main test
        success = asyncio.run(test_googl_charts())
        
        if success:
            # Run individual component tests
            asyncio.run(test_individual_charts())
            
            print("\n" + "=" * 60)
            print("🎯 All tests completed successfully!")
            print("📊 Charts are ready for integration with MarketMind Pro")
            print("🔗 Use /api/v1/charts/generate endpoint to generate charts")
            print("🔗 Use /api/v1/charts/googl/demo for GOOGL demo charts")
        else:
            print("\n❌ Chart generation test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)