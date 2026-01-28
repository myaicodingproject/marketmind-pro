import React from 'react';
import {
  RevenueBreakdownChart,
  MetricsComparisonChart,
  ValuationAnalysisChart,
  MarketShareChart,
  FinancialDashboard,
  sampleData
} from './FinancialCharts';
import '../styles/charts.css';

const ChartExample = () => {
  // Custom data examples
  const customRevenueData = [
    { name: 'Software Licenses', value: 40, amount: 2400000 },
    { name: 'Professional Services', value: 35, amount: 2100000 },
    { name: 'Support & Maintenance', value: 20, amount: 1200000 },
    { name: 'Training', value: 5, amount: 300000 }
  ];

  const customMetricsData = [
    { metric: 'Revenue', current: 6000000, previous: 5200000 },
    { metric: 'Gross Profit', current: 3600000, previous: 3000000 },
    { metric: 'Operating Income', current: 1200000, previous: 900000 },
    { metric: 'Net Income', current: 900000, previous: 650000 }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            MarketMind Pro Financial Analytics
          </h1>
          <p className="text-gray-600">
            Professional financial data visualization components
          </p>
        </div>

        {/* Individual Charts */}
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RevenueBreakdownChart data={customRevenueData} />
            <MetricsComparisonChart data={customMetricsData} />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ValuationAnalysisChart />
            <MarketShareChart />
          </div>
        </div>

        {/* Full Dashboard Example */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Complete Financial Dashboard
          </h2>
          <div className="bg-white rounded-lg shadow-sm">
            <FinancialDashboard 
              revenueData={sampleData.revenue}
              metricsData={sampleData.metrics}
              valuationData={sampleData.valuation}
              marketShareData={sampleData.marketShare}
            />
          </div>
        </div>

        {/* Print Instructions */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">Print Instructions</h3>
          <p className="text-blue-800 text-sm">
            These charts are optimized for PDF generation and printing. 
            Use your browser's print function or PDF export to create professional reports.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChartExample;