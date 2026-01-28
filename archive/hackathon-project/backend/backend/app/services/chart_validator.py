"""
Chart Validation and Quality Assurance Service
Validates chart configurations and ensures professional quality standards
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ChartValidator:
    """
    Validates Chart.js configurations and ensures quality standards
    Performs comprehensive validation for institutional-quality charts
    """
    
    def __init__(self):
        self.validation_rules = {
            'required_fields': ['type', 'data', 'options'],
            'valid_chart_types': ['line', 'bar', 'radar', 'doughnut', 'pie', 'scatter', 'bubble'],
            'max_datasets': 10,
            'max_data_points': 100,
            'min_data_points': 1,
            'required_data_fields': ['labels', 'datasets'],
            'color_pattern': r'^#[0-9A-Fa-f]{6}$|^rgba?\([^)]+\)$'
        }
        
        self.quality_standards = {
            'title_required': True,
            'legend_required': True,
            'responsive_required': True,
            'accessibility_required': True,
            'professional_colors': True,
            'proper_scaling': True
        }
    
    def validate_chart_config(self, config: Dict[str, Any], chart_name: str = '') -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Comprehensive chart configuration validation
        
        Returns:
            Tuple of (is_valid, error_messages, validation_report)
        """
        try:
            errors = []
            warnings = []
            validation_report = {
                'chart_name': chart_name,
                'validated_at': datetime.utcnow().isoformat(),
                'validation_version': '1.0.0',
                'overall_score': 0,
                'quality_checks': {}
            }
            
            # Basic structure validation
            structure_valid, structure_errors = self._validate_structure(config)
            errors.extend(structure_errors)
            
            if structure_valid:
                # Data validation
                data_valid, data_errors, data_warnings = self._validate_data(config['data'])
                errors.extend(data_errors)
                warnings.extend(data_warnings)
                
                # Options validation
                options_valid, options_errors, options_warnings = self._validate_options(config['options'])
                errors.extend(options_errors)
                warnings.extend(options_warnings)
                
                # Quality standards validation
                quality_score, quality_checks = self._validate_quality_standards(config)
                validation_report['quality_checks'] = quality_checks
                validation_report['overall_score'] = quality_score
                
                # Accessibility validation
                accessibility_valid, accessibility_warnings = self._validate_accessibility(config)
                warnings.extend(accessibility_warnings)
                
                # Performance validation
                performance_valid, performance_warnings = self._validate_performance(config)
                warnings.extend(performance_warnings)
            
            validation_report['errors'] = errors
            validation_report['warnings'] = warnings
            validation_report['is_valid'] = len(errors) == 0
            
            if len(errors) > 0:
                logger.warning(f"Chart validation failed for {chart_name}: {errors}")
            elif len(warnings) > 0:
                logger.info(f"Chart validation passed with warnings for {chart_name}: {warnings}")
            else:
                logger.info(f"Chart validation passed for {chart_name}")
            
            return len(errors) == 0, errors, validation_report
            
        except Exception as e:
            logger.error(f"Error during chart validation: {e}")
            return False, [f"Validation error: {str(e)}"], {}
    
    def _validate_structure(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate basic chart structure"""
        errors = []
        
        # Check required top-level fields
        for field in self.validation_rules['required_fields']:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate chart type
        if 'type' in config:
            chart_type = config['type']
            if chart_type not in self.validation_rules['valid_chart_types']:
                errors.append(f"Invalid chart type: {chart_type}")
        
        return len(errors) == 0, errors
    
    def _validate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate chart data structure"""
        errors = []
        warnings = []
        
        # Check required data fields
        for field in self.validation_rules['required_data_fields']:
            if field not in data:
                errors.append(f"Missing required data field: {field}")
        
        if 'labels' in data and 'datasets' in data:
            labels = data['labels']
            datasets = data['datasets']
            
            # Validate labels
            if not isinstance(labels, list):
                errors.append("Labels must be a list")
            elif len(labels) == 0:
                errors.append("Labels cannot be empty")
            elif len(labels) > self.validation_rules['max_data_points']:
                warnings.append(f"Large number of labels ({len(labels)}) may impact performance")
            
            # Validate datasets
            if not isinstance(datasets, list):
                errors.append("Datasets must be a list")
            elif len(datasets) == 0:
                errors.append("At least one dataset is required")
            elif len(datasets) > self.validation_rules['max_datasets']:
                warnings.append(f"Large number of datasets ({len(datasets)}) may impact readability")
            
            # Validate each dataset
            for i, dataset in enumerate(datasets):
                if not isinstance(dataset, dict):
                    errors.append(f"Dataset {i} must be an object")
                    continue
                
                # Check dataset data
                if 'data' not in dataset:
                    errors.append(f"Dataset {i} missing data field")
                elif not isinstance(dataset['data'], list):
                    errors.append(f"Dataset {i} data must be a list")
                elif len(dataset['data']) != len(labels):
                    errors.append(f"Dataset {i} data length doesn't match labels length")
                
                # Validate colors
                color_fields = ['backgroundColor', 'borderColor']
                for color_field in color_fields:
                    if color_field in dataset:
                        color_valid = self._validate_color(dataset[color_field])
                        if not color_valid:
                            warnings.append(f"Dataset {i} {color_field} may not be a valid color")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate chart options"""
        errors = []
        warnings = []
        
        # Check responsive setting
        if 'responsive' not in options:
            warnings.append("Responsive option not set - chart may not scale properly")
        elif not options['responsive']:
            warnings.append("Chart is not responsive - may not work well on mobile")
        
        # Validate plugins
        if 'plugins' in options:
            plugins = options['plugins']
            
            # Check title
            if 'title' not in plugins:
                warnings.append("Chart title not configured")
            elif not plugins['title'].get('display', False):
                warnings.append("Chart title is not displayed")
            
            # Check legend
            if 'legend' in plugins and not plugins['legend'].get('display', True):
                warnings.append("Legend is disabled - may reduce chart clarity")
        
        # Validate scales (for charts that use scales)
        if 'scales' in options:
            scales = options['scales']
            
            # Check axis titles
            for axis in ['x', 'y']:
                if axis in scales:
                    axis_config = scales[axis]
                    if 'title' not in axis_config or not axis_config['title'].get('display', False):
                        warnings.append(f"{axis.upper()}-axis title not configured")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_quality_standards(self, config: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Validate against quality standards"""
        quality_checks = {}
        total_score = 0
        max_score = len(self.quality_standards) * 10
        
        # Title check
        has_title = (
            config.get('options', {}).get('plugins', {}).get('title', {}).get('display', False)
        )
        quality_checks['title'] = {
            'passed': has_title,
            'score': 10 if has_title else 0,
            'message': 'Chart has proper title' if has_title else 'Chart missing title'
        }
        total_score += quality_checks['title']['score']
        
        # Legend check
        legend_config = config.get('options', {}).get('plugins', {}).get('legend', {})
        has_legend = legend_config.get('display', True)
        quality_checks['legend'] = {
            'passed': has_legend,
            'score': 10 if has_legend else 0,
            'message': 'Chart has legend' if has_legend else 'Chart missing legend'
        }
        total_score += quality_checks['legend']['score']
        
        # Responsive check
        is_responsive = config.get('options', {}).get('responsive', False)
        quality_checks['responsive'] = {
            'passed': is_responsive,
            'score': 10 if is_responsive else 0,
            'message': 'Chart is responsive' if is_responsive else 'Chart not responsive'
        }
        total_score += quality_checks['responsive']['score']
        
        # Color scheme check
        has_professional_colors = self._check_professional_colors(config)
        quality_checks['colors'] = {
            'passed': has_professional_colors,
            'score': 10 if has_professional_colors else 5,
            'message': 'Professional color scheme' if has_professional_colors else 'Basic color scheme'
        }
        total_score += quality_checks['colors']['score']
        
        # Accessibility check
        has_accessibility = self._check_accessibility_features(config)
        quality_checks['accessibility'] = {
            'passed': has_accessibility,
            'score': 10 if has_accessibility else 0,
            'message': 'Accessibility features present' if has_accessibility else 'Missing accessibility features'
        }
        total_score += quality_checks['accessibility']['score']
        
        # Scaling check
        has_proper_scaling = self._check_proper_scaling(config)
        quality_checks['scaling'] = {
            'passed': has_proper_scaling,
            'score': 10 if has_proper_scaling else 5,
            'message': 'Proper axis scaling' if has_proper_scaling else 'Basic axis scaling'
        }
        total_score += quality_checks['scaling']['score']
        
        overall_score = int((total_score / max_score) * 100)
        return overall_score, quality_checks
    
    def _validate_accessibility(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate accessibility features"""
        warnings = []
        
        # Check for alt text or aria labels
        options = config.get('options', {})
        plugins = options.get('plugins', {})
        
        # Check tooltip configuration
        if 'tooltip' not in plugins:
            warnings.append("Tooltips not configured - may impact accessibility")
        
        # Check color contrast (basic check)
        datasets = config.get('data', {}).get('datasets', [])
        for i, dataset in enumerate(datasets):
            if 'backgroundColor' in dataset and 'borderColor' in dataset:
                bg_color = dataset['backgroundColor']
                border_color = dataset['borderColor']
                if bg_color == border_color:
                    warnings.append(f"Dataset {i} background and border colors are identical - may impact visibility")
        
        return len(warnings) == 0, warnings
    
    def _validate_performance(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate performance considerations"""
        warnings = []
        
        # Check data size
        datasets = config.get('data', {}).get('datasets', [])
        labels = config.get('data', {}).get('labels', [])
        
        if len(labels) > 50:
            warnings.append(f"Large number of data points ({len(labels)}) may impact performance")
        
        if len(datasets) > 5:
            warnings.append(f"Large number of datasets ({len(datasets)}) may impact performance")
        
        # Check animation settings
        options = config.get('options', {})
        if 'animation' in options and options['animation'].get('duration', 1000) > 2000:
            warnings.append("Long animation duration may impact user experience")
        
        return len(warnings) == 0, warnings
    
    def _validate_color(self, color: Any) -> bool:
        """Validate color format"""
        if isinstance(color, str):
            return bool(re.match(self.validation_rules['color_pattern'], color))
        elif isinstance(color, list):
            return all(self._validate_color(c) for c in color)
        return False
    
    def _check_professional_colors(self, config: Dict[str, Any]) -> bool:
        """Check if chart uses professional color scheme"""
        professional_colors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#06B6D4', '#EC4899', '#6366F1', '#84CC16', '#F97316'
        ]
        
        datasets = config.get('data', {}).get('datasets', [])
        for dataset in datasets:
            bg_color = dataset.get('backgroundColor', '')
            border_color = dataset.get('borderColor', '')
            
            if isinstance(bg_color, str) and bg_color.startswith('#'):
                if bg_color not in professional_colors:
                    return False
            
            if isinstance(border_color, str) and border_color.startswith('#'):
                if border_color not in professional_colors:
                    return False
        
        return True
    
    def _check_accessibility_features(self, config: Dict[str, Any]) -> bool:
        """Check for accessibility features"""
        options = config.get('options', {})
        plugins = options.get('plugins', {})
        
        # Check for tooltips
        has_tooltips = 'tooltip' in plugins
        
        # Check for proper labels
        has_labels = bool(config.get('data', {}).get('labels', []))
        
        # Check for legend
        has_legend = plugins.get('legend', {}).get('display', True)
        
        return has_tooltips and has_labels and has_legend
    
    def _check_proper_scaling(self, config: Dict[str, Any]) -> bool:
        """Check for proper axis scaling"""
        options = config.get('options', {})
        scales = options.get('scales', {})
        
        # Check if axes have titles
        has_axis_titles = False
        for axis in ['x', 'y']:
            if axis in scales:
                axis_config = scales[axis]
                if axis_config.get('title', {}).get('display', False):
                    has_axis_titles = True
                    break
        
        return has_axis_titles
    
    def validate_chart_suite(self, charts: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire chart suite"""
        suite_report = {
            'validated_at': datetime.utcnow().isoformat(),
            'total_charts': 0,
            'valid_charts': 0,
            'invalid_charts': 0,
            'average_quality_score': 0,
            'chart_reports': {},
            'suite_warnings': []
        }
        
        total_quality_score = 0
        
        for chart_name, chart_config in charts.items():
            if chart_name in ['metadata', '_validation']:
                continue
            
            suite_report['total_charts'] += 1
            
            # Validate individual chart
            is_valid, errors, validation_report = self.validate_chart_config(chart_config, chart_name)
            
            suite_report['chart_reports'][chart_name] = validation_report
            
            if is_valid:
                suite_report['valid_charts'] += 1
            else:
                suite_report['invalid_charts'] += 1
            
            total_quality_score += validation_report.get('overall_score', 0)
        
        # Calculate average quality score
        if suite_report['total_charts'] > 0:
            suite_report['average_quality_score'] = int(total_quality_score / suite_report['total_charts'])
        
        # Suite-level warnings
        if suite_report['invalid_charts'] > 0:
            suite_report['suite_warnings'].append(f"{suite_report['invalid_charts']} charts failed validation")
        
        if suite_report['average_quality_score'] < 70:
            suite_report['suite_warnings'].append("Average quality score below recommended threshold (70)")
        
        return suite_report
    
    def create_validation_summary(self, validation_report: Dict[str, Any]) -> str:
        """Create human-readable validation summary"""
        summary_lines = []
        
        summary_lines.append(f"Chart Validation Report")
        summary_lines.append(f"Validated at: {validation_report.get('validated_at', 'Unknown')}")
        summary_lines.append(f"Overall Score: {validation_report.get('overall_score', 0)}/100")
        
        if validation_report.get('is_valid', False):
            summary_lines.append("✅ Chart configuration is valid")
        else:
            summary_lines.append("❌ Chart configuration has errors")
        
        errors = validation_report.get('errors', [])
        if errors:
            summary_lines.append(f"\nErrors ({len(errors)}):")
            for error in errors:
                summary_lines.append(f"  • {error}")
        
        warnings = validation_report.get('warnings', [])
        if warnings:
            summary_lines.append(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                summary_lines.append(f"  • {warning}")
        
        quality_checks = validation_report.get('quality_checks', {})
        if quality_checks:
            summary_lines.append(f"\nQuality Checks:")
            for check_name, check_result in quality_checks.items():
                status = "✅" if check_result['passed'] else "❌"
                summary_lines.append(f"  {status} {check_result['message']} ({check_result['score']}/10)")
        
        return "\n".join(summary_lines)