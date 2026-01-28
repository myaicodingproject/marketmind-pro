"""
Section 3 Agent - Company Deep Dive Generator
Production-ready agent using real Kiro CLI integration for comprehensive company analysis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class CompanyAnalysisMetrics:
    """Key company analysis metrics"""
    business_model_strength: str
    competitive_position: str
    market_share: float
    growth_strategy_score: int

class Section3CompanyDeepDiveAgent(KiroAgentBase):
    """Production-ready Section 3 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section3_CompanyDeepDive",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=150)
        )
        
        # Define prompt configurations for company analysis
        self.prompt_configs = [
            {
                'name': 'company_deep_dive',
                'prompt_file': 'enhanced-company-deep-dive.md',
                'custom_instructions': None
            },
            {
                'name': 'business_model',
                'prompt_file': 'section3-business-model-analysis.md',
                'custom_instructions': 'Focus on revenue streams and competitive moats'
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate company deep dive using Kiro CLI"""
        
        logger.info(f"Section 3: Starting company deep dive generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            deep_dive_result = results.get('company_deep_dive')
            business_model_result = results.get('business_model')
            
            if not deep_dive_result or not self.validate_result(deep_dive_result, min_length=1000):
                raise RuntimeError("Failed to generate valid company deep dive")
            
            # Combine results
            combined_content = self._combine_company_analysis(deep_dive_result, business_model_result)
            
            # Extract company metrics
            metrics = await self._extract_company_metrics(combined_content)
            
            # Structure the final output
            output = {
                'section': 'company_deep_dive',
                'ticker': ticker,
                'content': combined_content,
                'metrics': metrics,
                'execution_time': deep_dive_result.execution_time + (business_model_result.execution_time if business_model_result else 0),
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 3: Successfully generated company deep dive for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 3: Failed to generate company deep dive for {ticker}: {e}")
            return {
                'section': 'company_deep_dive',
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
        financial_data = context_data.get('financial_data', {})
        market_data = context_data.get('market_data', {})
        
        # Prepare comprehensive company context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            'country': company_info.get('country', 'Unknown'),
            'website': company_info.get('website', ''),
            'employees': company_info.get('fullTimeEmployees', 0),
            'founded_year': company_info.get('founded', 'Unknown'),
            
            # Business description
            'business_summary': company_info.get('longBusinessSummary', ''),
            'business_description': company_info.get('businessSummary', ''),
            
            # Financial context
            'market_cap': financial_data.get('market_cap', 0),
            'revenue_ttm': financial_data.get('revenue_ttm', 0),
            'enterprise_value': financial_data.get('enterprise_value', 0),
            
            # Market position
            'market_share': market_data.get('market_share', 0),
            'competitive_position': market_data.get('competitive_position', 'Unknown'),
            
            # Revenue breakdown
            'revenue_segments': json.dumps(context_data.get('segment_data', {})),
            'geographic_revenue': json.dumps(context_data.get('geographic_data', {})),
            
            # Leadership and governance
            'ceo_name': company_info.get('ceo', 'Unknown'),
            'leadership_team': json.dumps(context_data.get('leadership_data', {})),
            'board_composition': json.dumps(context_data.get('governance_data', {})),
            
            # Strategic initiatives
            'recent_acquisitions': json.dumps(context_data.get('acquisitions_data', {})),
            'rd_spending': financial_data.get('rd_expenses', 0),
            'capex_trend': json.dumps(context_data.get('capex_data', {})),
            
            # RAG context
            'rag_company_filings': context_data.get('rag_context', {}).get('company_filings', ''),
            'rag_management_commentary': context_data.get('rag_context', {}).get('management_commentary', ''),
            'rag_industry_analysis': context_data.get('rag_context', {}).get('industry_analysis', ''),
            
            # Competitive landscape
            'main_competitors': json.dumps(context_data.get('competitors_data', {})),
            'competitive_advantages': context_data.get('competitive_data', {}).get('advantages', ''),
            'market_trends': context_data.get('market_trends', ''),
            
            # ESG and sustainability
            'esg_score': context_data.get('esg_data', {}).get('overall_score', 0),
            'sustainability_initiatives': context_data.get('esg_data', {}).get('initiatives', ''),
            
            # Recent developments
            'recent_news': json.dumps(context_data.get('news_data', {})),
            'analyst_coverage': json.dumps(context_data.get('analyst_data', {}))
        }
        
        return kiro_context
    
    def _combine_company_analysis(self, 
                                  deep_dive_result: KiroExecutionResult, 
                                  business_model_result: Optional[KiroExecutionResult]) -> str:
        """Combine company deep dive and business model results"""
        
        combined = deep_dive_result.content
        
        if business_model_result and business_model_result.success:
            combined += "\n\n## Business Model Deep Dive\n\n"
            combined += business_model_result.content
        
        return combined
    
    async def _extract_company_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key company metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract business model strength
            if 'strong business model' in content.lower():
                metrics['business_model_strength'] = 'Strong'
            elif 'weak business model' in content.lower():
                metrics['business_model_strength'] = 'Weak'
            else:
                metrics['business_model_strength'] = 'Moderate'
            
            # Extract competitive position
            if 'market leader' in content.lower() or 'dominant position' in content.lower():
                metrics['competitive_position'] = 'Leader'
            elif 'challenger' in content.lower() or 'strong competitor' in content.lower():
                metrics['competitive_position'] = 'Challenger'
            else:
                metrics['competitive_position'] = 'Follower'
            
            # Extract market share
            share_match = re.search(r'market share.*?([0-9.]+)%', content, re.IGNORECASE)
            if share_match:
                metrics['market_share'] = float(share_match.group(1))
            else:
                metrics['market_share'] = 0.0
            
            # Score growth strategy (1-10 based on keywords)
            growth_keywords = ['expansion', 'innovation', 'acquisition', 'digital transformation', 'new markets']
            score = sum(1 for keyword in growth_keywords if keyword in content.lower())
            metrics['growth_strategy_score'] = min(score * 2, 10)  # Scale to 1-10
                
        except Exception as e:
            logger.warning(f"Failed to extract company metrics: {e}")
        
        return metrics

# Singleton instance
section3_agent = Section3CompanyDeepDiveAgent()

# Convenience function for FastAPI
async def generate_company_deep_dive(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate company deep dive using Section 3 agent"""
    return await section3_agent.generate_content(ticker, context_data)