"""
Enhanced Kiro Service with Robust Process Management
Integrates with ProcessManager for scalable, reliable Kiro CLI execution
"""
import asyncio
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

from app.core.process_manager import process_manager, ProcessStatus
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class KiroTask:
    """Represents a Kiro CLI task"""
    task_id: str
    ticker: str
    prompt_type: str
    status: ProcessStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = 0.0
    completed_at: Optional[float] = None

class KiroProcessService:
    """Enhanced Kiro service with process management"""
    
    def __init__(self):
        self.cli_path = getattr(settings, 'kiro_cli_path', 'kiro-cli')
        self.workspace_path = Path(getattr(settings, 'kiro_workspace_path', './workspace'))
        self.workspace_path.mkdir(exist_ok=True)
        
        # Task tracking
        self._active_tasks: Dict[str, KiroTask] = {}
        self._task_queue = asyncio.Queue()
        self._queue_processor: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the Kiro service"""
        logger.info("Starting Kiro Process Service")
        await process_manager.start()
        self._queue_processor = asyncio.create_task(self._process_queue())
        
    async def stop(self):
        """Stop the Kiro service"""
        logger.info("Stopping Kiro Process Service")
        
        if self._queue_processor:
            self._queue_processor.cancel()
            
        await process_manager.stop()
        
    async def generate_comprehensive_report(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report with concurrent processing"""
        try:
            logger.info(f"Starting comprehensive report generation for {ticker}")
            
            # Create tasks for each section
            tasks = [
                self._queue_analysis_task(ticker, "company_overview", company_data),
                self._queue_analysis_task(ticker, "financial_analysis", company_data),
                self._queue_analysis_task(ticker, "valuation_analysis", company_data),
                self._queue_analysis_task(ticker, "risk_assessment", company_data)
            ]
            
            # Execute tasks concurrently with proper resource management
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            report = {}
            for i, result in enumerate(results):
                section_name = ["company_overview", "financial_analysis", "valuation_analysis", "risk_assessment"][i]
                
                if isinstance(result, Exception):
                    logger.error(f"Error in {section_name}: {result}")
                    report[section_name] = {"error": str(result), "content": "Analysis failed"}
                else:
                    report[section_name] = result
                    
            logger.info(f"Completed comprehensive report for {ticker}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report for {ticker}: {e}")
            raise
            
    async def _queue_analysis_task(self, ticker: str, analysis_type: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Queue an analysis task for processing"""
        task_id = f"{ticker}_{analysis_type}_{uuid.uuid4().hex[:8]}"
        
        task = KiroTask(
            task_id=task_id,
            ticker=ticker,
            prompt_type=analysis_type,
            status=ProcessStatus.PENDING,
            created_at=asyncio.get_event_loop().time()
        )
        
        self._active_tasks[task_id] = task
        
        try:
            # Execute the analysis
            result = await self._execute_analysis(task_id, ticker, analysis_type, company_data)
            task.status = ProcessStatus.COMPLETED
            task.result = result
            task.completed_at = asyncio.get_event_loop().time()
            
            return result
            
        except Exception as e:
            task.status = ProcessStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task_id} failed: {e}")
            raise
        finally:
            # Cleanup task after some time
            asyncio.create_task(self._cleanup_task(task_id, delay=300))  # 5 minutes
            
    async def _execute_analysis(self, task_id: str, ticker: str, analysis_type: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific analysis type"""
        
        # Get the appropriate prompt
        prompt = self._get_prompt_for_analysis(analysis_type, ticker, company_data)
        
        # Prepare command
        command = [
            self.cli_path,
            "chat",
            "--prompt", prompt
        ]
        
        # Execute with process manager
        result = await process_manager.execute_with_timeout(
            process_id=task_id,
            command=command,
            timeout=180,  # 3 minutes per analysis
            cwd=str(self.workspace_path)
        )
        
        if not result["success"]:
            raise RuntimeError(f"Kiro CLI execution failed: {result.get('error', 'Unknown error')}")
            
        # Parse and format output
        return self._parse_kiro_output(result["stdout"], analysis_type)
        
    def _get_prompt_for_analysis(self, analysis_type: str, ticker: str, company_data: Dict[str, Any]) -> str:
        """Get the appropriate prompt for analysis type"""
        
        base_context = f"""
        Company: {company_data.get('company_name', ticker)}
        Ticker: {ticker}
        Sector: {company_data.get('sector', 'Unknown')}
        Market Cap: {company_data.get('market_cap', 'Unknown')}
        Current Price: {company_data.get('current_price', 'Unknown')}
        """
        
        prompts = {
            "company_overview": f"""
            {base_context}
            
            Create a comprehensive company overview and investment thesis for {ticker}. Include:
            
            1. **Business Model & Operations**
               - Core business segments and revenue streams
               - Competitive positioning and market share
               - Key products/services and target markets
               
            2. **Investment Thesis**
               - 3-5 key investment highlights
               - Competitive advantages and moats
               - Growth drivers and catalysts
               
            3. **Recent Developments**
               - Latest quarterly results summary
               - Recent strategic initiatives
               - Management guidance and outlook
               
            Format as professional investment research with clear sections and bullet points.
            """,
            
            "financial_analysis": f"""
            {base_context}
            
            Conduct detailed financial analysis for {ticker}:
            
            1. **Revenue Analysis**
               - 3-year revenue growth trends
               - Revenue by segment/geography
               - Seasonality and cyclicality
               
            2. **Profitability Metrics**
               - Gross, operating, and net margins
               - ROE, ROA, and ROIC trends
               - Margin expansion/compression drivers
               
            3. **Balance Sheet Strength**
               - Debt levels and leverage ratios
               - Working capital management
               - Cash position and liquidity
               
            4. **Cash Flow Analysis**
               - Operating cash flow trends
               - Free cash flow generation
               - Capital allocation priorities
               
            Provide specific numbers and ratios where possible.
            """,
            
            "valuation_analysis": f"""
            {base_context}
            
            Perform comprehensive valuation analysis for {ticker}:
            
            1. **Current Valuation Metrics**
               - P/E, EV/EBITDA, P/B ratios
               - PEG ratio and growth-adjusted metrics
               - Enterprise value analysis
               
            2. **Peer Comparison**
               - Trading multiples vs. sector peers
               - Premium/discount analysis
               - Relative valuation positioning
               
            3. **DCF Analysis Framework**
               - Revenue growth assumptions
               - Margin and FCF projections
               - Terminal value considerations
               - Discount rate (WACC) estimation
               
            4. **Price Target**
               - Bull, base, and bear case scenarios
               - Key valuation drivers and sensitivities
               - Recommendation (Buy/Hold/Sell)
               
            Provide detailed reasoning for all assumptions.
            """,
            
            "risk_assessment": f"""
            {base_context}
            
            Conduct comprehensive risk assessment for {ticker}:
            
            1. **Business Risks**
               - Competitive threats and market disruption
               - Regulatory and compliance risks
               - Operational and execution risks
               
            2. **Financial Risks**
               - Leverage and liquidity concerns
               - Currency and commodity exposure
               - Credit and counterparty risks
               
            3. **Market Risks**
               - Beta and volatility analysis
               - Correlation with market factors
               - Sector-specific risks
               
            4. **ESG and Sustainability**
               - Environmental impact and regulations
               - Social responsibility factors
               - Governance quality assessment
               
            5. **Risk Mitigation**
               - Management's risk management approach
               - Diversification strategies
               - Insurance and hedging programs
               
            Rate each risk category as Low/Medium/High with detailed explanations.
            """
        }
        
        return prompts.get(analysis_type, prompts["company_overview"])
        
    def _parse_kiro_output(self, output: str, analysis_type: str) -> Dict[str, Any]:
        """Parse and structure Kiro CLI output"""
        try:
            # Try to parse as JSON first
            if output.strip().startswith('{'):
                return json.loads(output)
        except json.JSONDecodeError:
            pass
            
        # Fallback to structured text parsing
        return {
            "analysis_type": analysis_type,
            "content": output.strip(),
            "formatted": True,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    async def _process_queue(self):
        """Process queued tasks (for future queue-based processing)"""
        while True:
            try:
                await asyncio.sleep(1)
                # Queue processing logic would go here
                # Currently using direct execution
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                
    async def _cleanup_task(self, task_id: str, delay: int = 300):
        """Cleanup completed task after delay"""
        await asyncio.sleep(delay)
        self._active_tasks.pop(task_id, None)
        
    def get_task_status(self, task_id: str) -> Optional[KiroTask]:
        """Get status of a specific task"""
        return self._active_tasks.get(task_id)
        
    def get_active_tasks(self) -> List[KiroTask]:
        """Get all active tasks"""
        return list(self._active_tasks.values())
        
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        process_metrics = process_manager.get_metrics()
        
        return {
            "active_tasks": len(self._active_tasks),
            "process_manager": process_metrics,
            "task_breakdown": {
                status.value: len([t for t in self._active_tasks.values() if t.status == status])
                for status in ProcessStatus
            }
        }

# Global service instance
kiro_process_service = KiroProcessService()