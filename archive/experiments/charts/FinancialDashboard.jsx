import React from 'react';
import {
  RevenueBreakdownChart,
  FinancialMetricsChart,
  ValuationAnalysisChart,
  MarketShareChart,
  sampleRevenueData,
  sampleMetricsData,
  sampleValuationData,
  sampleMarketShareData
} from './FinancialCharts';

const FinancialDashboard = () => {
  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%)',
          color: 'white',
          padding: '30px',
          textAlign: 'center'
        }}>
          <h1 style={{ margin: 0, fontSize: '2.5rem', fontWeight: 'bold' }}>
            Financial Analytics Dashboard
          </h1>
          <p style={{ margin: '10px 0 0 0', fontSize: '1.1rem', opacity: 0.9 }}>
            Professional Financial Data Visualization
          </p>
        </div>

        {/* Charts Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
          gap: '20px',
          padding: '20px'
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef'
          }}>
            <RevenueBreakdownChart 
              data={sampleRevenueData}
              title="Revenue Breakdown by Segment"
            />
          </div>

          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef'
          }}>
            <MarketShareChart 
              data={sampleMarketShareData}
              title="Market Share Distribution"
            />
          </div>

          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef',
            gridColumn: 'span 2'
          }}>
            <FinancialMetricsChart 
              data={sampleMetricsData}
              title="Key Financial Metrics ($ Millions)"
            />
          </div>

          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef',
            gridColumn: 'span 2'
          }}>
            <ValuationAnalysisChart 
              data={sampleValuationData}
              title="Valuation Ratios Trend Analysis"
            />
          </div>
        </div>

        {/* Footer */}
        <div style={{
          backgroundColor: '#f8f9fa',
          padding: '20px',
          textAlign: 'center',
          borderTop: '1px solid #e9ecef',
          color: '#6c757d'
        }}>
          <p style={{ margin: 0 }}>
            Built with Recharts • SVG-based for PDF compatibility • Corporate styling
          </p>
        </div>
      </div>
    </div>
  );
};

export default FinancialDashboard;