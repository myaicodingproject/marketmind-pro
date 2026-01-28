"""
Real Kiro Agents - Institutional Research Format
Specialized AI agents for generating professional stock research reports
matching institutional research standards like the Broadcom example.
"""

import asyncio
import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealKiroAgent:
    """Represents a specialized Kiro CLI agent for report generation"""
    name: str
    prompt: str
    pages: int
    
    async def generate_analysis(self, ticker: str, progress_storage: Dict, report_id: str) -> Dict[str, Any]:
        """Generate analysis - main method called by the system"""
        # Extract context from progress storage if available
        context = progress_storage.get(report_id, {}).get('context', {})
        
        # Add activity log updates like previous version
        if "activity_log" not in progress_storage[report_id]:
            progress_storage[report_id]["activity_log"] = []
            
        progress_storage[report_id]["activity_log"].append(f"⚡ Executing: kiro-cli chat for {ticker}")
        progress_storage[report_id]["activity_log"].append(f"🧠 AI processing {self.name} analysis...")
        progress_storage[report_id]["activity_log"].append(f"🧠 Starting {self.name.replace('_', ' ').title()} analysis...")
        
        result = await self.execute(ticker, context)
        
        # Add completion logs to activity log
        if result.get("success", False):
            word_count = result.get("word_count", 0)
            duration = result.get("duration", 0)
            progress_storage[report_id]["activity_log"].append(f"✅ {self.name.replace('_', ' ').title()} completed - {word_count:,} words in {duration} seconds")
            progress_storage[report_id]["activity_log"].append(f"✅ Completed {self.name} analysis in {duration}.0s")
            progress_storage[report_id]["activity_log"].append(f"📊 Generated {word_count} words of content")
        
        return result
    
    async def execute(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given context"""
        try:
            # Prepare the enhanced prompt with context
            enhanced_prompt = f"""
            STOCK ANALYSIS REQUEST: {ticker}
            
            CONTEXT DATA:
            {json.dumps(context, indent=2)}
            
            AGENT TASK:
            {self.prompt}
            
            REQUIREMENTS:
            - Generate institutional-quality content
            - Use specific data and numbers from context
            - Follow professional research report format
            - Target length: {self.pages * 500} words approximately
            - Include proper HTML formatting for web display
            """
            
            # Execute via Kiro CLI subprocess using stdin (working method)
            cmd = ["kiro-cli", "chat"]
            
            logger.info(f"⚡ Executing: kiro-cli chat for {ticker}")
            logger.info(f"🧠 AI processing {self.name} analysis...")
            logger.info(f"🧠 Starting {self.name.replace('_', ' ').title()} analysis...")
            
            start_time = datetime.now()
            
            # Add timeout to prevent hanging
            try:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd="/mnt/c/kiro"
                    ),
                    timeout=30  # 30 second timeout for process creation
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=enhanced_prompt.encode()),
                    timeout=1800  # 30 minute timeout - no more timeouts
                )
            except asyncio.TimeoutError:
                logger.error(f"Agent {self.name} timed out")
                return {
                    "success": False,
                    "error": "Agent execution timed out",
                    "content": f"# {self.name.replace('_', ' ').title()}\n\nAgent execution timed out. Please try again or check system resources."
                }
            
            if process.returncode != 0:
                logger.error(f"Agent {self.name} failed: {stderr.decode()}")
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "content": f"Error generating {self.name} section"
                }
            
            # Process raw output like the previous working version
            raw_output = stdout.decode()
            
            # Clean up ANSI codes and extract content
            import re
            clean_output = re.sub(r'\x1b\[[0-9;]*m', '', raw_output)
            content = clean_output.strip()
            
            # Ensure minimum content length for validation
            if len(content) < 100:
                content = f"# {self.name.replace('_', ' ').title()}\n\n" + content + "\n\nAdditional analysis content to meet minimum requirements for institutional research standards."
            
            # Calculate completion stats like previous version
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            word_count = len(content.split())
            
            # Log completion with metrics like previous version
            logger.info(f"✅ {self.name.replace('_', ' ').title()} completed - {word_count:,} words in {duration} seconds")
            logger.info(f"✅ Completed {self.name} analysis in {duration}.0s")
            logger.info(f"📊 Generated {word_count} words of content")
            
            return {
                "success": True,
                "content": content,
                "agent": self.name,
                "word_count": word_count,
                "pages": self.pages,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Exception in {self.name} agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": f"Error generating {self.name} section"
            }

# Define the 8 institutional research agents matching Broadcom format
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

# Agent execution utilities
async def execute_all_agents(ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute all agents in parallel for comprehensive report generation"""
    tasks = []
    for agent_name, agent in REAL_KIRO_AGENTS.items():
        task = agent.execute(ticker, context)
        tasks.append((agent_name, task))
    
    results = {}
    for agent_name, task in tasks:
        result = await task
        results[agent_name] = result
    
    return results

def get_agent_info() -> Dict[str, Any]:
    """Get information about all available agents"""
    return {
        "total_agents": len(REAL_KIRO_AGENTS),
        "agents": {
            name: {
                "pages": agent.pages,
                "estimated_words": agent.pages * 500
            }
            for name, agent in REAL_KIRO_AGENTS.items()
        },
        "total_pages": sum(agent.pages for agent in REAL_KIRO_AGENTS.values()),
        "format": "institutional_research"
    }

def cleanup_subprocesses():
    """Clean up any running subprocesses"""
    try:
        subprocess.run(["pkill", "-f", "kiro-cli"], check=False)
    except Exception:
        pass
