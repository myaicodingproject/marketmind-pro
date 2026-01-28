"""
Section 7 Agent - Investment Thesis Generator
Production-ready agent using real Kiro CLI integration for comprehensive investment thesis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class InvestmentThesisMetrics:
    """Key investment thesis metrics"""
    thesis_strength: str
    conviction_level: str
    time_horizon: str
    key_catalysts: List[str]
    investment_style: str

class Section7InvestmentThesisAgent(KiroAgentBase):
    """Production-ready Section 7 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section7_InvestmentThesis",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=120)
        )
        
        # Define prompt configurations for investment thesis
        self.prompt_configs = [
            {
                'name': 'investment_thesis',
                'prompt_file': 'company-overview-investment-thesis.md',
                'custom_instructions': 'Focus on comprehensive investment thesis with bull/bear cases'
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment thesis using Kiro CLI"""
        
        logger.info(f"Section 7: Starting investment thesis generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            thesis_result = results.get('investment_thesis')
            
            if not thesis_result or not self.validate_result(thesis_result, min_length=800):
                raise RuntimeError("Failed to generate valid investment thesis")
            
            # Extract thesis metrics
            metrics = await self._extract_thesis_metrics(thesis_result.content)
            
            # Structure the final output
            output = {
                'section': 'investment_thesis',
                'ticker': ticker,
                'content': thesis_result.content,
                'metrics': metrics,
                'execution_time': thesis_result.execution_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 7: Successfully generated investment thesis for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 7: Failed to generate investment thesis for {ticker}: {e}")
            return {
                'section': 'investment_thesis',
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
        
        # Aggregate insights from all previous sections
        financial_data = context_data.get('financial_data', {})
        company_info = context_data.get('company_info', {})
        
        # Prepare comprehensive investment thesis context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Executive summary insights
            'recommendation': context_data.get('section1_data', {}).get('recommendation', 'HOLD'),
            'price_target': context_data.get('section1_data', {}).get('price_target', 0),
            'upside_potential': context_data.get('section1_data', {}).get('upside_potential', 0),
            
            # Financial strength indicators
            'revenue_growth': financial_data.get('revenue_growth', 0),
            'profit_margin': financial_data.get('profit_margin', 0),
            'roe': financial_data.get('roe', 0),
            'debt_to_equity': financial_data.get('debt_to_equity', 0),
            'financial_strength': context_data.get('section2_data', {}).get('financial_strength', 'Medium'),
            
            # Company competitive position
            'business_model_strength': context_data.get('section3_data', {}).get('business_model_strength', 'Medium'),
            'competitive_position': context_data.get('section3_data', {}).get('competitive_position', 'Unknown'),
            'competitive_advantages': context_data.get('section3_data', {}).get('competitive_advantages', ''),
            
            # Valuation insights
            'valuation_method': context_data.get('section4_data', {}).get('valuation_method', 'Blended'),
            'dcf_fair_value': context_data.get('section4_data', {}).get('dcf_fair_value', 0),
            'peer_multiple_value': context_data.get('section4_data', {}).get('peer_multiple_value', 0),
            'valuation_attractiveness': context_data.get('section4_data', {}).get('attractiveness', 'Fair'),
            
            # Risk assessment
            'overall_risk_score': context_data.get('section5_data', {}).get('overall_risk_score', 5),
            'key_risk_factors': json.dumps(context_data.get('section5_data', {}).get('key_risk_factors', [])),
            'risk_mitigation': context_data.get('section5_data', {}).get('risk_mitigation', ''),
            
            # Market opportunity
            'market_size_billions': context_data.get('section6_data', {}).get('market_size_billions', 0),
            'market_growth_rate': context_data.get('section6_data', {}).get('market_growth_rate', 0),
            'market_position': context_data.get('section6_data', {}).get('market_position', 'Unknown'),
            'market_attractiveness': context_data.get('section6_data', {}).get('market_attractiveness_score', 5),
            
            # Investment catalysts
            'upcoming_catalysts': json.dumps(context_data.get('catalysts_data', {})),
            'earnings_catalysts': context_data.get('earnings_data', {}).get('catalysts', ''),
            'product_catalysts': context_data.get('product_data', {}).get('catalysts', ''),
            'strategic_catalysts': context_data.get('strategic_data', {}).get('catalysts', ''),
            
            # Bull case factors
            'growth_opportunities': json.dumps(context_data.get('growth_opportunities', {})),
            'market_expansion': context_data.get('expansion_data', {}).get('opportunities', ''),
            'innovation_pipeline': context_data.get('innovation_data', {}).get('pipeline', ''),
            'operational_improvements': context_data.get('operational_data', {}).get('improvements', ''),
            
            # Bear case factors
            'key_challenges': json.dumps(context_data.get('challenges_data', {})),
            'competitive_threats': context_data.get('competitive_data', {}).get('threats', ''),
            'market_headwinds': context_data.get('market_data', {}).get('headwinds', ''),
            'execution_risks': context_data.get('execution_data', {}).get('risks', ''),
            
            # Management and governance
            'management_quality': context_data.get('management_data', {}).get('quality_score', 50),
            'strategic_vision': context_data.get('management_data', {}).get('vision', ''),
            'execution_track_record': context_data.get('management_data', {}).get('track_record', ''),
            
            # ESG considerations
            'esg_score': context_data.get('esg_data', {}).get('overall_score', 50),
            'esg_investment_impact': context_data.get('esg_data', {}).get('investment_impact', ''),
            
            # Peer comparison
            'peer_performance': json.dumps(context_data.get('peer_data', {})),
            'relative_valuation': context_data.get('peer_data', {}).get('relative_valuation', 'Fair'),
            
            # RAG context
            'rag_investment_research': context_data.get('rag_context', {}).get('investment_research', ''),
            'rag_analyst_opinions': context_data.get('rag_context', {}).get('analyst_opinions', ''),
            'rag_management_interviews': context_data.get('rag_context', {}).get('management_interviews', ''),
            
            # Time horizon considerations
            'short_term_outlook': context_data.get('outlook_data', {}).get('short_term', ''),
            'medium_term_outlook': context_data.get('outlook_data', {}).get('medium_term', ''),
            'long_term_outlook': context_data.get('outlook_data', {}).get('long_term', ''),
            
            # Portfolio fit
            'investment_style_fit': context_data.get('portfolio_data', {}).get('style_fit', ''),
            'diversification_benefit': context_data.get('portfolio_data', {}).get('diversification', ''),
            'risk_return_profile': context_data.get('portfolio_data', {}).get('risk_return', '')
        }
        
        return kiro_context
    
    async def _extract_thesis_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key investment thesis metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract thesis strength
            if 'strong thesis' in content.lower() or 'compelling case' in content.lower():
                metrics['thesis_strength'] = 'Strong'
            elif 'weak thesis' in content.lower() or 'limited case' in content.lower():
                metrics['thesis_strength'] = 'Weak'
            else:
                metrics['thesis_strength'] = 'Moderate'
            
            # Extract conviction level
            if 'high conviction' in content.lower():
                metrics['conviction_level'] = 'High'
            elif 'low conviction' in content.lower():
                metrics['conviction_level'] = 'Low'
            else:
                metrics['conviction_level'] = 'Medium'
            
            # Extract time horizon
            if 'long-term' in content.lower() or 'long term' in content.lower():
                metrics['time_horizon'] = 'Long-term'
            elif 'short-term' in content.lower() or 'short term' in content.lower():
                metrics['time_horizon'] = 'Short-term'
            else:
                metrics['time_horizon'] = 'Medium-term'
            
            # Extract key catalysts
            catalysts = []
            catalyst_patterns = [
                r'Catalyst.*?:\s*([^.]+)',
                r'Key Driver.*?:\s*([^.]+)',
                r'Opportunity.*?:\s*([^.]+)'
            ]
            
            for pattern in catalyst_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                catalysts.extend(matches)
            
            metrics['key_catalysts'] = [catalyst.strip() for catalyst in catalysts[:5]]
            
            # Determine investment style
            if 'growth' in content.lower() and 'value' in content.lower():
                metrics['investment_style'] = 'GARP'  # Growth at Reasonable Price
            elif 'growth' in content.lower():
                metrics['investment_style'] = 'Growth'
            elif 'value' in content.lower() or 'undervalued' in content.lower():
                metrics['investment_style'] = 'Value'
            elif 'dividend' in content.lower() or 'income' in content.lower():
                metrics['investment_style'] = 'Income'
            else:
                metrics['investment_style'] = 'Blend'
                
        except Exception as e:
            logger.warning(f"Failed to extract thesis metrics: {e}")
            # Provide defaults
            metrics.setdefault('thesis_strength', 'Moderate')
            metrics.setdefault('conviction_level', 'Medium')
            metrics.setdefault('time_horizon', 'Medium-term')
            metrics.setdefault('key_catalysts', [])
            metrics.setdefault('investment_style', 'Blend')
        
        return metrics

# Singleton instance
section7_agent = Section7InvestmentThesisAgent()

# Convenience function for FastAPI
async def generate_investment_thesis(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate investment thesis using Section 7 agent"""
    return await section7_agent.generate_content(ticker, context_data)