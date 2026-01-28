"""
Mock Kiro Service for testing report integration
"""
from typing import Dict, Any
import asyncio
import json

class MockKiroService:
    """Mock Kiro service for testing"""
    
    async def execute_prompt(self, prompt_name: str, context_data: Dict[str, Any]) -> str:
        """Mock prompt execution"""
        
        # Return different mock responses based on prompt type
        if "investment-thesis" in prompt_name:
            return json.dumps({
                "investment_thesis": f"Strong investment opportunity for {context_data.get('ticker', 'TICKER')}",
                "summary": "Comprehensive analysis shows positive outlook",
                "key_highlights": ["Strong fundamentals", "Market leadership", "Growth potential"]
            })
        
        elif "price-target" in prompt_name:
            return json.dumps({
                "price_analysis": "Technical and fundamental analysis supports upside",
                "recommendation": {
                    "rating": "BUY",
                    "price_target": "200.00",
                    "current_price": "175.50",
                    "confidence": "High"
                }
            })
        
        elif "key-metrics" in prompt_name:
            return json.dumps({
                "financial_metrics": "Strong financial performance across key metrics",
                "key_ratios": {
                    "revenue": "394.3B",
                    "pe_ratio": "28.5",
                    "roe": "15.2%",
                    "debt_to_equity": "0.85",
                    "current_ratio": "1.2"
                }
            })
        
        elif "risk-assessment" in prompt_name:
            return json.dumps({
                "risk_analysis": "Moderate risk profile with manageable exposures",
                "risk_factors": [
                    "Market volatility risk",
                    "Competitive pressure",
                    "Regulatory changes",
                    "Economic downturn impact"
                ]
            })
        
        else:
            return json.dumps({
                "content": f"Mock analysis for {prompt_name}",
                "summary": "Generated mock content for testing purposes"
            })

class MockChartIntegration:
    """Mock chart integration for testing"""
    
    async def generate_chart(self, chart_type: str, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock chart generation"""
        return {
            "title": chart_type.replace('_', ' ').title(),
            "type": chart_type,
            "data": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "values": [100, 120, 110, 130]
            },
            "config": {
                "width": 800,
                "height": 400,
                "theme": "professional"
            },
            "status": "generated"
        }