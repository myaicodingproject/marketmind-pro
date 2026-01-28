import React, { useState } from 'react';
import { ResponsiveContainer } from 'recharts';
import { 
  HeatmapChart, 
  WaterfallChart, 
  GaugeChart, 
  AreaChartWithBands, 
  RiskMatrixChart 
} from './AdvancedCharts';
import { 
  InteractiveChart, 
  DrillDownModal 
} from './InteractiveFeatures';

const SectionChart = ({ section, chartData, title, height = 300 }) => {
  const [drillDownData, setDrillDownData] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleDataPointClick = (data) => {
    setDrillDownData(data);
    setModalOpen(true);
  };

  const renderChartBySection = () => {
    if (!chartData) return null;

    switch (section) {
      case 'executive_summary':
        return renderExecutiveSummaryCharts();
      case 'financial_analysis':
        return renderFinancialAnalysisCharts();
      case 'valuation_analysis':
        return renderValuationAnalysisCharts();
      case 'risk_assessment':
        return renderRiskAssessmentCharts();
      case 'market_analysis':
        return renderMarketAnalysisCharts();
      default:
        return null;
    }
  };

  const renderExecutiveSummaryCharts = () => {
    const data = chartData.executive_summary;
    if (!data) return null;

    return (
      <div className="space-y-6">
        {data.recommendation && (
          <GaugeChart
            value={data.recommendation.confidence}
            title="Investment Confidence"
            color="#0088FE"
          />
        )}
      </div>
    );
  };

  const renderFinancialAnalysisCharts = () => {
    const data = chartData.financial_analysis;
    if (!data) return null;

    return (
      <div className="space-y-6">
        {data.revenue_trend && (
          <InteractiveChart
            title="Revenue Projections with Confidence Bands"
            data={data.revenue_trend}
            filename="revenue-projections"
            series={['high', 'base', 'low']}
            onDataPointClick={handleDataPointClick}
          >
            <AreaChartWithBands data={data.revenue_trend} />
          </InteractiveChart>
        )}
        
        {data.cash_flow_waterfall && (
          <InteractiveChart
            title="Cash Flow Waterfall"
            data={data.cash_flow_waterfall}
            filename="cash-flow-waterfall"
            onDataPointClick={handleDataPointClick}
          >
            <WaterfallChart data={data.cash_flow_waterfall} />
          </InteractiveChart>
        )}
      </div>
    );
  };

  const renderValuationAnalysisCharts = () => {
    const data = chartData.valuation_analysis;
    if (!data) return null;

    return (
      <div className="space-y-6">
        {data.dcf_sensitivity && (
          <InteractiveChart
            title="DCF Sensitivity Analysis"
            data={data.dcf_sensitivity}
            filename="dcf-sensitivity"
            onDataPointClick={handleDataPointClick}
          >
            <HeatmapChart data={data.dcf_sensitivity} />
          </InteractiveChart>
        )}
      </div>
    );
  };

  const renderRiskAssessmentCharts = () => {
    const data = chartData.risk_assessment;
    if (!data) return null;

    return (
      <div className="space-y-6">
        {data.risk_matrix && (
          <InteractiveChart
            title="Risk Assessment Matrix"
            data={data.risk_matrix}
            filename="risk-matrix"
            onDataPointClick={handleDataPointClick}
          >
            <RiskMatrixChart data={data.risk_matrix} />
          </InteractiveChart>
        )}
      </div>
    );
  };

  const renderMarketAnalysisCharts = () => {
    const data = chartData.market_analysis;
    if (!data) return null;

    return (
      <div className="space-y-6">
        {/* Market analysis charts would go here */}
      </div>
    );
  };

  // Fallback for legacy usage
  if (!section && title) {
    return (
      <div className="chart-container mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">{title}</h3>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <ResponsiveContainer width="100%" height={height}>
            {/* Legacy children prop */}
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return (
    <>
      {renderChartBySection()}
      <DrillDownModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        data={drillDownData}
        title="Data Details"
      />
    </>
  );
};

export default SectionChart;