"""
Section 4 Agent - Valuation Analysis Generator
Production-ready agent using real Kiro CLI integration for comprehensive valuation analysis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class ValuationMetrics:
    """Key valuation metrics"""
    dcf_fair_value: float
    peer_multiple_value: float
    price_target: float
    valuation_method: str
    confidence_level: str

class Section4ValuationAnalysisAgent(KiroAgentBase):
    """Production-ready Section 4 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section4_ValuationAnalysis",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=180)
        )
        
        # Define prompt configurations for valuation analysis
        self.prompt_configs = [
            {
                'name': 'valuation_analysis',
                'prompt_file': 'enhanced-valuation-analysis.md',
                'custom_instructions': None
            },
            {
                'name': 'dcf_model',
                'prompt_file': 'dcf-model-analysis.md',
                'custom_instructions': 'Focus on 5-year DCF model with sensitivity analysis'
            },
            {
                'name': 'peer_comparison',
                'prompt_file': 'peer-comparison-analysis.md',
                'custom_instructions': 'Include EV/Revenue, P/E, and P/B multiples'
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate valuation analysis using Kiro CLI"""
        
        logger.info(f"Section 4: Starting valuation analysis generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            valuation_result = results.get('valuation_analysis')
            dcf_result = results.get('dcf_model')
            peer_result = results.get('peer_comparison')
            
            if not valuation_result or not self.validate_result(valuation_result, min_length=1200):
                raise RuntimeError("Failed to generate valid valuation analysis")
            
            # Combine results
            combined_content = self._combine_valuation_analysis(valuation_result, dcf_result, peer_result)
            
            # Extract valuation metrics
            metrics = await self._extract_valuation_metrics(combined_content)
            
            # Structure the final output
            total_time = valuation_result.execution_time
            total_time += dcf_result.execution_time if dcf_result else 0
            total_time += peer_result.execution_time if peer_result else 0
            
            output = {
                'section': 'valuation_analysis',
                'ticker': ticker,
                'content': combined_content,
                'metrics': metrics,
                'execution_time': total_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 4: Successfully generated valuation analysis for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 4: Failed to generate valuation analysis for {ticker}: {e}")
            return {
                'section': 'valuation_analysis',
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
        market_data = context_data.get('market_data', {})
        
        # Prepare comprehensive valuation context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Current market data
            'current_price': market_data.get('current_price', 0),
            'market_cap': financial_data.get('market_cap', 0),
            'enterprise_value': financial_data.get('enterprise_value', 0),
            'shares_outstanding': financial_data.get('shares_outstanding', 0),
            
            # Financial metrics for valuation
            'revenue_ttm': financial_data.get('revenue_ttm', 0),
            'ebitda_ttm': financial_data.get('ebitda_ttm', 0),
            'net_income_ttm': financial_data.get('net_income_ttm', 0),
            'free_cash_flow': financial_data.get('free_cash_flow', 0),
            'book_value': financial_data.get('book_value', 0),
            
            # Growth projections
            'revenue_growth_1yr': context_data.get('projections', {}).get('revenue_growth_1yr', 0),
            'revenue_growth_3yr': context_data.get('projections', {}).get('revenue_growth_3yr', 0),
            'earnings_growth_1yr': context_data.get('projections', {}).get('earnings_growth_1yr', 0),
            'earnings_growth_3yr': context_data.get('projections', {}).get('earnings_growth_3yr', 0),
            
            # Valuation multiples
            'pe_ratio': financial_data.get('pe_ratio', 0),
            'pb_ratio': financial_data.get('pb_ratio', 0),
            'ps_ratio': financial_data.get('ps_ratio', 0),
            'ev_revenue': financial_data.get('ev_revenue', 0),
            'ev_ebitda': financial_data.get('ev_ebitda', 0),
            
            # Peer comparison data
            'peer_pe_avg': context_data.get('peer_data', {}).get('avg_pe_ratio', 0),
            'peer_pb_avg': context_data.get('peer_data', {}).get('avg_pb_ratio', 0),
            'peer_ps_avg': context_data.get('peer_data', {}).get('avg_ps_ratio', 0),
            'peer_ev_revenue_avg': context_data.get('peer_data', {}).get('avg_ev_revenue', 0),
            'peer_ev_ebitda_avg': context_data.get('peer_data', {}).get('avg_ev_ebitda', 0),
            
            # DCF model inputs
            'wacc': context_data.get('dcf_inputs', {}).get('wacc', 0.10),
            'terminal_growth_rate': context_data.get('dcf_inputs', {}).get('terminal_growth', 0.025),
            'tax_rate': context_data.get('dcf_inputs', {}).get('tax_rate', 0.25),
            'capex_as_pct_revenue': context_data.get('dcf_inputs', {}).get('capex_pct', 0.03),
            
            # Historical data for trends
            'historical_multiples': json.dumps(context_data.get('historical_multiples', {})),
            'historical_growth': json.dumps(context_data.get('historical_growth', {})),
            
            # Analyst estimates
            'analyst_price_targets': json.dumps(context_data.get('analyst_data', {}).get('price_targets', {})),
            'analyst_estimates': json.dumps(context_data.get('analyst_data', {}).get('estimates', {})),
            
            # RAG context
            'rag_valuation_reports': context_data.get('rag_context', {}).get('valuation_reports', ''),
            'rag_dcf_models': context_data.get('rag_context', {}).get('dcf_models', ''),
            'rag_peer_analysis': context_data.get('rag_context', {}).get('peer_analysis', ''),
            
            # Risk factors for valuation
            'beta': financial_data.get('beta', 1.0),
            'volatility': market_data.get('volatility', 0),
            'business_risk': context_data.get('risk_data', {}).get('business_risk', 'Medium'),
            'financial_risk': context_data.get('risk_data', {}).get('financial_risk', 'Medium')
        }
        
        return kiro_context
    
    def _combine_valuation_analysis(self, 
                                    valuation_result: KiroExecutionResult,
                                    dcf_result: Optional[KiroExecutionResult],
                                    peer_result: Optional[KiroExecutionResult]) -> str:
        """Combine valuation analysis results"""
        
        combined = valuation_result.content
        
        if dcf_result and dcf_result.success:
            combined += "\n\n## DCF Model Analysis\n\n"
            combined += dcf_result.content
        
        if peer_result and peer_result.success:
            combined += "\n\n## Peer Comparison Analysis\n\n"
            combined += peer_result.content
        
        return combined
    
    async def _extract_valuation_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key valuation metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract DCF fair value
            dcf_match = re.search(r'DCF.*?Fair Value.*?\$?([0-9,.]+)', content, re.IGNORECASE)
            if dcf_match:
                metrics['dcf_fair_value'] = float(dcf_match.group(1).replace(',', ''))
            
            # Extract peer multiple value
            peer_match = re.search(r'Peer.*?Multiple.*?Value.*?\$?([0-9,.]+)', content, re.IGNORECASE)
            if peer_match:
                metrics['peer_multiple_value'] = float(peer_match.group(1).replace(',', ''))
            
            # Extract price target
            target_match = re.search(r'Price Target.*?\$?([0-9,.]+)', content, re.IGNORECASE)
            if target_match:
                metrics['price_target'] = float(target_match.group(1).replace(',', ''))
            
            # Determine primary valuation method
            if 'dcf' in content.lower() and 'primary' in content.lower():
                metrics['valuation_method'] = 'DCF'
            elif 'multiple' in content.lower() and 'primary' in content.lower():
                metrics['valuation_method'] = 'Multiples'
            else:
                metrics['valuation_method'] = 'Blended'
            
            # Extract confidence level
            if 'high confidence' in content.lower():
                metrics['confidence_level'] = 'High'
            elif 'low confidence' in content.lower():
                metrics['confidence_level'] = 'Low'
            else:
                metrics['confidence_level'] = 'Medium'
                
        except Exception as e:
            logger.warning(f"Failed to extract valuation metrics: {e}")
        
        return metrics

# Singleton instance
section4_agent = Section4ValuationAnalysisAgent()

# Convenience function for FastAPI
async def generate_valuation_analysis(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate valuation analysis using Section 4 agent"""
    return await section4_agent.generate_content(ticker, context_data)