"""
GOOGL Report Template Test
Tests the new Handlebars + React template system with GOOGL data
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Import our new template services
from app.services.template_integration import template_service
from app.services.template_pipeline import data_pipeline

def create_googl_sample_data():
    """Create comprehensive GOOGL sample data for template testing"""
    
    googl_data = {
        "ticker": "GOOGL",
        "company_name": "Alphabet Inc.",
        "executive_summary": {
            "content": """
            <p><strong>Alphabet Inc. (GOOGL)</strong> continues to demonstrate exceptional performance across its diversified technology portfolio. The company's dominant position in search, robust cloud growth, and emerging AI capabilities position it well for sustained long-term growth.</p>
            
            <p>Our analysis indicates <strong>strong fundamentals</strong> with revenue growth accelerating in Q4 2023, driven by:</p>
            <ul>
                <li>Google Search revenue growth of 13% year-over-year</li>
                <li>Google Cloud achieving $8.03B in quarterly revenue (+26% YoY)</li>
                <li>YouTube advertising revenue recovery showing positive momentum</li>
                <li>Significant progress in AI integration across all product lines</li>
            </ul>
            
            <p>We maintain a <strong>BUY</strong> recommendation with a 12-month price target of <strong>$175.00</strong>, representing 5.7% upside from current levels.</p>
            """,
            "recommendation": "Buy",
            "price_target": "$175.00",
            "current_price": "$165.50",
            "market_cap": "$2.1T",
            "pe_ratio": "24.5",
            "revenue_growth": "12.3%"
        },
        
        "financial_analysis": {
            "content": """
            <p>Alphabet's financial performance demonstrates <strong>consistent execution</strong> across key metrics with improving operational efficiency and strong cash generation.</p>
            
            <h4>Revenue Analysis</h4>
            <p>Total revenue reached <strong>$307.4B in 2023</strong>, representing 8.7% year-over-year growth. Key drivers include:</p>
            <ul>
                <li><strong>Google Search:</strong> $175.0B (+8.4% YoY) - Core search remains resilient</li>
                <li><strong>Google Cloud:</strong> $33.1B (+26.1% YoY) - Accelerating enterprise adoption</li>
                <li><strong>YouTube Ads:</strong> $31.5B (+1.3% YoY) - Stabilizing after 2022 decline</li>
                <li><strong>Other Bets:</strong> $1.3B (+21.4% YoY) - Early-stage ventures showing promise</li>
            </ul>
            
            <h4>Profitability Metrics</h4>
            <p>Operating margins expanded to <strong>25.3%</strong> in 2023, up from 23.1% in 2022, driven by:</p>
            <ul>
                <li>Improved cost discipline and operational efficiency</li>
                <li>Higher-margin cloud services growth</li>
                <li>AI-driven automation reducing operational costs</li>
            </ul>
            """,
            "revenue": [
                {"year": "2021", "value": "$257.6B", "growth": "41.2%"},
                {"year": "2022", "value": "$282.8B", "growth": "9.8%"},
                {"year": "2023", "value": "$307.4B", "growth": "8.7%"}
            ],
            "profit_margins": {
                "gross": "57.2%",
                "operating": "25.3%",
                "net": "21.1%"
            },
            "growth_rates": {
                "revenue_3yr": "15.2%",
                "earnings_3yr": "18.7%",
                "free_cash_flow": "22.1%"
            }
        },
        
        "company_overview": {
            "content": """
            <p>Alphabet Inc. operates as a holding company with subsidiaries that provide a wide range of products and services in the technology sector. The company's primary focus areas include:</p>
            
            <h4>Core Business Segments</h4>
            <ul>
                <li><strong>Google Services:</strong> Search, Ads, Gmail, Maps, Play, YouTube</li>
                <li><strong>Google Cloud:</strong> Infrastructure, platform, and software services</li>
                <li><strong>Other Bets:</strong> Waymo, Verily, Wing, and other emerging technologies</li>
            </ul>
            """,
            "business_model": """
            <p>Alphabet's business model is built on <strong>multiple revenue streams</strong> with advertising as the primary driver:</p>
            <ul>
                <li><strong>Advertising (77% of revenue):</strong> Search ads, YouTube ads, Network ads</li>
                <li><strong>Cloud Services (11% of revenue):</strong> Infrastructure, platform, and software services</li>
                <li><strong>Other Revenue (12% of revenue):</strong> Play Store, hardware, subscriptions</li>
            </ul>
            <p>The company benefits from <strong>network effects</strong>, vast data advantages, and high switching costs that create sustainable competitive moats.</p>
            """,
            "competitive_analysis": """
            <p>Alphabet maintains <strong>dominant market positions</strong> across key segments:</p>
            <ul>
                <li><strong>Search:</strong> ~92% global market share with strong barriers to entry</li>
                <li><strong>Mobile OS:</strong> Android powers 71% of global smartphones</li>
                <li><strong>Video Platform:</strong> YouTube is the #2 search engine globally</li>
                <li><strong>Cloud Computing:</strong> #3 position with 8% market share, growing rapidly</li>
            </ul>
            """
        },
        
        "valuation_analysis": {
            "content": """
            <p>Our valuation analysis employs multiple methodologies to arrive at a <strong>fair value estimate of $175 per share</strong>.</p>
            
            <h4>Valuation Summary</h4>
            <ul>
                <li><strong>DCF Model:</strong> $178 per share (10% discount rate, 3% terminal growth)</li>
                <li><strong>P/E Multiple:</strong> $172 per share (26x 2024E EPS of $6.62)</li>
                <li><strong>EV/Revenue:</strong> $170 per share (6.5x 2024E revenue)</li>
                <li><strong>Sum-of-Parts:</strong> $180 per share (individual segment valuations)</li>
            </ul>
            """,
            "dcf_analysis": """
            <p>Our DCF model assumes:</p>
            <ul>
                <li><strong>Revenue Growth:</strong> 10-12% CAGR over next 5 years</li>
                <li><strong>Operating Margins:</strong> Expanding to 28% by 2028</li>
                <li><strong>Free Cash Flow:</strong> $85B in 2024, growing to $140B by 2028</li>
                <li><strong>Terminal Value:</strong> 3% perpetual growth rate</li>
            </ul>
            """,
            "peer_comparison": """
            <p>Alphabet trades at attractive valuations relative to mega-cap tech peers:</p>
            <ul>
                <li><strong>P/E Ratio:</strong> 24.5x vs. 28.2x peer average</li>
                <li><strong>EV/Revenue:</strong> 5.8x vs. 7.1x peer average</li>
                <li><strong>PEG Ratio:</strong> 1.3x vs. 1.8x peer average</li>
            </ul>
            """
        },
        
        "risk_assessment": {
            "content": """
            <p>While Alphabet presents compelling investment opportunities, several key risks warrant consideration:</p>
            
            <h4>Primary Risk Factors</h4>
            <ul>
                <li><strong>Regulatory Risk:</strong> Ongoing antitrust investigations and potential breakup scenarios</li>
                <li><strong>Competition Risk:</strong> Emerging AI competitors and search alternatives</li>
                <li><strong>Privacy Concerns:</strong> Changing privacy regulations affecting data collection</li>
                <li><strong>Economic Sensitivity:</strong> Advertising revenue cyclicality during downturns</li>
            </ul>
            """,
            "risk_factors": """
            <p><strong>Regulatory and Legal Risks:</strong></p>
            <ul>
                <li>DOJ antitrust case targeting search monopoly</li>
                <li>EU Digital Markets Act compliance requirements</li>
                <li>Potential forced divestiture of Chrome or Android</li>
            </ul>
            
            <p><strong>Competitive and Technology Risks:</strong></p>
            <ul>
                <li>Microsoft/OpenAI partnership in AI search</li>
                <li>TikTok's impact on YouTube engagement</li>
                <li>Apple's privacy changes affecting ad targeting</li>
            </ul>
            """,
            "mitigation_strategies": """
            <p>Alphabet has implemented several strategies to mitigate key risks:</p>
            <ul>
                <li><strong>Diversification:</strong> Expanding beyond advertising into cloud and hardware</li>
                <li><strong>AI Leadership:</strong> Significant investment in Bard, Gemini, and AI infrastructure</li>
                <li><strong>Regulatory Compliance:</strong> Proactive engagement with regulators globally</li>
                <li><strong>Privacy-First Approach:</strong> Developing privacy-preserving advertising technologies</li>
            </ul>
            """
        }
    }
    
    return googl_data

def test_handlebars_template():
    """Test Handlebars template rendering with GOOGL data"""
    
    print("🔧 Testing Handlebars Template System...")
    
    # Create sample data
    googl_data = create_googl_sample_data()
    
    try:
        # Render using Handlebars
        html_output = template_service.render_report("GOOGL", googl_data, "handlebars")
        
        # Save output
        output_path = Path("test_output/googl_handlebars_report.html")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"✅ Handlebars template rendered successfully!")
        print(f"📄 Output saved to: {output_path}")
        print(f"📊 Report size: {len(html_output):,} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Handlebars template test failed: {str(e)}")
        return False

def test_react_template():
    """Test React template data preparation"""
    
    print("\n⚛️  Testing React Template System...")
    
    # Create sample data
    googl_data = create_googl_sample_data()
    
    try:
        # Prepare React data
        react_data = template_service.render_report("GOOGL", googl_data, "react")
        
        # Save React props
        output_path = Path("test_output/googl_react_props.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(react_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ React template data prepared successfully!")
        print(f"📄 Props saved to: {output_path}")
        print(f"🧩 Component: {react_data['component']}")
        
        return True
        
    except Exception as e:
        print(f"❌ React template test failed: {str(e)}")
        return False

def test_data_validation():
    """Test template data validation"""
    
    print("\n🔍 Testing Data Validation...")
    
    googl_data = create_googl_sample_data()
    
    try:
        # Validate data
        validation_result = template_service.validate_template_data("GOOGL", 
                                                                   data_pipeline.process_report_data("GOOGL", googl_data))
        
        print(f"✅ Data validation completed!")
        print(f"📊 Valid: {validation_result['valid']}")
        print(f"⚠️  Warnings: {len(validation_result['warnings'])}")
        print(f"❌ Errors: {len(validation_result['errors'])}")
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                print(f"   ⚠️  {warning}")
        
        if validation_result['errors']:
            for error in validation_result['errors']:
                print(f"   ❌ {error}")
        
        return validation_result['valid']
        
    except Exception as e:
        print(f"❌ Data validation test failed: {str(e)}")
        return False

def test_template_config():
    """Test template configuration export"""
    
    print("\n⚙️  Testing Template Configuration...")
    
    try:
        config = template_service.export_template_config()
        
        # Save config
        output_path = Path("test_output/template_config.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Template configuration exported!")
        print(f"📄 Config saved to: {output_path}")
        print(f"🏗️  Template Engine: {config['template_engine']}")
        print(f"📦 Version: {config['version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template configuration test failed: {str(e)}")
        return False

def main():
    """Run all template system tests"""
    
    print("🚀 MarketMind Pro - Phase 2 Template Migration System Test")
    print("=" * 60)
    
    # Create test output directory
    Path("test_output").mkdir(exist_ok=True)
    
    # Run tests
    tests = [
        ("Handlebars Template", test_handlebars_template),
        ("React Template", test_react_template), 
        ("Data Validation", test_data_validation),
        ("Template Configuration", test_template_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Template migration system is ready.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()