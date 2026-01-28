"""
Section 2 Agent - Financial Analysis Generator
Production-ready agent using real Kiro CLI integration for comprehensive financial analysis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class FinancialMetrics:
    """Key financial metrics"""
    revenue_growth_3yr: float
    profit_margin_trend: float
    roe_current: float
    debt_to_equity: float
    cash_flow_strength: str

class Section2FinancialAnalysisAgent(KiroAgentBase):
    """Production-ready Section 2 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section2_FinancialAnalysis",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=120)
        )
        
        # Define prompt configurations for financial analysis
        self.prompt_configs = [
            {
                'name': 'financial_analysis',
                'prompt_file': 'enhanced-financial-analysis.md',
                'custom_instructions': None
            },
            {
                'name': 'key_metrics',
                'prompt_file': 'financial-analysis-key-metrics.md',
                'custom_instructions': 'Focus on 3-year historical trends and peer comparisons'
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial analysis using Kiro CLI"""
        
        logger.info(f"Section 2: Starting financial analysis generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            financial_result = results.get('financial_analysis')
            metrics_result = results.get('key_metrics')
            
            if not financial_result or not self.validate_result(financial_result, min_length=800):
                raise RuntimeError("Failed to generate valid financial analysis")
            
            # Combine results
            combined_content = self._combine_analysis_results(financial_result, metrics_result)
            
            # Extract financial metrics
            metrics = await self._extract_financial_metrics(combined_content)
            
            # Structure the final output
            output = {
                'section': 'financial_analysis',
                'ticker': ticker,
                'content': combined_content,
                'metrics': metrics,
                'execution_time': financial_result.execution_time + (metrics_result.execution_time if metrics_result else 0),
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 2: Successfully generated financial analysis for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 2: Failed to generate financial analysis for {ticker}: {e}")
            return {
                'section': 'financial_analysis',
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
        
        financial_data = context_data.get('financial_data', {})
        company_info = context_data.get('company_info', {})
        historical_data = context_data.get('historical_data', {})
        
        # Prepare comprehensive financial context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Current financial metrics
            'revenue_ttm': financial_data.get('revenue_ttm', 0),
            'revenue_growth': financial_data.get('revenue_growth', 0),
            'gross_profit': financial_data.get('gross_profit', 0),
            'operating_income': financial_data.get('operating_income', 0),
            'net_income_ttm': financial_data.get('net_income_ttm', 0),
            'eps_ttm': financial_data.get('eps_ttm', 0),
            'profit_margin': financial_data.get('profit_margin', 0),
            'operating_margin': financial_data.get('operating_margin', 0),
            'roe': financial_data.get('roe', 0),
            'roa': financial_data.get('roa', 0),
            'debt_to_equity': financial_data.get('debt_to_equity', 0),
            'current_ratio': financial_data.get('current_ratio', 0),
            'free_cash_flow': financial_data.get('free_cash_flow', 0),
            
            # Historical data (3-year trends)
            'revenue_3yr_cagr': historical_data.get('revenue_3yr_cagr', 0),
            'earnings_3yr_cagr': historical_data.get('earnings_3yr_cagr', 0),
            'historical_margins': json.dumps(historical_data.get('margins_trend', {})),
            'historical_ratios': json.dumps(historical_data.get('ratios_trend', {})),
            
            # Peer comparison data
            'peer_revenue_growth': context_data.get('peer_data', {}).get('avg_revenue_growth', 0),
            'peer_profit_margin': context_data.get('peer_data', {}).get('avg_profit_margin', 0),
            'peer_roe': context_data.get('peer_data', {}).get('avg_roe', 0),
            
            # RAG context
            'rag_financial_statements': context_data.get('rag_context', {}).get('financial_statements', ''),
            'rag_earnings_transcripts': context_data.get('rag_context', {}).get('earnings_transcripts', ''),
            'rag_analyst_reports': context_data.get('rag_context', {}).get('analyst_reports', ''),
            
            # Additional context
            'quarterly_trends': json.dumps(context_data.get('quarterly_data', {})),
            'segment_performance': json.dumps(context_data.get('segment_data', {}))
        }
        
        return kiro_context
    
    def _combine_analysis_results(self, 
                                  financial_result: KiroExecutionResult, 
                                  metrics_result: Optional[KiroExecutionResult]) -> str:
        """Combine financial analysis and metrics results"""
        
        combined = financial_result.content
        
        if metrics_result and metrics_result.success:
            combined += "\n\n## Key Financial Metrics Analysis\n\n"
            combined += metrics_result.content
        
        return combined
    
    async def _extract_financial_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key financial metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract revenue growth
            rev_growth_match = re.search(r'Revenue Growth.*?([0-9.]+)%', content, re.IGNORECASE)
            if rev_growth_match:
                metrics['revenue_growth_3yr'] = float(rev_growth_match.group(1))
            
            # Extract profit margin
            margin_match = re.search(r'Profit Margin.*?([0-9.]+)%', content, re.IGNORECASE)
            if margin_match:
                metrics['profit_margin_trend'] = float(margin_match.group(1))
            
            # Extract ROE
            roe_match = re.search(r'ROE.*?([0-9.]+)%', content, re.IGNORECASE)
            if roe_match:
                metrics['roe_current'] = float(roe_match.group(1))
            
            # Extract debt-to-equity
            debt_match = re.search(r'Debt.*Equity.*?([0-9.]+)', content, re.IGNORECASE)
            if debt_match:
                metrics['debt_to_equity'] = float(debt_match.group(1))
            
            # Determine cash flow strength
            if 'strong cash flow' in content.lower():
                metrics['cash_flow_strength'] = 'Strong'
            elif 'weak cash flow' in content.lower():
                metrics['cash_flow_strength'] = 'Weak'
            else:
                metrics['cash_flow_strength'] = 'Moderate'
                
        except Exception as e:
            logger.warning(f"Failed to extract financial metrics: {e}")
        
        return metrics

# Singleton instance
section2_agent = Section2FinancialAnalysisAgent()

# Convenience function for FastAPI
async def generate_financial_analysis(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate financial analysis using Section 2 agent"""
    return await section2_agent.generate_content(ticker, context_data)