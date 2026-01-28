"""
Chart.js Configuration Generator
Generates professional Chart.js configurations with validation and styling
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ChartConfigGenerator:
    """
    Generates Chart.js configurations with professional styling and validation
    Ensures all charts meet institutional quality standards
    """
    
    def __init__(self):
        self.brand_colors = {
            'primary': '#3B82F6',
            'secondary': '#6366F1',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'info': '#06B6D4',
            'purple': '#8B5CF6',
            'pink': '#EC4899',
            'neutral': '#6B7280',
            'dark': '#1F2937'
        }
        
        self.chart_defaults = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top',
                    'labels': {
                        'usePointStyle': True,
                        'padding': 20,
                        'font': {
                            'size': 12,
                            'family': 'Inter, system-ui, sans-serif'
                        }
                    }
                },
                'tooltip': {
                    'backgroundColor': 'rgba(0, 0, 0, 0.8)',
                    'titleColor': '#fff',
                    'bodyColor': '#fff',
                    'borderColor': '#3B82F6',
                    'borderWidth': 1,
                    'cornerRadius': 8,
                    'displayColors': True
                }
            },
            'elements': {
                'point': {
                    'radius': 4,
                    'hoverRadius': 6,
                    'borderWidth': 2
                },
                'line': {
                    'borderWidth': 3,
                    'tension': 0.4
                },
                'bar': {
                    'borderRadius': 4,
                    'borderSkipped': False
                }
            }
        }
    
    def generate_line_chart(
        self, 
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        y_axis_title: str = '',
        x_axis_title: str = '',
        **options
    ) -> Dict[str, Any]:
        """Generate line chart configuration"""
        try:
            # Apply default styling to datasets
            styled_datasets = []
            for i, dataset in enumerate(datasets):
                styled_dataset = self._apply_line_styling(dataset, i)
                styled_datasets.append(styled_dataset)
            
            config = {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': styled_datasets
                },
                'options': self._merge_options({
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': title,
                            'font': {
                                'size': 16,
                                'weight': 'bold',
                                'family': 'Inter, system-ui, sans-serif'
                            },
                            'padding': 20
                        }
                    },
                    'scales': {
                        'y': {
                            'title': {
                                'display': bool(y_axis_title),
                                'text': y_axis_title,
                                'font': {'size': 12, 'weight': '600'}
                            },
                            'grid': {
                                'color': '#E5E7EB',
                                'drawBorder': False
                            },
                            'ticks': {
                                'font': {'size': 11}
                            }
                        },
                        'x': {
                            'title': {
                                'display': bool(x_axis_title),
                                'text': x_axis_title,
                                'font': {'size': 12, 'weight': '600'}
                            },
                            'grid': {
                                'color': '#F3F4F6',
                                'drawBorder': False
                            },
                            'ticks': {
                                'font': {'size': 11}
                            }
                        }
                    }
                }, options)
            }
            
            return self._validate_chart_config(config)
            
        except Exception as e:
            logger.error(f"Error generating line chart: {e}")
            return self._create_error_chart('line', title)
    
    def generate_bar_chart(
        self,
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        horizontal: bool = False,
        y_axis_title: str = '',
        x_axis_title: str = '',
        **options
    ) -> Dict[str, Any]:
        """Generate bar chart configuration"""
        try:
            # Apply default styling to datasets
            styled_datasets = []
            for i, dataset in enumerate(datasets):
                styled_dataset = self._apply_bar_styling(dataset, i)
                styled_datasets.append(styled_dataset)
            
            config = {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': styled_datasets
                },
                'options': self._merge_options({
                    'indexAxis': 'y' if horizontal else 'x',
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': title,
                            'font': {
                                'size': 16,
                                'weight': 'bold',
                                'family': 'Inter, system-ui, sans-serif'
                            },
                            'padding': 20
                        }
                    },
                    'scales': {
                        'y': {
                            'title': {
                                'display': bool(y_axis_title),
                                'text': y_axis_title,
                                'font': {'size': 12, 'weight': '600'}
                            },
                            'grid': {
                                'color': '#E5E7EB',
                                'drawBorder': False
                            },
                            'ticks': {
                                'font': {'size': 11}
                            }
                        },
                        'x': {
                            'title': {
                                'display': bool(x_axis_title),
                                'text': x_axis_title,
                                'font': {'size': 12, 'weight': '600'}
                            },
                            'grid': {
                                'color': '#F3F4F6',
                                'drawBorder': False
                            },
                            'ticks': {
                                'font': {'size': 11}
                            }
                        }
                    }
                }, options)
            }
            
            return self._validate_chart_config(config)
            
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            return self._create_error_chart('bar', title)
    
    def generate_radar_chart(
        self,
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        max_value: int = 100,
        **options
    ) -> Dict[str, Any]:
        """Generate radar chart configuration"""
        try:
            # Apply default styling to datasets
            styled_datasets = []
            for i, dataset in enumerate(datasets):
                styled_dataset = self._apply_radar_styling(dataset, i)
                styled_datasets.append(styled_dataset)
            
            config = {
                'type': 'radar',
                'data': {
                    'labels': labels,
                    'datasets': styled_datasets
                },
                'options': self._merge_options({
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': title,
                            'font': {
                                'size': 16,
                                'weight': 'bold',
                                'family': 'Inter, system-ui, sans-serif'
                            },
                            'padding': 20
                        }
                    },
                    'scales': {
                        'r': {
                            'beginAtZero': True,
                            'max': max_value,
                            'ticks': {
                                'stepSize': max_value / 5,
                                'font': {'size': 10},
                                'backdropColor': 'transparent'
                            },
                            'pointLabels': {
                                'font': {
                                    'size': 12,
                                    'weight': '500'
                                }
                            },
                            'grid': {
                                'color': '#E5E7EB'
                            },
                            'angleLines': {
                                'color': '#D1D5DB'
                            }
                        }
                    }
                }, options)
            }
            
            return self._validate_chart_config(config)
            
        except Exception as e:
            logger.error(f"Error generating radar chart: {e}")
            return self._create_error_chart('radar', title)
    
    def generate_doughnut_chart(
        self,
        title: str,
        labels: List[str],
        data: List[float],
        colors: Optional[List[str]] = None,
        **options
    ) -> Dict[str, Any]:
        """Generate doughnut chart configuration"""
        try:
            if not colors:
                colors = [self.brand_colors['primary'], self.brand_colors['success'], 
                         self.brand_colors['warning'], self.brand_colors['danger'],
                         self.brand_colors['purple']][:len(labels)]
            
            config = {
                'type': 'doughnut',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': data,
                        'backgroundColor': colors,
                        'borderColor': '#fff',
                        'borderWidth': 2,
                        'hoverBorderWidth': 3
                    }]
                },
                'options': self._merge_options({
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': title,
                            'font': {
                                'size': 16,
                                'weight': 'bold',
                                'family': 'Inter, system-ui, sans-serif'
                            },
                            'padding': 20
                        },
                        'legend': {
                            'position': 'right',
                            'labels': {
                                'padding': 15,
                                'usePointStyle': True
                            }
                        }
                    },
                    'cutout': '60%'
                }, options)
            }
            
            return self._validate_chart_config(config)
            
        except Exception as e:
            logger.error(f"Error generating doughnut chart: {e}")
            return self._create_error_chart('doughnut', title)
    
    def _apply_line_styling(self, dataset: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Apply professional styling to line dataset"""
        color_keys = list(self.brand_colors.keys())
        color = self.brand_colors[color_keys[index % len(color_keys)]]
        
        styled = {
            'borderColor': dataset.get('borderColor', color),
            'backgroundColor': dataset.get('backgroundColor', f"{color}20"),
            'fill': dataset.get('fill', False),
            'tension': dataset.get('tension', 0.4),
            'pointRadius': dataset.get('pointRadius', 4),
            'pointHoverRadius': dataset.get('pointHoverRadius', 6),
            'pointBorderWidth': dataset.get('pointBorderWidth', 2),
            'pointBackgroundColor': dataset.get('pointBackgroundColor', color),
            'pointBorderColor': dataset.get('pointBorderColor', '#fff'),
            'borderWidth': dataset.get('borderWidth', 3)
        }
        
        # Merge with original dataset
        return {**dataset, **styled}
    
    def _apply_bar_styling(self, dataset: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Apply professional styling to bar dataset"""
        color_keys = list(self.brand_colors.keys())
        color = self.brand_colors[color_keys[index % len(color_keys)]]
        
        styled = {
            'backgroundColor': dataset.get('backgroundColor', color),
            'borderColor': dataset.get('borderColor', color),
            'borderWidth': dataset.get('borderWidth', 1),
            'borderRadius': dataset.get('borderRadius', 4),
            'borderSkipped': dataset.get('borderSkipped', False)
        }
        
        return {**dataset, **styled}
    
    def _apply_radar_styling(self, dataset: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Apply professional styling to radar dataset"""
        color_keys = list(self.brand_colors.keys())
        color = self.brand_colors[color_keys[index % len(color_keys)]]
        
        styled = {
            'borderColor': dataset.get('borderColor', color),
            'backgroundColor': dataset.get('backgroundColor', f"{color}30"),
            'pointBackgroundColor': dataset.get('pointBackgroundColor', color),
            'pointBorderColor': dataset.get('pointBorderColor', '#fff'),
            'pointHoverBackgroundColor': dataset.get('pointHoverBackgroundColor', '#fff'),
            'pointHoverBorderColor': dataset.get('pointHoverBorderColor', color),
            'borderWidth': dataset.get('borderWidth', 2),
            'pointRadius': dataset.get('pointRadius', 4),
            'pointHoverRadius': dataset.get('pointHoverRadius', 6)
        }
        
        return {**dataset, **styled}
    
    def _merge_options(self, base_options: Dict[str, Any], custom_options: Dict[str, Any]) -> Dict[str, Any]:
        """Merge chart options with defaults"""
        merged = {**self.chart_defaults}
        
        # Deep merge base options
        for key, value in base_options.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        # Deep merge custom options
        for key, value in custom_options.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        return merged
    
    def _validate_chart_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Chart.js configuration"""
        try:
            # Check required fields
            required_fields = ['type', 'data', 'options']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate data structure
            data = config['data']
            if 'labels' not in data or 'datasets' not in data:
                raise ValueError("Invalid data structure")
            
            # Ensure datasets is a list
            if not isinstance(data['datasets'], list):
                raise ValueError("Datasets must be a list")
            
            # Add validation metadata
            config['_validation'] = {
                'validated_at': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'valid': True
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Chart validation failed: {e}")
            config['_validation'] = {
                'validated_at': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'valid': False,
                'error': str(e)
            }
            return config
    
    def _create_error_chart(self, chart_type: str, title: str) -> Dict[str, Any]:
        """Create error fallback chart"""
        return {
            'type': chart_type,
            'data': {
                'labels': ['Error'],
                'datasets': [{
                    'label': 'Data Unavailable',
                    'data': [0],
                    'backgroundColor': self.brand_colors['neutral'],
                    'borderColor': self.brand_colors['neutral']
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f"{title} - Error Loading Data",
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                }
            },
            '_validation': {
                'validated_at': datetime.utcnow().isoformat(),
                'valid': False,
                'error': 'Chart generation failed'
            }
        }
    
    def create_chart_summary(self, charts: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of generated charts"""
        summary = {
            'total_charts': 0,
            'successful_charts': 0,
            'failed_charts': 0,
            'chart_types': [],
            'generation_time': datetime.utcnow().isoformat()
        }
        
        for chart_name, chart_config in charts.items():
            if chart_name == 'metadata':
                continue
                
            summary['total_charts'] += 1
            
            if isinstance(chart_config, dict):
                chart_type = chart_config.get('type', 'unknown')
                summary['chart_types'].append(chart_type)
                
                validation = chart_config.get('_validation', {})
                if validation.get('valid', True):
                    summary['successful_charts'] += 1
                else:
                    summary['failed_charts'] += 1
        
        summary['success_rate'] = (
            summary['successful_charts'] / summary['total_charts'] * 100
            if summary['total_charts'] > 0 else 0
        )
        
        return summary