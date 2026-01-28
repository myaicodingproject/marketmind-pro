import plotly.graph_objects as go
import base64
from io import BytesIO
from typing import List, Dict, Any


class ChartImageService:
    colors = {
        'primary': '#2563eb',
        'success': '#10b981',
        'danger': '#ef4444'
    }
    
    layout_defaults = {
        'font': {'family': 'Inter'},
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'width': 800,
        'height': 400
    }
    
    def generate_revenue_chart(self, data: List[Dict[str, Any]]) -> str:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[item['year'] for item in data],
            y=[item['revenue'] for item in data],
            marker_color=self.colors['primary']
        ))
        fig.update_layout(**self.layout_defaults, title='Revenue Growth')
        return self._fig_to_png(fig)
    
    def generate_margin_chart(self, data: List[Dict[str, Any]]) -> str:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[item['year'] for item in data],
            y=[item['margin'] for item in data],
            mode='lines+markers',
            line=dict(color=self.colors['success'])
        ))
        fig.update_layout(**self.layout_defaults, title='Profit Margins')
        return self._fig_to_png(fig)
    
    def generate_comparison_chart(self, data: List[Dict[str, Any]]) -> str:
        fig = go.Figure()
        companies = list(data[0].keys())[1:]  # Skip 'metric' key
        for i, company in enumerate(companies):
            color = list(self.colors.values())[i % len(self.colors)]
            fig.add_trace(go.Bar(
                name=company,
                x=[item['metric'] for item in data],
                y=[item[company] for item in data],
                marker_color=color
            ))
        fig.update_layout(**self.layout_defaults, title='Peer Comparison')
        return self._fig_to_png(fig)
    
    def generate_trend_chart(self, data: List[Dict[str, Any]]) -> str:
        fig = go.Figure()
        metrics = list(data[0].keys())[1:]  # Skip 'year' key
        for i, metric in enumerate(metrics):
            color = list(self.colors.values())[i % len(self.colors)]
            fig.add_trace(go.Scatter(
                name=metric,
                x=[item['year'] for item in data],
                y=[item[metric] for item in data],
                mode='lines+markers',
                line=dict(color=color)
            ))
        fig.update_layout(**self.layout_defaults, title='Financial Trends')
        return self._fig_to_png(fig)
    
    def _fig_to_png(self, fig: go.Figure) -> str:
        img_bytes = fig.to_image(format="png")
        return base64.b64encode(img_bytes).decode('utf-8')


# Global instance
chart_service = ChartImageService()
