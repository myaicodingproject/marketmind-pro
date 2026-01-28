import asyncio
import subprocess
import json
import os
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KiroEngine:
    def __init__(self):
        self.cli_path = settings.kiro_cli_path
        self.workspace_path = settings.kiro_workspace_path
        os.makedirs(self.workspace_path, exist_ok=True)
    
    async def execute_prompt(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Execute a single Kiro CLI prompt"""
        try:
            cmd = [self.cli_path, "chat", "--prompt", prompt]
            if context:
                cmd.extend(["--context", context])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_path
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Kiro CLI error: {stderr.decode()}")
                return {"success": False, "error": stderr.decode()}
            
            return {"success": True, "output": stdout.decode()}
        
        except Exception as e:
            logger.error(f"Kiro execution error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def analyze_company_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Analyze company fundamentals using Kiro CLI"""
        prompt = f"""
        Analyze the fundamental metrics for {ticker}. Provide:
        1. Revenue growth trends (3-year historical)
        2. Profitability metrics (margins, ROE, ROA)
        3. Balance sheet strength (debt ratios, current ratio)
        4. Cash flow analysis
        5. Key financial ratios vs industry peers
        
        Format the response as structured JSON with clear sections.
        """
        return await self.execute_prompt(prompt)
    
    async def generate_valuation_analysis(self, ticker: str) -> Dict[str, Any]:
        """Generate valuation analysis using Kiro CLI"""
        prompt = f"""
        Perform comprehensive valuation analysis for {ticker}:
        1. DCF model with 5-year projections
        2. Peer comparison (P/E, EV/EBITDA, P/B ratios)
        3. Price target calculation with bull/base/bear scenarios
        4. Relative valuation vs sector
        5. Key valuation drivers and assumptions
        
        Provide detailed calculations and reasoning in JSON format.
        """
        return await self.execute_prompt(prompt)
    
    async def assess_investment_risks(self, ticker: str) -> Dict[str, Any]:
        """Assess investment risks using Kiro CLI"""
        prompt = f"""
        Conduct comprehensive risk assessment for {ticker}:
        1. Business risks (competitive, operational, regulatory)
        2. Financial risks (leverage, liquidity, credit)
        3. Market risks (volatility, correlation, beta)
        4. ESG risks and sustainability factors
        5. Risk mitigation strategies
        
        Rate each risk category (Low/Medium/High) with detailed explanations.
        """
        return await self.execute_prompt(prompt)
    
    async def generate_executive_summary(self, ticker: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary using Kiro CLI"""
        context = json.dumps(analysis_data)
        prompt = f"""
        Create an executive summary for {ticker} investment analysis:
        1. Investment thesis (2-3 key points)
        2. Price target and recommendation (Buy/Hold/Sell)
        3. Key catalysts and risks
        4. Financial highlights
        5. Conclusion and next steps
        
        Keep it concise but comprehensive, suitable for institutional investors.
        """
        return await self.execute_prompt(prompt, context)

kiro_engine = KiroEngine()