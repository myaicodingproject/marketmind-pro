"""
Celery Worker Configuration for Background Report Generation
Handles async task processing with Redis backend
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from celery import Celery
from celery.exceptions import Retry

from app.core.config import settings
from app.services.report_generator import report_generator
from app.services.websocket_manager import websocket_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'marketmind_worker',
    broker=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
    backend=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.worker.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_routes={
        'app.worker.tasks.generate_report': {'queue': 'reports'},
        'app.worker.tasks.generate_report_section': {'queue': 'sections'},
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default'
)

@celery_app.task(bind=True, name='app.worker.tasks.generate_report')
def generate_report_task(
    self,
    ticker: str,
    company_data: Dict[str, Any],
    user_id: Optional[str] = None,
    report_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Celery task for generating comprehensive reports
    
    Args:
        ticker: Stock ticker symbol
        company_data: Company data for analysis
        user_id: User ID for tracking
        report_id: Report ID for tracking
        
    Returns:
        Generated report data
    """
    
    try:
        logger.info(f"Starting report generation task for {ticker} (Task ID: {self.request.id})")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': 'Initializing report generation...',
                'ticker': ticker,
                'report_id': report_id
            }
        )
        
        # Run the async report generation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                report_generator.generate_comprehensive_report(
                    ticker=ticker,
                    company_data=company_data,
                    user_id=user_id,
                    report_id=report_id or self.request.id
                )
            )
            
            logger.info(f"Successfully completed report generation for {ticker}")
            
            return {
                'status': 'SUCCESS',
                'result': result,
                'task_id': self.request.id,
                'ticker': ticker,
                'completion_time': datetime.now().isoformat()
            }
            
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Report generation failed for {ticker}: {str(e)}")
        
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'ticker': ticker,
                'report_id': report_id,
                'task_id': self.request.id
            }
        )
        
        # Send error notification via WebSocket
        if report_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    websocket_manager.send_error(report_id, {
                        'error': str(e),
                        'task_id': self.request.id,
                        'ticker': ticker
                    })
                )
            finally:
                loop.close()
        
        raise

@celery_app.task(bind=True, name='app.worker.tasks.generate_report_section')
def generate_report_section_task(
    self,
    section_name: str,
    ticker: str,
    company_data: Dict[str, Any],
    report_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Celery task for generating individual report sections
    
    Args:
        section_name: Name of the section to generate
        ticker: Stock ticker symbol
        company_data: Company data for analysis
        report_id: Report ID for tracking
        
    Returns:
        Generated section data
    """
    
    try:
        logger.info(f"Starting section generation: {section_name} for {ticker}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': f'Generating {section_name}...',
                'ticker': ticker,
                'section': section_name
            }
        )
        
        # Run async section generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            from app.services.kiro_engine import kiro_engine
            
            # Prepare context
            context_data = {
                'ticker': ticker,
                'company_name': company_data.get('company_name', f"{ticker} Inc."),
                'sector': company_data.get('sector', 'Unknown'),
                'market_cap': company_data.get('market_cap', 'Unknown'),
                'current_price': company_data.get('current_price', 'Unknown'),
                'business_description': company_data.get('business_description', 'Not available'),
                'recent_news': company_data.get('recent_news', 'Not available'),
                'financial_statements': company_data.get('financial_statements', 'Not available'),
                'historical_data': company_data.get('historical_data', 'Not available'),
                'peer_data': company_data.get('peer_data', 'Not available'),
                'industry_averages': company_data.get('industry_averages', 'Not available'),
                'quarterly_results': company_data.get('quarterly_results', 'Not available'),
                'guidance': company_data.get('guidance', 'Not available')
            }
            
            # Execute the prompt
            result = loop.run_until_complete(
                kiro_engine.execute_prompt(section_name, context_data)
            )
            
            logger.info(f"Successfully generated section {section_name} for {ticker}")
            
            return {
                'status': 'SUCCESS',
                'result': result,
                'task_id': self.request.id,
                'ticker': ticker,
                'section': section_name,
                'completion_time': datetime.now().isoformat()
            }
            
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Section generation failed for {section_name}/{ticker}: {str(e)}")
        
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'ticker': ticker,
                'section': section_name,
                'task_id': self.request.id
            }
        )
        
        raise

@celery_app.task(name='app.worker.tasks.health_check')
def health_check_task() -> Dict[str, Any]:
    """Health check task for monitoring worker status"""
    
    try:
        # Test basic functionality
        from app.services.kiro_engine import kiro_engine
        
        # Validate Kiro setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            validation_result = loop.run_until_complete(kiro_engine.validate_setup())
        finally:
            loop.close()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'kiro_status': validation_result,
            'worker_id': f"worker-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@celery_app.task(name='app.worker.tasks.cleanup_old_results')
def cleanup_old_results_task(max_age_hours: int = 24) -> Dict[str, Any]:
    """Clean up old task results and generation data"""
    
    try:
        # Clean up report generator data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            report_generator.cleanup_completed_generations(max_age_hours)
        finally:
            loop.close()
        
        logger.info(f"Cleaned up old results older than {max_age_hours} hours")
        
        return {
            'status': 'success',
            'cleaned_up_hours': max_age_hours,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Task routing and monitoring
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing worker functionality"""
    print(f'Request: {self.request!r}')
    return {'status': 'debug_complete', 'task_id': self.request.id}

if __name__ == '__main__':
    celery_app.start()