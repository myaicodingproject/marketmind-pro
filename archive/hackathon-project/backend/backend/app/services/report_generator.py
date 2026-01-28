"""
Report Generation Pipeline
Orchestrates the complete report generation process using Kiro prompts
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.services.kiro_engine import kiro_engine, KiroExecutionError
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

class ReportGenerationError(Exception):
    """Custom exception for report generation errors"""
    pass

class ReportGenerator:
    """
    Manages the complete report generation pipeline
    Coordinates multiple Kiro prompts to create comprehensive reports
    """
    
    # Define the 4 specialized prompts for our report
    REPORT_PROMPTS = [
        {
            'name': 'company-overview-investment-thesis',
            'title': 'Company Overview & Investment Thesis',
            'page': 1,
            'weight': 25
        },
        {
            'name': 'financial-analysis-key-metrics', 
            'title': 'Financial Analysis & Key Metrics',
            'page': 2,
            'weight': 25
        },
        {
            'name': 'valuation-analysis-price-target',
            'title': 'Valuation Analysis & Price Target', 
            'page': 3,
            'weight': 25
        },
        {
            'name': 'risk-assessment-summary',
            'title': 'Risk Assessment & Summary',
            'pages': '4-5',
            'weight': 25
        }
    ]
    
    def __init__(self):
        self.active_generations = {}
    
    async def generate_comprehensive_report(
        self,
        ticker: str,
        company_data: Dict[str, Any],
        user_id: Optional[str] = None,
        report_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete 5-page executive summary report
        
        Args:
            ticker: Stock ticker symbol
            company_data: Comprehensive company data for context
            user_id: User ID for progress tracking
            report_id: Report ID for tracking
            
        Returns:
            Complete report with all sections
        """
        
        if not report_id:
            report_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting report generation for {ticker} (Report ID: {report_id})")
            
            # Track generation progress
            self.active_generations[report_id] = {
                'ticker': ticker,
                'user_id': user_id,
                'start_time': datetime.now(),
                'status': 'initializing',
                'progress': 0
            }
            
            # Send initial progress update
            await self._update_progress(report_id, 0, "Initializing report generation...")
            
            # Prepare context for all prompts
            context_data = self._prepare_report_context(ticker, company_data)
            
            await self._update_progress(report_id, 10, "Context prepared, starting analysis...")
            
            # Configure prompt executions
            prompt_configs = []
            for prompt_config in self.REPORT_PROMPTS:
                prompt_configs.append({
                    'prompt_name': prompt_config['name'],
                    'context_data': context_data,
                    'timeout': 300,
                    'config': prompt_config
                })
            
            # Execute all prompts concurrently
            await self._update_progress(report_id, 20, "Executing specialized analysis prompts...")
            
            results = await self._execute_prompts_with_progress(
                prompt_configs, 
                report_id,
                start_progress=20,
                end_progress=90
            )
            
            # Assemble final report
            await self._update_progress(report_id, 90, "Assembling final report...")
            
            report = await self._assemble_report(ticker, results, company_data)
            
            # Finalize
            await self._update_progress(report_id, 100, "Report generation complete!")
            
            # Update tracking
            self.active_generations[report_id].update({
                'status': 'completed',
                'progress': 100,
                'end_time': datetime.now(),
                'report': report
            })
            
            logger.info(f"Successfully generated report for {ticker} (Report ID: {report_id})")
            
            return {
                'report_id': report_id,
                'ticker': ticker,
                'status': 'success',
                'report': report,
                'generation_time': (datetime.now() - self.active_generations[report_id]['start_time']).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Report generation failed for {ticker}: {str(e)}")
            
            # Update error status
            if report_id in self.active_generations:
                self.active_generations[report_id].update({
                    'status': 'error',
                    'error': str(e),
                    'end_time': datetime.now()
                })
            
            await self._update_progress(report_id, -1, f"Error: {str(e)}")
            
            raise ReportGenerationError(f"Failed to generate report for {ticker}: {str(e)}")
    
    async def _execute_prompts_with_progress(
        self,
        prompt_configs: list,
        report_id: str,
        start_progress: int,
        end_progress: int
    ) -> Dict[str, Any]:
        """Execute prompts with progress tracking"""
        
        total_weight = sum(config['config']['weight'] for config in prompt_configs)
        current_progress = start_progress
        results = {}
        
        # Execute prompts with controlled concurrency
        semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent executions
        
        async def execute_with_progress(config):
            async with semaphore:
                prompt_name = config['prompt_name']
                weight = config['config']['weight']
                
                try:
                    # Update progress for this prompt start
                    await self._update_progress(
                        report_id, 
                        current_progress, 
                        f"Analyzing {config['config']['title']}..."
                    )
                    
                    # Execute the prompt
                    result = await kiro_engine.execute_prompt(
                        prompt_name,
                        config['context_data'],
                        config.get('timeout', 300)
                    )
                    
                    # Calculate progress increment
                    progress_increment = (weight / total_weight) * (end_progress - start_progress)
                    
                    return prompt_name, result, progress_increment
                    
                except Exception as e:
                    logger.error(f"Failed to execute prompt {prompt_name}: {str(e)}")
                    return prompt_name, {'status': 'error', 'error': str(e)}, 0
        
        # Execute all prompts
        tasks = [execute_with_progress(config) for config in prompt_configs]
        
        # Process results as they complete
        for task in asyncio.as_completed(tasks):
            prompt_name, result, progress_increment = await task
            results[prompt_name] = result
            current_progress += progress_increment
            
            await self._update_progress(
                report_id,
                int(current_progress),
                f"Completed {prompt_name.replace('-', ' ').title()}"
            )
        
        return results
    
    def _prepare_report_context(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive context for all prompts"""
        
        # Extract and format data for prompts
        context = {
            'ticker': ticker,
            'company_name': company_data.get('company_name', f"{ticker} Inc."),
            'sector': company_data.get('sector', 'Unknown'),
            'market_cap': company_data.get('market_cap', 'Unknown'),
            'current_price': company_data.get('current_price', 'Unknown'),
            'business_description': company_data.get('business_description', 'Business description not available'),
            'recent_news': company_data.get('recent_news', 'Recent news not available'),
            'financial_statements': company_data.get('financial_statements', 'Financial data not available'),
            'historical_data': company_data.get('historical_data', 'Historical data not available'),
            'peer_data': company_data.get('peer_data', 'Peer data not available'),
            'industry_averages': company_data.get('industry_averages', 'Industry averages not available'),
            'quarterly_results': company_data.get('quarterly_results', 'Quarterly results not available'),
            'guidance': company_data.get('guidance', 'Guidance not available'),
            
            # Additional context for comprehensive analysis
            'analyst_estimates': company_data.get('analyst_estimates', 'Analyst estimates not available'),
            'insider_trading': company_data.get('insider_trading', 'Insider trading data not available'),
            'institutional_ownership': company_data.get('institutional_ownership', 'Institutional ownership data not available'),
            'technical_indicators': company_data.get('technical_indicators', 'Technical indicators not available'),
            'esg_scores': company_data.get('esg_scores', 'ESG scores not available'),
            'regulatory_environment': company_data.get('regulatory_environment', 'Regulatory information not available')
        }
        
        return context
    
    async def _assemble_report(
        self, 
        ticker: str, 
        results: Dict[str, Any], 
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assemble the final report from all prompt results"""
        
        report = {
            'ticker': ticker,
            'company_name': company_data.get('company_name', f"{ticker} Inc."),
            'generation_timestamp': datetime.now().isoformat(),
            'report_type': 'comprehensive_executive_summary',
            'page_count': 5,
            'sections': {}
        }
        
        # Process each section
        for prompt_config in self.REPORT_PROMPTS:
            prompt_name = prompt_config['name']
            
            if prompt_name in results:
                result = results[prompt_name]
                
                if result.get('status') == 'success':
                    report['sections'][prompt_name] = {
                        'title': prompt_config['title'],
                        'page': prompt_config.get('page', prompt_config.get('pages')),
                        'content': result['content'],
                        'execution_time': result.get('execution_time', 0),
                        'status': 'success'
                    }
                else:
                    # Handle failed sections
                    report['sections'][prompt_name] = {
                        'title': prompt_config['title'],
                        'page': prompt_config.get('page', prompt_config.get('pages')),
                        'content': f"Error generating section: {result.get('error', 'Unknown error')}",
                        'status': 'error',
                        'error': result.get('error')
                    }
        
        # Add summary metadata
        successful_sections = sum(1 for section in report['sections'].values() if section['status'] == 'success')
        total_sections = len(self.REPORT_PROMPTS)
        
        report['metadata'] = {
            'successful_sections': successful_sections,
            'total_sections': total_sections,
            'completion_rate': (successful_sections / total_sections) * 100,
            'total_execution_time': sum(
                section.get('execution_time', 0) 
                for section in report['sections'].values()
            )
        }
        
        return report
    
    async def _update_progress(self, report_id: str, progress: int, message: str):
        """Update progress and send WebSocket notification"""
        
        if report_id in self.active_generations:
            self.active_generations[report_id]['progress'] = progress
            self.active_generations[report_id]['status_message'] = message
        
        # Send WebSocket update
        await websocket_manager.send_progress_update(report_id, {
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Report {report_id}: {progress}% - {message}")
    
    def get_generation_status(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of report generation"""
        return self.active_generations.get(report_id)
    
    def cleanup_completed_generations(self, max_age_hours: int = 24):
        """Clean up old generation tracking data"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for report_id, data in self.active_generations.items():
            if data.get('end_time') and data['end_time'].timestamp() < cutoff_time:
                to_remove.append(report_id)
        
        for report_id in to_remove:
            del self.active_generations[report_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old generation records")

# Global instance
report_generator = ReportGenerator()