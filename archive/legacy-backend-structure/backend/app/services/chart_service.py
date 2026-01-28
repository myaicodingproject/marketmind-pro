# MarketMind Pro Chart Generation Service
# Hybrid Chart.js + Python matplotlib system for financial charts

import asyncio
import json
import base64
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from io import BytesIO
import seaborn as sns

class ChartGenerationService:
    """Hybrid chart generation service using Chart.js + matplotlib"""
    
    def __init__(self):
        self.chart_cache = {}
        self.setup_matplotlib_style()
    
    def setup_matplotlib_style(self):
        """Configure matplotlib for institutional-quality charts"""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.size': 11,
            'font.family': 'Arial',
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16,
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.facecolor': 'white'
        })
    
    async def generate_financial_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all financial charts for a report"""
        charts = {}
        
        try:
            # Extract financial data
            ticker = report_data.get('ticker', 'UNKNOWN')
            
            # Generate Chart.js charts (standard financial charts)
            charts.update(await self._generate_chartjs_charts(report_data))
            
            # Generate matplotlib charts (complex models)
            charts.update(await self._generate_matplotlib_charts(report_data))
            
            return charts
            
        except Exception as e:
            print(f"Error generating charts: {e}")
            return {}
    
    async def _generate_chartjs_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate Chart.js charts using Puppeteer"""
        charts = {}
        
        # Revenue trend chart
        if 'financial_performance' in report_data.get('chart_data', {}):
            revenue_chart = await self._create_revenue_trend_chart(report_data)
            if revenue_chart:
                charts['revenue_trend'] = revenue_chart
        
        # Peer comparison radar chart
        peer_chart = await self._create_peer_comparison_chart(report_data)
        if peer_chart:
            charts['peer_comparison'] = peer_chart
        
        return charts
    
    async def _generate_matplotlib_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate matplotlib charts for complex financial models"""
        charts = {}
        
        # DCF waterfall chart
        dcf_chart = await self._create_dcf_waterfall_chart(report_data)
        if dcf_chart:
            charts['dcf_waterfall'] = dcf_chart
        
        # Sensitivity analysis heatmap
        sensitivity_chart = await self._create_sensitivity_heatmap(report_data)
        if sensitivity_chart:
            charts['sensitivity_analysis'] = sensitivity_chart
        
        # Financial metrics comparison
        metrics_chart = await self._create_financial_metrics_chart(report_data)
        if metrics_chart:
            charts['financial_metrics'] = metrics_chart
        
        return charts
    
    async def _create_revenue_trend_chart(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Create revenue trend chart using Chart.js"""
        try:
            # Sample data for GOOGL
            chart_config = {
                "type": "line",
                "data": {
                    "labels": ["2022", "2023", "2024", "2025E", "2026E"],
                    "datasets": [{
                        "label": "Revenue ($B)",
                        "data": [282.8, 307.4, 339.7, 375.2, 415.8],
                        "borderColor": "#2563eb",
                        "backgroundColor": "rgba(37, 99, 235, 0.1)",
                        "borderWidth": 3,
                        "fill": True
                    }, {
                        "label": "Net Income ($B)",
                        "data": [59.9, 73.8, 88.3, 98.1, 109.2],
                        "borderColor": "#059669",
                        "backgroundColor": "rgba(5, 150, 105, 0.1)",
                        "borderWidth": 3,
                        "fill": True
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"{report_data.get('ticker', 'GOOGL')} - Revenue & Profitability Trend",
                            "font": {"size": 18, "weight": "bold"}
                        },
                        "legend": {"display": True}
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {"display": True, "text": "Amount ($ Billions)"}
                        }
                    }
                }
            }
            
            return await self._render_chartjs(chart_config)
            
        except Exception as e:
            print(f"Error creating revenue trend chart: {e}")
            return None
    
    async def _create_peer_comparison_chart(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Create peer comparison radar chart"""
        try:
            # Sample peer data
            chart_config = {
                "type": "radar",
                "data": {
                    "labels": ["P/E Ratio", "EV/EBITDA", "ROE (%)", "Revenue Growth (%)", "Margin (%)"],
                    "datasets": [{
                        "label": report_data.get('ticker', 'GOOGL'),
                        "data": [24.1, 18.2, 29.2, 10.5, 26.0],
                        "borderColor": "#2563eb",
                        "backgroundColor": "rgba(37, 99, 235, 0.2)",
                        "pointBackgroundColor": "#2563eb"
                    }, {
                        "label": "Peer Average",
                        "data": [28.4, 22.1, 22.8, 12.3, 21.5],
                        "borderColor": "#dc2626",
                        "backgroundColor": "rgba(220, 38, 38, 0.2)",
                        "pointBackgroundColor": "#dc2626"
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "Peer Group Valuation Comparison",
                            "font": {"size": 18, "weight": "bold"}
                        }
                    },
                    "scales": {
                        "r": {
                            "beginAtZero": True,
                            "max": 35
                        }
                    }
                }
            }
            
            return await self._render_chartjs(chart_config)
            
        except Exception as e:
            print(f"Error creating peer comparison chart: {e}")
            return None
    
    async def _render_chartjs(self, chart_config: Dict) -> Optional[str]:
        """Render Chart.js chart using Puppeteer"""
        try:
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body {{ margin: 0; padding: 20px; background: white; font-family: Arial, sans-serif; }}
                    #chartContainer {{ width: 800px; height: 500px; }}
                </style>
            </head>
            <body>
                <div id="chartContainer">
                    <canvas id="chart"></canvas>
                </div>
                <script>
                    const ctx = document.getElementById('chart').getContext('2d');
                    const chart = new Chart(ctx, {json.dumps(chart_config)});
                    
                    // Wait for chart to render then capture
                    setTimeout(() => {{
                        const canvas = document.getElementById('chart');
                        const dataURL = canvas.toDataURL('image/png');
                        console.log('CHART_DATA_URL:' + dataURL);
                    }}, 1000);
                </script>
            </body>
            </html>
            """
            
            # Write HTML to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_template)
                html_file = f.name
            
            try:
                # Use puppeteer to render chart
                result = subprocess.run([
                    'node', '-e', f'''
                    const puppeteer = require('puppeteer');
                    (async () => {{
                        const browser = await puppeteer.launch({{headless: true}});
                        const page = await browser.newPage();
                        await page.goto('file://{html_file}');
                        await page.waitForTimeout(2000);
                        
                        const canvas = await page.$('#chart');
                        const image = await canvas.screenshot({{type: 'png'}});
                        console.log(image.toString('base64'));
                        
                        await browser.close();
                    }})();
                    '''
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                    
            finally:
                os.unlink(html_file)
                
        except Exception as e:
            print(f"Error rendering Chart.js: {e}")
            
        return None
    
    async def _create_dcf_waterfall_chart(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Create DCF waterfall chart using matplotlib"""
        try:
            # Sample DCF data for GOOGL
            cash_flows = {
                '2026E': 78.2,
                '2027E': 89.1, 
                '2028E': 101.4,
                '2029E': 113.8,
                '2030E': 126.1,
                'Terminal': 1856.0
            }
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            years = list(cash_flows.keys())
            values = list(cash_flows.values())
            
            # Create waterfall chart
            x_pos = np.arange(len(years))
            colors = ['#2563eb' if i < len(years)-1 else '#059669' for i in range(len(years))]
            
            bars = ax.bar(x_pos, values, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                       f'${value:.1f}B', ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Formatting
            ax.set_title(f'{report_data.get("ticker", "GOOGL")} - DCF Valuation Waterfall', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Projection Period', fontsize=12)
            ax.set_ylabel('Present Value ($ Billions)', fontsize=12)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(years)
            
            # Add total enterprise value line
            total_ev = sum(values)
            ax.axhline(y=total_ev, color='red', linestyle='--', alpha=0.7)
            ax.text(len(x_pos)/2, total_ev + (max(values) * 0.05), 
                   f'Total Enterprise Value: ${total_ev:.0f}B', 
                   ha='center', fontweight='bold', color='red')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating DCF waterfall chart: {e}")
            return None
    
    async def _create_sensitivity_heatmap(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Create sensitivity analysis heatmap"""
        try:
            # Sample sensitivity data
            growth_rates = np.array([0.015, 0.020, 0.025, 0.030, 0.035])
            discount_rates = np.array([0.08, 0.085, 0.09, 0.095, 0.10])
            
            # Create sensitivity matrix (simplified DCF)
            base_value = 2000  # $2T enterprise value
            sensitivity_matrix = np.zeros((len(discount_rates), len(growth_rates)))
            
            for i, dr in enumerate(discount_rates):
                for j, gr in enumerate(growth_rates):
                    if dr > gr:
                        sensitivity_matrix[i, j] = base_value * (1 + gr) / (dr - gr)
                    else:
                        sensitivity_matrix[i, j] = base_value * 2  # Cap at 2x for extreme cases
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            im = ax.imshow(sensitivity_matrix, cmap='RdYlGn', aspect='auto')
            
            # Add text annotations
            for i in range(len(discount_rates)):
                for j in range(len(growth_rates)):
                    value = sensitivity_matrix[i, j]
                    text = ax.text(j, i, f'${value/1000:.0f}B',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            # Formatting
            ax.set_xticks(np.arange(len(growth_rates)))
            ax.set_yticks(np.arange(len(discount_rates)))
            ax.set_xticklabels([f'{gr:.1%}' for gr in growth_rates])
            ax.set_yticklabels([f'{dr:.1%}' for dr in discount_rates])
            
            ax.set_xlabel('Terminal Growth Rate', fontsize=12)
            ax.set_ylabel('Discount Rate (WACC)', fontsize=12)
            ax.set_title(f'{report_data.get("ticker", "GOOGL")} - DCF Sensitivity Analysis', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Enterprise Value ($B)', rotation=270, labelpad=20)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating sensitivity heatmap: {e}")
            return None
    
    async def _create_financial_metrics_chart(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Create financial metrics comparison chart"""
        try:
            # Sample financial metrics data
            metrics = ['Revenue Growth', 'EBITDA Margin', 'ROE', 'ROIC', 'FCF Margin']
            googl_values = [10.5, 33.9, 27.8, 24.1, 22.6]
            peer_avg = [12.3, 28.4, 22.4, 18.7, 19.2]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            x = np.arange(len(metrics))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, googl_values, width, label=report_data.get('ticker', 'GOOGL'), 
                          color='#2563eb', alpha=0.8)
            bars2 = ax.bar(x + width/2, peer_avg, width, label='Peer Average', 
                          color='#dc2626', alpha=0.8)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Formatting
            ax.set_xlabel('Financial Metrics', fontsize=12)
            ax.set_ylabel('Percentage (%)', fontsize=12)
            ax.set_title(f'{report_data.get("ticker", "GOOGL")} vs Peer Group - Key Financial Metrics', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(metrics, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating financial metrics chart: {e}")
            return None
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64

# Chart data processor for JSON report data
class ChartDataProcessor:
    """Process JSON report data for chart generation"""
    
    @staticmethod
    def extract_financial_data(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure financial data for charts"""
        try:
            # Extract from GOOGL report structure
            financial_data = {
                'ticker': report_data.get('ticker', 'UNKNOWN'),
                'revenue_trend': [],
                'profitability_metrics': {},
                'peer_comparison': {},
                'dcf_inputs': {}
            }
            
            # Process chart_data if available
            if 'chart_data' in report_data:
                chart_data = report_data['chart_data']
                
                if 'financial_performance' in chart_data:
                    perf_data = chart_data['financial_performance']
                    
                    # Revenue trend
                    if 'revenue_trend' in perf_data:
                        financial_data['revenue_trend'] = perf_data['revenue_trend']
                    
                    # Margins
                    if 'margins' in perf_data:
                        financial_data['profitability_metrics'] = {
                            margin['metric']: margin['value'] 
                            for margin in perf_data['margins']
                        }
            
            return financial_data
            
        except Exception as e:
            print(f"Error processing chart data: {e}")
            return {'ticker': 'UNKNOWN'}