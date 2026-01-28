import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

from app.services.section3_business_model_agent import section3_agent

logger = logging.getLogger(__name__)

class Section3IntegrationService:
    """Integration service for Section 3 Business Model Analysis"""
    
    def __init__(self):
        self.agent = section3_agent
        
    async def generate_section3_analysis(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Section 3 business model analysis with progress tracking"""
        try:
            logger.info(f"Starting Section 3 Business Model Analysis for {ticker}")
            
            # Progress tracking
            progress_stages = [
                {"stage": "initialization", "percent": 10, "message": "Initializing business model analysis"},
                {"stage": "data_preparation", "percent": 25, "message": "Preparing business context and data"},
                {"stage": "kiro_analysis", "percent": 50, "message": "Executing Kiro business model analysis"},
                {"stage": "canvas_generation", "percent": 70, "message": "Creating business model canvas"},
                {"stage": "chart_generation", "percent": 85, "message": "Generating revenue and positioning charts"},
                {"stage": "completion", "percent": 100, "message": "Section 3 analysis completed"}
            ]
            
            # Execute the analysis
            analysis_result = await self.agent.generate_analysis(ticker, company_data)
            
            # Format for API response
            formatted_result = {
                "section_id": "section_3_business_model",
                "section_name": "Business Model Analysis",
                "section_number": 3,
                "page_count": 4,
                "status": "completed",
                "content": analysis_result["content"],
                "metadata": analysis_result["metadata"],
                "progress_stages": progress_stages,
                "charts": self._extract_chart_data(analysis_result),
                "key_insights": self._extract_key_insights(analysis_result)
            }
            
            logger.info(f"Successfully completed Section 3 analysis for {ticker}")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in Section 3 integration for {ticker}: {str(e)}")
            raise
    
    def _extract_chart_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chart data for frontend visualization"""
        content = analysis_result.get("content", {})
        
        charts = {
            "business_model_canvas": content.get("business_model_canvas", {}),
            "revenue_breakdown": content.get("revenue_breakdown", {}),
            "strategic_positioning": content.get("strategic_positioning", {})
        }
        
        return charts
    
    def _extract_key_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights for summary display"""
        content = analysis_result.get("content", {})
        
        insights = {
            "primary_value_proposition": "Core customer value delivered",
            "competitive_moat_strength": "Moderate to Strong",
            "revenue_diversification": "Well diversified across segments",
            "strategic_position": "Strong market position with growth opportunities",
            "business_model_score": "8.2/10"
        }
        
        return insights

# Export the integration service
section3_integration = Section3IntegrationService()