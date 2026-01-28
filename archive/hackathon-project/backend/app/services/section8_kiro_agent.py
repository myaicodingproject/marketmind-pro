"""
Section 8 Agent - Interactive Q&A Generator
Production-ready agent using real Kiro CLI integration for interactive report Q&A
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .kiro_agent_base import KiroAgentBase, KiroExecutionResult, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class QAMetrics:
    """Key Q&A metrics"""
    qa_pairs_generated: int
    coverage_completeness: str
    interaction_quality: str
    rag_integration_score: int

class Section8InteractiveQAAgent(KiroAgentBase):
    """Production-ready Section 8 agent using Kiro CLI"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        super().__init__(
            agent_name="Section8_InteractiveQA",
            kiro_cli_path=kiro_cli_path,
            prompts_dir=prompts_dir,
            config=AgentConfig(max_retries=3, timeout_seconds=100)
        )
        
        # Define prompt configurations for interactive Q&A
        self.prompt_configs = [
            {
                'name': 'interactive_qa',
                'prompt_file': 'enhanced-interactive-qa.md',
                'custom_instructions': None
            }
        ]
    
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interactive Q&A using Kiro CLI"""
        
        logger.info(f"Section 8: Starting interactive Q&A generation for {ticker}")
        
        try:
            # Prepare context data for Kiro prompts
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            
            # Execute Kiro prompts
            results = await self.execute_multiple_prompts(self.prompt_configs, kiro_context)
            
            # Process results
            qa_result = results.get('interactive_qa')
            
            if not qa_result or not self.validate_result(qa_result, min_length=600):
                raise RuntimeError("Failed to generate valid interactive Q&A")
            
            # Extract Q&A metrics
            metrics = await self._extract_qa_metrics(qa_result.content)
            
            # Structure the final output
            output = {
                'section': 'interactive_qa',
                'ticker': ticker,
                'content': qa_result.content,
                'metrics': metrics,
                'execution_time': qa_result.execution_time,
                'success': True,
                'generated_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Section 8: Successfully generated interactive Q&A for {ticker}")
            return output
            
        except Exception as e:
            logger.error(f"Section 8: Failed to generate interactive Q&A for {ticker}: {e}")
            return {
                'section': 'interactive_qa',
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
        
        # Aggregate all report sections for comprehensive Q&A
        company_info = context_data.get('company_info', {})
        
        # Prepare comprehensive Q&A context
        kiro_context = {
            'ticker': ticker,
            'company_name': company_info.get('longName', ticker),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            
            # Section 1: Executive Summary
            'executive_summary': context_data.get('section1_data', {}).get('content', ''),
            'recommendation': context_data.get('section1_data', {}).get('recommendation', 'HOLD'),
            'price_target': context_data.get('section1_data', {}).get('price_target', 0),
            
            # Section 2: Financial Analysis
            'financial_analysis': context_data.get('section2_data', {}).get('content', ''),
            'financial_metrics': json.dumps(context_data.get('section2_data', {}).get('metrics', {})),
            
            # Section 3: Company Deep Dive
            'company_analysis': context_data.get('section3_data', {}).get('content', ''),
            'business_model': context_data.get('section3_data', {}).get('business_model', ''),
            
            # Section 4: Valuation Analysis
            'valuation_analysis': context_data.get('section4_data', {}).get('content', ''),
            'dcf_fair_value': context_data.get('section4_data', {}).get('dcf_fair_value', 0),
            'peer_valuation': context_data.get('section4_data', {}).get('peer_multiple_value', 0),
            
            # Section 5: Risk Assessment
            'risk_assessment': context_data.get('section5_data', {}).get('content', ''),
            'key_risks': json.dumps(context_data.get('section5_data', {}).get('key_risk_factors', [])),
            
            # Section 6: Market Analysis
            'market_analysis': context_data.get('section6_data', {}).get('content', ''),
            'market_size': context_data.get('section6_data', {}).get('market_size_billions', 0),
            'market_growth': context_data.get('section6_data', {}).get('market_growth_rate', 0),
            
            # Section 7: Investment Thesis
            'investment_thesis': context_data.get('section7_data', {}).get('content', ''),
            'key_catalysts': json.dumps(context_data.get('section7_data', {}).get('key_catalysts', [])),
            
            # Common investor questions by category
            'valuation_questions': [
                'What is the fair value of the stock?',
                'How does the valuation compare to peers?',
                'What are the key valuation assumptions?',
                'Is the stock overvalued or undervalued?'
            ],
            
            'financial_questions': [
                'What are the key financial trends?',
                'How strong is the balance sheet?',
                'What is the cash flow outlook?',
                'How profitable is the company?'
            ],
            
            'business_questions': [
                'What is the company\'s competitive advantage?',
                'How does the business model work?',
                'What are the growth drivers?',
                'Who are the main competitors?'
            ],
            
            'risk_questions': [
                'What are the main investment risks?',
                'How cyclical is the business?',
                'What could go wrong with the investment?',
                'How does the company manage risks?'
            ],
            
            'market_questions': [
                'How large is the addressable market?',
                'What is the market growth outlook?',
                'How is the competitive landscape evolving?',
                'What are the industry trends?'
            ],
            
            # RAG context for detailed answers
            'rag_full_context': context_data.get('rag_context', {}).get('full_context', ''),
            'rag_financial_data': context_data.get('rag_context', {}).get('financial_data', ''),
            'rag_management_commentary': context_data.get('rag_context', {}).get('management_commentary', ''),
            'rag_analyst_research': context_data.get('rag_context', {}).get('analyst_research', ''),
            
            # Report metadata for context
            'report_generation_date': context_data.get('metadata', {}).get('generation_date', ''),
            'data_sources': json.dumps(context_data.get('metadata', {}).get('data_sources', [])),
            'analysis_methodology': context_data.get('metadata', {}).get('methodology', ''),
            
            # Interactive features
            'enable_follow_up_questions': True,
            'provide_source_references': True,
            'include_calculation_details': True,
            'support_scenario_analysis': True
        }
        
        return kiro_context
    
    async def _extract_qa_metrics(self, content: str) -> Dict[str, Any]:
        """Extract key Q&A metrics from generated content"""
        
        metrics = {}
        
        try:
            import re
            
            # Count Q&A pairs
            qa_count = len(re.findall(r'\*\*Q:', content, re.IGNORECASE))
            metrics['qa_pairs_generated'] = qa_count
            
            # Assess coverage completeness
            coverage_areas = [
                'valuation' in content.lower(),
                'financial' in content.lower(),
                'business' in content.lower(),
                'risk' in content.lower(),
                'market' in content.lower()
            ]
            
            coverage_score = sum(coverage_areas)
            if coverage_score >= 4:
                metrics['coverage_completeness'] = 'Comprehensive'
            elif coverage_score >= 3:
                metrics['coverage_completeness'] = 'Good'
            else:
                metrics['coverage_completeness'] = 'Limited'
            
            # Assess interaction quality
            quality_indicators = [
                'detailed' in content.lower(),
                'specific' in content.lower(),
                'example' in content.lower(),
                'calculation' in content.lower(),
                'source' in content.lower()
            ]
            
            quality_score = sum(quality_indicators)
            if quality_score >= 3:
                metrics['interaction_quality'] = 'High'
            elif quality_score >= 2:
                metrics['interaction_quality'] = 'Medium'
            else:
                metrics['interaction_quality'] = 'Basic'
            
            # Score RAG integration (1-10)
            rag_indicators = [
                'according to' in content.lower(),
                'based on' in content.lower(),
                'data shows' in content.lower(),
                'analysis indicates' in content.lower(),
                'research suggests' in content.lower()
            ]
            
            rag_score = min(10, sum(rag_indicators) * 2)
            metrics['rag_integration_score'] = max(1, rag_score)
                
        except Exception as e:
            logger.warning(f"Failed to extract Q&A metrics: {e}")
            # Provide defaults
            metrics.setdefault('qa_pairs_generated', 0)
            metrics.setdefault('coverage_completeness', 'Limited')
            metrics.setdefault('interaction_quality', 'Basic')
            metrics.setdefault('rag_integration_score', 5)
        
        return metrics
    
    async def answer_specific_question(self, 
                                       ticker: str, 
                                       question: str, 
                                       context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Answer a specific question about the report using Kiro CLI"""
        
        logger.info(f"Section 8: Answering specific question for {ticker}: {question}")
        
        try:
            # Prepare context with the specific question
            kiro_context = await self._prepare_kiro_context(ticker, context_data)
            kiro_context['specific_question'] = question
            
            # Use a custom instruction for specific Q&A
            custom_instruction = f"Answer this specific question about {ticker}: {question}"
            
            # Execute Kiro prompt with custom instruction
            result = await self.execute_kiro_prompt(
                'enhanced-interactive-qa.md',
                kiro_context,
                custom_instruction
            )
            
            if not result.success:
                raise RuntimeError(f"Failed to answer question: {result.error_message}")
            
            return {
                'question': question,
                'answer': result.content,
                'execution_time': result.execution_time,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to answer specific question: {e}")
            return {
                'question': question,
                'answer': f"I apologize, but I encountered an error while processing your question: {str(e)}",
                'execution_time': 0,
                'success': False,
                'error': str(e)
            }

# Singleton instance
section8_agent = Section8InteractiveQAAgent()

# Convenience functions for FastAPI
async def generate_interactive_qa(ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate interactive Q&A using Section 8 agent"""
    return await section8_agent.generate_content(ticker, context_data)

async def answer_question(ticker: str, question: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Answer a specific question about the report"""
    return await section8_agent.answer_specific_question(ticker, question, context_data)