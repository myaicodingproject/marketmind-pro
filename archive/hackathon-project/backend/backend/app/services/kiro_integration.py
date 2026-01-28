"""
Kiro CLI Integration for Document Processing Pipeline

This module integrates the document processing pipeline with Kiro CLI for:
- Context preparation for financial analysis prompts
- Real-time document processing and retrieval
- Structured context formatting for different analysis types
- Quality assurance and validation
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from .document_processor import DocumentProcessor, ProcessedDocument, DocumentType
from .sec_filing_parser import SECFilingParser
from .document_chunker import DocumentChunker, DocumentChunk
from .semantic_search import SemanticSearchEngine, SearchMode, SearchResult

logger = logging.getLogger(__name__)

class KiroContextPreparer:
    """Prepare optimized context for Kiro CLI prompts"""
    
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.document_processor = DocumentProcessor(chroma_path)
        self.sec_parser = SECFilingParser()
        self.chunker = DocumentChunker()
        self.search_engine = SemanticSearchEngine(chroma_path)
        
        # Context templates for different analysis types
        self.context_templates = {
            "company_overview": {
                "max_chunks": 15,
                "search_queries": [
                    "business operations products services",
                    "company overview competitive position",
                    "market position industry analysis"
                ],
                "required_sections": ["business", "management_discussion"],
                "weight_recent": 0.3
            },
            "financial_analysis": {
                "max_chunks": 20,
                "search_queries": [
                    "revenue income earnings financial performance",
                    "financial statements balance sheet cash flow",
                    "profitability margins ratios metrics"
                ],
                "required_sections": ["financial_statements", "management_discussion"],
                "weight_recent": 0.4
            },
            "risk_assessment": {
                "max_chunks": 12,
                "search_queries": [
                    "risk factors uncertainties challenges",
                    "regulatory compliance legal proceedings",
                    "market risks operational risks"
                ],
                "required_sections": ["risk_factors", "legal_proceedings"],
                "weight_recent": 0.5
            },
            "valuation_analysis": {
                "max_chunks": 18,
                "search_queries": [
                    "valuation metrics ratios multiples",
                    "dcf discounted cash flow comparable",
                    "market value enterprise value"
                ],
                "required_sections": ["financial_statements", "management_discussion"],
                "weight_recent": 0.4
            },
            "investment_thesis": {
                "max_chunks": 25,
                "search_queries": [
                    "investment opportunity growth prospects",
                    "competitive advantages moat strategy",
                    "future outlook guidance projections"
                ],
                "required_sections": ["business", "management_discussion", "risk_factors"],
                "weight_recent": 0.3
            }
        }
    
    async def prepare_comprehensive_context(self, ticker: str, analysis_type: str = "investment_thesis") -> Dict[str, str]:
        """Prepare comprehensive context for Kiro analysis"""
        logger.info(f"Preparing {analysis_type} context for {ticker}")
        
        template = self.context_templates.get(analysis_type, self.context_templates["investment_thesis"])
        
        # Get context sections
        contexts = {}
        
        # 1. Business Overview Context
        contexts["business_overview"] = await self._get_business_context(ticker)
        
        # 2. Financial Performance Context
        contexts["financial_performance"] = await self._get_financial_context(ticker)
        
        # 3. Risk Factors Context
        contexts["risk_factors"] = await self._get_risk_context(ticker)
        
        # 4. Recent Developments Context
        contexts["recent_developments"] = await self._get_recent_developments_context(ticker)
        
        # 5. Industry and Competitive Context
        contexts["competitive_position"] = await self._get_competitive_context(ticker)
        
        # 6. Management Discussion Context
        contexts["management_discussion"] = await self._get_management_discussion_context(ticker)
        
        # 7. Financial Tables Context
        contexts["financial_tables"] = await self._get_financial_tables_context(ticker)
        
        logger.info(f"Prepared {len(contexts)} context sections for {ticker}")
        return contexts
    
    async def _get_business_context(self, ticker: str) -> str:
        """Get business overview and operations context"""
        results = await self.search_engine.search(
            query="business operations products services competitive position market share",
            ticker=ticker,
            search_mode=SearchMode.FINANCIAL,
            max_results=8
        )
        
        return self._format_context_section("Business Overview", results, ticker)
    
    async def _get_financial_context(self, ticker: str) -> str:
        """Get financial performance context"""
        results = await self.search_engine.search(
            query="revenue income earnings financial performance profitability margins",
            ticker=ticker,
            search_mode=SearchMode.FINANCIAL,
            max_results=10
        )
        
        return self._format_context_section("Financial Performance", results, ticker)
    
    async def _get_risk_context(self, ticker: str) -> str:
        """Get risk factors context"""
        results = await self.search_engine.search(
            query="risk factors uncertainties challenges regulatory compliance",
            ticker=ticker,
            search_mode=SearchMode.FINANCIAL,
            max_results=8
        )
        
        return self._format_context_section("Risk Factors", results, ticker)
    
    async def _get_recent_developments_context(self, ticker: str) -> str:
        """Get recent developments and current events context"""
        results = await self.search_engine.search(
            query="recent developments quarterly results current events guidance",
            ticker=ticker,
            search_mode=SearchMode.TEMPORAL,
            max_results=6
        )
        
        return self._format_context_section("Recent Developments", results, ticker)
    
    async def _get_competitive_context(self, ticker: str) -> str:
        """Get competitive position and industry context"""
        results = await self.search_engine.search(
            query="competitive position industry analysis market competition",
            ticker=ticker,
            search_mode=SearchMode.HYBRID,
            max_results=6
        )
        
        return self._format_context_section("Competitive Position", results, ticker)
    
    async def _get_management_discussion_context(self, ticker: str) -> str:
        """Get management discussion and analysis context"""
        results = await self.search_engine.search(
            query="management discussion analysis md&a liquidity capital resources",
            ticker=ticker,
            search_mode=SearchMode.FINANCIAL,
            max_results=8
        )
        
        return self._format_context_section("Management Discussion", results, ticker)
    
    async def _get_financial_tables_context(self, ticker: str) -> str:
        """Get financial tables and quantitative data context"""
        results = await self.search_engine.search(
            query="consolidated statements financial data income balance sheet cash flow",
            ticker=ticker,
            document_types=["financial_statement", "10-K", "10-Q"],
            search_mode=SearchMode.FINANCIAL,
            max_results=8
        )
        
        # Filter for table-heavy content
        table_results = [r for r in results if r.metadata.get('chunk_type') == 'table' or 
                        'table' in r.content.lower() or 'consolidated' in r.content.lower()]
        
        return self._format_context_section("Financial Tables", table_results[:6], ticker)
    
    def _format_context_section(self, section_title: str, results: List[SearchResult], ticker: str) -> str:
        """Format search results into a context section"""
        if not results:
            return f"=== {section_title.upper()} ===\nNo relevant information found for {ticker}.\n"
        
        context_lines = [f"=== {section_title.upper()} ==="]
        
        # Group results by document type and date
        grouped_results = {}
        for result in results:
            doc_key = f"{result.document_type}_{result.filing_date or 'unknown'}"
            if doc_key not in grouped_results:
                grouped_results[doc_key] = []
            grouped_results[doc_key].append(result)
        
        # Sort by date (most recent first)
        sorted_groups = sorted(grouped_results.items(), 
                             key=lambda x: x[0].split('_')[1] if '_' in x[0] else '0000', 
                             reverse=True)
        
        for doc_key, group_results in sorted_groups[:3]:  # Top 3 document groups
            doc_type, date = doc_key.split('_', 1)
            
            context_lines.append(f"\n--- {doc_type.upper()} ({date}) ---")
            
            for result in group_results[:2]:  # Top 2 results per document
                # Add relevance and metadata info
                metadata_info = []
                if result.section_name:
                    metadata_info.append(f"Section: {result.section_name}")
                if result.score > 0:
                    metadata_info.append(f"Relevance: {result.score:.2f}")
                
                if metadata_info:
                    context_lines.append(f"[{' | '.join(metadata_info)}]")
                
                # Add content with length limit
                content = result.content.strip()
                if len(content) > 800:
                    content = content[:800] + "..."
                
                context_lines.append(content)
                context_lines.append("")  # Empty line between results
        
        return "\n".join(context_lines)
    
    async def prepare_prompt_specific_context(self, ticker: str, prompt_type: str, 
                                            custom_query: Optional[str] = None) -> str:
        """Prepare context for specific Kiro prompt types"""
        
        # Define prompt-specific search strategies
        prompt_strategies = {
            "company-overview-investment-thesis": {
                "queries": [
                    "business model competitive advantages",
                    "investment opportunity growth prospects",
                    "market position industry leadership"
                ],
                "max_results": 15
            },
            "financial-analysis-key-metrics": {
                "queries": [
                    "financial metrics ratios performance",
                    "revenue growth profitability margins",
                    "key financial indicators"
                ],
                "max_results": 12
            },
            "risk-assessment-summary": {
                "queries": [
                    "risk factors key risks uncertainties",
                    "regulatory risks operational challenges",
                    "market risks competitive threats"
                ],
                "max_results": 10
            },
            "valuation-analysis-price-target": {
                "queries": [
                    "valuation metrics dcf analysis",
                    "comparable companies peer analysis",
                    "price targets fair value"
                ],
                "max_results": 12
            }
        }
        
        strategy = prompt_strategies.get(prompt_type, {
            "queries": [custom_query or "comprehensive analysis"],
            "max_results": 15
        })
        
        # Execute searches
        all_results = []
        for query in strategy["queries"]:
            results = await self.search_engine.search(
                query=query,
                ticker=ticker,
                search_mode=SearchMode.FINANCIAL,
                max_results=strategy["max_results"] // len(strategy["queries"])
            )
            all_results.extend(results)
        
        # Remove duplicates and sort by relevance
        unique_results = {}
        for result in all_results:
            if result.chunk_id not in unique_results or result.score > unique_results[result.chunk_id].score:
                unique_results[result.chunk_id] = result
        
        sorted_results = sorted(unique_results.values(), key=lambda x: x.score, reverse=True)
        
        # Format for Kiro prompt
        return self._format_kiro_context(sorted_results[:strategy["max_results"]], ticker, prompt_type)
    
    def _format_kiro_context(self, results: List[SearchResult], ticker: str, prompt_type: str) -> str:
        """Format context specifically for Kiro CLI consumption"""
        if not results:
            return f"Limited context available for {ticker} analysis."
        
        context_sections = []
        
        # Add header with metadata
        context_sections.append(f"CONTEXT FOR {ticker.upper()} - {prompt_type.upper()}")
        context_sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        context_sections.append(f"Total Sources: {len(results)}")
        context_sections.append("")
        
        # Group by document type for better organization
        by_doc_type = {}
        for result in results:
            doc_type = result.document_type or "unknown"
            if doc_type not in by_doc_type:
                by_doc_type[doc_type] = []
            by_doc_type[doc_type].append(result)
        
        # Format each document type section
        for doc_type, doc_results in by_doc_type.items():
            context_sections.append(f"## {doc_type.upper().replace('_', ' ')} ##")
            
            for i, result in enumerate(doc_results[:4], 1):  # Limit per document type
                # Add source information
                source_info = f"Source {i}"
                if result.filing_date:
                    source_info += f" ({result.filing_date})"
                if result.section_name:
                    source_info += f" - {result.section_name}"
                
                context_sections.append(f"[{source_info}]")
                
                # Add content with smart truncation
                content = result.content.strip()
                
                # For financial data, preserve key numbers
                if result.contains_numbers and len(content) > 600:
                    # Try to keep sentences with numbers
                    sentences = content.split('. ')
                    important_sentences = []
                    other_sentences = []
                    
                    for sentence in sentences:
                        if any(char.isdigit() for char in sentence) or '$' in sentence or '%' in sentence:
                            important_sentences.append(sentence)
                        else:
                            other_sentences.append(sentence)
                    
                    # Combine important sentences first, then others as space allows
                    formatted_content = '. '.join(important_sentences)
                    remaining_space = 600 - len(formatted_content)
                    
                    if remaining_space > 100 and other_sentences:
                        additional_content = '. '.join(other_sentences)[:remaining_space]
                        formatted_content += '. ' + additional_content
                    
                    content = formatted_content + "..."
                elif len(content) > 600:
                    content = content[:600] + "..."
                
                context_sections.append(content)
                context_sections.append("")  # Empty line
        
        # Add summary statistics
        context_sections.append("## CONTEXT SUMMARY ##")
        context_sections.append(f"Document Types: {', '.join(by_doc_type.keys())}")
        
        # Extract key financial concepts
        all_concepts = []
        for result in results:
            all_concepts.extend(result.financial_concepts)
        
        concept_counts = {}
        for concept in all_concepts:
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_concepts:
            context_sections.append(f"Key Financial Concepts: {', '.join([c[0] for c in top_concepts])}")
        
        # Date range
        dates = [r.filing_date for r in results if r.filing_date]
        if dates:
            context_sections.append(f"Date Range: {min(dates)} to {max(dates)}")
        
        return "\n".join(context_sections)
    
    async def validate_context_quality(self, context: str, ticker: str) -> Dict[str, Any]:
        """Validate the quality of prepared context"""
        validation_results = {
            "ticker": ticker,
            "context_length": len(context),
            "word_count": len(context.split()),
            "has_financial_data": False,
            "has_recent_data": False,
            "document_diversity": 0,
            "quality_score": 0.0,
            "recommendations": []
        }
        
        # Check for financial data
        financial_indicators = ['$', '%', 'million', 'billion', 'revenue', 'income', 'earnings']
        validation_results["has_financial_data"] = any(indicator in context.lower() for indicator in financial_indicators)
        
        # Check for recent data (within last 2 years)
        current_year = datetime.now().year
        recent_years = [str(current_year), str(current_year - 1)]
        validation_results["has_recent_data"] = any(year in context for year in recent_years)
        
        # Check document diversity
        doc_types = set()
        for line in context.split('\n'):
            if '##' in line and '##' in line:
                doc_types.add(line.strip('#').strip())
        validation_results["document_diversity"] = len(doc_types)
        
        # Calculate quality score
        quality_factors = [
            validation_results["context_length"] > 1000,  # Sufficient length
            validation_results["has_financial_data"],      # Contains financial data
            validation_results["has_recent_data"],         # Has recent information
            validation_results["document_diversity"] >= 2, # Multiple document types
            validation_results["word_count"] > 200        # Adequate word count
        ]
        
        validation_results["quality_score"] = sum(quality_factors) / len(quality_factors)
        
        # Generate recommendations
        if validation_results["context_length"] < 500:
            validation_results["recommendations"].append("Context is too short - consider expanding search criteria")
        
        if not validation_results["has_financial_data"]:
            validation_results["recommendations"].append("Context lacks financial data - include more financial statements")
        
        if not validation_results["has_recent_data"]:
            validation_results["recommendations"].append("Context lacks recent data - prioritize recent filings")
        
        if validation_results["document_diversity"] < 2:
            validation_results["recommendations"].append("Context lacks diversity - include multiple document types")
        
        return validation_results
    
    async def process_new_document(self, ticker: str, document_url: str, 
                                 document_metadata: Dict[str, Any]) -> ProcessedDocument:
        """Process a new document and add to the knowledge base"""
        logger.info(f"Processing new document for {ticker}: {document_url}")
        
        try:
            # Parse the document
            parsed_data = await self.sec_parser.parse_sec_filing(document_url, document_metadata)
            
            # Process through document processor
            processed_doc = await self.document_processor.process_sec_filing(
                ticker, document_url, document_metadata
            )
            
            logger.info(f"Successfully processed document {processed_doc.document_id}")
            return processed_doc
        
        except Exception as e:
            logger.error(f"Failed to process document for {ticker}: {e}")
            raise
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = {
            "document_processor": self.document_processor.get_processing_stats(),
            "search_engine": self.search_engine.get_search_stats(),
            "context_templates": len(self.context_templates),
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.document_processor.cleanup()
        await self.sec_parser.cleanup()

# Utility function for testing
async def test_kiro_integration():
    """Test the Kiro integration with sample data"""
    preparer = KiroContextPreparer()
    
    try:
        # Test context preparation
        context = await preparer.prepare_comprehensive_context("AAPL", "investment_thesis")
        print(f"Generated context length: {len(context)} characters")
        
        # Test validation
        validation = await preparer.validate_context_quality(context["business_overview"], "AAPL")
        print(f"Context quality score: {validation['quality_score']:.2f}")
        
        # Test prompt-specific context
        prompt_context = await preparer.prepare_prompt_specific_context(
            "AAPL", "company-overview-investment-thesis"
        )
        print(f"Prompt context length: {len(prompt_context)} characters")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        await preparer.cleanup()

if __name__ == "__main__":
    asyncio.run(test_kiro_integration())