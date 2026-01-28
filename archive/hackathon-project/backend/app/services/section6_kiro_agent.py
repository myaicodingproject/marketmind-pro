"""
Section 6 Agent - Market Analysis Generator
Production-ready agent using real Kiro CLI integration for comprehensive market analysis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class MarketAnalysisMetrics:
    """Key market analysis metrics"""
    market_size_billions: float
    market_growth_rate: float
    market_position: str
    competitive_intensity: str
    market_attractiveness_score: int

class Section6MarketAnalysisAgent(KiroAgentBase):
    """Production-ready Section 6 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section6_MarketAnalysis",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=150)
        )
        
        # Define prompt configurations for market analysis
        self.prompt_configs = [
            {
                'name': 'market_analysis',
                'prompt_file': 'section6-market-size-growth-analysis.md',
                'custom_instructions': None
            },
            {
                'name': 'competitive_analysis',
                'prompt_file': 'competitive-positioning-analysis.md',
                'custom_instructions': 'Focus on Porter\'s Five Forces and competitive dynamics'
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market analysis using Kiro CLI"""
        
        logger.info(f"Section 6: Starting market analysis generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            market_result = results.get('market_analysis')
            competitive_result = results.get('competitive_analysis')
            
            if not market_result or not self.validate_result(market_result, min_length=1000):
                raise RuntimeError("Failed to generate valid market analysis")
            
            # Combine results
            combined_content = self._combine_market_analysis(market_result, competitive_result)
            
            # Extract market metrics
            metrics = await self._extract_market_metrics(combined_content)
            
            # Structure the final output
            total_time = market_result.execution_time
            total_time += competitive_result.execution_time if competitive_result else 0
            
            output = {
                'section': 'market_analysis',
                'ticker': ticker,
                'content': combined_content,
                'metrics': metrics,
                'execution_time': total_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 6: Successfully generated market analysis for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 6: Failed to generate market analysis for {ticker}: {e}")
            return {
                'section': 'market_analysis',
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
        
        company_info = context_data.get('company_info', {})
        market_data = context_data.get('market_data', {})
        industry_data = context_data.get('industry_data', {})
        
        # Prepare comprehensive market context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Market size and growth
            'total_addressable_market': market_data.get('tam_billions', 0),
            'serviceable_addressable_market': market_data.get('sam_billions', 0),
            'market_growth_rate': market_data.get('growth_rate', 0),
            'market_maturity': market_data.get('maturity_stage', 'Unknown'),
            
            # Company market position
            'market_share': market_data.get('market_share', 0),
            'market_rank': market_data.get('market_rank', 0),
            'competitive_position': market_data.get('competitive_position', 'Unknown'),
            
            # Industry dynamics
            'industry_concentration': industry_data.get('concentration_ratio', 0),
            'barriers_to_entry': industry_data.get('barriers_to_entry', 'Medium'),
            'supplier_power': industry_data.get('supplier_power', 'Medium'),
            'buyer_power': industry_data.get('buyer_power', 'Medium'),
            'threat_of_substitutes': industry_data.get('threat_substitutes', 'Medium'),
            'competitive_rivalry': industry_data.get('competitive_rivalry', 'Medium'),
            
            # Key competitors
            'main_competitors': json.dumps(context_data.get('competitors_data', {})),
            'competitive_advantages': context_data.get('competitive_data', {}).get('advantages', ''),
            'competitive_disadvantages': context_data.get('competitive_data', {}).get('disadvantages', ''),
            
            # Market trends and drivers
            'key_market_trends': json.dumps(context_data.get('market_trends', {})),
            'growth_drivers': json.dumps(context_data.get('growth_drivers', {})),
            'market_headwinds': json.dumps(context_data.get('market_headwinds', {})),
            
            # Technology and innovation
            'technology_trends': context_data.get('tech_data', {}).get('trends', ''),
            'innovation_cycle': context_data.get('tech_data', {}).get('innovation_cycle', 'Unknown'),
            'rd_intensity': context_data.get('tech_data', {}).get('rd_intensity', 0),
            
            # Regulatory environment
            'regulatory_environment': context_data.get('regulatory_data', {}).get('environment', ''),
            'regulatory_changes': context_data.get('regulatory_data', {}).get('recent_changes', ''),
            'compliance_requirements': context_data.get('regulatory_data', {}).get('requirements', ''),
            
            # Geographic markets
            'geographic_presence': json.dumps(context_data.get('geographic_data', {})),
            'international_expansion': context_data.get('expansion_data', {}).get('international', ''),
            'emerging_markets_exposure': context_data.get('geographic_data', {}).get('emerging_markets', 0),
            
            # Customer analysis
            'customer_segments': json.dumps(context_data.get('customer_data', {})),
            'customer_loyalty': context_data.get('customer_data', {}).get('loyalty_score', 50),
            'customer_acquisition_cost': context_data.get('customer_data', {}).get('cac', 0),
            'customer_lifetime_value': context_data.get('customer_data', {}).get('clv', 0),
            
            # RAG context
            'rag_industry_reports': context_data.get('rag_context', {}).get('industry_reports', ''),
            'rag_market_research': context_data.get('rag_context', {}).get('market_research', ''),
            'rag_competitive_intelligence': context_data.get('rag_context', {}).get('competitive_intelligence', ''),
            
            # Economic factors
            'economic_sensitivity': industry_data.get('economic_sensitivity', 'Medium'),
            'cyclicality': industry_data.get('cyclicality', 'Medium'),
            'interest_rate_sensitivity': industry_data.get('interest_sensitivity', 'Medium'),
            
            # ESG and sustainability trends
            'esg_market_trends': context_data.get('esg_data', {}).get('market_trends', ''),
            'sustainability_requirements': context_data.get('esg_data', {}).get('requirements', ''),
            'green_transition_impact': context_data.get('esg_data', {}).get('transition_impact', '')
        }
        
        return kiro_context
    
    def _combine_market_analysis(self, 
                                 market_result: KiroExecutionResult,
                                 competitive_result: Optional[KiroExecutionResult]) -> str:
        """Combine market analysis and competitive analysis results"""
        
        combined = market_result.content
        
        if competitive_result and competitive_result.success:
            combined += "\n\n## Competitive Landscape Analysis\n\n"
            combined += competitive_result.content
        
        return combined
    
    async def _extract_market_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key market metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract market size
            size_match = re.search(r'Market Size.*?\$?([0-9,.]+)\s*billion', content, re.IGNORECASE)
            if size_match:
                metrics['market_size_billions'] = float(size_match.group(1).replace(',', ''))
            else:
                metrics['market_size_billions'] = 0.0
            
            # Extract market growth rate
            growth_match = re.search(r'Growth Rate.*?([0-9.]+)%', content, re.IGNORECASE)
            if growth_match:
                metrics['market_growth_rate'] = float(growth_match.group(1))
            else:
                metrics['market_growth_rate'] = 0.0
            
            # Extract market position
            if 'market leader' in content.lower() or 'dominant' in content.lower():
                metrics['market_position'] = 'Leader'
            elif 'challenger' in content.lower() or 'strong position' in content.lower():
                metrics['market_position'] = 'Challenger'
            elif 'niche player' in content.lower():
                metrics['market_position'] = 'Niche'
            else:
                metrics['market_position'] = 'Follower'
            
            # Extract competitive intensity
            if 'intense competition' in content.lower() or 'highly competitive' in content.lower():
                metrics['competitive_intensity'] = 'High'
            elif 'low competition' in content.lower() or 'limited competition' in content.lower():
                metrics['competitive_intensity'] = 'Low'
            else:
                metrics['competitive_intensity'] = 'Medium'
            
            # Calculate market attractiveness score (1-10)
            attractiveness_factors = [
                'growing market' in content.lower(),
                'high barriers' in content.lower(),
                'strong demand' in content.lower(),
                'innovation' in content.lower(),
                'profitable' in content.lower()
            ]
            
            base_score = 5
            score_adjustment = sum(attractiveness_factors) - 2  # Neutral at 2-3 factors
            metrics['market_attractiveness_score'] = max(1, min(10, base_score + score_adjustment))
                
        except Exception as e:
            logger.warning(f"Failed to extract market metrics: {e}")
            # Provide defaults
            metrics.setdefault('market_size_billions', 0.0)
            metrics.setdefault('market_growth_rate', 0.0)
            metrics.setdefault('market_position', 'Unknown')
            metrics.setdefault('competitive_intensity', 'Medium')
            metrics.setdefault('market_attractiveness_score', 5)
        
        return metrics

# Singleton instance
section6_agent = Section6MarketAnalysisAgent()

# Convenience function for FastAPI
async def generate_market_analysis(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate market analysis using Section 6 agent"""
    return await section6_agent.generate_content(ticker, context_data)