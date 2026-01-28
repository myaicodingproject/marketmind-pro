# Python matplotlib implementation for complex financial charts
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO
import base64

class AdvancedFinancialCharts:
    def __init__(self):
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def generate_dcf_waterfall(self, cash_flows, discount_rate, terminal_value):
        """Generate DCF waterfall chart with terminal value"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        years = list(cash_flows.keys())
        cf_values = list(cash_flows.values())
        
        # Calculate present values
        pv_values = [cf / (1 + discount_rate) ** i for i, cf in enumerate(cf_values)]
        terminal_pv = terminal_value / (1 + discount_rate) ** len(years)
        
        # Create waterfall
        x_pos = np.arange(len(years) + 1)
        values = pv_values + [terminal_pv]
        labels = years + ['Terminal']
        
        colors = ['#2563eb' if v > 0 else '#dc2626' for v in values]
        bars = ax.bar(x_pos, values, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                   f'${value/1e6:.1f}M', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('DCF Valuation Waterfall Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Projection Period', fontsize=12)
        ax.set_ylabel('Present Value ($ Millions)', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        
        # Add total enterprise value
        total_ev = sum(values)
        ax.axhline(y=total_ev, color='red', linestyle='--', alpha=0.7)
        ax.text(len(x_pos)/2, total_ev + (max(values) * 0.05), 
               f'Enterprise Value: ${total_ev/1e6:.1f}M', 
               ha='center', fontweight='bold', color='red')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_sensitivity_analysis(self, base_value, growth_rates, discount_rates):
        """Generate sensitivity analysis heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create sensitivity matrix
        sensitivity_matrix = np.zeros((len(discount_rates), len(growth_rates)))
        
        for i, dr in enumerate(discount_rates):
            for j, gr in enumerate(growth_rates):
                # Simplified DCF calculation for sensitivity
                sensitivity_matrix[i, j] = base_value * (1 + gr) / (dr - gr) if dr > gr else 0
        
        im = ax.imshow(sensitivity_matrix, cmap='RdYlGn', aspect='auto')
        
        # Add text annotations
        for i in range(len(discount_rates)):
            for j in range(len(growth_rates)):
                text = ax.text(j, i, f'${sensitivity_matrix[i, j]/1e6:.0f}M',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_xticks(np.arange(len(growth_rates)))
        ax.set_yticks(np.arange(len(discount_rates)))
        ax.set_xticklabels([f'{gr:.1%}' for gr in growth_rates])
        ax.set_yticklabels([f'{dr:.1%}' for dr in discount_rates])
        
        ax.set_xlabel('Terminal Growth Rate', fontsize=12)
        ax.set_ylabel('Discount Rate (WACC)', fontsize=12)
        ax.set_title('DCF Sensitivity Analysis', fontsize=16, fontweight='bold', pad=20)
        
        plt.colorbar(im, ax=ax, label='Enterprise Value ($M)')
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_peer_multiples_comparison(self, peer_data):
        """Generate comprehensive peer multiples comparison"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        companies = [p['name'] for p in peer_data]
        
        # P/E Ratio comparison
        pe_ratios = [p['pe_ratio'] for p in peer_data]
        bars1 = ax1.bar(companies, pe_ratios, color='#2563eb', alpha=0.7)
        ax1.set_title('P/E Ratio Comparison', fontweight='bold')
        ax1.set_ylabel('P/E Ratio')
        ax1.tick_params(axis='x', rotation=45)
        
        # EV/EBITDA comparison
        ev_ebitda = [p['ev_ebitda'] for p in peer_data]
        bars2 = ax2.bar(companies, ev_ebitda, color='#059669', alpha=0.7)
        ax2.set_title('EV/EBITDA Comparison', fontweight='bold')
        ax2.set_ylabel('EV/EBITDA')
        ax2.tick_params(axis='x', rotation=45)
        
        # Revenue Growth comparison
        revenue_growth = [p['revenue_growth'] for p in peer_data]
        bars3 = ax3.bar(companies, revenue_growth, color='#dc2626', alpha=0.7)
        ax3.set_title('Revenue Growth Rate', fontweight='bold')
        ax3.set_ylabel('Growth Rate (%)')
        ax3.tick_params(axis='x', rotation=45)
        
        # ROE comparison
        roe = [p['roe'] for p in peer_data]
        bars4 = ax4.bar(companies, roe, color='#7c3aed', alpha=0.7)
        ax4.set_title('Return on Equity (ROE)', fontweight='bold')
        ax4.set_ylabel('ROE (%)')
        ax4.tick_params(axis='x', rotation=45)
        
        # Add value labels on all bars
        for ax, bars, values in [(ax1, bars1, pe_ratios), (ax2, bars2, ev_ebitda), 
                                (ax3, bars3, revenue_growth), (ax4, bars4, roe)]:
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                       f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Peer Group Valuation Analysis', fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64