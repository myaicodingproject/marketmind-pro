import React, { useState } from 'react';
import { FinancialCharts, ValuationCharts, RiskCharts, MarketCharts } from './charts/SectionSpecificCharts';
import { HeatmapChart, WaterfallChart, GaugeChart, AreaChartWithBands, RiskMatrixChart } from './charts/AdvancedCharts';
import { DrillDownModal } from './charts/InteractiveFeatures';

const ReportCharts = ({ chartData }) => {
  const [drillDownData, setDrillDownData] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  if (!chartData) return null;

  const handleDataPointClick = (data) => {
    setDrillDownData(data);
    setModalOpen(true);
  };

  return (
    <div className="report-charts space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">📊 Interactive Financial Analysis</h2>
        <p className="text-gray-600">Click on any chart element for detailed information</p>
      </div>
      
      {/* Executive Summary Charts */}
      {chartData.executive_summary && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Executive Summary</h3>
          {chartData.executive_summary.recommendation && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <GaugeChart
                value={chartData.executive_summary.recommendation.confidence}
                title="Investment Confidence"
                color="#0088FE"
              />
              <GaugeChart
                value={chartData.executive_summary.recommendation.risk_level === 'Low' ? 25 : 
                       chartData.executive_summary.recommendation.risk_level === 'Medium' ? 50 : 75}
                title="Risk Level"
                color={chartData.executive_summary.recommendation.risk_level === 'Low' ? '#00C49F' : 
                       chartData.executive_summary.recommendation.risk_level === 'Medium' ? '#FFBB28' : '#FF8042'}
              />
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold mb-2">Recommendation</h4>
                <div className="text-3xl font-bold text-center py-4" 
                     style={{ color: chartData.executive_summary.recommendation.rating === 'BUY' ? '#00C49F' : 
                                     chartData.executive_summary.recommendation.rating === 'HOLD' ? '#FFBB28' : '#FF8042' }}>
                  {chartData.executive_summary.recommendation.rating}
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Financial Analysis Charts */}
      {chartData.financial_analysis && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Financial Analysis</h3>
          <FinancialCharts data={chartData.financial_analysis} onDataPointClick={handleDataPointClick} />
          
          {/* Cash Flow Waterfall if available */}
          {chartData.financial_analysis.cash_flow_waterfall && (
            <WaterfallChart 
              data={chartData.financial_analysis.cash_flow_waterfall}
              title="Cash Flow Components"
            />
          )}
        </section>
      )}

      {/* Valuation Analysis Charts */}
      {chartData.valuation_analysis && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Valuation Analysis</h3>
          <ValuationCharts data={chartData.valuation_analysis} onDataPointClick={handleDataPointClick} />
          
          {/* DCF Sensitivity Heatmap */}
          {chartData.valuation_analysis.dcf_sensitivity && (
            <HeatmapChart 
              data={chartData.valuation_analysis.dcf_sensitivity}
              title="DCF Sensitivity Analysis"
            />
          )}
        </section>
      )}

      {/* Risk Assessment Charts */}
      {chartData.risk_assessment && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Risk Assessment</h3>
          <RiskCharts data={chartData.risk_assessment} onDataPointClick={handleDataPointClick} />
          
          {/* Risk Matrix */}
          {chartData.risk_assessment.risk_matrix && (
            <RiskMatrixChart 
              data={chartData.risk_assessment.risk_matrix}
              title="Risk Impact vs Probability Matrix"
            />
          )}
        </section>
      )}

      {/* Market Analysis Charts */}
      {chartData.market_analysis && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Market Analysis</h3>
          <MarketCharts data={chartData.market_analysis} onDataPointClick={handleDataPointClick} />
        </section>
      )}

      {/* Legacy Financial Performance Charts */}
      {chartData.financial_performance && (
        <section className="chart-section">
          <h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">Financial Performance (Legacy)</h3>
          
          {/* Revenue Trend with Confidence Bands */}
          {chartData.financial_performance.revenue_trend && (
            <AreaChartWithBands 
              data={chartData.financial_performance.revenue_trend}
              title="Revenue Trend with Projections"
            />
          )}
        </section>
      )}

      {/* Drill-down Modal */}
      <DrillDownModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        data={drillDownData}
        title="Detailed Information"
      />
    </div>
  );
};

export default ReportCharts;
