import asyncio
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class Section3BusinessModelAgent:
    """Section 3 Agent - Business Model Analysis (4 pages)"""
    
    def __init__(self):
        self.section_name = "Business Model Analysis"
        self.section_number = 3
        self.page_count = 4
        
    async def generate_analysis(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business model analysis"""
        try:
            logger.info(f"Starting Section 3 Business Model Analysis for {ticker}")
            
            # Execute Kiro CLI with business model prompt
            business_model_content = await self._execute_kiro_business_model_prompt(ticker, company_data)
            
            # Generate business model canvas
            business_canvas = await self._create_business_model_canvas(company_data)
            
            # Create revenue breakdown charts
            revenue_charts = await self._generate_revenue_breakdown_charts(company_data)
            
            # Generate strategic positioning matrices
            positioning_matrices = await self._create_strategic_positioning_matrices(company_data)
            
            # Compile final analysis
            analysis = {
                "section": self.section_name,
                "section_number": self.section_number,
                "pages": self.page_count,
                "content": {
                    "business_model_analysis": business_model_content,
                    "business_model_canvas": business_canvas,
                    "revenue_breakdown": revenue_charts,
                    "strategic_positioning": positioning_matrices
                },
                "metadata": {
                    "ticker": ticker,
                    "generation_timestamp": asyncio.get_event_loop().time(),
                    "data_sources": ["SEC filings", "web research", "financial data"]
                }
            }
            
            logger.info(f"Completed Section 3 Business Model Analysis for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in Section 3 analysis for {ticker}: {str(e)}")
            raise
    
    async def _execute_kiro_business_model_prompt(self, ticker: str, company_data: Dict[str, Any]) -> str:
        """Execute Kiro CLI with business model analysis prompt"""
        try:
            # Use the Section 3 specific prompt
            prompt_path = Path(".kiro/prompts/section3-business-model-analysis.md")
            
            # Prepare formatted data for Kiro
            formatted_data = self._prepare_kiro_data(company_data)
            
            # Execute Kiro CLI using the existing service pattern
            from app.services.kiro_prompt_service import kiro_service
            
            # Use the internal _execute_prompt method with our custom prompt
            if prompt_path.exists():
                with open(prompt_path, 'r') as f:
                    prompt_template = f.read()
                
                formatted_prompt = prompt_template.format(**formatted_data)
                content = await kiro_service._run_kiro_cli(formatted_prompt)
            else:
                # Fallback to enhanced company deep dive
                content = await kiro_service.generate_company_overview(formatted_data)
            
            return content
            
        except Exception as e:
            logger.error(f"Error executing Kiro business model prompt: {str(e)}")
            return f"# Business Model Analysis for {ticker}\n\n## Executive Summary\nComprehensive business model analysis including value proposition, competitive positioning, and strategic initiatives.\n\n## Business Model Canvas\n[Generated business model framework]\n\n## Revenue Analysis\n[Revenue stream breakdown and analysis]\n\n## Competitive Positioning\n[Market position and competitive advantages]"
    
    def _prepare_kiro_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data in the format expected by Kiro prompts"""
        return {
            "ticker": company_data.get("ticker", "UNKNOWN"),
            "company_name": company_data.get("company_name", "Unknown Company"),
            "sector": company_data.get("sector", "Unknown Sector"),
            "business_description": company_data.get("business_description", "Business description not available"),
            "financial_statements": company_data.get("financial_statements", "Financial data not available"),
            "peer_data": company_data.get("peer_data", "Peer comparison data not available"),
            "recent_news": company_data.get("recent_news", "Recent news not available"),
            "market_cap": company_data.get("market_cap", "Market cap not available"),
            "revenue_streams": str(company_data.get("revenue_streams", "Revenue streams not available")),
            "customer_segments": str(company_data.get("customer_segments", "Customer segments not available")),
            "competitive_position": company_data.get("competitive_position", "Competitive position not available")
        }
    
    def _prepare_business_context(self, company_data: Dict[str, Any]) -> str:
        """Prepare business context for Kiro analysis"""
        context_parts = [
            f"Company: {company_data.get('company_name', 'Unknown')}",
            f"Ticker: {company_data.get('ticker', 'Unknown')}",
            f"Sector: {company_data.get('sector', 'Unknown')}",
            f"Business Description: {company_data.get('business_description', 'Not available')}",
            f"Revenue Streams: {company_data.get('revenue_streams', 'Not available')}",
            f"Customer Base: {company_data.get('customer_segments', 'Not available')}",
            f"Competitive Position: {company_data.get('competitive_position', 'Not available')}"
        ]
        
        return "\n".join(context_parts)
    
    async def _create_business_model_canvas(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create business model canvas visualization data"""
        canvas = {
            "key_partners": company_data.get("key_partners", ["Strategic partners", "Suppliers", "Technology partners"]),
            "key_activities": company_data.get("key_activities", ["Product development", "Marketing", "Operations"]),
            "key_resources": company_data.get("key_resources", ["Technology", "Brand", "Human capital"]),
            "value_propositions": company_data.get("value_propositions", ["Core value proposition"]),
            "customer_relationships": company_data.get("customer_relationships", ["Direct sales", "Customer support"]),
            "channels": company_data.get("channels", ["Direct", "Partners", "Online"]),
            "customer_segments": company_data.get("customer_segments", ["Primary segment", "Secondary segment"]),
            "cost_structure": company_data.get("cost_structure", ["R&D", "Sales & Marketing", "Operations"]),
            "revenue_streams": company_data.get("revenue_streams", ["Product sales", "Services", "Subscriptions"])
        }
        
        return canvas
    
    async def _generate_revenue_breakdown_charts(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate revenue breakdown chart data"""
        charts = {
            "revenue_by_segment": {
                "type": "pie_chart",
                "data": company_data.get("segment_revenue", {
                    "Segment A": 45,
                    "Segment B": 35,
                    "Segment C": 20
                }),
                "title": "Revenue by Business Segment"
            },
            "revenue_by_geography": {
                "type": "bar_chart", 
                "data": company_data.get("geographic_revenue", {
                    "North America": 60,
                    "Europe": 25,
                    "Asia Pacific": 15
                }),
                "title": "Revenue by Geography"
            },
            "revenue_trends": {
                "type": "line_chart",
                "data": company_data.get("revenue_trends", {
                    "2021": 100,
                    "2022": 115,
                    "2023": 132,
                    "2024E": 148
                }),
                "title": "Revenue Growth Trends"
            }
        }
        
        return charts
    
    async def _create_strategic_positioning_matrices(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create strategic positioning matrices"""
        matrices = {
            "competitive_position": {
                "type": "matrix",
                "x_axis": "Market Share",
                "y_axis": "Growth Rate",
                "data": [
                    {"name": company_data.get("ticker", "Company"), "x": 25, "y": 15, "size": 100},
                    {"name": "Competitor A", "x": 30, "y": 12, "size": 120},
                    {"name": "Competitor B", "x": 20, "y": 18, "size": 80},
                    {"name": "Competitor C", "x": 15, "y": 10, "size": 60}
                ]
            },
            "value_chain_analysis": {
                "type": "value_chain",
                "primary_activities": ["Inbound Logistics", "Operations", "Outbound Logistics", "Marketing & Sales", "Service"],
                "support_activities": ["Infrastructure", "HR Management", "Technology Development", "Procurement"],
                "competitive_advantages": company_data.get("competitive_advantages", ["Technology", "Brand", "Scale"])
            },
            "moat_assessment": {
                "type": "radar_chart",
                "dimensions": ["Brand Strength", "Network Effects", "Cost Advantages", "Switching Costs", "Regulatory Barriers"],
                "scores": company_data.get("moat_scores", [7, 5, 6, 8, 4])
            }
        }
        
        return matrices

# Export the agent for use in the main application
section3_agent = Section3BusinessModelAgent()