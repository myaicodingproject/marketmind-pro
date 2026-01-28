# Main Chart Service - Coordinates Chart.js and matplotlib
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional
from app.services.matplotlib_charts import MatplotlibFinancialCharts

class HybridChartService:
    def __init__(self):
        self.matplotlib_service = MatplotlibFinancialCharts()
        
    async def generate_all_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all charts for a report"""
        charts = {}
        ticker = report_data.get('ticker', 'GOOGL')
        
        try:
            # Generate matplotlib charts (complex models)
            charts.update(await self._generate_matplotlib_charts(report_data))
            
            # Generate Chart.js charts (standard charts)
            charts.update(await self._generate_chartjs_charts(report_data))
            
            print(f"✅ Generated {len(charts)} charts for {ticker}")
            return charts
            
        except Exception as e:
            print(f"❌ Error generating charts for {ticker}: {e}")
            return {}
    
    async def _generate_matplotlib_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate matplotlib charts"""
        charts = {}
        
        # DCF waterfall chart
        dcf_chart = self.matplotlib_service.generate_dcf_waterfall(data)
        if dcf_chart:
            charts['dcf_waterfall'] = dcf_chart
        
        # Sensitivity analysis
        sensitivity_chart = self.matplotlib_service.generate_sensitivity_heatmap(data)
        if sensitivity_chart:
            charts['sensitivity_analysis'] = sensitivity_chart
        
        # Peer multiples
        peer_chart = self.matplotlib_service.generate_peer_multiples(data)
        if peer_chart:
            charts['peer_multiples'] = peer_chart
        
        return charts
    
    async def _generate_chartjs_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate Chart.js charts using Node.js service"""
        charts = {}
        
        try:
            # Call Node.js Chart.js service
            result = subprocess.run([
                'node', '-e', f'''
                const ChartJSService = require('./app/services/chartjs_service.js');
                const service = new ChartJSService();
                
                (async () => {{
                    await service.init();
                    
                    const data = {json.dumps(data)};
                    
                    // Generate revenue trend
                    const revenueTrend = await service.generateRevenueTrend(data);
                    console.log("REVENUE_TREND:" + revenueTrend);
                    
                    // Generate peer comparison
                    const peerComparison = await service.generatePeerComparison(data);
                    console.log("PEER_COMPARISON:" + peerComparison);
                    
                    await service.close();
                }})();
                '''
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('REVENUE_TREND:'):
                        charts['revenue_trend'] = line.replace('REVENUE_TREND:', '')
                    elif line.startswith('PEER_COMPARISON:'):
                        charts['peer_comparison'] = line.replace('PEER_COMPARISON:', '')
            
        except Exception as e:
            print(f"Error generating Chart.js charts: {e}")
        
        return charts