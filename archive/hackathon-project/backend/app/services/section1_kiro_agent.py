"""
Section 1 Agent - Executive Summary Generator
Production-ready agent using real Kiro CLI integration for institutional-grade executive summaries
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class ExecutiveSummaryMetrics:
    """Key metrics for executive summary"""
    recommendation: str
    price_target: float
    current_price: float
    upside_potential: float
    confidence_level: str
    timeframe_months: int

class Section1ExecutiveSummaryAgent(KiroAgentBase):
    """Production-ready Section 1 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section1_ExecutiveSummary",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=90)
        )
        
        # Define prompt configurations for this section
        self.prompt_configs = [
            {
                'name': 'executive_summary',
                'prompt_file': 'enhanced-executive-summary.md',
                'custom_instructions': None
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary using Kiro CLI"""
        
        logger.info(f"Section 1: Starting executive summary generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            executive_summary_result = results.get('executive_summary')
            
            if not executive_summary_result or not self.validate_result(executive_summary_result, min_length=500):
                raise RuntimeError("Failed to generate valid executive summary")
            
            # Extract key metrics from the generated content
            metrics = await self._extract_metrics(executive_summary_result.content)
            
            # Structure the final output
            output = {
                'section': 'executive_summary',
                'ticker': ticker,
                'content': executive_summary_result.content,
                'metrics': metrics,
                'execution_time': executive_summary_result.execution_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 1: Successfully generated executive summary for {ticker} in {executive_summary_result.execution_time:.2f}s")
            return output
            
        except Exception as e:
            logger.error(f"Section 1: Failed to generate executive summary for {ticker}: {e}")
            return {
                'section': 'executive_summary',
                'ticker': ticker,
                'content': '',
                'metrics': {},
                'execution_time': 0,
                'success': False,
                'error': str(e),
                'generated_at': asyncio.get_event_loop().time()
            }
    
    async def _prepare_kiro_context(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context data for Kiro prompts"""
        
        # Extract financial data
        financial_data = context_data.get('financial_data', {})
        company_info = context_data.get('company_info', {})
        market_data = context_data.get('market_data', {})
        
        # Prepare comprehensive context for Kiro
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            'current_price': market_data.get('current_price', 0),
            'market_cap': financial_data.get('market_cap', 0),
            'revenue_ttm': financial_data.get('revenue_ttm', 0),
            'net_income_ttm': financial_data.get('net_income_ttm', 0),
            'eps_ttm': financial_data.get('eps_ttm', 0),
            'pe_ratio': financial_data.get('pe_ratio', 0),
            'revenue_growth': financial_data.get('revenue_growth', 0),
            'profit_margin': financial_data.get('profit_margin', 0),
            'roe': financial_data.get('roe', 0),
            'debt_to_equity': financial_data.get('debt_to_equity', 0),
            'business_summary': company_info.get('longBusinessSummary', ''),
            'rag_financial_data': context_data.get('rag_context', {}).get('financial_data', ''),
            'rag_sec_filings': context_data.get('rag_context', {}).get('sec_filings', ''),
            'rag_earnings_calls': context_data.get('rag_context', {}).get('earnings_calls', ''),
            'web_market_data': context_data.get('web_research', {}).get('market_data', ''),
            'web_news_sentiment': context_data.get('web_research', {}).get('news_sentiment', ''),
            'web_peer_analysis': context_data.get('web_research', {}).get('peer_analysis', ''),
            'api_company_profile': json.dumps(company_info, indent=2),
            'api_financial_metrics': json.dumps(financial_data, indent=2)
        }
        
        return kiro_context
    
    async def _extract_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key metrics from generated content"""
        
        metrics = {}
        
        try:
            # Use simple regex patterns to extract key metrics
            import re
            
            # Extract recommendation
            rec_match = re.search(r'Rating:\s*([A-Z]+)', content)
            if rec_match:
                metrics['recommendation'] = rec_match.group(1)
            
            # Extract price target
            target_match = re.search(r'Price Target:\s*\$?([0-9,.]+)', content)
            if target_match:
                metrics['price_target'] = float(target_match.group(1).replace(',', ''))
            
            # Extract current price
            price_match = re.search(r'Current:\s*\$?([0-9,.]+)', content)
            if price_match:
                metrics['current_price'] = float(price_match.group(1).replace(',', ''))
            
            # Extract upside
            upside_match = re.search(r'Upside:\s*([0-9.]+)%', content)
            if upside_match:
                metrics['upside_potential'] = float(upside_match.group(1))
            
            # Extract confidence
            conf_match = re.search(r'Confidence:\s*([A-Za-z]+)', content)
            if conf_match:
                metrics['confidence_level'] = conf_match.group(1)
            
        except Exception as e:
            logger.warning(f"Failed to extract metrics from content: {e}")
        
        return metrics

# Singleton instance for use in FastAPI endpoints
section1_agent = Section1ExecutiveSummaryAgent()

# Convenience function for FastAPI
async def generate_executive_summary(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate executive summary using Section 1 agent"""
    return await section1_agent.generate_content(ticker, context_data)