"""
Real Kiro CLI Agent Integration for Production - WITH PROCESS MANAGEMENT
Executes actual Kiro CLI subagents for report generation with proper cleanup
"""

import asyncio
import subprocess
import json
import logging
import signal
import os
from typing import Dict, Any, Set
from datetime import datetime
from content_pipeline import clean_ai_content

logger = logging.getLogger(__name__)

# Global set to track active subprocess PIDs
active_subprocesses: Set[int] = set()

def cleanup_subprocesses():
    """Clean up only OUR tracked subprocesses"""
    global active_subprocesses
    logger.info(f"🧹 Cleaning up {len(active_subprocesses)} MarketMind subprocesses")
    
    for pid in list(active_subprocesses):
        try:
            # Only kill processes we created and are tracking
            os.kill(pid, signal.SIGTERM)
            logger.info(f"🔪 Terminated MarketMind subprocess {pid}")
        except (OSError, ProcessLookupError):
            pass  # Process already dead
    
    active_subprocesses.clear()

def signal_handler(signum, frame):
    """Handle interrupt signals - only kill our subprocesses"""
    logger.info(f"📡 MarketMind received signal {signum}, cleaning up only our subprocesses...")
    cleanup_subprocesses()
    # Don't exit - let the main process handle the signal

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class RealKiroAgent:
    """Real Kiro CLI agent that executes actual prompts"""
    
    def __init__(self, section_name: str, prompt_content: str, pages: int):
        self.section_name = section_name
        self.prompt_content = prompt_content
        self.pages = pages
    
    async def generate_analysis(self, ticker: str, progress_storage: Dict, report_id: str) -> Dict[str, Any]:
        """Generate analysis using real Kiro CLI"""
        logger.info(f"🚀 Starting REAL Kiro CLI for {self.section_name} - {ticker}")
        
        try:
            # Safe access to activity_log
            if "activity_log" not in progress_storage[report_id]:
                progress_storage[report_id]["activity_log"] = []
                
            # Execute real Kiro CLI command
            progress_storage[report_id]["activity_log"].append(f"⚡ Executing: kiro-cli chat for {ticker}")
            progress_storage[report_id]["activity_log"].append(f"🧠 AI processing {self.section_name} analysis...")
            
            start_time = datetime.now()
            result = await self._execute_kiro_cli(ticker, progress_storage, report_id)
            
            # Mark agent as completed
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            progress_storage[report_id]["activity_log"].append(f"✅ Completed {self.section_name} analysis in {duration:.1f}s")
            progress_storage[report_id]["activity_log"].append(f"📊 Generated {len(result.split())} words of content")
            
            # Structure the result
            structured_result = {
                "title": f"{self.section_name.replace('_', ' ').title()}",
                "content": result,
                "generated_at": datetime.now().isoformat(),
                "generated_by": "real_kiro_cli",
                "ticker": ticker,
                "pages": self.pages
            }
            
            logger.info(f"✅ Completed REAL Kiro CLI for {self.section_name}")
            return structured_result
            
        except Exception as e:
            logger.error(f"❌ Kiro CLI failed for {self.section_name}: {str(e)}")
            logger.error(f"❌ Full error details: {repr(e)}")
            
            # Safe access to activity_log
            if "activity_log" not in progress_storage[report_id]:
                progress_storage[report_id]["activity_log"] = []
            progress_storage[report_id]["activity_log"].append(f"❌ Error in {self.section_name}: {str(e)}")
            
            # Return error result instead of crashing
            return {
                "title": f"{self.section_name.replace('_', ' ').title()}",
                "content": f"Analysis generation failed: {str(e)}",
                "generated_at": datetime.now().isoformat(),
                "generated_by": "error",
                "ticker": ticker,
                "error": str(e)
            }
    
    async def _execute_kiro_cli(self, ticker: str, progress_storage: Dict, report_id: str) -> str:
        """Execute actual Kiro CLI command with proper cleanup"""
        global active_subprocesses
        
        # Prepare the prompt
        full_prompt = f"""
Analyze {ticker} stock for institutional investment research.

Section: {self.section_name}
Target Length: {self.pages} pages
Analysis Type: Professional institutional-grade financial research

{self.prompt_content}

Provide comprehensive analysis with specific data points, metrics, and investment insights.
"""
        
        logger.info(f"Executing Kiro CLI for {ticker} - Section: {self.section_name}")
        
        # Safe access to activity_log
        if "activity_log" not in progress_storage[report_id]:
            progress_storage[report_id]["activity_log"] = []
        
        progress_storage[report_id]["activity_log"].append(f"🧠 Starting {self.section_name.replace('_', ' ').title()} analysis...")
        
        process = None
        start_time = datetime.now()
        try:
            # Execute Kiro CLI
            cmd = ["kiro-cli", "chat"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/mnt/c/kiro"
            )
            
            # Track ONLY our subprocess PID (not other kiro-cli processes)
            active_subprocesses.add(process.pid)
            # Don't log PID - users don't need to see it
            
            # All sections get 15 minutes timeout
            timeout_seconds = 900
            
            # Execute with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=full_prompt.encode()),
                timeout=timeout_seconds
            )
            
            # Process completed - remove from tracking
            active_subprocesses.discard(process.pid)
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                progress_storage[report_id]["activity_log"].append(f"❌ {self.section_name.replace('_', ' ').title()} failed: {error_msg}")
                raise Exception(f"Kiro CLI failed: {error_msg}")
            
            raw_output = stdout.decode()
            
            # Calculate completion stats
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            
            # Clean up ANSI codes and extract content
            import re
            clean_output = re.sub(r'\x1b\[[0-9;]*m', '', raw_output)
            
            # Extract substantial content
            if len(clean_output.strip()) < 100:
                raise Exception(f"Insufficient content generated: {len(clean_output)} characters")
            
            # Clean AI-generated content
            cleaned_content = clean_ai_content(clean_output.strip())
            word_count = len(cleaned_content.split())
            
            # Log completion with stats
            progress_storage[report_id]["activity_log"].append(f"✅ {self.section_name.replace('_', ' ').title()} completed - {word_count:,} words in {duration} seconds")
            
            return cleaned_content
            
        except asyncio.TimeoutError:
            timeout_minutes = timeout_seconds // 60
            progress_storage[report_id]["activity_log"].append(f"⏰ {self.section_name.replace('_', ' ').title()} timed out after {timeout_minutes} minutes")
            if process and process.returncode is None:
                # Kill the process and remove from tracking
                process.kill()
                active_subprocesses.discard(process.pid)
                await process.wait()
            raise Exception(f"Kiro CLI timeout after {timeout_minutes} minutes for {self.section_name}")
            
        except Exception as e:
            # Clean up process on any error
            if process and process.returncode is None:
                process.kill()
                active_subprocesses.discard(process.pid)
                await process.wait()
            progress_storage[report_id]["activity_log"].append(f"❌ {self.section_name.replace('_', ' ').title()} failed: {str(e)}")
            raise
        
        finally:
            # Ensure process is cleaned up
            if process:
                active_subprocesses.discard(process.pid)

# Define the 8 specialized agents with word limits
REAL_KIRO_AGENTS = {
    "executive_summary": RealKiroAgent(
        "executive_summary",
        """Generate a comprehensive executive summary (TARGET: 800-1000 words MAX):
        1. Investment recommendation (BUY/HOLD/SELL) with price target
        2. Key financial metrics and valuation multiples
        3. Core investment thesis (3-5 key points)
        4. Primary risks and concerns
        5. Financial performance snapshot
        
        Include specific numbers, percentages, and actionable insights.
        BE CONCISE - Maximum 1000 words.""",
        2
    ),
    "company_analysis": RealKiroAgent(
        "company_analysis", 
        """Analyze the company's business model, competitive position, and strategic initiatives (TARGET: 1500-2000 words MAX):
        1. Business model and revenue streams
        2. Competitive landscape and market position
        3. Products/services portfolio and innovation pipeline
        4. Management team and corporate strategy
        5. Key partnerships and ecosystem
        
        Provide detailed analysis with specific examples and market context.
        BE CONCISE - Maximum 2000 words.""",
        5
    ),
    "financial_analysis": RealKiroAgent(
        "financial_analysis",
        """Perform comprehensive financial analysis (TARGET: 2500-3000 words MAX):
        1. Revenue analysis (historical trends, growth drivers, segment breakdown)
        2. Profitability metrics (margins, efficiency ratios, peer comparison)
        3. Balance sheet strength (assets, liabilities, working capital)
        4. Cash flow analysis (operating, investing, financing activities)
        5. Financial projections (2-3 year forward estimates)
        
        Include detailed financial tables and trend analysis.
        BE CONCISE - Maximum 3000 words.""",
        8
    ),
    "valuation_analysis": RealKiroAgent(
        "valuation_analysis",
        """Perform FOCUSED valuation analysis (TARGET: 2000-2500 words):
        
        **IMPORTANT: Choose appropriate valuation methods for the company type:**
        
        For MATURE companies (stable FCF):
        1. DCF Analysis (800 words): 3-year projections, WACC, terminal value
        2. Peer P/E & EV/EBITDA multiples (600 words)
        
        For GROWTH companies (negative/low FCF):
        1. Forward P/E & P/S multiples (800 words): NTM earnings, revenue multiples
        2. PEG ratio analysis (400 words)
        
        For FINANCIAL companies (banks, insurance):
        1. P/B & P/TBV multiples (800 words): Book value, tangible book
        2. ROE-based valuation (400 words)
        
        For ALL companies:
        3. Peer Comparison (600 words):
           - Select 3-4 comparable companies
           - Apply appropriate multiples for industry
           - Implied valuation range
        
        4. Scenario Analysis (500 words):
           - Bull case price target
           - Base case price target
           - Bear case price target
        
        5. Recommendation (300 words):
           - Blended fair value using appropriate methods
           - Risk-adjusted target
           - Investment thesis
        
        BE CONCISE. Use methods appropriate for the business model. Maximum 2500 words.""",
        6
    ),
    "risk_assessment": RealKiroAgent(
        "risk_assessment",
        """Analyze key risks and mitigation strategies (TARGET: 1000-1500 words MAX):
        1. Market and competitive risks
        2. Operational and execution risks
        3. Financial and liquidity risks
        4. Regulatory and legal risks
        5. Risk mitigation strategies and management approach
        
        Provide specific risk assessment with impact analysis.
        BE CONCISE - Maximum 1500 words.""",
        3
    ),
    "market_analysis": RealKiroAgent(
        "market_analysis",
        """Conduct comprehensive market analysis (TARGET: 1500-2000 words MAX):
        1. Industry overview and market size
        2. Competitive landscape and market share analysis  
        3. Growth trends and market dynamics
        4. Regulatory environment and industry challenges
        5. Market opportunities and threats
        
        Provide specific data points, market metrics, and competitive positioning analysis.
        BE CONCISE - Maximum 2000 words.""",
        4
    ),
    "technical_analysis": RealKiroAgent(
        "technical_analysis",
        """Provide technical analysis with chart patterns and price targets (TARGET: 1500-2000 words MAX):
        1. Price trend analysis and momentum indicators
        2. Support and resistance levels
        3. Volume analysis and trading patterns
        4. Technical indicators (RSI, MACD, moving averages)
        5. Price targets and technical outlook
        
        Include specific technical levels and actionable insights.
        BE CONCISE - Maximum 2000 words.""",
        2
    ),
    "investment_thesis": RealKiroAgent(
        "investment_thesis",
        """Synthesize final investment thesis and recommendation (TARGET: 1500-2000 words MAX):
        1. Core investment rationale and key catalysts
        2. Risk/reward profile and expected returns
        3. Portfolio positioning and allocation guidance
        4. Investment timeframe and exit strategy
        5. Final recommendation with conviction level
        
        Provide clear, actionable investment thesis with supporting evidence.
        BE CONCISE - Maximum 2000 words.""",
        2
    )
}
