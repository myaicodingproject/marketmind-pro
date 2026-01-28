# A4.5: RAG-Kiro Integration - CRITICAL Context Bridging

import chromadb
from typing import List, Dict, Any
import asyncio
from pathlib import Path
import json

class RAGKiroIntegration:
    def __init__(self, chromadb_path: str, kiro_cli_path: str):
        self.chroma_client = chromadb.PersistentClient(path=chromadb_path)
        self.kiro_cli_path = Path(kiro_cli_path)
        self.collections = {}
        self._init_collections()
    
    def _init_collections(self):
        """Initialize ChromaDB collections"""
        self.collections = {
            'sec_filings': self.chroma_client.get_or_create_collection("sec_filings"),
            'financial_data': self.chroma_client.get_or_create_collection("financial_data"),
            'market_data': self.chroma_client.get_or_create_collection("market_data")
        }
    
    async def prepare_context_for_kiro(self, ticker: str, analysis_type: str) -> str:
        """Prepare optimized context for Kiro CLI processing"""
        
        # Retrieve relevant documents
        contexts = await asyncio.gather(
            self._get_sec_context(ticker),
            self._get_financial_context(ticker),
            self._get_market_context(ticker)
        )
        
        # Combine and optimize context
        combined_context = self._optimize_context_for_kiro(contexts, analysis_type)
        
        return combined_context
    
    async def _get_sec_context(self, ticker: str) -> List[str]:
        """Retrieve SEC filing context"""
        results = self.collections['sec_filings'].query(
            query_texts=[f"{ticker} business operations risks financial performance"],
            n_results=5
        )
        return results['documents'][0] if results['documents'] else []
    
    async def _get_financial_context(self, ticker: str) -> List[str]:
        """Retrieve financial data context"""
        results = self.collections['financial_data'].query(
            query_texts=[f"{ticker} revenue earnings cash flow balance sheet"],
            n_results=3
        )
        return results['documents'][0] if results['documents'] else []
    
    async def _get_market_context(self, ticker: str) -> List[str]:
        """Retrieve market analysis context"""
        results = self.collections['market_data'].query(
            query_texts=[f"{ticker} industry competition market position"],
            n_results=3
        )
        return results['documents'][0] if results['documents'] else []
    
    def _optimize_context_for_kiro(self, contexts: List[List[str]], analysis_type: str) -> str:
        """Optimize context for Kiro CLI token limits"""
        
        # Flatten and prioritize context
        all_context = []
        for context_list in contexts:
            all_context.extend(context_list)
        
        # Truncate to optimal length (8000 tokens ≈ 32000 chars)
        combined = "\n\n".join(all_context)
        if len(combined) > 32000:
            combined = combined[:32000] + "..."
        
        # Add analysis-specific instructions
        context_template = f"""
FINANCIAL ANALYSIS CONTEXT FOR {analysis_type.upper()}:

{combined}

ANALYSIS INSTRUCTIONS:
- Focus on quantitative metrics and financial ratios
- Include peer comparison data where available
- Highlight key risks and growth drivers
- Provide specific numerical targets and projections
"""
        
        return context_template
    
    async def execute_kiro_with_context(self, ticker: str, prompt_type: str, context: str) -> str:
        """Execute Kiro CLI with prepared context"""
        
        # Create context file
        context_file = Path(f"/tmp/context_{ticker}_{prompt_type}.txt")
        context_file.write_text(context)
        
        # Prepare Kiro command
        kiro_prompts = {
            'executive_summary': 'Generate executive summary with price target and rating',
            'financial_analysis': 'Perform detailed financial analysis with 3-year projections',
            'valuation': 'Calculate DCF valuation with sensitivity analysis',
            'risk_assessment': 'Identify and quantify key investment risks'
        }
        
        prompt = kiro_prompts.get(prompt_type, 'Analyze the provided financial data')
        
        # Execute Kiro CLI
        import subprocess
        result = await asyncio.create_subprocess_exec(
            str(self.kiro_cli_path), 'chat',
            '--context-file', str(context_file),
            '--prompt', f"{prompt}\n\nContext: {context[:1000]}...",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        # Cleanup
        context_file.unlink(missing_ok=True)
        
        if result.returncode != 0:
            raise Exception(f"Kiro CLI error: {stderr.decode()}")
        
        return stdout.decode()
    
    async def process_report_section(self, ticker: str, section: str, queue_id: str) -> Dict[str, Any]:
        """Process individual report section with RAG context"""
        
        # Prepare context
        context = await self.prepare_context_for_kiro(ticker, section)
        
        # Execute Kiro processing
        result = await self.execute_kiro_with_context(ticker, section, context)
        
        # Update progress
        from app.services.report_queue import ReportQueue
        queue = ReportQueue("redis://localhost:6379/0")
        
        progress_map = {
            'executive_summary': 25,
            'financial_analysis': 50,
            'valuation': 75,
            'risk_assessment': 90
        }
        
        await queue.update_progress(queue_id, progress_map.get(section, 10), f"Completed {section}")
        
        return {
            'section': section,
            'content': result,
            'context_used': len(context),
            'ticker': ticker
        }

# Context optimization utilities
class ContextOptimizer:
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into optimal chunks for embedding"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    @staticmethod
    def rank_context_relevance(contexts: List[str], query: str) -> List[str]:
        """Rank contexts by relevance to query"""
        # Simple keyword-based ranking
        query_words = set(query.lower().split())
        
        scored_contexts = []
        for context in contexts:
            context_words = set(context.lower().split())
            score = len(query_words.intersection(context_words))
            scored_contexts.append((score, context))
        
        # Sort by score descending
        scored_contexts.sort(key=lambda x: x[0], reverse=True)
        
        return [context for score, context in scored_contexts]