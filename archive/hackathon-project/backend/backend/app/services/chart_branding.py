"""
Professional Chart Styling and Branding Configuration
Defines MarketMind Pro's institutional-quality chart styling standards
"""

from typing import Dict, List, Any, Optional
import json

class MarketMindChartBranding:
    """
    Professional chart branding and styling configuration for MarketMind Pro
    Ensures all charts meet institutional quality standards
    """
    
    def __init__(self):
        # MarketMind Pro Brand Colors
        self.brand_colors = {
            # Primary Brand Colors
            'primary': '#1E40AF',        # Deep Blue - Primary brand color
            'primary_light': '#3B82F6',  # Light Blue - Secondary brand
            'primary_dark': '#1E3A8A',   # Dark Blue - Accent
            
            # Financial Colors
            'success': '#059669',        # Dark Green - Positive/Growth
            'success_light': '#10B981',  # Green - Profit/Revenue
            'warning': '#D97706',        # Dark Orange - Caution
            'warning_light': '#F59E0B',  # Orange - Neutral/Fair value
            'danger': '#DC2626',         # Dark Red - Negative/Risk
            'danger_light': '#EF4444',   # Red - Loss/Decline
            
            # Supporting Colors
            'purple': '#7C3AED',         # Purple - Premium metrics
            'purple_light': '#8B5CF6',   # Light Purple - Secondary metrics
            'teal': '#0D9488',          # Teal - Technology/Innovation
            'teal_light': '#14B8A6',    # Light Teal - Growth metrics
            'indigo': '#4F46E5',        # Indigo - Valuation
            'pink': '#DB2777',          # Pink - Special categories
            
            # Neutral Colors
            'neutral_900': '#111827',    # Almost Black - Text
            'neutral_700': '#374151',    # Dark Gray - Secondary text
            'neutral_500': '#6B7280',    # Medium Gray - Muted elements
            'neutral_300': '#D1D5DB',    # Light Gray - Borders
            'neutral_100': '#F3F4F6',    # Very Light Gray - Backgrounds
            'white': '#FFFFFF',          # White - Backgrounds
            
            # Gradient Colors
            'gradient_blue': ['#1E40AF', '#3B82F6', '#60A5FA'],
            'gradient_green': ['#059669', '#10B981', '#34D399'],
            'gradient_red': ['#DC2626', '#EF4444', '#F87171'],
            'gradient_purple': ['#7C3AED', '#8B5CF6', '#A78BFA']
        }
        
        # Typography Configuration
        self.typography = {
            'font_family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'title': {
                'size': 18,
                'weight': 'bold',
                'color': self.brand_colors['neutral_900']
            },
            'subtitle': {
                'size': 14,
                'weight': '600',
                'color': self.brand_colors['neutral_700']
            },
            'axis_title': {
                'size': 12,
                'weight': '600',
                'color': self.brand_colors['neutral_700']
            },
            'axis_labels': {
                'size': 11,
                'weight': 'normal',
                'color': self.brand_colors['neutral_500']
            },
            'legend': {
                'size': 12,
                'weight': '500',
                'color': self.brand_colors['neutral_700']
            },
            'tooltip': {
                'size': 12,
                'weight': 'normal',
                'color': self.brand_colors['white']
            }
        }
        
        # Chart-specific color schemes
        self.color_schemes = {
            'financial_performance': [
                self.brand_colors['success'],      # Revenue/Profit
                self.brand_colors['primary'],      # Assets/Equity
                self.brand_colors['warning'],      # Expenses/Costs
                self.brand_colors['purple'],       # Other metrics
                self.brand_colors['teal']          # Growth metrics
            ],
            'valuation_analysis': [
                self.brand_colors['primary'],      # Current valuation
                self.brand_colors['success'],      # Undervalued
                self.brand_colors['warning'],      # Fair value
                self.brand_colors['danger'],       # Overvalued
                self.brand_colors['neutral_500']   # No data
            ],
            'risk_assessment': [
                self.brand_colors['success'],      # Low risk
                self.brand_colors['warning'],      # Medium risk
                self.brand_colors['danger'],       # High risk
                self.brand_colors['neutral_500']   # Unknown risk
            ],
            'peer_comparison': [
                self.brand_colors['primary'],      # Target company
                self.brand_colors['neutral_500'],  # Peer companies
                self.brand_colors['success'],      # Best performer
                self.brand_colors['danger'],       # Worst performer
                self.brand_colors['warning']       # Average performer
            ],
            'trend_analysis': [
                self.brand_colors['success'],      # Positive trend
                self.brand_colors['danger'],       # Negative trend
                self.brand_colors['warning'],      # Neutral trend
                self.brand_colors['primary'],      # Current period
                self.brand_colors['neutral_500']   # Historical average
            ]
        }
    
    def get_chart_theme(self, chart_type: str = 'default') -> Dict[str, Any]:
        """Get complete chart theme configuration"""
        return {
            'colors': self.get_color_scheme(chart_type),
            'typography': self.typography,
            'layout': self.get_layout_config(),
            'interactions': self.get_interaction_config(),
            'animations': self.get_animation_config()
        }
    
    def get_color_scheme(self, scheme_name: str) -> List[str]:
        """Get color scheme for specific chart type"""
        return self.color_schemes.get(scheme_name, self.color_schemes['financial_performance'])
    
    def get_layout_config(self) -> Dict[str, Any]:
        """Get layout configuration for professional charts"""
        return {
            'padding': {
                'top': 20,
                'right': 20,
                'bottom': 20,
                'left': 20
            },
            'background_color': self.brand_colors['white'],
            'border_color': self.brand_colors['neutral_300'],
            'border_width': 1,
            'border_radius': 8,
            'grid': {
                'color': self.brand_colors['neutral_100'],
                'line_width': 1,
                'display': True
            }
        }
    
    def get_interaction_config(self) -> Dict[str, Any]:
        """Get interaction configuration"""
        return {
            'hover': {
                'mode': 'nearest',
                'intersect': False,
                'animation_duration': 200
            },
            'tooltip': {
                'enabled': True,
                'background_color': 'rgba(17, 24, 39, 0.95)',  # neutral_900 with opacity
                'title_color': self.brand_colors['white'],
                'body_color': self.brand_colors['white'],
                'border_color': self.brand_colors['primary'],
                'border_width': 1,
                'corner_radius': 8,
                'padding': 12,
                'font': self.typography['tooltip']
            },
            'legend': {
                'position': 'top',
                'align': 'center',
                'labels': {
                    'use_point_style': True,
                    'padding': 20,
                    'font': self.typography['legend']
                }
            }
        }
    
    def get_animation_config(self) -> Dict[str, Any]:
        """Get animation configuration for smooth, professional animations"""
        return {
            'duration': 750,
            'easing': 'easeInOutQuart',
            'delay': 0,
            'loop': False,
            'resize': {
                'duration': 300,
                'easing': 'easeInOutQuart'
            }
        }
    
    def apply_professional_styling(self, chart_config: Dict[str, Any], chart_category: str = 'default') -> Dict[str, Any]:
        """Apply professional styling to chart configuration"""
        theme = self.get_chart_theme(chart_category)
        
        # Apply colors to datasets
        if 'data' in chart_config and 'datasets' in chart_config['data']:
            colors = theme['colors']
            
            for i, dataset in enumerate(chart_config['data']['datasets']):
                color_index = i % len(colors)
                base_color = colors[color_index]
                
                # Apply colors based on chart type
                if chart_config.get('type') == 'line':
                    dataset.setdefault('borderColor', base_color)
                    dataset.setdefault('backgroundColor', f"{base_color}20")  # 20% opacity
                    dataset.setdefault('pointBackgroundColor', base_color)
                    dataset.setdefault('pointBorderColor', self.brand_colors['white'])
                    dataset.setdefault('pointBorderWidth', 2)
                    dataset.setdefault('borderWidth', 3)
                    dataset.setdefault('tension', 0.4)
                
                elif chart_config.get('type') == 'bar':
                    dataset.setdefault('backgroundColor', base_color)
                    dataset.setdefault('borderColor', base_color)
                    dataset.setdefault('borderWidth', 1)
                    dataset.setdefault('borderRadius', 4)
                
                elif chart_config.get('type') == 'radar':
                    dataset.setdefault('borderColor', base_color)
                    dataset.setdefault('backgroundColor', f"{base_color}30")  # 30% opacity
                    dataset.setdefault('pointBackgroundColor', base_color)
                    dataset.setdefault('pointBorderColor', self.brand_colors['white'])
                    dataset.setdefault('borderWidth', 2)
                
                elif chart_config.get('type') in ['doughnut', 'pie']:
                    if 'backgroundColor' not in dataset:
                        dataset['backgroundColor'] = colors[:len(chart_config['data']['labels'])]
                    dataset.setdefault('borderColor', self.brand_colors['white'])
                    dataset.setdefault('borderWidth', 2)
        
        # Apply typography and layout
        options = chart_config.setdefault('options', {})
        
        # Responsive settings
        options['responsive'] = True
        options['maintainAspectRatio'] = False
        
        # Plugin configuration
        plugins = options.setdefault('plugins', {})
        
        # Title styling
        if 'title' in plugins and plugins['title'].get('display', False):
            title_config = plugins['title']
            title_config.setdefault('font', {})
            title_config['font'].update({
                'family': theme['typography']['font_family'],
                'size': theme['typography']['title']['size'],
                'weight': theme['typography']['title']['weight']
            })
            title_config.setdefault('color', theme['typography']['title']['color'])
            title_config.setdefault('padding', 20)
        
        # Legend styling
        legend = plugins.setdefault('legend', {})
        legend.setdefault('display', True)
        legend.setdefault('position', 'top')
        legend_labels = legend.setdefault('labels', {})
        legend_labels.setdefault('usePointStyle', True)
        legend_labels.setdefault('padding', 20)
        legend_labels.setdefault('font', {})
        legend_labels['font'].update({
            'family': theme['typography']['font_family'],
            'size': theme['typography']['legend']['size'],
            'weight': theme['typography']['legend']['weight']
        })
        legend_labels.setdefault('color', theme['typography']['legend']['color'])
        
        # Tooltip styling
        tooltip = plugins.setdefault('tooltip', {})
        tooltip.update({
            'backgroundColor': theme['interactions']['tooltip']['background_color'],
            'titleColor': theme['interactions']['tooltip']['title_color'],
            'bodyColor': theme['interactions']['tooltip']['body_color'],
            'borderColor': theme['interactions']['tooltip']['border_color'],
            'borderWidth': theme['interactions']['tooltip']['border_width'],
            'cornerRadius': theme['interactions']['tooltip']['corner_radius'],
            'padding': theme['interactions']['tooltip']['padding'],
            'displayColors': True,
            'titleFont': {
                'family': theme['typography']['font_family'],
                'size': theme['typography']['tooltip']['size'],
                'weight': '600'
            },
            'bodyFont': {
                'family': theme['typography']['font_family'],
                'size': theme['typography']['tooltip']['size'],
                'weight': 'normal'
            }
        })
        
        # Scale styling (for charts that use scales)
        if 'scales' in options:
            for axis_name, axis_config in options['scales'].items():
                # Grid styling
                grid = axis_config.setdefault('grid', {})
                grid.update({
                    'color': theme['layout']['grid']['color'],
                    'lineWidth': theme['layout']['grid']['line_width'],
                    'drawBorder': False
                })
                
                # Tick styling
                ticks = axis_config.setdefault('ticks', {})
                ticks.setdefault('font', {})
                ticks['font'].update({
                    'family': theme['typography']['font_family'],
                    'size': theme['typography']['axis_labels']['size'],
                    'weight': theme['typography']['axis_labels']['weight']
                })
                ticks.setdefault('color', theme['typography']['axis_labels']['color'])
                
                # Title styling
                if 'title' in axis_config and axis_config['title'].get('display', False):
                    title = axis_config['title']
                    title.setdefault('font', {})
                    title['font'].update({
                        'family': theme['typography']['font_family'],
                        'size': theme['typography']['axis_title']['size'],
                        'weight': theme['typography']['axis_title']['weight']
                    })
                    title.setdefault('color', theme['typography']['axis_title']['color'])
        
        # Animation configuration
        options.setdefault('animation', theme['animations'])
        
        # Interaction configuration
        options.setdefault('interaction', {
            'mode': 'nearest',
            'intersect': False
        })
        
        return chart_config
    
    def get_color_by_value(self, value: float, thresholds: Dict[str, float], scheme: str = 'risk_assessment') -> str:
        """Get color based on value and thresholds"""
        colors = self.get_color_scheme(scheme)
        
        if scheme == 'risk_assessment':
            if value >= thresholds.get('low', 80):
                return colors[0]  # Low risk - green
            elif value >= thresholds.get('medium', 50):
                return colors[1]  # Medium risk - yellow
            else:
                return colors[2]  # High risk - red
        
        elif scheme == 'valuation_analysis':
            if value <= thresholds.get('undervalued', 0.8):
                return colors[1]  # Undervalued - green
            elif value <= thresholds.get('fair', 1.2):
                return colors[2]  # Fair value - yellow
            else:
                return colors[3]  # Overvalued - red
        
        return colors[0]  # Default color
    
    def create_gradient_background(self, color: str, opacity: float = 0.1) -> str:
        """Create gradient background from color"""
        # Convert hex to rgba with opacity
        if color.startswith('#'):
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"
        return color
    
    def get_accessibility_config(self) -> Dict[str, Any]:
        """Get accessibility configuration for charts"""
        return {
            'high_contrast_mode': False,
            'color_blind_friendly': True,
            'screen_reader_support': True,
            'keyboard_navigation': True,
            'aria_labels': True,
            'alternative_text': True
        }
    
    def export_theme_config(self) -> Dict[str, Any]:
        """Export complete theme configuration for external use"""
        return {
            'brand_name': 'MarketMind Pro',
            'version': '1.0.0',
            'colors': self.brand_colors,
            'typography': self.typography,
            'color_schemes': self.color_schemes,
            'layout': self.get_layout_config(),
            'interactions': self.get_interaction_config(),
            'animations': self.get_animation_config(),
            'accessibility': self.get_accessibility_config()
        }

# Global instance for easy access
marketmind_branding = MarketMindChartBranding()

# Export commonly used functions
def apply_marketmind_styling(chart_config: Dict[str, Any], category: str = 'default') -> Dict[str, Any]:
    """Apply MarketMind Pro styling to chart configuration"""
    return marketmind_branding.apply_professional_styling(chart_config, category)

def get_marketmind_colors(scheme: str = 'financial_performance') -> List[str]:
    """Get MarketMind Pro color scheme"""
    return marketmind_branding.get_color_scheme(scheme)

def get_marketmind_theme() -> Dict[str, Any]:
    """Get complete MarketMind Pro theme"""
    return marketmind_branding.export_theme_config()