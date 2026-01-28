"""
Kiro Prompts Integration for Report Generation
Integrates with Kiro CLI prompts and chart pipeline for comprehensive reports
"""
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
from datetime import datetime
from .structure import ReportStructure, ReportAssembler, ReportVersioning
from .pdf_generator import PDFGenerator

# Try to import real services, fall back to mock for testing
try:
    from app.services.kiro_service import KiroService
    from app.features.chart_integration import ChartIntegration
except ImportError:
    # Use mock services for testing
    from app.services.mock_kiro_service import MockKiroService as KiroService
    from app.services.mock_kiro_service import MockChartIntegration as ChartIntegration

logger = logging.getLogger(__name__)

class KiroReportGenerator:
    """Integrates Kiro prompts with report structure for comprehensive generation"""
    
    def __init__(self):
        self.kiro_service = KiroService()
        self.chart_integration = ChartIntegration()
        self.assembler = ReportAssembler()
        self.pdf_generator = PDFGenerator()
        
        # Map report sections to Kiro prompts
        self.prompt_mapping = {
            "executive_summary": [
                "company-overview-investment-thesis",
                "valuation-analysis-price-target"
            ],
            "company_deep_dive": [
                "company-overview-investment-thesis",
                "competitive-analysis-market-position"
            ],
            "financial_analysis": [
                "financial-analysis-key-metrics",
                "financial-projections-growth"
            ],
            "valuation_analysis": [
                "valuation-analysis-price-target",
                "peer-comparison-analysis"
            ],
            "risk_assessment": [
                "risk-assessment-summary",
                "scenario-analysis-sensitivity"
            ]
        }
        
        # Map sections to required charts
        self.chart_mapping = {
            "executive_summary": ["price_performance", "key_metrics_comparison"],
            "company_deep_dive": ["market_share", "competitive_positioning"],
            "financial_analysis": ["revenue_trends", "profit_margins", "balance_sheet_metrics"],
            "valuation_analysis": ["dcf_sensitivity", "peer_multiples"],
            "risk_assessment": ["risk_matrix", "sensitivity_analysis"]
        }
    
    async def generate_comprehensive_report(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete comprehensive report using Kiro prompts and charts"""
        start_time = datetime.now()
        
        try:
            # Create report metadata
            metadata = ReportVersioning.create_metadata(
                ticker=ticker,
                company_name=company_data.get('company_name', f'{ticker} Corporation'),
                report_type="comprehensive"
            )
            
            logger.info(f"Starting comprehensive report generation for {ticker}")
            
            # Generate all sections concurrently
            sections_data = await self._generate_all_sections(ticker, company_data)
            
            # Generate charts for all sections
            charts_data = await self._generate_all_charts(ticker, company_data)
            
            # Integrate charts into sections
            self._integrate_charts_into_sections(sections_data, charts_data)
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            metadata = ReportVersioning.update_generation_time(metadata, generation_time)
            
            # Assemble final report
            final_report = self.assembler.assemble_report(sections_data, metadata)
            
            logger.info(f"Completed report generation for {ticker} in {generation_time:.2f}s")
            return final_report
            
        except Exception as e:
            logger.error(f"Report generation failed for {ticker}: {e}")
            raise
    
    async def _generate_all_sections(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all report sections using Kiro prompts"""
        sections_data = {}
        
        # Create tasks for concurrent execution
        tasks = []
        for section_id, prompts in self.prompt_mapping.items():
            task = self._generate_section(section_id, ticker, company_data, prompts)
            tasks.append((section_id, task))
        
        # Execute all sections concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        for (section_id, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Section {section_id} generation failed: {result}")
                sections_data[section_id] = self._get_fallback_section_content(section_id)
            else:
                sections_data[section_id] = result
        
        return sections_data
    
    async def _generate_section(self, section_id: str, ticker: str, company_data: Dict[str, Any], prompts: List[str]) -> Dict[str, Any]:
        """Generate individual section using specified Kiro prompts"""
        section_content = {}
        
        try:
            # Execute each prompt for the section
            for prompt_name in prompts:
                prompt_result = await self.kiro_service.execute_prompt(
                    prompt_name=prompt_name,
                    context_data={
                        "ticker": ticker,
                        "company_data": company_data,
                        "section_focus": section_id
                    }
                )
                
                # Parse and integrate prompt result
                parsed_content = self._parse_prompt_result(prompt_name, prompt_result)
                section_content.update(parsed_content)
            
            # Add section-specific processing
            section_content = await self._post_process_section(section_id, section_content, ticker, company_data)
            
            logger.info(f"Generated section {section_id} for {ticker}")
            return section_content
            
        except Exception as e:
            logger.error(f"Section {section_id} generation failed for {ticker}: {e}")
            return self._get_fallback_section_content(section_id)
    
    def _parse_prompt_result(self, prompt_name: str, result: str) -> Dict[str, Any]:
        """Parse Kiro prompt result into structured content"""
        try:
            # Try to parse as JSON first
            if result.strip().startswith('{'):
                return json.loads(result)
            
            # Otherwise, structure based on prompt type
            if "investment-thesis" in prompt_name:
                return {
                    "investment_thesis": result,
                    "summary": result[:500] + "..." if len(result) > 500 else result
                }
            elif "price-target" in prompt_name:
                return {
                    "price_analysis": result,
                    "recommendation": self._extract_recommendation(result)
                }
            elif "key-metrics" in prompt_name:
                return {
                    "financial_metrics": result,
                    "key_ratios": self._extract_metrics(result)
                }
            elif "risk-assessment" in prompt_name:
                return {
                    "risk_analysis": result,
                    "risk_factors": self._extract_risks(result)
                }
            else:
                return {
                    "content": result,
                    "summary": result[:300] + "..." if len(result) > 300 else result
                }
                
        except Exception as e:
            logger.error(f"Failed to parse prompt result for {prompt_name}: {e}")
            return {"content": result, "raw_result": result}
    
    def _extract_recommendation(self, content: str) -> Dict[str, Any]:
        """Extract investment recommendation from content"""
        # Simple extraction logic (would be more sophisticated in production)
        content_lower = content.lower()
        
        if "strong buy" in content_lower or "buy" in content_lower:
            rating = "BUY"
        elif "hold" in content_lower:
            rating = "HOLD"
        elif "sell" in content_lower:
            rating = "SELL"
        else:
            rating = "HOLD"
        
        return {
            "rating": rating,
            "price_target": "N/A",  # Would extract from content
            "current_price": "N/A",
            "confidence": "Medium"
        }
    
    def _extract_metrics(self, content: str) -> Dict[str, Any]:
        """Extract financial metrics from content"""
        return {
            "revenue": "N/A",
            "pe_ratio": "N/A", 
            "roe": "N/A",
            "debt_to_equity": "N/A",
            "current_ratio": "N/A"
        }
    
    def _extract_risks(self, content: str) -> List[str]:
        """Extract risk factors from content"""
        # Simple extraction (would use NLP in production)
        return [
            "Market volatility risk",
            "Competitive pressure risk", 
            "Regulatory risk",
            "Economic downturn risk"
        ]
    
    async def _post_process_section(self, section_id: str, content: Dict[str, Any], ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process section content with additional enhancements"""
        
        if section_id == "executive_summary":
            # Ensure executive summary has all required components
            content.setdefault("recommendation", {"rating": "HOLD", "price_target": "N/A"})
            content.setdefault("key_highlights", [])
            
        elif section_id == "financial_analysis":
            # Add financial calculations and ratios
            content.setdefault("financial_ratios", {})
            content.setdefault("trend_analysis", {})
            
        elif section_id == "valuation_analysis":
            # Add valuation models and scenarios
            content.setdefault("dcf_model", {})
            content.setdefault("peer_comparison", {})
            
        return content
    
    async def _generate_all_charts(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all required charts for the report"""
        charts_data = {}
        
        try:
            # Get all unique chart types needed
            all_charts = set()
            for charts in self.chart_mapping.values():
                all_charts.update(charts)
            
            # Generate charts concurrently
            chart_tasks = []
            for chart_type in all_charts:
                task = self.chart_integration.generate_chart(
                    chart_type=chart_type,
                    ticker=ticker,
                    data=company_data
                )
                chart_tasks.append((chart_type, task))
            
            # Execute chart generation
            results = await asyncio.gather(*[task for _, task in chart_tasks], return_exceptions=True)
            
            # Process chart results
            for (chart_type, _), result in zip(chart_tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Chart {chart_type} generation failed: {result}")
                    charts_data[chart_type] = self._get_fallback_chart(chart_type)
                else:
                    charts_data[chart_type] = result
            
            logger.info(f"Generated {len(charts_data)} charts for {ticker}")
            return charts_data
            
        except Exception as e:
            logger.error(f"Chart generation failed for {ticker}: {e}")
            return {}
    
    def _integrate_charts_into_sections(self, sections_data: Dict[str, Any], charts_data: Dict[str, Any]):
        """Integrate generated charts into appropriate sections"""
        for section_id, chart_types in self.chart_mapping.items():
            if section_id in sections_data:
                section_charts = {}
                for chart_type in chart_types:
                    if chart_type in charts_data:
                        section_charts[chart_type] = charts_data[chart_type]
                
                sections_data[section_id]["charts"] = section_charts
    
    def _get_fallback_section_content(self, section_id: str) -> Dict[str, Any]:
        """Get fallback content when section generation fails"""
        fallback_content = {
            "executive_summary": {
                "summary": "Executive summary content is being generated...",
                "recommendation": {"rating": "HOLD", "price_target": "N/A"},
                "key_highlights": ["Analysis in progress"]
            },
            "company_deep_dive": {
                "summary": "Company analysis content is being generated...",
                "business_model": "Business model analysis in progress",
                "competitive_position": "Competitive analysis in progress"
            },
            "financial_analysis": {
                "summary": "Financial analysis content is being generated...",
                "revenue_analysis": "Revenue analysis in progress",
                "profitability_analysis": "Profitability analysis in progress"
            },
            "valuation_analysis": {
                "summary": "Valuation analysis content is being generated...",
                "dcf_analysis": "DCF model in progress",
                "peer_analysis": "Peer comparison in progress"
            },
            "risk_assessment": {
                "summary": "Risk assessment content is being generated...",
                "risk_factors": ["Risk analysis in progress"],
                "mitigation_strategies": ["Mitigation analysis in progress"]
            }
        }
        
        return fallback_content.get(section_id, {"summary": "Content is being generated..."})
    
    def _get_fallback_chart(self, chart_type: str) -> Dict[str, Any]:
        """Get fallback chart when generation fails"""
        return {
            "title": chart_type.replace('_', ' ').title(),
            "type": "placeholder",
            "data": {},
            "status": "generation_failed"
        }
    
    async def generate_pdf_report(self, report_data: Dict[str, Any], ticker: str) -> str:
        """Generate PDF from report data"""
        try:
            filename = f"{ticker}_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            pdf_path = await self.pdf_generator.generate_pdf(report_data, filename)
            
            logger.info(f"Generated PDF report for {ticker}: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed for {ticker}: {e}")
            raise
    
    async def get_generation_progress(self, ticker: str) -> Dict[str, Any]:
        """Get real-time progress of report generation"""
        # This would integrate with the queue system to provide real-time updates
        return {
            "ticker": ticker,
            "status": "processing",
            "progress": 45,
            "current_stage": "Generating financial analysis",
            "estimated_completion": "2 minutes"
        }