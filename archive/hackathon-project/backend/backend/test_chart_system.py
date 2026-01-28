"""
Test Chart Data Extraction System
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.features.charts.service import ChartService
from app.features.charts.processor import ChartDataProcessor
from app.features.charts.validator import ChartDataValidator

# Sample financial data for testing
SAMPLE_FINANCIAL_DATA = {
    "overview": {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "Technology",
        "Industry": "Consumer Electronics",
        "PERatio": "28.5",
        "PriceToBookRatio": "45.2",
        "PriceToSalesRatioTTM": "7.8",
        "ReturnOnEquityTTM": "0.175",
        "Beta": "1.2",
        "DividendYield": "0.0044",
        "DebtToEquityRatio": "1.73",
        "CurrentRatio": "0.93",
        "EVToEBITDA": "22.1",
        "PEGRatio": "2.8"
    },
    "income_statement": {
        "annualReports": [
            {
                "fiscalDateEnding": "2023-09-30",
                "totalRevenue": "383285000000",
                "grossProfit": "169148000000",
                "operatingIncome": "114301000000",
                "netIncome": "96995000000"
            },
            {
                "fiscalDateEnding": "2022-09-24",
                "totalRevenue": "394328000000",
                "grossProfit": "170782000000",
                "operatingIncome": "119437000000",
                "netIncome": "99803000000"
            },
            {
                "fiscalDateEnding": "2021-09-25",
                "totalRevenue": "365817000000",
                "grossProfit": "152836000000",
                "operatingIncome": "108949000000",
                "netIncome": "94680000000"
            },
            {
                "fiscalDateEnding": "2020-09-26",
                "totalRevenue": "274515000000",
                "grossProfit": "104956000000",
                "operatingIncome": "66288000000",
                "netIncome": "57411000000"
            },
            {
                "fiscalDateEnding": "2019-09-28",
                "totalRevenue": "260174000000",
                "grossProfit": "98392000000",
                "operatingIncome": "63930000000",
                "netIncome": "55256000000"
            }
        ],
        "quarterlyReports": [
            {
                "fiscalDateEnding": "2023-09-30",
                "totalRevenue": "89498000000",
                "grossProfit": "41671000000",
                "operatingIncome": "22999000000",
                "netIncome": "22956000000"
            },
            {
                "fiscalDateEnding": "2023-06-30",
                "totalRevenue": "81797000000",
                "grossProfit": "35383000000",
                "operatingIncome": "21973000000",
                "netIncome": "19881000000"
            }
        ]
    },
    "balance_sheet": {
        "annualReports": [
            {
                "fiscalDateEnding": "2023-09-30",
                "totalAssets": "352755000000",
                "totalLiabilities": "290437000000",
                "totalShareholderEquity": "62318000000"
            }
        ]
    },
    "daily_prices": {
        "Time Series (Daily)": {
            "2023-12-01": {
                "1. open": "189.84",
                "2. high": "190.32",
                "3. low": "188.19",
                "4. close": "189.95",
                "5. volume": "48744644"
            },
            "2023-11-30": {
                "1. open": "190.90",
                "2. high": "191.08",
                "3. low": "189.25",
                "4. close": "189.95",
                "5. volume": "51131065"
            }
        }
    }
}

SAMPLE_PEER_DATA = [
    {
        "overview": {
            "Symbol": "MSFT",
            "Name": "Microsoft Corporation",
            "PERatio": "32.1",
            "PriceToBookRatio": "12.8",
            "PriceToSalesRatioTTM": "11.2",
            "ReturnOnEquityTTM": "0.38"
        }
    },
    {
        "overview": {
            "Symbol": "GOOGL",
            "Name": "Alphabet Inc.",
            "PERatio": "25.4",
            "PriceToBookRatio": "5.2",
            "PriceToSalesRatioTTM": "4.8",
            "ReturnOnEquityTTM": "0.28"
        }
    }
]

async def test_chart_processor():
    """Test the chart data processor"""
    print("=== Testing Chart Data Processor ===")
    
    processor = ChartDataProcessor()
    
    # Test revenue trends
    print("\n1. Testing Revenue Trends Chart...")
    revenue_chart = processor.process_revenue_trends(SAMPLE_FINANCIAL_DATA)
    print(f"   Chart Type: {revenue_chart.type}")
    print(f"   Labels: {revenue_chart.data['labels']}")
    print(f"   Datasets: {len(revenue_chart.data['datasets'])}")
    
    # Test profit margins
    print("\n2. Testing Profit Margins Chart...")
    margins_chart = processor.process_profit_margins(SAMPLE_FINANCIAL_DATA)
    print(f"   Chart Type: {margins_chart.type}")
    print(f"   Labels: {margins_chart.data['labels']}")
    print(f"   Datasets: {len(margins_chart.data['datasets'])}")
    
    # Test valuation multiples
    print("\n3. Testing Valuation Multiples Chart...")
    valuation_chart = processor.process_valuation_multiples(SAMPLE_FINANCIAL_DATA)
    print(f"   Chart Type: {valuation_chart.type}")
    print(f"   Labels: {valuation_chart.data['labels']}")
    print(f"   Values: {valuation_chart.data['datasets'][0]['data']}")
    
    # Test risk metrics
    print("\n4. Testing Risk Metrics Chart...")
    risk_chart = processor.process_risk_metrics(SAMPLE_FINANCIAL_DATA)
    print(f"   Chart Type: {risk_chart.type}")
    print(f"   Labels: {risk_chart.data['labels']}")
    print(f"   Values: {risk_chart.data['datasets'][0]['data']}")
    
    # Test peer comparison
    print("\n5. Testing Peer Comparison Chart...")
    peer_chart = processor.process_peer_comparison(SAMPLE_FINANCIAL_DATA, SAMPLE_PEER_DATA)
    print(f"   Chart Type: {peer_chart.type}")
    print(f"   Companies: {peer_chart.data['labels']}")
    print(f"   Metrics: {len(peer_chart.data['datasets'])}")
    
    return True

async def test_chart_validator():
    """Test the chart data validator"""
    print("\n=== Testing Chart Data Validator ===")
    
    validator = ChartDataValidator()
    
    # Test data validation
    print("\n1. Testing Financial Data Validation...")
    is_valid, errors, cleaned_data = validator.validate_financial_data(SAMPLE_FINANCIAL_DATA)
    print(f"   Valid: {is_valid}")
    print(f"   Errors: {len(errors)}")
    if errors:
        for error in errors[:3]:  # Show first 3 errors
            print(f"     - {error}")
    print(f"   Cleaned data keys: {list(cleaned_data.keys())}")
    
    # Test chart config validation
    print("\n2. Testing Chart Config Validation...")
    sample_config = {
        "type": "line",
        "data": {
            "labels": ["2019", "2020", "2021", "2022", "2023"],
            "datasets": [{
                "label": "Revenue",
                "data": [260.2, 274.5, 365.8, 394.3, 383.3]
            }]
        },
        "options": {
            "responsive": True
        }
    }
    
    config_valid, config_errors = validator.validate_chart_config(sample_config)
    print(f"   Valid: {config_valid}")
    print(f"   Errors: {len(config_errors)}")
    
    return True

async def test_chart_service():
    """Test the chart service"""
    print("\n=== Testing Chart Service ===")
    
    service = ChartService()
    
    # Test chart generation
    print("\n1. Testing Company Chart Generation...")
    charts = await service.generate_company_charts("AAPL", SAMPLE_FINANCIAL_DATA)
    print(f"   Generated charts: {list(charts.keys())}")
    
    for chart_name, chart_config in charts.items():
        print(f"   {chart_name}: {chart_config.type} chart with {len(chart_config.data.get('datasets', []))} datasets")
    
    # Test chart serialization
    print("\n2. Testing Chart Serialization...")
    serialized = service.serialize_charts_for_api(charts)
    print(f"   Serialized charts: {list(serialized.keys())}")
    
    # Test chart summary
    print("\n3. Testing Chart Data Summary...")
    summary = await service.get_chart_data_summary("AAPL", SAMPLE_FINANCIAL_DATA)
    print(f"   Available charts: {summary['available_charts']}")
    print(f"   Data quality: {summary['data_quality']}")
    
    # Test peer comparison
    print("\n4. Testing Peer Comparison...")
    peer_chart = await service.generate_peer_comparison_chart(
        "AAPL", SAMPLE_FINANCIAL_DATA, ["MSFT", "GOOGL"], SAMPLE_PEER_DATA
    )
    print(f"   Peer chart type: {peer_chart.type}")
    print(f"   Companies compared: {len(peer_chart.data['labels'])}")
    
    return True

def save_sample_charts():
    """Save sample chart configurations to files"""
    print("\n=== Saving Sample Chart Configurations ===")
    
    processor = ChartDataProcessor()
    
    # Generate all chart types
    charts = {
        'revenue_trends': processor.process_revenue_trends(SAMPLE_FINANCIAL_DATA),
        'profit_margins': processor.process_profit_margins(SAMPLE_FINANCIAL_DATA),
        'valuation_multiples': processor.process_valuation_multiples(SAMPLE_FINANCIAL_DATA),
        'risk_metrics': processor.process_risk_metrics(SAMPLE_FINANCIAL_DATA),
        'peer_comparison': processor.process_peer_comparison(SAMPLE_FINANCIAL_DATA, SAMPLE_PEER_DATA)
    }
    
    # Create output directory
    output_dir = Path("chart_samples")
    output_dir.mkdir(exist_ok=True)
    
    # Save each chart configuration
    for chart_name, chart_config in charts.items():
        chart_dict = {
            'type': chart_config.type,
            'data': chart_config.data,
            'options': chart_config.options
        }
        
        output_file = output_dir / f"{chart_name}.json"
        with open(output_file, 'w') as f:
            json.dump(chart_dict, f, indent=2, default=str)
        
        print(f"   Saved {chart_name} to {output_file}")
    
    # Save sample data
    data_file = output_dir / "sample_data.json"
    with open(data_file, 'w') as f:
        json.dump({
            'financial_data': SAMPLE_FINANCIAL_DATA,
            'peer_data': SAMPLE_PEER_DATA
        }, f, indent=2)
    
    print(f"   Saved sample data to {data_file}")
    
    return True

async def run_comprehensive_test():
    """Run comprehensive test of the chart system"""
    print("🚀 MarketMind Pro - Chart Data Extraction System Test")
    print("=" * 60)
    
    try:
        # Test individual components
        await test_chart_processor()
        await test_chart_validator()
        await test_chart_service()
        
        # Save sample outputs
        save_sample_charts()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\nChart system is ready for integration with report generation pipeline.")
        
        # Performance summary
        print("\n📊 Chart Generation Summary:")
        print("   - Revenue Trends: Line chart with annual/quarterly data")
        print("   - Profit Margins: Multi-line chart (gross, operating, net)")
        print("   - Valuation Multiples: Bar chart with color-coded values")
        print("   - Risk Metrics: Radar chart with normalized scores")
        print("   - Peer Comparison: Horizontal bar chart with multiple metrics")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)