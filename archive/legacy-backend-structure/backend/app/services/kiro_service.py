import asyncio
import json
import logging
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings
from app.services.kiro_prompt_service import kiro_service

logger = logging.getLogger(__name__)

class KiroService:
    """Service for executing Kiro CLI commands for financial analysis"""
    
    @staticmethod
    async def generate_comprehensive_analysis(ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all specialized prompts for comprehensive report generation"""
        try:
            logger.info(f"Starting comprehensive analysis for {ticker}")
            
            # Use the new specialized prompt service
            report = await kiro_service.generate_full_report(ticker, company_data)
            
            # Format for backward compatibility
            results = {
                "company_overview": {
                    "prompt_key": "company_overview",
                    "content": report["page_1_company_overview"],
                    "metadata": {"page": 1, "section": "Company Overview & Investment Thesis"}
                },
                "financial_analysis": {
                    "prompt_key": "financial_analysis", 
                    "content": report["page_2_financial_analysis"],
                    "metadata": {"page": 2, "section": "Financial Analysis & Key Metrics"}
                },
                "valuation_analysis": {
                    "prompt_key": "valuation_analysis",
                    "content": report["page_3_valuation_analysis"], 
                    "metadata": {"page": 3, "section": "Valuation Analysis & Price Target"}
                },
                "risk_assessment": {
                    "prompt_key": "risk_assessment",
                    "content": report["pages_4_5_risk_assessment"],
                    "metadata": {"pages": "4-5", "section": "Risk Assessment & Summary"}
                }
            }
            
            logger.info(f"Successfully completed comprehensive analysis for {ticker}")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {ticker}: {str(e)}")
            raise
    
    @staticmethod
    async def execute_prompt(prompt_key: str, ticker: str, context: str = "") -> Dict[str, Any]:
        """Execute a single specialized prompt (backward compatibility)"""
        try:
            # Map old prompt keys to new sections
            section_mapping = {
                "company_overview": "company_overview",
                "financial_analysis": "financial_analysis",
                "valuation_dcf": "valuation_analysis", 
                "peer_comparison": "financial_analysis",  # Included in financial analysis
                "risk_assessment": "risk_assessment",
                "executive_summary": "risk_assessment"  # Included in risk assessment
            }
            
            section = section_mapping.get(prompt_key, "company_overview")
            
            # Prepare data (this would normally come from data service)
            company_data = {
                "ticker": ticker,
                "company_name": f"{ticker} Inc.",  # Placeholder
                "sector": "Unknown",  # Would be fetched from data service
                "market_cap": "Unknown",
                "current_price": "Unknown",
                "business_description": context or "Business description not available",
                "recent_news": "Recent news not available",
                "financial_statements": "Financial data not available",
                "historical_data": "Historical data not available",
                "peer_data": "Peer data not available",
                "industry_averages": "Industry averages not available",
                "quarterly_results": "Quarterly results not available",
                "guidance": "Guidance not available"
            }
            
            # Execute the appropriate section
            from app.services.kiro_prompt_service import generate_report_section
            content = await generate_report_section(section, company_data)
            
            return {
                "prompt_key": prompt_key,
                "content": content,
                "metadata": {"section": section, "ticker": ticker}
            }
            
        except Exception as e:
            logger.error(f"Error executing prompt {prompt_key}: {str(e)}")
            raise