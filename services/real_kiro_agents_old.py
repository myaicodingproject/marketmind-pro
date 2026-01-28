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
from .content_pipeline import clean_ai_content

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

# Define the 8 specialized agents matching institutional research format
REAL_KIRO_AGENTS = {
    "executive_summary": RealKiroAgent(
        "executive_summary",
        """Generate an institutional-quality Executive Summary (TARGET: 800-1200 words):
        
        Structure as professional research report opening:
        1. **Company Overview** - Brief description, ticker, market cap, sector
        2. **Investment Recommendation** - Clear BUY/HOLD/SELL with price target and timeframe
        3. **Key Investment Highlights** - 4-5 compelling reasons to invest
        4. **Investment Risk Warnings** - Primary risks and concerns
        5. **Financial Performance Summary** - Key metrics, growth rates, profitability
        6. **Future Outlook & Investment Advice** - 12-month outlook and strategic direction
        
        Use institutional language with specific numbers, percentages, and actionable insights.
        Include price targets, valuation multiples, and clear investment thesis.""",
        2
    ),
    "company_history": RealKiroAgent(
        "company_history", 
        """Generate Chapter 1: Company History and Evolution (TARGET: 1500-2000 words):
        
        Structure as detailed corporate history:
        1. **Company Formation Background** - Founding story, initial vision, key founders
        2. **Important Development Milestones** - Chronological timeline with specific dates:
           - Early years and initial growth (founding to 5 years)
           - Expansion phase (major acquisitions, IPO, geographic expansion)
           - Transformation period (strategic pivots, major deals)
           - Recent developments (last 3-5 years)
        3. **Company Vision and Mission** - Current strategic direction and core values
        4. **Transformation Journey Summary** - How company evolved to current state
        
        Include specific dates, key executives, major acquisitions, and strategic turning points.
        Write in institutional research style with detailed corporate chronology.""",
        3
    ),
    "leadership_analysis": RealKiroAgent(
        "leadership_analysis",
        """Generate Chapter 2: Company Leadership (TARGET: 1200-1500 words):
        
        Structure as comprehensive leadership analysis:
        1. **Leadership Team Characteristics** - Management structure and decision-making style
        2. **Key Executive Backgrounds** - CEO, CFO, and key leaders:
           - Professional experience and track record
           - Previous roles and achievements
           - Leadership style and strategic vision
           - Any controversies or challenges
        3. **Strategic Leadership Decisions** - Major strategic moves under current leadership
        4. **Corporate Governance** - Board composition, compensation, shareholder relations
        
        Focus on leadership quality, strategic vision, execution capability, and governance.
        Include specific examples of leadership decisions and their outcomes.""",
        3
    ),
    "business_model": RealKiroAgent(
        "business_model",
        """Generate Chapter 3: Business Model Analysis (TARGET: 2000-2500 words):
        
        Structure as detailed business model breakdown:
        1. **Core Business Model** - How the company creates and captures value
        2. **Revenue Streams and Business Lines** - Detailed breakdown by segment/geography
        3. **Geographic Revenue Analysis** - Regional performance and market presence
        4. **Customer Base Analysis** - Key customer segments and relationships
        5. **Competitive Advantages** - Sustainable competitive moats and differentiators
        6. **Business Model Evolution** - How model has changed and future direction
        
        Include revenue percentages by segment, geographic breakdown, customer concentration,
        and competitive positioning. Use charts and data to support analysis.""",
        4
    ),
    "financial_analysis": RealKiroAgent(
        "financial_analysis",
        """Generate Chapter 4: Financial Analysis (TARGET: 2500-3000 words):
        
        Structure as comprehensive financial deep-dive:
        1. **Revenue Analysis** - Historical trends, growth drivers, segment performance
        2. **Profitability Analysis** - Margins, efficiency ratios, peer comparison
        3. **Balance Sheet Strength** - Assets, liabilities, working capital, debt levels
        4. **Cash Flow Analysis** - Operating, investing, financing cash flows
        5. **Financial Ratios and Metrics** - ROE, ROA, debt ratios, efficiency metrics
        6. **Peer Comparison** - Financial benchmarking against key competitors
        
        Include 3-year historical analysis and 2-year forward projections.
        Use tables and charts to present financial data clearly.""",
        5
    ),
    "valuation_analysis": RealKiroAgent(
        "valuation_analysis",
        """Generate Chapter 5: Valuation Analysis (TARGET: 2000-2500 words):
        
        Structure as institutional valuation methodology:
        1. **Valuation Methodology Overview** - Approaches used and rationale
        2. **Discounted Cash Flow (DCF) Analysis** - Detailed DCF model with assumptions
        3. **Peer Comparison Analysis** - Trading multiples vs comparable companies
        4. **Scenario Analysis** - Bull, base, bear case valuations
        5. **Price Target Derivation** - Weighted average of valuation methods
        6. **Valuation Risks** - Key assumptions and sensitivity analysis
        
        Include specific price targets, valuation multiples, and detailed assumptions.
        Present multiple valuation scenarios with clear methodology.""",
        4
    ),
    "market_analysis": RealKiroAgent(
        "market_analysis",
        """Generate Chapter 6: Market Analysis and Competitive Position (TARGET: 1800-2200 words):
        
        Structure as comprehensive market assessment:
        1. **Market Size and Growth** - TAM, SAM, SOM analysis with market sizing
        2. **Industry Dynamics** - Key trends, growth drivers, regulatory environment
        3. **Competitive Landscape** - Major competitors, market share analysis
        4. **Competitive Advantages** - Sustainable moats and differentiation
        5. **Market Position Assessment** - Company's position vs competitors
        6. **Future Market Opportunities** - Growth vectors and expansion potential
        
        Include market size data, competitive positioning charts, and growth projections.
        Focus on company's competitive advantages and market opportunity.""",
        4
    ),
    "risk_assessment": RealKiroAgent(
        "risk_assessment",
        """Generate Chapter 7: Risk Assessment (TARGET: 1500-2000 words):
        
        Structure as comprehensive risk analysis:
        1. **Business Risk Factors** - Operational, strategic, and execution risks
        2. **Financial Risk Analysis** - Leverage, liquidity, credit risks
        3. **Market and Industry Risks** - Cyclical, regulatory, competitive risks
        4. **ESG and Regulatory Risks** - Environmental, social, governance concerns
        5. **Risk Mitigation Strategies** - How company addresses key risks
        6. **Risk-Adjusted Investment View** - Impact on investment thesis
        
        Prioritize risks by probability and impact. Include specific risk mitigation measures
        and how risks affect the investment recommendation.""",
        3
    ),
    "investment_thesis": RealKiroAgent(
        "investment_thesis",
        """Generate Chapter 8: Investment Thesis and Recommendation (TARGET: 1200-1500 words):
        
        Structure as final investment conclusion:
        1. **Investment Thesis Summary** - Core reasons to invest (3-5 key points)
        2. **Catalysts and Value Drivers** - Near-term and long-term growth catalysts
        3. **Financial Projections Summary** - Key financial forecasts and targets
        4. **Valuation Summary** - Price target methodology and rationale
        5. **Investment Recommendation** - Final BUY/HOLD/SELL with conviction level
        6. **Key Monitoring Points** - Metrics and milestones to track
        
        Synthesize all analysis into clear, actionable investment recommendation.
        Include specific price targets, timeframes, and key success metrics.""",
        3
    )
}
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
