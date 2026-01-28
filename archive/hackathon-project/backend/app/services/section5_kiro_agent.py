"""
Section 5 Agent - Risk Assessment Generator
Production-ready agent using real Kiro CLI integration for comprehensive risk analysis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Key risk assessment metrics"""
    overall_risk_score: int  # 1-10 scale
    business_risk_level: str
    financial_risk_level: str
    market_risk_level: str
    key_risk_factors: List[str]

class Section5RiskAssessmentAgent(KiroAgentBase):
    """Production-ready Section 5 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section5_RiskAssessment",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=120)
        )
        
        # Define prompt configurations for risk assessment
        self.prompt_configs = [
            {
                'name': 'risk_assessment',
                'prompt_file': 'enhanced-risk-assessment.md',
                'custom_instructions': None
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment using Kiro CLI"""
        
        logger.info(f"Section 5: Starting risk assessment generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            risk_result = results.get('risk_assessment')
            
            if not risk_result or not self.validate_result(risk_result, min_length=800):
                raise RuntimeError("Failed to generate valid risk assessment")
            
            # Extract risk metrics
            metrics = await self._extract_risk_metrics(risk_result.content)
            
            # Structure the final output
            output = {
                'section': 'risk_assessment',
                'ticker': ticker,
                'content': risk_result.content,
                'metrics': metrics,
                'execution_time': risk_result.execution_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 5: Successfully generated risk assessment for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 5: Failed to generate risk assessment for {ticker}: {e}")
            return {
                'section': 'risk_assessment',
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
        
        # Prepare comprehensive risk context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Financial risk indicators
            'debt_to_equity': financial_data.get('debt_to_equity', 0),
            'current_ratio': financial_data.get('current_ratio', 0),
            'interest_coverage': financial_data.get('interest_coverage', 0),
            'cash_ratio': financial_data.get('cash_ratio', 0),
            'revenue_volatility': context_data.get('risk_data', {}).get('revenue_volatility', 0),
            'earnings_volatility': context_data.get('risk_data', {}).get('earnings_volatility', 0),
            
            # Market risk indicators
            'beta': financial_data.get('beta', 1.0),
            'stock_volatility': market_data.get('volatility', 0),
            'correlation_market': market_data.get('market_correlation', 0),
            'trading_volume': market_data.get('avg_volume', 0),
            
            # Business risk factors
            'customer_concentration': context_data.get('risk_data', {}).get('customer_concentration', 0),
            'supplier_dependence': context_data.get('risk_data', {}).get('supplier_dependence', 'Low'),
            'regulatory_risk': context_data.get('risk_data', {}).get('regulatory_risk', 'Medium'),
            'competitive_intensity': context_data.get('risk_data', {}).get('competitive_intensity', 'Medium'),
            
            # Industry and macro risks
            'industry_cyclicality': context_data.get('industry_data', {}).get('cyclicality', 'Medium'),
            'technology_disruption_risk': context_data.get('industry_data', {}).get('tech_disruption', 'Medium'),
            'economic_sensitivity': context_data.get('industry_data', {}).get('economic_sensitivity', 'Medium'),
            
            # ESG and governance risks
            'esg_score': context_data.get('esg_data', {}).get('overall_score', 50),
            'governance_score': context_data.get('esg_data', {}).get('governance_score', 50),
            'environmental_risks': context_data.get('esg_data', {}).get('environmental_risks', ''),
            'social_risks': context_data.get('esg_data', {}).get('social_risks', ''),
            
            # Geographic and operational risks
            'geographic_concentration': json.dumps(context_data.get('geographic_data', {})),
            'operational_leverage': financial_data.get('operating_leverage', 0),
            'capital_intensity': financial_data.get('capital_intensity', 0),
            
            # Recent risk events
            'recent_controversies': json.dumps(context_data.get('controversy_data', {})),
            'litigation_risks': context_data.get('legal_data', {}).get('litigation_summary', ''),
            'management_changes': json.dumps(context_data.get('management_changes', {})),
            
            # RAG context
            'rag_risk_factors': context_data.get('rag_context', {}).get('risk_factors', ''),
            'rag_sec_risk_disclosures': context_data.get('rag_context', {}).get('sec_risk_disclosures', ''),
            'rag_analyst_risk_notes': context_data.get('rag_context', {}).get('analyst_risk_notes', ''),
            
            # Forward-looking risk indicators
            'guidance_reliability': context_data.get('guidance_data', {}).get('reliability_score', 50),
            'earnings_surprise_history': json.dumps(context_data.get('earnings_surprises', {})),
            'analyst_revision_trends': json.dumps(context_data.get('analyst_revisions', {}))
        }
        
        return kiro_context
    
    async def _extract_risk_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key risk metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Extract overall risk score (1-10)
            score_match = re.search(r'Overall Risk.*?([1-9]|10)', content, re.IGNORECASE)
            if score_match:
                metrics['overall_risk_score'] = int(score_match.group(1))
            else:
                # Estimate based on risk level keywords
                if 'high risk' in content.lower():
                    metrics['overall_risk_score'] = 8
                elif 'low risk' in content.lower():
                    metrics['overall_risk_score'] = 3
                else:
                    metrics['overall_risk_score'] = 5
            
            # Extract business risk level
            if 'high business risk' in content.lower():
                metrics['business_risk_level'] = 'High'
            elif 'low business risk' in content.lower():
                metrics['business_risk_level'] = 'Low'
            else:
                metrics['business_risk_level'] = 'Medium'
            
            # Extract financial risk level
            if 'high financial risk' in content.lower():
                metrics['financial_risk_level'] = 'High'
            elif 'low financial risk' in content.lower():
                metrics['financial_risk_level'] = 'Low'
            else:
                metrics['financial_risk_level'] = 'Medium'
            
            # Extract market risk level
            if 'high market risk' in content.lower() or 'volatile' in content.lower():
                metrics['market_risk_level'] = 'High'
            elif 'low market risk' in content.lower() or 'stable' in content.lower():
                metrics['market_risk_level'] = 'Low'
            else:
                metrics['market_risk_level'] = 'Medium'
            
            # Extract key risk factors
            risk_factors = []
            risk_patterns = [
                r'Key Risk.*?:\s*([^.]+)',
                r'Primary Risk.*?:\s*([^.]+)',
                r'Main Risk.*?:\s*([^.]+)',
                r'Risk Factor.*?:\s*([^.]+)'
            ]
            
            for pattern in risk_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                risk_factors.extend(matches)
            
            # Clean and limit risk factors
            metrics['key_risk_factors'] = [factor.strip() for factor in risk_factors[:5]]
                
        except Exception as e:
            logger.warning(f"Failed to extract risk metrics: {e}")
            # Provide defaults
            metrics.setdefault('overall_risk_score', 5)
            metrics.setdefault('business_risk_level', 'Medium')
            metrics.setdefault('financial_risk_level', 'Medium')
            metrics.setdefault('market_risk_level', 'Medium')
            metrics.setdefault('key_risk_factors', [])
        
        return metrics

# Singleton instance
section5_agent = Section5RiskAssessmentAgent()

# Convenience function for FastAPI
async def generate_risk_assessment(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate risk assessment using Section 5 agent"""
    return await section5_agent.generate_content(ticker, context_data)