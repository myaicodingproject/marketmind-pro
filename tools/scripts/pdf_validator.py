#!/usr/bin/env python3
"""
MarketMind Pro - PDF Quality Validation CLI Tool
Command-line interface for validating PDF quality against institutional standards
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
import logging

# Add the app directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.quality.pdf_quality_validator import PDFQualityValidator, PerformanceBenchmarker
from app.services.quality_validation_service import QualityValidationService, BatchValidator

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_single_pdf(pdf_path: str, verbose: bool = False) -> dict:
    """Validate a single PDF file"""
    setup_logging(verbose)
    
    if not Path(pdf_path).exists():
        return {'error': f'PDF file not found: {pdf_path}'}
    
    service = QualityValidationService()
    symbol = Path(pdf_path).stem.split('_')[-1] if '_' in Path(pdf_path).stem else 'UNKNOWN'
    
    result = asyncio.run(service.validate_report_async(pdf_path, symbol))
    return result

def validate_batch(directory: str, output_file: str = None, verbose: bool = False) -> dict:
    """Validate all PDFs in a directory"""
    setup_logging(verbose)
    
    if not Path(directory).exists():
        return {'error': f'Directory not found: {directory}'}
    
    validator = BatchValidator()
    results = validator.validate_directory(directory, output_file)
    return results

def benchmark_pdf(pdf_path: str, verbose: bool = False) -> dict:
    """Benchmark a PDF against industry standards"""
    setup_logging(verbose)
    
    if not Path(pdf_path).exists():
        return {'error': f'PDF file not found: {pdf_path}'}
    
    validator = PDFQualityValidator()
    benchmarker = PerformanceBenchmarker()
    
    quality_score = validator.validate_pdf(pdf_path)
    benchmark_report = benchmarker.generate_benchmark_report(quality_score)
    
    return {
        'quality_score': quality_score,
        'benchmark_report': benchmark_report
    }

def print_results(results: dict, format_type: str = 'text'):
    """Print validation results in specified format"""
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    if format_type == 'json':
        print(json.dumps(results, indent=2, default=str))
        return
    
    # Text format output
    if 'quality_score' in results:
        # Single file results
        score = results['quality_score']
        print(f"\n{'='*60}")
        print(f"PDF Quality Validation Report")
        print(f"{'='*60}")
        print(f"File: {results.get('pdf_path', 'Unknown')}")
        print(f"Symbol: {results.get('symbol', 'Unknown')}")
        print(f"\nOverall Score: {score['total']:.1f}/100 ({'PASSED' if score['passed'] else 'FAILED'})")
        
        print(f"\nCategory Breakdown:")
        print(f"  Structure:     {score['structure']:.1f}/100")
        print(f"  Content:       {score['content']:.1f}/100")
        print(f"  Typography:    {score['typography']:.1f}/100")
        print(f"  Technical:     {score['technical']:.1f}/100")
        print(f"  Accessibility: {score['accessibility']:.1f}/100")
        
        if 'institutional_compliance' in results:
            compliance = results['institutional_compliance']
            print(f"\nInstitutional Compliance:")
            print(f"  SEC Compliant:  {'✓' if compliance['sec_compliant'] else '✗'}")
            print(f"  CFA Compliant:  {'✓' if compliance['cfa_compliant'] else '✗'}")
            print(f"  WCAG Compliant: {'✓' if compliance['wcag_compliant'] else '✗'}")
            print(f"  Overall:        {'✓' if compliance['overall_institutional'] else '✗'}")
        
        if results.get('issues'):
            print(f"\nIssues Identified:")
            for issue in results['issues']:
                print(f"  - {issue}")
        
        if results.get('improvements'):
            print(f"\nRecommended Improvements:")
            for improvement in results['improvements'][:5]:  # Show top 5
                print(f"  - {improvement}")
    
    elif 'summary' in results:
        # Batch results
        summary = results['summary']
        print(f"\n{'='*60}")
        print(f"Batch PDF Quality Validation Summary")
        print(f"{'='*60}")
        print(f"Total Files:    {summary['total_files']}")
        print(f"Passed Files:   {summary['passed_files']}")
        print(f"Pass Rate:      {summary['pass_rate']:.1f}%")
        print(f"Average Score:  {summary['average_score']:.1f}/100")
        print(f"Overall Grade:  {summary['grade']}")
        
        print(f"\nCategory Averages:")
        for category, avg in summary['category_averages'].items():
            print(f"  {category.title():12}: {avg:.1f}/100")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='MarketMind Pro PDF Quality Validation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single PDF
  python pdf_validator.py validate GOOGL_Enhanced_Professional.pdf
  
  # Validate all PDFs in directory
  python pdf_validator.py batch ./reports/ --output results.json
  
  # Benchmark against industry standards
  python pdf_validator.py benchmark GOOGL_Enhanced_Professional.pdf
  
  # Get JSON output
  python pdf_validator.py validate report.pdf --format json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single file validation
    validate_parser = subparsers.add_parser('validate', help='Validate a single PDF')
    validate_parser.add_argument('pdf_path', help='Path to PDF file')
    validate_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Output format')
    validate_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')
    
    # Batch validation
    batch_parser = subparsers.add_parser('batch', help='Validate all PDFs in directory')
    batch_parser.add_argument('directory', help='Directory containing PDF files')
    batch_parser.add_argument('--output', '-o', help='Output file for results')
    batch_parser.add_argument('--format', choices=['text', 'json'], default='text',
                            help='Output format')
    batch_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Verbose output')
    
    # Benchmark
    benchmark_parser = subparsers.add_parser('benchmark', help='Benchmark against industry standards')
    benchmark_parser.add_argument('pdf_path', help='Path to PDF file')
    benchmark_parser.add_argument('--format', choices=['text', 'json'], default='text',
                                help='Output format')
    benchmark_parser.add_argument('--verbose', '-v', action='store_true',
                                help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'validate':
            results = validate_single_pdf(args.pdf_path, args.verbose)
            print_results(results, args.format)
            
        elif args.command == 'batch':
            results = validate_batch(args.directory, args.output, args.verbose)
            print_results(results, args.format)
            
        elif args.command == 'benchmark':
            results = benchmark_pdf(args.pdf_path, args.verbose)
            if args.format == 'json':
                print(json.dumps(results, indent=2, default=str))
            else:
                print(results['benchmark_report'])
    
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()