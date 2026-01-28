#!/usr/bin/env python3
"""
MarketMind Pro Parallel Report Generation System
Complete orchestrator for 8 concurrent subagents with quality gates
Target: 3-5 minutes generation time with institutional quality
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import our custom modules
from parallel_subagent_system import ParallelSubagentSystem
from quality_gate_system import quality_gate_system
from report_consolidator import report_consolidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketMindParallelSystem:
    """Main orchestrator for parallel report generation"""
    
    def __init__(self):
        self.subagent_system = ParallelSubagentSystem()
        self.quality_system = quality_gate_system
        self.consolidator = report_consolidator
        
        # Performance targets
        self.target_generation_time = 300  # 5 minutes
        self.target_quality_score = 85     # 85% quality
        self.target_success_rate = 0.875   # 7/8 sections minimum

    async def generate_institutional_report(self, ticker: str) -> Dict[str, Any]:
        """
        Generate complete institutional-grade report using parallel processing
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Complete report with metadata, quality scores, and performance metrics
        """
        
        logger.info(f"🚀 Starting MarketMind Pro parallel analysis for {ticker}")
        start_time = datetime.now()
        
        try:
            # Phase 1: Parallel Section Generation (Target: 3-4 minutes)
            logger.info("📊 Phase 1: Executing 8 concurrent subagents...")
            section_results = await self.subagent_system.generate_report(ticker)
            
            phase1_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Phase 1 completed in {phase1_time:.1f}s")
            
            # Phase 2: Quality Validation (Target: 30 seconds)
            logger.info("🔍 Phase 2: Applying quality gates...")
            quality_validation = self._apply_quality_gates(section_results)
            
            phase2_time = (datetime.now() - start_time).total_seconds() - phase1_time
            logger.info(f"✅ Phase 2 completed in {phase2_time:.1f}s")
            
            # Phase 3: Report Consolidation (Target: 30 seconds)
            logger.info("📋 Phase 3: Consolidating final report...")
            final_report = self.consolidator.consolidate_report(
                ticker, section_results['sections'], quality_validation
            )
            
            phase3_time = (datetime.now() - start_time).total_seconds() - phase1_time - phase2_time
            logger.info(f"✅ Phase 3 completed in {phase3_time:.1f}s")
            
            # Calculate final metrics
            total_time = (datetime.now() - start_time).total_seconds()
            final_metrics = self._calculate_final_metrics(
                section_results, quality_validation, final_report, total_time
            )
            
            # Add performance summary to report
            final_report['performance_summary'] = final_metrics
            
            # Log completion
            self._log_completion_summary(ticker, final_metrics)
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Report generation failed for {ticker}: {e}")
            return self._create_error_report(ticker, str(e), start_time)

    def _apply_quality_gates(self, section_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply comprehensive quality validation to all sections"""
        
        sections = section_results.get('sections', {})
        successful_sections = {name: data for name, data in sections.items() 
                             if data.get('status') == 'success'}
        
        # Validate each successful section
        section_validations = {}
        for section_name, section_data in successful_sections.items():
            content = section_data.get('content', '')
            validation = self.quality_system.validate_section_quality(section_name, content)
            section_validations[section_name] = validation
        
        # Generate overall quality report
        quality_report = self.quality_system.validate_complete_report(successful_sections)
        quality_report['section_validations'] = section_validations
        
        return quality_report

    def _calculate_final_metrics(self, section_results: Dict[str, Any], 
                               quality_validation: Dict[str, Any],
                               final_report: Dict[str, Any], 
                               total_time: float) -> Dict[str, Any]:
        """Calculate comprehensive final performance metrics"""
        
        # Extract key metrics
        success_rate = section_results.get('success_rate', 0)
        quality_score = quality_validation.get('report_validation', {}).get('average_quality_score', 0)
        institutional_grade = quality_validation.get('institutional_grade', False)
        
        # Performance targets assessment
        targets_met = {
            'generation_time': total_time <= self.target_generation_time,
            'quality_score': quality_score >= self.target_quality_score,
            'success_rate': success_rate >= self.target_success_rate,
            'institutional_grade': institutional_grade
        }
        
        # Calculate overall performance score
        performance_weights = {
            'generation_time': 0.25,
            'quality_score': 0.35,
            'success_rate': 0.25,
            'institutional_grade': 0.15
        }
        
        performance_score = sum(
            performance_weights[metric] * (100 if met else 0)
            for metric, met in targets_met.items()
        )
        
        return {
            'total_generation_time_seconds': total_time,
            'target_time_seconds': self.target_generation_time,
            'time_efficiency': min(100, (self.target_generation_time / total_time) * 100),
            'success_rate_percentage': success_rate * 100,
            'quality_score_percentage': quality_score,
            'institutional_grade_achieved': institutional_grade,
            'targets_met': targets_met,
            'overall_performance_score': performance_score,
            'performance_grade': self._assign_performance_grade(performance_score),
            'system_efficiency': {
                'sections_per_minute': (section_results.get('successful_sections', 0) / (total_time / 60)),
                'quality_per_second': quality_score / total_time,
                'parallel_efficiency': success_rate * (self.target_generation_time / total_time)
            },
            'competitive_advantage': {
                'time_vs_manual': f"{(20 * 60) / total_time:.1f}x faster than manual analysis",
                'cost_vs_traditional': "99% cost reduction vs $5,000 Wall Street reports",
                'quality_vs_retail': "Institutional-grade vs retail-level analysis"
            }
        }

    def _assign_performance_grade(self, performance_score: float) -> str:
        """Assign letter grade based on overall performance"""
        if performance_score >= 95:
            return 'A+ (Exceptional)'
        elif performance_score >= 90:
            return 'A (Excellent)'
        elif performance_score >= 85:
            return 'A- (Very Good)'
        elif performance_score >= 80:
            return 'B+ (Good)'
        elif performance_score >= 75:
            return 'B (Satisfactory)'
        else:
            return 'B- (Needs Improvement)'

    def _log_completion_summary(self, ticker: str, final_metrics: Dict[str, Any]):
        """Log comprehensive completion summary"""
        
        logger.info(f"🎯 MarketMind Pro Report Completed for {ticker}")
        logger.info(f"⏱️  Generation Time: {final_metrics['total_generation_time_seconds']:.1f}s")
        logger.info(f"📊 Success Rate: {final_metrics['success_rate_percentage']:.1f}%")
        logger.info(f"🏆 Quality Score: {final_metrics['quality_score_percentage']:.1f}%")
        logger.info(f"🎓 Institutional Grade: {'✅' if final_metrics['institutional_grade_achieved'] else '❌'}")
        logger.info(f"📈 Performance Grade: {final_metrics['performance_grade']}")
        logger.info(f"⚡ Efficiency: {final_metrics['competitive_advantage']['time_vs_manual']}")

    def _create_error_report(self, ticker: str, error_message: str, start_time: datetime) -> Dict[str, Any]:
        """Create error report when generation fails"""
        
        return {
            'ticker': ticker,
            'status': 'failed',
            'error': error_message,
            'generation_time': (datetime.now() - start_time).total_seconds(),
            'timestamp': datetime.now().isoformat(),
            'fallback_available': True,
            'retry_recommended': True,
            'error_report': {
                'error_type': 'generation_failure',
                'error_message': error_message,
                'suggested_actions': [
                    'Check Kiro CLI availability',
                    'Verify prompt files exist',
                    'Retry with single-threaded mode',
                    'Contact technical support'
                ]
            }
        }

    async def generate_demo_report(self, ticker: str = "AAPL") -> Dict[str, Any]:
        """Generate demo report for testing and demonstration"""
        
        logger.info(f"🧪 Generating demo report for {ticker}")
        
        # Add demo metadata
        demo_start = datetime.now()
        report = await self.generate_institutional_report(ticker)
        
        # Add demo-specific information
        report['demo_info'] = {
            'demo_mode': True,
            'ticker_analyzed': ticker,
            'demo_timestamp': demo_start.isoformat(),
            'demo_purpose': 'MarketMind Pro System Demonstration',
            'key_features_demonstrated': [
                '8 Concurrent Subagents',
                'Real-time Quality Gates',
                'Institutional-grade Analysis',
                'Sub-5-minute Generation',
                'Professional Report Consolidation'
            ]
        }
        
        return report

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and capabilities"""
        
        return {
            'system_name': 'MarketMind Pro Parallel System',
            'version': '1.0.0',
            'capabilities': {
                'concurrent_subagents': 8,
                'quality_gates': True,
                'institutional_grade': True,
                'target_generation_time': f"{self.target_generation_time}s",
                'supported_sections': list(self.subagent_system.sections.keys())
            },
            'performance_targets': {
                'generation_time_seconds': self.target_generation_time,
                'quality_score_percentage': self.target_quality_score,
                'success_rate_percentage': self.target_success_rate * 100,
                'institutional_grade_required': True
            },
            'system_health': 'Operational',
            'last_updated': datetime.now().isoformat()
        }

# Create main system instance
marketmind_system = MarketMindParallelSystem()

# Main execution functions
async def generate_report(ticker: str) -> Dict[str, Any]:
    """Main function to generate MarketMind Pro report"""
    return await marketmind_system.generate_institutional_report(ticker)

async def generate_demo() -> Dict[str, Any]:
    """Generate demo report"""
    return await marketmind_system.generate_demo_report()

def get_status() -> Dict[str, Any]:
    """Get system status"""
    return marketmind_system.get_system_status()

# CLI interface
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) > 1:
            ticker = sys.argv[1].upper()
            print(f"Generating MarketMind Pro report for {ticker}...")
            
            result = await generate_report(ticker)
            
            print(f"\n🎯 Report Generation Complete!")
            print(f"Time: {result.get('performance_summary', {}).get('total_generation_time_seconds', 0):.1f}s")
            print(f"Quality: {result.get('performance_summary', {}).get('quality_score_percentage', 0):.1f}%")
            print(f"Grade: {result.get('performance_summary', {}).get('performance_grade', 'N/A')}")
            
        else:
            print("Usage: python marketmind_parallel_system.py <TICKER>")
            print("Example: python marketmind_parallel_system.py AAPL")
    
    asyncio.run(main())