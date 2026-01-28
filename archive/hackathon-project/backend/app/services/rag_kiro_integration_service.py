"""
RAG-Kiro Integration Service - Session A4.5
Seamless integration between ChromaDB RAG context and Kiro CLI processing
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
import redis
from concurrent.futures import ThreadPoolExecutor

from backend.data.optimized_embeddings import OptimizedChromaDBManager
from app.services.report_queue import ReportQueue

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL_ANALYSIS = "financial_analysis"
    VALUATION_ANALYSIS = "valuation_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    ESG_ANALYSIS = "esg_analysis"

@dataclass
class ContextConfig:
    max_tokens: int = 4000
    relevance_threshold: float = 0.7
    chunk_overlap: int = 100
    priority_sources: List[str] = None
    
    def __post_init__(self):
        if self.priority_sources is None:
            self.priority_sources = ["sec_filings", "financial_data", "company_profiles"]

@dataclass
class KiroExecutionResult:
    success: bool
    content: str
    execution_time: float
    context_tokens: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class ContextPreparer:
    """Prepares optimized context for Kiro CLI processing"""
    
    def __init__(self, chroma_manager: OptimizedChromaDBManager):
        self.chroma_manager = chroma_manager
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def prepare_context(self, ticker: str, analysis_type: AnalysisType, 
                            config: ContextConfig) -> Dict[str, Any]:
        """Prepare optimized context for specific analysis type"""
        cache_key = f"{ticker}_{analysis_type.value}_{hash(str(config))}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Using cached context for {ticker} {analysis_type.value}")
                return cached_data
        
        start_time = time.time()
        
        # Get analysis-specific query
        query = self._get_analysis_query(ticker, analysis_type)
        
        # Retrieve relevant documents
        search_results = await self.chroma_manager.optimized_search(
            query=query,
            ticker=ticker,
            n_results=15,
            relevance_threshold=config.relevance_threshold
        )
        
        # Process and optimize context
        context_data = await self._process_search_results(
            search_results, analysis_type, config
        )
        
        # Cache result
        self.cache[cache_key] = (context_data, time.time())
        
        processing_time = time.time() - start_time
        logger.info(f"Context prepared for {ticker} {analysis_type.value} in {processing_time:.3f}s")
        
        return context_data
    
    def _get_analysis_query(self, ticker: str, analysis_type: AnalysisType) -> str:
        """Generate analysis-specific search queries"""
        base_query = f"{ticker} financial analysis"
        
        query_templates = {
            AnalysisType.EXECUTIVE_SUMMARY: f"{ticker} business model revenue growth profitability key metrics",
            AnalysisType.FINANCIAL_ANALYSIS: f"{ticker} financial statements revenue earnings cash flow balance sheet ratios",
            AnalysisType.VALUATION_ANALYSIS: f"{ticker} valuation DCF multiples peer comparison price target",
            AnalysisType.RISK_ASSESSMENT: f"{ticker} risks challenges regulatory competitive market",
            AnalysisType.COMPETITIVE_ANALYSIS: f"{ticker} competition market share industry position competitive advantages",
            AnalysisType.ESG_ANALYSIS: f"{ticker} ESG sustainability environmental social governance"
        }
        
        return query_templates.get(analysis_type, base_query)
    
    async def _process_search_results(self, results: List[Dict], 
                                    analysis_type: AnalysisType, 
                                    config: ContextConfig) -> Dict[str, Any]:
        """Process and structure search results for Kiro consumption"""
        
        # Group results by source type
        grouped_results = self._group_by_source_type(results)
        
        # Apply source prioritization
        prioritized_content = self._prioritize_content(grouped_results, config.priority_sources)
        
        # Build structured context
        context_sections = {}
        current_tokens = 0
        
        for source_type, documents in prioritized_content.items():
            section_content = []
            section_tokens = 0
            
            for doc in documents:
                content = doc["document"]
                estimated_tokens = len(content) // 4  # Rough token estimation
                
                if current_tokens + estimated_tokens > config.max_tokens:
                    break
                
                # Add metadata context
                metadata = doc["metadata"]
                doc_header = self._create_document_header(metadata)
                formatted_content = f"{doc_header}\n{content}"
                
                section_content.append(formatted_content)
                section_tokens += estimated_tokens
                current_tokens += estimated_tokens
            
            if section_content:
                context_sections[source_type] = {
                    "content": "\n\n".join(section_content),
                    "token_count": section_tokens,
                    "document_count": len(section_content)
                }
        
        # Create final context structure
        return {
            "ticker": results[0]["metadata"]["ticker"] if results else "UNKNOWN",
            "analysis_type": analysis_type.value,
            "context_sections": context_sections,
            "total_tokens": current_tokens,
            "total_documents": sum(section["document_count"] for section in context_sections.values()),
            "generated_at": datetime.now().isoformat()
        }
    
    def _group_by_source_type(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Group search results by source type"""
        grouped = {}
        for result in results:
            source_type = result["metadata"].get("type", "unknown")
            if source_type not in grouped:
                grouped[source_type] = []
            grouped[source_type].append(result)
        return grouped
    
    def _prioritize_content(self, grouped_results: Dict[str, List[Dict]], 
                          priority_sources: List[str]) -> Dict[str, List[Dict]]:
        """Prioritize content based on source importance and relevance"""
        prioritized = {}
        
        # Process priority sources first
        for source_type in priority_sources:
            if source_type in grouped_results:
                # Sort by relevance score
                sorted_docs = sorted(
                    grouped_results[source_type],
                    key=lambda x: x.get("relevance_score", 0),
                    reverse=True
                )
                prioritized[source_type] = sorted_docs
        
        # Add remaining sources
        for source_type, docs in grouped_results.items():
            if source_type not in prioritized:
                sorted_docs = sorted(docs, key=lambda x: x.get("relevance_score", 0), reverse=True)
                prioritized[source_type] = sorted_docs
        
        return prioritized
    
    def _create_document_header(self, metadata: Dict) -> str:
        """Create informative document header"""
        doc_type = metadata.get("type", "UNKNOWN").upper()
        ticker = metadata.get("ticker", "")
        date = metadata.get("filing_date", metadata.get("added_at", ""))
        
        header_parts = [f"[{doc_type}]"]
        if ticker:
            header_parts.append(f"Ticker: {ticker}")
        if date:
            header_parts.append(f"Date: {date}")
        
        return " | ".join(header_parts)

class KiroExecutor:
    """Executes Kiro CLI with optimized context"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli"):
        self.kiro_cli_path = kiro_cli_path
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.temp_dir = Path(tempfile.gettempdir()) / "rag_kiro_integration"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def execute_with_context(self, ticker: str, analysis_type: AnalysisType,
                                 context_data: Dict[str, Any],
                                 prompt_template: Optional[str] = None) -> KiroExecutionResult:
        """Execute Kiro CLI with prepared context"""
        start_time = time.time()
        
        try:
            # Create context file
            context_file = await self._create_context_file(ticker, analysis_type, context_data)
            
            # Get prompt template
            if prompt_template is None:
                prompt_template = self._get_prompt_template(analysis_type)
            
            # Prepare Kiro command
            kiro_command = self._build_kiro_command(
                ticker, analysis_type, context_file, prompt_template, context_data
            )
            
            # Execute Kiro CLI
            result = await self._execute_kiro_command(kiro_command)
            
            # Cleanup
            context_file.unlink(missing_ok=True)
            
            execution_time = time.time() - start_time
            
            return KiroExecutionResult(
                success=result["success"],
                content=result["content"],
                execution_time=execution_time,
                context_tokens=context_data.get("total_tokens", 0),
                error_message=result.get("error"),
                metadata={
                    "ticker": ticker,
                    "analysis_type": analysis_type.value,
                    "context_documents": context_data.get("total_documents", 0),
                    "prompt_template": prompt_template[:100] + "..." if len(prompt_template) > 100 else prompt_template
                }
            )
            
        except Exception as e:
            logger.error(f"Kiro execution failed for {ticker} {analysis_type.value}: {e}")
            return KiroExecutionResult(
                success=False,
                content="",
                execution_time=time.time() - start_time,
                context_tokens=context_data.get("total_tokens", 0),
                error_message=str(e)
            )
    
    async def _create_context_file(self, ticker: str, analysis_type: AnalysisType,
                                 context_data: Dict[str, Any]) -> Path:
        """Create temporary context file for Kiro CLI"""
        timestamp = int(time.time())
        context_file = self.temp_dir / f"context_{ticker}_{analysis_type.value}_{timestamp}.txt"
        
        # Build context content
        context_content = self._format_context_for_kiro(context_data)
        
        # Write to file
        context_file.write_text(context_content, encoding='utf-8')
        
        return context_file
    
    def _format_context_for_kiro(self, context_data: Dict[str, Any]) -> str:
        """Format context data for Kiro CLI consumption"""
        ticker = context_data.get("ticker", "UNKNOWN")
        analysis_type = context_data.get("analysis_type", "unknown")
        
        content_parts = [
            f"FINANCIAL ANALYSIS CONTEXT FOR {ticker}",
            f"Analysis Type: {analysis_type.upper()}",
            f"Generated: {context_data.get('generated_at', 'Unknown')}",
            f"Total Documents: {context_data.get('total_documents', 0)}",
            f"Total Tokens: {context_data.get('total_tokens', 0)}",
            "=" * 80
        ]
        
        # Add context sections
        context_sections = context_data.get("context_sections", {})
        for source_type, section_data in context_sections.items():
            content_parts.extend([
                f"\n{source_type.upper()} CONTEXT:",
                f"Documents: {section_data['document_count']}, Tokens: {section_data['token_count']}",
                "-" * 40,
                section_data["content"],
                "=" * 80
            ])
        
        return "\n".join(content_parts)
    
    def _get_prompt_template(self, analysis_type: AnalysisType) -> str:
        """Get analysis-specific prompt template"""
        prompt_templates = {
            AnalysisType.EXECUTIVE_SUMMARY: """
Generate a comprehensive executive summary for the provided company using the RAG context.
Focus on: business model, financial performance, key metrics, investment thesis, and price target.
Use specific data from the context to support all claims and recommendations.
""",
            AnalysisType.FINANCIAL_ANALYSIS: """
Perform detailed financial analysis using the provided RAG context.
Focus on: revenue trends, profitability metrics, cash flow analysis, balance sheet strength, and peer comparisons.
Calculate key financial ratios and provide 3-year projections based on the context data.
""",
            AnalysisType.VALUATION_ANALYSIS: """
Conduct comprehensive valuation analysis using the RAG context.
Focus on: DCF modeling, peer multiples, scenario analysis, and price target derivation.
Use specific financial data from the context to build valuation models.
""",
            AnalysisType.RISK_ASSESSMENT: """
Analyze investment risks using the provided RAG context.
Focus on: business risks, financial risks, regulatory risks, and competitive risks.
Quantify risks where possible using data from the context.
""",
            AnalysisType.COMPETITIVE_ANALYSIS: """
Analyze competitive position using the RAG context.
Focus on: market share, competitive advantages, industry dynamics, and strategic positioning.
Use context data to support competitive assessments.
""",
            AnalysisType.ESG_ANALYSIS: """
Evaluate ESG factors using the provided RAG context.
Focus on: environmental impact, social responsibility, governance practices, and sustainability metrics.
Use specific ESG data from the context to support analysis.
"""
        }
        
        return prompt_templates.get(analysis_type, "Analyze the provided financial data and context.")
    
    def _build_kiro_command(self, ticker: str, analysis_type: AnalysisType,
                          context_file: Path, prompt_template: str,
                          context_data: Dict[str, Any]) -> List[str]:
        """Build Kiro CLI command with context"""
        
        # Enhanced prompt with context integration
        enhanced_prompt = f"""
{prompt_template}

CONTEXT INTEGRATION INSTRUCTIONS:
- Use the provided RAG context as the primary source of information
- Cite specific documents and data points from the context
- Ensure all financial metrics are sourced from the context data
- Cross-reference information across multiple context sources
- Highlight any gaps or inconsistencies in the context data

TICKER: {ticker}
ANALYSIS TYPE: {analysis_type.value.upper()}

Please analyze the company using the comprehensive context provided in the context file.
"""
        
        command = [
            self.kiro_cli_path,
            "chat",
            "--context-file", str(context_file),
            "--prompt", enhanced_prompt
        ]
        
        return command
    
    async def _execute_kiro_command(self, command: List[str]) -> Dict[str, Any]:
        """Execute Kiro CLI command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "content": stdout.decode('utf-8', errors='ignore').strip()
                }
            else:
                error_msg = stderr.decode('utf-8', errors='ignore').strip()
                logger.error(f"Kiro CLI error (return code {process.returncode}): {error_msg}")
                return {
                    "success": False,
                    "content": "",
                    "error": f"Kiro CLI failed: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"Failed to execute Kiro CLI: {e}")
            return {
                "success": False,
                "content": "",
                "error": f"Execution failed: {str(e)}"
            }

class RAGKiroIntegrationService:
    """Main service for RAG-Kiro integration"""
    
    def __init__(self, chroma_manager: OptimizedChromaDBManager = None,
                 kiro_cli_path: str = "kiro-cli",
                 redis_url: str = "redis://localhost:6379/0"):
        
        self.chroma_manager = chroma_manager or OptimizedChromaDBManager()
        self.context_preparer = ContextPreparer(self.chroma_manager)
        self.kiro_executor = KiroExecutor(kiro_cli_path)
        self.report_queue = ReportQueue(redis_url)
        
        # Performance tracking
        self.execution_metrics = []
        
        logger.info("RAG-Kiro Integration Service initialized")
    
    async def generate_analysis(self, ticker: str, analysis_type: AnalysisType,
                              queue_id: Optional[str] = None,
                              config: Optional[ContextConfig] = None) -> KiroExecutionResult:
        """Generate analysis using RAG-enhanced Kiro processing"""
        
        if config is None:
            config = ContextConfig()
        
        start_time = time.time()
        
        try:
            # Update progress
            if queue_id:
                await self.report_queue.update_progress(
                    queue_id, 10, f"Preparing context for {analysis_type.value}"
                )
            
            # Prepare context
            context_data = await self.context_preparer.prepare_context(
                ticker, analysis_type, config
            )
            
            # Update progress
            if queue_id:
                await self.report_queue.update_progress(
                    queue_id, 30, f"Executing Kiro analysis for {analysis_type.value}"
                )
            
            # Execute Kiro with context
            result = await self.kiro_executor.execute_with_context(
                ticker, analysis_type, context_data
            )
            
            # Update progress
            if queue_id:
                progress_map = {
                    AnalysisType.EXECUTIVE_SUMMARY: 25,
                    AnalysisType.FINANCIAL_ANALYSIS: 50,
                    AnalysisType.VALUATION_ANALYSIS: 75,
                    AnalysisType.RISK_ASSESSMENT: 90,
                    AnalysisType.COMPETITIVE_ANALYSIS: 95,
                    AnalysisType.ESG_ANALYSIS: 98
                }
                progress = progress_map.get(analysis_type, 80)
                await self.report_queue.update_progress(
                    queue_id, progress, f"Completed {analysis_type.value}"
                )
            
            # Track performance
            total_time = time.time() - start_time
            self.execution_metrics.append({
                "ticker": ticker,
                "analysis_type": analysis_type.value,
                "total_time": total_time,
                "context_tokens": result.context_tokens,
                "success": result.success,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Analysis completed for {ticker} {analysis_type.value} in {total_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis generation failed for {ticker} {analysis_type.value}: {e}")
            
            if queue_id:
                await self.report_queue.update_progress(
                    queue_id, -1, f"Failed: {str(e)}"
                )
            
            return KiroExecutionResult(
                success=False,
                content="",
                execution_time=time.time() - start_time,
                context_tokens=0,
                error_message=str(e)
            )
    
    async def generate_comprehensive_report(self, ticker: str, 
                                          queue_id: str,
                                          analysis_types: Optional[List[AnalysisType]] = None) -> Dict[str, Any]:
        """Generate comprehensive report with multiple analysis types"""
        
        if analysis_types is None:
            analysis_types = [
                AnalysisType.EXECUTIVE_SUMMARY,
                AnalysisType.FINANCIAL_ANALYSIS,
                AnalysisType.VALUATION_ANALYSIS,
                AnalysisType.RISK_ASSESSMENT
            ]
        
        start_time = time.time()
        results = {}
        
        try:
            await self.report_queue.update_progress(
                queue_id, 5, "Starting comprehensive report generation"
            )
            
            # Execute analyses sequentially to manage resources
            for i, analysis_type in enumerate(analysis_types):
                logger.info(f"Generating {analysis_type.value} for {ticker}")
                
                result = await self.generate_analysis(
                    ticker, analysis_type, queue_id
                )
                
                results[analysis_type.value] = {
                    "success": result.success,
                    "content": result.content,
                    "execution_time": result.execution_time,
                    "context_tokens": result.context_tokens,
                    "error_message": result.error_message,
                    "metadata": result.metadata
                }
                
                # Brief pause between analyses
                await asyncio.sleep(0.5)
            
            # Final progress update
            await self.report_queue.update_progress(
                queue_id, 100, "Report generation completed"
            )
            
            total_time = time.time() - start_time
            
            return {
                "ticker": ticker,
                "queue_id": queue_id,
                "total_execution_time": total_time,
                "analyses": results,
                "success": all(r["success"] for r in results.values()),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed for {ticker}: {e}")
            
            await self.report_queue.update_progress(
                queue_id, -1, f"Report generation failed: {str(e)}"
            )
            
            return {
                "ticker": ticker,
                "queue_id": queue_id,
                "success": False,
                "error": str(e),
                "analyses": results
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get integration performance metrics"""
        if not self.execution_metrics:
            return {"status": "No executions recorded"}
        
        successful_executions = [m for m in self.execution_metrics if m["success"]]
        
        if not successful_executions:
            return {"status": "No successful executions"}
        
        execution_times = [m["total_time"] for m in successful_executions]
        context_tokens = [m["context_tokens"] for m in successful_executions]
        
        return {
            "total_executions": len(self.execution_metrics),
            "successful_executions": len(successful_executions),
            "success_rate": len(successful_executions) / len(self.execution_metrics),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "avg_context_tokens": sum(context_tokens) / len(context_tokens),
            "chroma_performance": self.chroma_manager.get_performance_metrics()
        }

# Global service instance
rag_kiro_service = RAGKiroIntegrationService()