"""
Smart Chart Generation System
Dynamically selects relevant charts based on company characteristics and data availability
"""

from typing import Dict, List, Any
from enum import Enum

class CompanyType(Enum):
    GROWTH_TECH = "growth_tech"
    VALUE = "value"
    CYCLICAL = "cyclical"
    DIVIDEND = "dividend"
    TURNAROUND = "turnaround"

class ChartRelevance(Enum):
    ESSENTIAL = 3  # Must show
    RECOMMENDED = 2  # Show if data available
    OPTIONAL = 1  # Show only if specifically requested

def detect_company_type(ticker: str, financial_data: Dict) -> CompanyType:
    """Detect company type based on financial characteristics"""
    
    # Extract key metrics
    revenue_growth = financial_data.get('revenue_growth_3y', 0)
    dividend_yield = financial_data.get('dividend_yield', 0)
    pe_ratio = financial_data.get('pe_ratio', 0)
    volatility = financial_data.get('beta', 1.0)
    
    # Decision logic
    if revenue_growth > 20 and pe_ratio > 30:
        return CompanyType.GROWTH_TECH
    elif dividend_yield > 3 and pe_ratio < 20:
        return CompanyType.DIVIDEND
    elif volatility > 1.5:
        return CompanyType.CYCLICAL
    elif pe_ratio < 15:
        return CompanyType.VALUE
    else:
        return CompanyType.GROWTH_TECH  # Default

def get_chart_relevance_map(company_type: CompanyType) -> Dict[str, ChartRelevance]:
    """Return chart relevance scores based on company type"""
    
    base_charts = {
        "revenue_trend": ChartRelevance.ESSENTIAL,
        "key_metrics": ChartRelevance.ESSENTIAL,
        "recommendation": ChartRelevance.ESSENTIAL,
    }
    
    type_specific = {
        CompanyType.GROWTH_TECH: {
            "tam_sam_som": ChartRelevance.ESSENTIAL,
            "market_share": ChartRelevance.RECOMMENDED,
            "dcf_sensitivity": ChartRelevance.RECOMMENDED,
            "segment_breakdown": ChartRelevance.RECOMMENDED,
            "peer_comparison": ChartRelevance.ESSENTIAL,
            "cash_flow_waterfall": ChartRelevance.OPTIONAL,
            "dividend_history": ChartRelevance.OPTIONAL,
        },
        CompanyType.VALUE: {
            "margins": ChartRelevance.ESSENTIAL,
            "cash_flow_waterfall": ChartRelevance.ESSENTIAL,
            "peer_comparison": ChartRelevance.ESSENTIAL,
            "dcf_sensitivity": ChartRelevance.ESSENTIAL,
            "dividend_history": ChartRelevance.RECOMMENDED,
            "tam_sam_som": ChartRelevance.OPTIONAL,
        },
        CompanyType.DIVIDEND: {
            "dividend_history": ChartRelevance.ESSENTIAL,
            "cash_flow_waterfall": ChartRelevance.ESSENTIAL,
            "margins": ChartRelevance.RECOMMENDED,
            "peer_comparison": ChartRelevance.RECOMMENDED,
            "dcf_sensitivity": ChartRelevance.OPTIONAL,
        },
        CompanyType.CYCLICAL: {
            "historical_cycles": ChartRelevance.ESSENTIAL,
            "margins": ChartRelevance.ESSENTIAL,
            "scenario_analysis": ChartRelevance.ESSENTIAL,
            "peer_comparison": ChartRelevance.RECOMMENDED,
        }
    }
    
    return {**base_charts, **type_specific.get(company_type, {})}

def check_data_quality(chart_type: str, data: Dict) -> bool:
    """Check if we have sufficient data quality for a chart"""
    
    requirements = {
        "dcf_sensitivity": ["cash_flow_projections", "wacc", "growth_rate"],
        "peer_comparison": ["peer_companies", "valuation_multiples"],
        "segment_breakdown": ["segment_revenue"],
        "tam_sam_som": ["market_size_data"],
        "cash_flow_waterfall": ["operating_cf", "capex", "fcf"],
    }
    
    required_fields = requirements.get(chart_type, [])
    return all(field in data and data[field] is not None for field in required_fields)

def generate_smart_chart_data(ticker: str, sections: Dict, financial_data: Dict) -> Dict:
    """
    Generate chart data dynamically based on:
    1. Company type
    2. Data availability
    3. Chart relevance
    """
    
    # Detect company type
    company_type = detect_company_type(ticker, financial_data)
    
    # Get relevance map
    relevance_map = get_chart_relevance_map(company_type)
    
    # Generate charts based on relevance and data availability
    chart_data = {}
    
    for chart_type, relevance in relevance_map.items():
        # Essential charts: always try to generate
        if relevance == ChartRelevance.ESSENTIAL:
            chart_data[chart_type] = generate_chart(chart_type, sections, financial_data)
        
        # Recommended charts: only if data quality is good
        elif relevance == ChartRelevance.RECOMMENDED:
            if check_data_quality(chart_type, financial_data):
                chart_data[chart_type] = generate_chart(chart_type, sections, financial_data)
        
        # Optional charts: skip unless explicitly requested
        # (could be added via user preference)
    
    # Add metadata
    chart_data['_metadata'] = {
        'company_type': company_type.value,
        'charts_generated': list(chart_data.keys()),
        'generation_strategy': 'smart_selection'
    }
    
    return chart_data

def generate_chart(chart_type: str, sections: Dict, financial_data: Dict) -> Dict:
    """Generate specific chart data (placeholder - implement actual logic)"""
    # This would contain the actual chart generation logic
    # For now, return structure
    return {
        "type": chart_type,
        "data": [],
        "config": {}
    }

# Example usage
if __name__ == "__main__":
    # Example for AVGO (Growth Tech company)
    financial_data = {
        "revenue_growth_3y": 44.1,
        "pe_ratio": 42.0,
        "dividend_yield": 1.8,
        "beta": 1.2,
        "cash_flow_projections": [21.9, 24.5, 27.2],
        "wacc": 9.0,
        "growth_rate": 15.0,
        "peer_companies": ["NVDA", "AMD", "QCOM"],
        "valuation_multiples": {"pe": 42, "ev_ebitda": 53.9}
    }
    
    company_type = detect_company_type("AVGO", financial_data)
    print(f"Company Type: {company_type.value}")
    
    relevance_map = get_chart_relevance_map(company_type)
    print(f"\nChart Relevance Map:")
    for chart, relevance in relevance_map.items():
        print(f"  {chart}: {relevance.name}")
