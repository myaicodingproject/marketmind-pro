"""
Optimized Kiro Service with Enhanced RAG Integration
Session C2.5: Integration of optimized embeddings with Kiro CLI
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import optimized components
try:
    from backend.data.optimized_embeddings import optimized_chroma_manager
    from backend.data.rag_optimizer import rag_optimizer
    from backend.data.embedding_performance_monitor import performance_monitor
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False
    logging.warning("Optimized embedding components not available, using fallback")

from app.core.config import settings

logger = logging.getLogger(__name__)

class OptimizedKiroService:
    """Enhanced Kiro service with optimized RAG context retrieval"""
    
    def __init__(self):
        self.use_optimized = OPTIMIZED_AVAILABLE
        self.context_cache = {}  # Simple context caching
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        logger.info(f"OptimizedKiroService initialized (optimized: {self.use_optimized})")
    
    async def generate_comprehensive_analysis_optimized(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis with optimized context retrieval"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting optimized comprehensive analysis for {ticker}")
            
            # Generate optimized contexts for each section
            contexts = await self._prepare_all_contexts(ticker, company_data)
            
            # Execute Kiro prompts with optimized contexts
            report_sections = await self._execute_optimized_prompts(ticker, contexts, company_data)
            
            # Format results
            results = {
                "company_overview": {
                    "prompt_key": "company_overview",
                    "content": report_sections.get("company_overview", ""),
                    "metadata": {
                        "page": 1, 
                        "section": "Company Overview & Investment Thesis",
                        "context_tokens": contexts.get("company_overview", {}).get("token_count", 0),
                        "retrieval_time_ms": contexts.get("company_overview", {}).get("retrieval_time_ms", 0)
                    }
                },
                "financial_analysis": {
                    "prompt_key": "financial_analysis",
                    "content": report_sections.get("financial_analysis", ""),
                    "metadata": {
                        "page": 2,
                        "section": "Financial Analysis & Key Metrics", 
                        "context_tokens": contexts.get("financial_analysis", {}).get("token_count", 0),
                        "retrieval_time_ms": contexts.get("financial_analysis", {}).get("retrieval_time_ms", 0)
                    }
                },
                "valuation_analysis": {
                    "prompt_key": "valuation_analysis",
                    "content": report_sections.get("valuation_analysis", ""),
                    "metadata": {
                        "page": 3,
                        "section": "Valuation Analysis & Price Target",
                        "context_tokens": contexts.get("valuation_analysis", {}).get("token_count", 0),
                        "retrieval_time_ms": contexts.get("valuation_analysis", {}).get("retrieval_time_ms", 0)
                    }
                },
                "risk_assessment": {
                    "prompt_key": "risk_assessment", 
                    "content": report_sections.get("risk_assessment", ""),
                    "metadata": {
                        "pages": "4-5",
                        "section": "Risk Assessment & Summary",
                        "context_tokens": contexts.get("risk_assessment", {}).get("token_count", 0),
                        "retrieval_time_ms": contexts.get("risk_assessment", {}).get("retrieval_time_ms", 0)
                    }
                }
            }
            
            # Add performance metrics
            total_time = time.time() - start_time
            total_context_tokens = sum(ctx.get("token_count", 0) for ctx in contexts.values())
            avg_retrieval_time = sum(ctx.get("retrieval_time_ms", 0) for ctx in contexts.values()) / len(contexts)
            
            results["performance_metrics"] = {
                "total_generation_time_s": total_time,
                "total_context_tokens": total_context_tokens,
                "avg_context_retrieval_time_ms": avg_retrieval_time,
                "optimized_rag_used": self.use_optimized,
                "sections_generated": len(report_sections)
            }
            
            logger.info(f"Optimized comprehensive analysis completed for {ticker} in {total_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized comprehensive analysis for {ticker}: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_analysis(ticker, company_data)
    
    async def _prepare_all_contexts(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Prepare optimized contexts for all report sections"""
        contexts = {}
        
        # Define section-specific context requirements
        section_configs = {
            "company_overview": {
                "query": f"{ticker} business model operations competitive position market share",
                "max_tokens": 3000,
                "focus": "business_overview"
            },
            "financial_analysis": {
                "query": f"{ticker} financial performance revenue earnings cash flow margins profitability",
                "max_tokens": 4000,
                "focus": "financial_performance"
            },
            "valuation_analysis": {
                "query": f"{ticker} valuation analysis price target DCF multiples peer comparison",
                "max_tokens": 3500,
                "focus": "valuation"
            },
            "risk_assessment": {
                "query": f"{ticker} risk factors challenges threats regulatory market volatility",
                "max_tokens": 3000,
                "focus": "risk_assessment"
            }
        }
        
        # Prepare contexts concurrently for better performance
        if self.use_optimized:
            context_tasks = []
            for section, config in section_configs.items():
                task = self._get_optimized_context_with_monitoring(
                    ticker, section, config["query"], config["max_tokens"]
                )
                context_tasks.append((section, task))
            
            # Execute all context retrievals concurrently
            for section, task in context_tasks:
                try:
                    context, metrics = await task
                    contexts[section] = {
                        "content": context,
                        "token_count": metrics.get("final_token_count", 0),
                        "retrieval_time_ms": metrics.get("retrieval_time_ms", 0),
                        "target_achieved": metrics.get("target_achieved", False)
                    }
                except Exception as e:
                    logger.warning(f"Failed to get optimized context for {section}: {e}")
                    contexts[section] = {
                        "content": self._get_fallback_context(ticker, company_data, section),
                        "token_count": 0,
                        "retrieval_time_ms": 0,
                        "target_achieved": False
                    }
        else:
            # Fallback context preparation
            for section, config in section_configs.items():
                contexts[section] = {
                    "content": self._get_fallback_context(ticker, company_data, section),
                    "token_count": 0,
                    "retrieval_time_ms": 0,
                    "target_achieved": False
                }
        
        return contexts
    
    async def _get_optimized_context_with_monitoring(self, ticker: str, section: str, 
                                                   query: str, max_tokens: int) -> tuple:
        """Get optimized context with performance monitoring"""
        # Check cache first
        cache_key = f"{ticker}_{section}_{hash(query)}"
        if cache_key in self.context_cache:
            cached_entry = self.context_cache[cache_key]
            if time.time() - cached_entry["timestamp"] < self.cache_ttl:
                logger.info(f"Using cached context for {ticker} {section}")
                return cached_entry["context"], cached_entry["metrics"]
        
        # Monitor the operation
        async with performance_monitor.monitor_operation("kiro_context_retrieval", section, ticker) as monitor:
            try:
                context, metrics = await rag_optimizer.prepare_kiro_context(
                    ticker=ticker,
                    prompt_type=section,
                    additional_context=query
                )
                
                monitor.set_result_count(metrics.get("chunks_selected", 0))
                
                # Cache the result
                self.context_cache[cache_key] = {
                    "context": context,
                    "metrics": metrics,
                    "timestamp": time.time()
                }
                
                return context, metrics
                
            except Exception as e:
                logger.error(f"Optimized context retrieval failed for {ticker} {section}: {e}")
                raise
    
    def _get_fallback_context(self, ticker: str, company_data: Dict[str, Any], section: str) -> str:
        """Get fallback context when optimized retrieval is not available"""
        context_parts = []
        
        # Use provided company data
        if company_data.get("business_description"):
            context_parts.append(f"Business Description: {company_data['business_description']}")
        
        if company_data.get("financial_statements"):
            context_parts.append(f"Financial Data: {company_data['financial_statements']}")
        
        if company_data.get("recent_news"):
            context_parts.append(f"Recent News: {company_data['recent_news']}")
        
        # Section-specific fallback content
        section_defaults = {
            "company_overview": f"{ticker} is a public company operating in its respective industry sector.",
            "financial_analysis": f"Financial analysis for {ticker} based on available public information.",
            "valuation_analysis": f"Valuation analysis for {ticker} using standard financial metrics.",
            "risk_assessment": f"Risk assessment for {ticker} considering market and operational factors."
        }
        
        if not context_parts:
            context_parts.append(section_defaults.get(section, f"Analysis for {ticker}"))
        
        return "\n\n".join(context_parts)
    
    async def _execute_optimized_prompts(self, ticker: str, contexts: Dict[str, Dict[str, Any]], 
                                       company_data: Dict[str, Any]) -> Dict[str, str]:
        """Execute Kiro prompts with optimized contexts"""
        report_sections = {}
        
        # Mock Kiro CLI execution (replace with actual Kiro CLI calls)
        for section, context_data in contexts.items():
            try:
                # Simulate Kiro CLI execution with optimized context
                prompt_content = self._build_kiro_prompt(section, ticker, context_data["content"], company_data)
                
                # In real implementation, this would call Kiro CLI
                # result = await kiro_cli.execute(prompt_content)
                
                # Mock result for testing
                result = self._generate_mock_section_content(section, ticker, context_data["content"])
                
                report_sections[section] = result
                
                logger.info(f"Generated {section} for {ticker} using {context_data['token_count']} context tokens")
                
            except Exception as e:
                logger.error(f"Failed to generate {section} for {ticker}: {e}")
                report_sections[section] = f"Error generating {section}: {str(e)}"
        
        return report_sections
    
    def _build_kiro_prompt(self, section: str, ticker: str, context: str, company_data: Dict[str, Any]) -> str:
        """Build optimized Kiro prompt with context"""
        prompt_templates = {
            "company_overview": f"""
Analyze {ticker} and provide a comprehensive company overview and investment thesis.

CONTEXT:
{context}

COMPANY DATA:
- Ticker: {ticker}
- Sector: {company_data.get('sector', 'Unknown')}
- Market Cap: {company_data.get('market_cap', 'Unknown')}

Generate a detailed company overview covering:
1. Business model and operations
2. Competitive position
3. Key strengths and differentiators
4. Investment thesis and outlook
""",
            "financial_analysis": f"""
Conduct a comprehensive financial analysis for {ticker}.

CONTEXT:
{context}

Analyze and provide:
1. Revenue and earnings trends
2. Profitability metrics and margins
3. Cash flow analysis
4. Balance sheet strength
5. Key financial ratios
6. Year-over-year performance comparison
""",
            "valuation_analysis": f"""
Perform a detailed valuation analysis for {ticker}.

CONTEXT:
{context}

Provide:
1. Current valuation metrics (P/E, EV/EBITDA, etc.)
2. DCF analysis and assumptions
3. Peer comparison and relative valuation
4. Price target and recommendation
5. Valuation scenarios (bull/base/bear)
""",
            "risk_assessment": f"""
Assess the key risks and challenges for {ticker}.

CONTEXT:
{context}

Identify and analyze:
1. Business and operational risks
2. Market and competitive risks
3. Financial and liquidity risks
4. Regulatory and compliance risks
5. Risk mitigation strategies
6. Overall risk rating
"""
        }
        
        return prompt_templates.get(section, f"Analyze {ticker} for {section}")
    
    def _generate_mock_section_content(self, section: str, ticker: str, context: str) -> str:
        """Generate mock section content for testing"""
        mock_content = {
            "company_overview": f"""
# {ticker} Company Overview & Investment Thesis

## Business Model
{ticker} operates as a leading company in its sector, with a diversified business model focused on innovation and market leadership.

## Competitive Position
The company maintains a strong competitive position through:
- Market-leading products and services
- Strong brand recognition
- Operational excellence
- Strategic partnerships

## Investment Thesis
{ticker} presents a compelling investment opportunity based on:
- Strong financial performance
- Market expansion opportunities
- Technological innovation
- Experienced management team

*Analysis based on optimized RAG context with {len(context)} characters of relevant data.*
""",
            "financial_analysis": f"""
# {ticker} Financial Analysis & Key Metrics

## Revenue Performance
- Strong revenue growth trajectory
- Diversified revenue streams
- Consistent market share gains

## Profitability Analysis
- Improving operating margins
- Strong cash generation
- Efficient capital allocation

## Key Financial Ratios
- ROE: Above industry average
- Debt-to-Equity: Conservative leverage
- Current Ratio: Strong liquidity position

*Analysis leverages {len(context)} characters of financial data through optimized retrieval.*
""",
            "valuation_analysis": f"""
# {ticker} Valuation Analysis & Price Target

## Current Valuation Metrics
- P/E Ratio: Reasonable relative to growth
- EV/EBITDA: Attractive compared to peers
- Price-to-Book: Reflects asset quality

## DCF Analysis
- Base case fair value: $XXX
- Bull case scenario: $XXX
- Bear case scenario: $XXX

## Recommendation
BUY with 12-month price target of $XXX

*Valuation based on {len(context)} characters of comprehensive market data.*
""",
            "risk_assessment": f"""
# {ticker} Risk Assessment & Summary

## Key Risk Factors
1. **Market Risk**: Exposure to economic cycles
2. **Competitive Risk**: Intense industry competition
3. **Operational Risk**: Execution challenges
4. **Regulatory Risk**: Changing regulatory environment

## Risk Mitigation
- Diversified business model
- Strong balance sheet
- Experienced management
- Strategic flexibility

## Overall Risk Rating: MODERATE

*Risk analysis incorporates {len(context)} characters of relevant risk data.*
"""
        }
        
        return mock_content.get(section, f"Mock content for {section} - {ticker}")
    
    async def _fallback_analysis(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when optimized system fails"""
        logger.warning(f"Using fallback analysis for {ticker}")
        
        # Basic analysis without optimized RAG
        return {
            "company_overview": {
                "prompt_key": "company_overview",
                "content": f"Basic company overview for {ticker}",
                "metadata": {"page": 1, "section": "Company Overview", "fallback": True}
            },
            "financial_analysis": {
                "prompt_key": "financial_analysis", 
                "content": f"Basic financial analysis for {ticker}",
                "metadata": {"page": 2, "section": "Financial Analysis", "fallback": True}
            },
            "valuation_analysis": {
                "prompt_key": "valuation_analysis",
                "content": f"Basic valuation analysis for {ticker}",
                "metadata": {"page": 3, "section": "Valuation Analysis", "fallback": True}
            },
            "risk_assessment": {
                "prompt_key": "risk_assessment",
                "content": f"Basic risk assessment for {ticker}",
                "metadata": {"pages": "4-5", "section": "Risk Assessment", "fallback": True}
            }
        }
    
    async def execute_single_prompt_optimized(self, prompt_key: str, ticker: str, 
                                            context: str = "") -> Dict[str, Any]:
        """Execute single prompt with optimized context"""
        try:
            if self.use_optimized and not context:
                # Get optimized context for the specific prompt
                optimized_context, metrics = await rag_optimizer.prepare_kiro_context(
                    ticker=ticker,
                    prompt_type=prompt_key,
                    additional_context=context
                )
                context = optimized_context
            
            # Execute prompt (mock implementation)
            content = self._generate_mock_section_content(prompt_key, ticker, context)
            
            return {
                "prompt_key": prompt_key,
                "content": content,
                "metadata": {
                    "section": prompt_key,
                    "ticker": ticker,
                    "optimized": self.use_optimized,
                    "context_length": len(context)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing optimized prompt {prompt_key}: {str(e)}")
            raise
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of the optimized service"""
        if not self.use_optimized:
            return {"status": "Optimized components not available"}
        
        try:
            chroma_metrics = optimized_chroma_manager.get_performance_metrics()
            monitor_metrics = performance_monitor.generate_performance_report(hours_back=1)
            
            return {
                "optimized_system_active": True,
                "chroma_performance": chroma_metrics,
                "monitoring_summary": monitor_metrics,
                "cache_stats": {
                    "cached_contexts": len(self.context_cache),
                    "cache_ttl_seconds": self.cache_ttl
                }
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}

# Global instance
optimized_kiro_service = OptimizedKiroService()