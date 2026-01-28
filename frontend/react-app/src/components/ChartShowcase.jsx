import React from 'react';
import { generateSampleChartData } from '../utils/sampleChartData';
import { HeatmapChart, WaterfallChart, GaugeChart, AreaChartWithBands, RiskMatrixChart } from './charts/AdvancedCharts';
import { FinancialCharts, ValuationCharts, RiskCharts, MarketCharts } from './charts/SectionSpecificCharts';
import { InteractiveChart } from './charts/InteractiveFeatures';

const ChartShowcase = () => {
  const sampleData = generateSampleChartData('DEMO');

  const handleDataPointClick = (data) => {
    console.log('Chart data clicked:', data);
    alert(`Clicked on: ${JSON.stringify(data, null, 2)}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            📊 MarketMind Pro - Advanced Chart Showcase
          </h1>
          <p className="text-xl text-gray-600">
            Interactive financial visualizations with export capabilities
          </p>
        </div>

        <div className="space-y-12">
          {/* Advanced Chart Types Section */}
          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              🚀 Advanced Chart Types
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Heatmap Chart */}
              <div>
                <HeatmapChart 
                  data={sampleData.valuation_analysis.dcf_sensitivity}
                  title="DCF Sensitivity Heatmap"
                />
              </div>

              {/* Waterfall Chart */}
              <div>
                <WaterfallChart 
                  data={sampleData.financial_analysis.cash_flow_waterfall}
                  title="Cash Flow Waterfall"
                />
              </div>

              {/* Gauge Charts */}
              <div>
                <GaugeChart
                  value={sampleData.executive_summary.recommendation.confidence}
                  title="Investment Confidence Score"
                  color="#0088FE"
                />
              </div>

              {/* Area Chart with Bands */}
              <div>
                <AreaChartWithBands 
                  data={sampleData.financial_analysis.revenue_trend}
                  title="Revenue Projections with Confidence Bands"
                />
              </div>

              {/* Risk Matrix Scatter Plot */}
              <div className="lg:col-span-2">
                <RiskMatrixChart 
                  data={sampleData.risk_assessment.risk_matrix}
                  title="Risk Assessment Matrix"
                />
              </div>
            </div>
          </section>

          {/* Interactive Features Section */}
          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              🎯 Interactive Features Demo
            </h2>
            
            <div className="space-y-8">
              <InteractiveChart
                title="Interactive Revenue Trend (Click data points!)"
                data={sampleData.financial_analysis.revenue_trend}
                filename="demo-revenue-trend"
                series={['revenue', 'growth']}
                onDataPointClick={handleDataPointClick}
                height={350}
              >
                <FinancialCharts 
                  data={sampleData.financial_analysis} 
                  onDataPointClick={handleDataPointClick}
                />
              </InteractiveChart>
            </div>
          </section>

          {/* Section-Specific Charts */}
          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              📈 Financial Analysis Charts
            </h2>
            <FinancialCharts 
              data={sampleData.financial_analysis} 
              onDataPointClick={handleDataPointClick}
            />
          </section>

          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              💰 Valuation Analysis Charts
            </h2>
            <ValuationCharts 
              data={sampleData.valuation_analysis} 
              onDataPointClick={handleDataPointClick}
            />
          </section>

          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              ⚠️ Risk Assessment Charts
            </h2>
            <RiskCharts 
              data={sampleData.risk_assessment} 
              onDataPointClick={handleDataPointClick}
            />
          </section>

          <section className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-2">
              🌍 Market Analysis Charts
            </h2>
            <MarketCharts 
              data={sampleData.market_analysis} 
              onDataPointClick={handleDataPointClick}
            />
          </section>

          {/* Feature Summary */}
          <section className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              ✨ New Features Implemented
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-2">📊 Advanced Chart Types</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Heatmap for sensitivity analysis</li>
                  <li>• Waterfall for cash flow</li>
                  <li>• Gauge for metrics</li>
                  <li>• Area charts with confidence bands</li>
                  <li>• Scatter plots for risk matrix</li>
                </ul>
              </div>
              
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-2">🎯 Interactive Features</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Export as PNG with html2canvas</li>
                  <li>• Enhanced tooltips</li>
                  <li>• Drill-down modals</li>
                  <li>• Chart controls (zoom, series toggle)</li>
                  <li>• Click-to-explore data points</li>
                </ul>
              </div>
              
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-2">🎨 Professional Design</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Consistent color schemes</li>
                  <li>• Responsive layouts</li>
                  <li>• Smooth animations</li>
                  <li>• Mobile-optimized</li>
                  <li>• Institutional-quality styling</li>
                </ul>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default ChartShowcase;