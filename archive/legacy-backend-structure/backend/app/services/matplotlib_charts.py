# Python matplotlib service for complex financial charts
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO
import base64
import seaborn as sns

class MatplotlibFinancialCharts:
    def __init__(self):
        self.setup_style()
        
    def setup_style(self):
        """Configure matplotlib for institutional-quality charts"""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.size': 11,
            'font.family': 'Arial',
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.facecolor': 'white'
        })
    
    def generate_dcf_waterfall(self, data):
        """Generate DCF waterfall chart"""
        try:
            # Sample DCF data for GOOGL
            cash_flows = {
                '2026E': 78.2, '2027E': 89.1, '2028E': 101.4,
                '2029E': 113.8, '2030E': 126.1, 'Terminal': 1856.0
            }
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            years = list(cash_flows.keys())
            values = list(cash_flows.values())
            
            x_pos = np.arange(len(years))
            colors = ['#2563eb' if i < len(years)-1 else '#059669' for i in range(len(years))]
            
            bars = ax.bar(x_pos, values, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                       f'${value:.1f}B', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title(f'{data.get("ticker", "GOOGL")} - DCF Valuation Waterfall', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Projection Period', fontsize=12)
            ax.set_ylabel('Present Value ($ Billions)', fontsize=12)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(years)
            
            total_ev = sum(values)
            ax.axhline(y=total_ev, color='red', linestyle='--', alpha=0.7)
            ax.text(len(x_pos)/2, total_ev + (max(values) * 0.05), 
                   f'Enterprise Value: ${total_ev:.0f}B', 
                   ha='center', fontweight='bold', color='red')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating DCF waterfall: {e}")
            return None
    
    def generate_sensitivity_heatmap(self, data):
        """Generate sensitivity analysis heatmap"""
        try:
            growth_rates = np.array([0.015, 0.020, 0.025, 0.030, 0.035])
            discount_rates = np.array([0.08, 0.085, 0.09, 0.095, 0.10])
            
            base_value = 2000
            sensitivity_matrix = np.zeros((len(discount_rates), len(growth_rates)))
            
            for i, dr in enumerate(discount_rates):
                for j, gr in enumerate(growth_rates):
                    if dr > gr:
                        sensitivity_matrix[i, j] = base_value * (1 + gr) / (dr - gr)
                    else:
                        sensitivity_matrix[i, j] = base_value * 2
            
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(sensitivity_matrix, cmap='RdYlGn', aspect='auto')
            
            # Add text annotations
            for i in range(len(discount_rates)):
                for j in range(len(growth_rates)):
                    value = sensitivity_matrix[i, j]
                    ax.text(j, i, f'${value/1000:.0f}B',
                           ha="center", va="center", color="black", fontweight='bold')
            
            ax.set_xticks(np.arange(len(growth_rates)))
            ax.set_yticks(np.arange(len(discount_rates)))
            ax.set_xticklabels([f'{gr:.1%}' for gr in growth_rates])
            ax.set_yticklabels([f'{dr:.1%}' for dr in discount_rates])
            
            ax.set_xlabel('Terminal Growth Rate', fontsize=12)
            ax.set_ylabel('Discount Rate (WACC)', fontsize=12)
            ax.set_title(f'{data.get("ticker", "GOOGL")} - DCF Sensitivity Analysis', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.colorbar(im, ax=ax, label='Enterprise Value ($B)')
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating sensitivity heatmap: {e}")
            return None
    
    def generate_peer_multiples(self, data):
        """Generate peer multiples comparison"""
        try:
            companies = ['GOOGL', 'MSFT', 'AMZN', 'META', 'AAPL']
            pe_ratios = [24.1, 28.5, 35.2, 22.1, 26.8]
            ev_ebitda = [18.2, 22.4, 28.7, 16.8, 19.2]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # P/E Ratio comparison
            bars1 = ax1.bar(companies, pe_ratios, color='#2563eb', alpha=0.7)
            ax1.set_title('P/E Ratio Comparison', fontweight='bold')
            ax1.set_ylabel('P/E Ratio')
            
            for bar, value in zip(bars1, pe_ratios):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{value:.1f}x', ha='center', va='bottom', fontweight='bold')
            
            # EV/EBITDA comparison
            bars2 = ax2.bar(companies, ev_ebitda, color='#059669', alpha=0.7)
            ax2.set_title('EV/EBITDA Comparison', fontweight='bold')
            ax2.set_ylabel('EV/EBITDA')
            
            for bar, value in zip(bars2, ev_ebitda):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{value:.1f}x', ha='center', va='bottom', fontweight='bold')
            
            plt.suptitle('Peer Group Valuation Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Error creating peer multiples chart: {e}")
            return None
    
    def _fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64