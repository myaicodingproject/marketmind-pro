"""
Quality Validation Service - Integration with MarketMind Pro
Provides automated quality validation with retry mechanisms
"""

from typing import Dict, Optional, Callable
import asyncio
import time
from pathlib import Path
import logging

from app.quality.pdf_quality_validator import PDFQualityValidator, QualityGateIntegrator, PerformanceBenchmarker, QualityScore

class QualityValidationService:
    """Main service for PDF quality validation and improvement"""
    
    def __init__(self):
        self.validator = PDFQualityValidator()
        self.gate_integrator = QualityGateIntegrator(max_retries=2)
        self.benchmarker = PerformanceBenchmarker()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.validation_stats = {
            'total_validations': 0,
            'passed_first_attempt': 0,
            'passed_after_retry': 0,
            'failed_final': 0,
            'average_score': 0.0
        }
    
    async def validate_report_async(self, pdf_path: str, symbol: str) -> Dict:
        """Async validation for integration with report generation"""
        start_time = time.time()
        
        try:
            # Validate PDF quality
            quality_score = self.validator.validate_pdf(pdf_path)
            
            # Generate benchmark comparison
            benchmark_comparison = self.benchmarker.benchmark_against_industry(quality_score)
            
            # Update statistics
            self._update_stats(quality_score)
            
            validation_time = time.time() - start_time
            
            result = {
                'symbol': symbol,
                'pdf_path': pdf_path,
                'quality_score': {
                    'total': quality_score.total,
                    'structure': quality_score.structure,
                    'content': quality_score.content,
                    'typography': quality_score.typography,
                    'technical': quality_score.technical,
                    'accessibility': quality_score.accessibility,
                    'passed': quality_score.passed
                },
                'issues': quality_score.issues,
                'improvements': quality_score.improvements,
                'benchmark_comparison': benchmark_comparison,
                'validation_time': validation_time,
                'institutional_compliance': self._check_institutional_compliance(quality_score)
            }
            
            self.logger.info(f"PDF validation completed for {symbol}: {quality_score.total:.1f}/100")
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'pdf_path': pdf_path,
                'error': str(e),
                'quality_score': {'total': 0, 'passed': False},
                'validation_time': time.time() - start_time
            }
    
    def validate_with_improvements(self, pdf_path: str, symbol: str, 
                                 regeneration_callback: Optional[Callable] = None) -> Dict:
        """Validate with automatic improvement retry"""
        
        def improvement_generator(improvements):
            if regeneration_callback:
                return regeneration_callback(symbol, improvements)
            return pdf_path
        
        quality_score, attempts = self.gate_integrator.validate_with_retry(
            pdf_path, improvement_generator
        )
        
        benchmark_comparison = self.benchmarker.benchmark_against_industry(quality_score)
        
        return {
            'symbol': symbol,
            'pdf_path': pdf_path,
            'quality_score': {
                'total': quality_score.total,
                'structure': quality_score.structure,
                'content': quality_score.content,
                'typography': quality_score.typography,
                'technical': quality_score.technical,
                'accessibility': quality_score.accessibility,
                'passed': quality_score.passed
            },
            'issues': quality_score.issues,
            'improvements': quality_score.improvements,
            'benchmark_comparison': benchmark_comparison,
            'retry_attempts': attempts,
            'institutional_compliance': self._check_institutional_compliance(quality_score)
        }
    
    def _check_institutional_compliance(self, quality_score: QualityScore) -> Dict[str, bool]:
        """Check compliance with specific institutional standards"""
        return {
            'sec_compliant': quality_score.structure >= 80 and quality_score.content >= 85,
            'cfa_compliant': quality_score.typography >= 80 and quality_score.content >= 80,
            'wcag_compliant': quality_score.accessibility >= 80,
            'overall_institutional': quality_score.total >= 85
        }
    
    def _update_stats(self, quality_score: QualityScore):
        """Update validation statistics"""
        self.validation_stats['total_validations'] += 1
        
        if quality_score.passed:
            self.validation_stats['passed_first_attempt'] += 1
        
        # Update running average
        total = self.validation_stats['total_validations']
        current_avg = self.validation_stats['average_score']
        self.validation_stats['average_score'] = (
            (current_avg * (total - 1) + quality_score.total) / total
        )
    
    def get_performance_metrics(self) -> Dict:
        """Get validation performance metrics"""
        stats = self.validation_stats
        total = stats['total_validations']
        
        if total == 0:
            return {'message': 'No validations performed yet'}
        
        return {
            'total_validations': total,
            'success_rate_first_attempt': (stats['passed_first_attempt'] / total) * 100,
            'average_quality_score': stats['average_score'],
            'performance_grade': self._calculate_performance_grade(stats['average_score'])
        }
    
    def _calculate_performance_grade(self, avg_score: float) -> str:
        """Calculate performance grade based on average score"""
        if avg_score >= 95:
            return 'A+'
        elif avg_score >= 90:
            return 'A'
        elif avg_score >= 85:
            return 'B+'
        elif avg_score >= 80:
            return 'B'
        elif avg_score >= 75:
            return 'C+'
        else:
            return 'C'

# Integration with existing report generation
class QualityEnhancedReportGenerator:
    """Enhanced report generator with integrated quality validation"""
    
    def __init__(self, base_generator, quality_service: QualityValidationService):
        self.base_generator = base_generator
        self.quality_service = quality_service
        self.logger = logging.getLogger(__name__)
    
    async def generate_with_quality_gates(self, symbol: str, options: Dict) -> Dict:
        """Generate report with automatic quality validation and improvement"""
        
        # Generate initial report
        initial_result = await self.base_generator.generate_report(symbol, options)
        
        if not initial_result.get('success'):
            return initial_result
        
        pdf_path = initial_result['pdf_path']
        
        # Define improvement callback
        def regenerate_with_improvements(symbol: str, improvements: list) -> str:
            self.logger.info(f"Regenerating {symbol} with improvements: {improvements[:3]}...")
            
            # Apply specific improvements to options
            enhanced_options = self._apply_improvements(options, improvements)
            
            # Regenerate report
            result = asyncio.run(self.base_generator.generate_report(symbol, enhanced_options))
            return result.get('pdf_path', pdf_path)
        
        # Validate with automatic improvements
        validation_result = self.quality_service.validate_with_improvements(
            pdf_path, symbol, regenerate_with_improvements
        )
        
        # Combine results
        return {
            **initial_result,
            'quality_validation': validation_result,
            'final_quality_score': validation_result['quality_score']['total'],
            'institutional_compliant': validation_result['institutional_compliance']['overall_institutional']
        }
    
    def _apply_improvements(self, base_options: Dict, improvements: list) -> Dict:
        """Apply quality improvements to generation options"""
        enhanced_options = base_options.copy()
        
        # Map improvements to generation parameters
        improvement_mappings = {
            'Add PDF bookmarks': {'add_bookmarks': True},
            'Include comprehensive table of contents': {'include_toc': True},
            'Add more financial tables': {'enhanced_tables': True},
            'Use professional fonts': {'professional_typography': True},
            'Add PDF tags': {'accessibility_tags': True},
            'Include proper risk disclosures': {'enhanced_disclaimers': True}
        }
        
        for improvement in improvements:
            for key_phrase, options_update in improvement_mappings.items():
                if key_phrase.lower() in improvement.lower():
                    enhanced_options.update(options_update)
                    break
        
        return enhanced_options

# CLI tool for batch validation
class BatchValidator:
    """Command-line tool for batch PDF validation"""
    
    def __init__(self):
        self.quality_service = QualityValidationService()
    
    def validate_directory(self, directory_path: str, output_file: str = None) -> Dict:
        """Validate all PDFs in a directory"""
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            return {'error': 'No PDF files found in directory'}
        
        results = []
        
        for pdf_file in pdf_files:
            symbol = pdf_file.stem.split('_')[-1] if '_' in pdf_file.stem else pdf_file.stem
            
            result = asyncio.run(
                self.quality_service.validate_report_async(str(pdf_file), symbol)
            )
            results.append(result)
        
        # Generate summary
        summary = self._generate_batch_summary(results)
        
        # Save results if output file specified
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump({'summary': summary, 'detailed_results': results}, f, indent=2)
        
        return {'summary': summary, 'results': results}
    
    def _generate_batch_summary(self, results: list) -> Dict:
        """Generate summary statistics for batch validation"""
        total_files = len(results)
        passed_files = sum(1 for r in results if r.get('quality_score', {}).get('passed', False))
        
        if total_files == 0:
            return {'error': 'No files processed'}
        
        avg_score = sum(r.get('quality_score', {}).get('total', 0) for r in results) / total_files
        
        category_averages = {}
        categories = ['structure', 'content', 'typography', 'technical', 'accessibility']
        
        for category in categories:
            scores = [r.get('quality_score', {}).get(category, 0) for r in results]
            category_averages[category] = sum(scores) / len(scores) if scores else 0
        
        return {
            'total_files': total_files,
            'passed_files': passed_files,
            'pass_rate': (passed_files / total_files) * 100,
            'average_score': avg_score,
            'category_averages': category_averages,
            'grade': self.quality_service._calculate_performance_grade(avg_score)
        }