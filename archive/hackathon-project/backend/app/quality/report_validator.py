import asyncio
from typing import Dict, List, Any
from datetime import datetime
from .models import ValidationResult, ValidationLevel, ValidationStatus, ReportSection, QualityMetrics

class ReportLevelValidator:
    """Validates overall report quality with 80% minimum quality score and professional standards"""
    
    def __init__(self):
        self.min_quality_score = 0.80
        self.professional_standards = {
            'min_total_pages': 20,
            'max_total_pages': 35,
            'min_charts': 8,
            'required_sections': 6,
            'min_references': 5
        }
        
    async def validate_report(self, 
                            section_results: Dict[ReportSection, ValidationResult],
                            cross_section_result: ValidationResult,
                            report_data: Dict[str, Any]) -> ValidationResult:
        """Validate overall report quality and professional standards"""
        issues = []
        warnings = []
        scores = {}
        
        # Calculate section quality score
        section_score = await self._calculate_section_quality(section_results, issues, warnings)
        scores['section_quality'] = section_score
        
        # Validate professional standards
        standards_score = await self._validate_professional_standards(report_data, issues, warnings)
        scores['professional_standards'] = standards_score
        
        # Cross-section consistency score
        scores['cross_section_consistency'] = cross_section_result.score
        
        # Content depth and analysis quality
        depth_score = await self._validate_content_depth(report_data, issues, warnings)
        scores['content_depth'] = depth_score
        
        # Visual presentation quality
        visual_score = await self._validate_visual_presentation(report_data, issues, warnings)
        scores['visual_presentation'] = visual_score
        
        # Calculate overall quality score
        weights = {
            'section_quality': 0.35,
            'professional_standards': 0.20,
            'cross_section_consistency': 0.20,
            'content_depth': 0.15,
            'visual_presentation': 0.10
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        # Determine status based on minimum quality threshold
        status = ValidationStatus.PASSED if overall_score >= self.min_quality_score else ValidationStatus.FAILED
        
        # Flag for manual review if close to threshold or has critical issues
        requires_manual_review = (
            0.75 <= overall_score < self.min_quality_score or
            any('critical' in issue.lower() for issue in issues) or
            len(issues) > 10
        )
        
        if requires_manual_review and status == ValidationStatus.FAILED:
            status = ValidationStatus.MANUAL_REVIEW
            
        return ValidationResult(
            level=ValidationLevel.REPORT,
            section=None,
            status=status,
            score=overall_score,
            issues=issues,
            warnings=warnings,
            metadata={
                'scores': scores,
                'requires_manual_review': requires_manual_review,
                'quality_metrics': self._create_quality_metrics(scores, overall_score)
            },
            timestamp=datetime.utcnow()
        )
    
    async def _calculate_section_quality(self, section_results: Dict[ReportSection, ValidationResult], issues: List[str], warnings: List[str]) -> float:
        """Calculate average quality score across all sections"""
        if not section_results:
            issues.append("No section validation results available")
            return 0.0
            
        total_score = 0.0
        failed_sections = []
        
        for section, result in section_results.items():
            total_score += result.score
            if result.status == ValidationStatus.FAILED:
                failed_sections.append(section.value)
                
        average_score = total_score / len(section_results)
        
        if failed_sections:
            issues.append(f"Failed sections: {', '.join(failed_sections)}")
            
        # Penalize if too many sections need retry
        retry_sections = [s for s, r in section_results.items() if r.status == ValidationStatus.RETRY]
        if len(retry_sections) > 2:
            warnings.append(f"Multiple sections need retry: {len(retry_sections)}")
            average_score *= 0.9
            
        return average_score
    
    async def _validate_professional_standards(self, report_data: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate professional presentation standards"""
        score = 1.0
        
        # Check total page count
        total_pages = report_data.get('total_pages', 0)
        min_pages = self.professional_standards['min_total_pages']
        max_pages = self.professional_standards['max_total_pages']
        
        if total_pages < min_pages:
            issues.append(f"Report too short: {total_pages} pages (minimum: {min_pages})")
            score -= 0.3
        elif total_pages > max_pages:
            warnings.append(f"Report may be too long: {total_pages} pages (maximum: {max_pages})")
            score -= 0.1
            
        # Check number of charts/visualizations
        total_charts = sum(len(section.get('charts', [])) for section in report_data.get('sections', {}).values())
        min_charts = self.professional_standards['min_charts']
        
        if total_charts < min_charts:
            issues.append(f"Insufficient visualizations: {total_charts} charts (minimum: {min_charts})")
            score -= 0.2
            
        # Check section completeness
        available_sections = len(report_data.get('sections', {}))
        required_sections = self.professional_standards['required_sections']
        
        if available_sections < required_sections:
            issues.append(f"Missing sections: {available_sections}/{required_sections} sections present")
            score -= 0.4
            
        # Check references and sources
        total_references = len(report_data.get('references', []))
        min_references = self.professional_standards['min_references']
        
        if total_references < min_references:
            warnings.append(f"Limited references: {total_references} (recommended: {min_references}+)")
            score -= 0.1
            
        # Check executive summary quality (critical for professional reports)
        exec_summary = report_data.get('sections', {}).get('executive_summary', {})
        if not exec_summary.get('price_target'):
            issues.append("Missing price target in executive summary")
            score -= 0.3
            
        if not exec_summary.get('rating'):
            issues.append("Missing investment rating in executive summary")
            score -= 0.2
            
        return max(0.0, score)
    
    async def _validate_content_depth(self, report_data: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate content depth and analytical rigor"""
        score = 1.0
        
        # Check financial analysis depth
        financial_section = report_data.get('sections', {}).get('financial_analysis', {})
        financial_data = financial_section.get('financial_data', {})
        
        if not financial_data:
            issues.append("No financial data in financial analysis section")
            score -= 0.4
        else:
            # Check historical data depth
            annual_data = financial_data.get('annual_data', {})
            if len(annual_data) < 3:
                warnings.append(f"Limited historical data: {len(annual_data)} years")
                score -= 0.2
                
            # Check key metrics presence
            required_metrics = ['revenue', 'net_income', 'total_assets', 'shareholders_equity']
            missing_metrics = [m for m in required_metrics if m not in financial_data.get('key_metrics', {})]
            
            if missing_metrics:
                issues.append(f"Missing key financial metrics: {', '.join(missing_metrics)}")
                score -= 0.2
                
        # Check valuation analysis depth
        valuation_section = report_data.get('sections', {}).get('valuation_analysis', {})
        
        if not valuation_section.get('dcf_valuation'):
            issues.append("No DCF valuation provided")
            score -= 0.3
            
        if not valuation_section.get('peer_comparison'):
            warnings.append("No peer comparison analysis")
            score -= 0.1
            
        # Check risk analysis comprehensiveness
        risk_section = report_data.get('sections', {}).get('risk_assessment', {})
        risks = risk_section.get('key_risks', [])
        
        if len(risks) < 3:
            warnings.append(f"Limited risk analysis: {len(risks)} risks identified")
            score -= 0.1
        elif len(risks) > 8:
            warnings.append("Risk analysis may be too detailed")
            score -= 0.05
            
        return max(0.0, score)
    
    async def _validate_visual_presentation(self, report_data: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate visual presentation and chart quality"""
        score = 1.0
        
        sections = report_data.get('sections', {})
        chart_quality_issues = 0
        
        for section_name, section_data in sections.items():
            charts = section_data.get('charts', [])
            
            for i, chart in enumerate(charts):
                # Check chart completeness
                if not chart.get('title'):
                    chart_quality_issues += 1
                    
                if not chart.get('data', {}).get('labels'):
                    chart_quality_issues += 1
                    
                # Check data quality
                datasets = chart.get('data', {}).get('datasets', [])
                for dataset in datasets:
                    if not dataset.get('data') or len(dataset['data']) == 0:
                        chart_quality_issues += 1
                        
        # Penalize based on chart quality issues
        if chart_quality_issues > 0:
            penalty = min(0.5, chart_quality_issues * 0.05)
            score -= penalty
            
            if chart_quality_issues > 5:
                issues.append(f"Multiple chart quality issues: {chart_quality_issues} problems found")
            else:
                warnings.append(f"Chart quality issues: {chart_quality_issues} problems found")
                
        # Check for consistent styling (simplified check)
        chart_types = set()
        for section_data in sections.values():
            for chart in section_data.get('charts', []):
                chart_types.add(chart.get('type'))
                
        if len(chart_types) > 6:
            warnings.append("Too many different chart types - consider consistency")
            score -= 0.1
            
        return max(0.0, score)
    
    def _create_quality_metrics(self, scores: Dict[str, float], overall_score: float) -> QualityMetrics:
        """Create quality metrics summary"""
        return QualityMetrics(
            completeness_score=scores.get('section_quality', 0.0),
            accuracy_score=scores.get('content_depth', 0.0),
            consistency_score=scores.get('cross_section_consistency', 0.0),
            format_score=scores.get('professional_standards', 0.0),
            overall_score=overall_score
        )