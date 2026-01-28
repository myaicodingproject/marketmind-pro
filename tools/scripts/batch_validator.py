#!/usr/bin/env python3
"""
Batch PDF Quality Validator
Validates multiple PDFs and generates comprehensive quality reports
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scripts.pdf_validator import validate_single_pdf, setup_logging

class BatchQualityValidator:
    """Enhanced batch validator with detailed reporting"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def validate_files(self, pdf_paths: List[str], verbose: bool = False) -> Dict:
        """Validate multiple PDF files"""
        setup_logging(verbose)
        self.start_time = time.time()
        
        print(f"Starting batch validation of {len(pdf_paths)} PDF files...")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\n[{i}/{len(pdf_paths)}] Validating: {Path(pdf_path).name}")
            
            result = validate_single_pdf(pdf_path, verbose=False)
            result['file_index'] = i
            result['file_name'] = Path(pdf_path).name
            self.results.append(result)
            
            # Show quick status
            if 'quality_score' in result:
                score = result['quality_score']['total']
                status = "PASSED" if result['quality_score']['passed'] else "FAILED"
                print(f"    Score: {score:.1f}/100 ({status})")
            else:
                print(f"    ERROR: {result.get('error', 'Unknown error')}")
        
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate detailed batch validation report"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        # Filter successful validations
        successful_results = [r for r in self.results if 'quality_score' in r]
        failed_results = [r for r in self.results if 'error' in r]
        
        if not successful_results:
            return {
                'summary': {
                    'total_files': len(self.results),
                    'successful_validations': 0,
                    'failed_validations': len(failed_results),
                    'error': 'No successful validations'
                },
                'failed_files': failed_results
            }
        
        # Calculate statistics
        scores = [r['quality_score']['total'] for r in successful_results]
        passed_count = sum(1 for r in successful_results if r['quality_score']['passed'])
        
        # Category statistics
        categories = ['structure', 'content', 'typography', 'technical', 'accessibility']
        category_stats = {}
        
        for category in categories:
            category_scores = [r['quality_score'][category] for r in successful_results]
            category_stats[category] = {
                'average': sum(category_scores) / len(category_scores),
                'min': min(category_scores),
                'max': max(category_scores),
                'below_80': sum(1 for s in category_scores if s < 80)
            }
        
        # Institutional compliance statistics
        compliance_stats = {
            'sec_compliant': 0,
            'cfa_compliant': 0,
            'wcag_compliant': 0,
            'overall_institutional': 0
        }
        
        for result in successful_results:
            if 'institutional_compliance' in result:
                compliance = result['institutional_compliance']
                for key in compliance_stats:
                    if compliance.get(key, False):
                        compliance_stats[key] += 1
        
        # Common issues analysis
        all_issues = []
        for result in successful_results:
            all_issues.extend(result.get('issues', []))
        
        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1
        
        # Top improvement recommendations
        all_improvements = []
        for result in successful_results:
            all_improvements.extend(result.get('improvements', []))
        
        improvement_frequency = {}
        for improvement in all_improvements:
            improvement_frequency[improvement] = improvement_frequency.get(improvement, 0) + 1
        
        return {
            'summary': {
                'total_files': len(self.results),
                'successful_validations': len(successful_results),
                'failed_validations': len(failed_results),
                'pass_rate': (passed_count / len(successful_results)) * 100,
                'average_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'validation_time': total_time,
                'files_per_second': len(self.results) / total_time if total_time > 0 else 0
            },
            'category_analysis': category_stats,
            'institutional_compliance': {
                key: (count / len(successful_results)) * 100 
                for key, count in compliance_stats.items()
            },
            'common_issues': sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_improvements': sorted(improvement_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            'detailed_results': successful_results,
            'failed_files': failed_results
        }
    
    def print_comprehensive_report(self, report: Dict):
        """Print detailed batch validation report"""
        summary = report['summary']
        
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE PDF QUALITY VALIDATION REPORT")
        print(f"{'='*80}")
        
        print(f"\nEXECUTIVE SUMMARY:")
        print(f"  Total Files Processed:     {summary['total_files']}")
        print(f"  Successful Validations:    {summary['successful_validations']}")
        print(f"  Failed Validations:        {summary['failed_validations']}")
        print(f"  Overall Pass Rate:         {summary['pass_rate']:.1f}%")
        print(f"  Average Quality Score:     {summary['average_score']:.1f}/100")
        print(f"  Score Range:               {summary['min_score']:.1f} - {summary['max_score']:.1f}")
        print(f"  Total Validation Time:     {summary['validation_time']:.2f} seconds")
        print(f"  Processing Speed:          {summary['files_per_second']:.2f} files/second")
        
        print(f"\nCATEGORY PERFORMANCE ANALYSIS:")
        for category, stats in report['category_analysis'].items():
            print(f"  {category.title():15}: Avg {stats['average']:.1f} | Range {stats['min']:.1f}-{stats['max']:.1f} | {stats['below_80']} files below 80")
        
        print(f"\nINSTITUTIONAL COMPLIANCE RATES:")
        for standard, rate in report['institutional_compliance'].items():
            print(f"  {standard.replace('_', ' ').title():20}: {rate:.1f}%")
        
        if report['common_issues']:
            print(f"\nMOST COMMON ISSUES:")
            for issue, count in report['common_issues'][:5]:
                print(f"  [{count:2d}] {issue}")
        
        if report['top_improvements']:
            print(f"\nTOP IMPROVEMENT RECOMMENDATIONS:")
            for improvement, count in report['top_improvements'][:5]:
                print(f"  [{count:2d}] {improvement}")
        
        if report['failed_files']:
            print(f"\nFAILED VALIDATIONS:")
            for failed in report['failed_files']:
                print(f"  - {failed['file_name']}: {failed.get('error', 'Unknown error')}")
        
        print(f"\n{'='*80}")

def main():
    """Main function for batch validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch PDF Quality Validator')
    parser.add_argument('files', nargs='+', help='PDF files to validate')
    parser.add_argument('--output', '-o', help='Output JSON file for detailed results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate file paths
    valid_files = []
    for file_path in args.files:
        if Path(file_path).exists():
            valid_files.append(file_path)
        else:
            print(f"Warning: File not found: {file_path}")
    
    if not valid_files:
        print("Error: No valid PDF files found")
        return
    
    # Run batch validation
    validator = BatchQualityValidator()
    report = validator.validate_files(valid_files, args.verbose)
    
    # Print comprehensive report
    validator.print_comprehensive_report(report)
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {args.output}")

if __name__ == '__main__':
    main()