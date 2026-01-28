import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import SectionChart from './charts/SectionChart';
import ReportCharts from './ReportCharts';
import FinancialTable from './FinancialTable';
import UniversalContentRenderer from './UniversalContentRenderer';

// Import professional styling
import '../styles/typography.css';
import '../styles/colors.css';
import '../styles/tables.css';
import '../styles/sections.css';
import '../styles/markdown.css';
import '../styles/institutional-report.css';

const ReportViewerPage = () => {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState('executive_summary');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/reports/${reportId}`);
        if (!response.ok) {
          throw new Error('Report not found');
        }
        const data = await response.json();
        setReport(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      fetchReport();
    }
  }, [reportId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto" style={{ borderColor: 'var(--color-primary)' }}></div>
          <p className="mt-4" style={{ color: 'var(--color-text-secondary)' }}>Loading report...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4" style={{ color: 'var(--color-danger)' }}>Error Loading Report</h2>
          <p className="mb-4" style={{ color: 'var(--color-text-secondary)' }}>{error}</p>
          <button
            onClick={() => navigate('/')}
            className="text-white px-4 py-2 rounded hover:opacity-90 transition-colors"
            style={{ backgroundColor: 'var(--color-primary)' }}
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>Report Not Found</h2>
          <button
            onClick={() => navigate('/')}
            className="text-white px-4 py-2 rounded hover:opacity-90 transition-colors"
            style={{ backgroundColor: 'var(--color-primary)' }}
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const sections = report.sections || {};
  const sectionKeys = Object.keys(sections);

  const renderSectionContent = (sectionKey, sectionData) => {
    const content = sectionData.content || 'No content available for this section.';
    
    return (
      <div className="report-section">
        <div className="section-header">
          <h2 className="section-title">
            {sectionData.title || sectionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </h2>
          {sectionData.subtitle && (
            <p className="section-subtitle" style={{ 
              color: 'var(--color-text-secondary)', 
              fontSize: '1.1rem',
              fontWeight: '500',
              marginTop: '0.5rem',
              marginBottom: '1.5rem'
            }}>
              {sectionData.subtitle}
            </p>
          )}
        </div>
        
        <div className="section-content">
          {/* Render content using universal renderer */}
          <div className="markdown-content">
            {sectionData.blocks ? (
              <UniversalContentRenderer blocks={sectionData.blocks} />
            ) : (
              <div dangerouslySetInnerHTML={{ __html: content }} />
            )}
          </div>
          
          {/* Render metrics grid */}
          {sectionData.metrics && sectionData.metrics.length > 0 && (
            <div className="metrics-grid">
              {sectionData.metrics.map((metric, index) => (
                <div key={index} className="metric-item">
                  <div className="metric-label">{metric.label}</div>
                  <div className="metric-value">{metric.value}</div>
                </div>
              ))}
            </div>
          )}
          
          {/* Render tables */}
          {sectionData.tables && sectionData.tables.map((table, index) => (
            <FinancialTable
              key={`${sectionKey}-table-${index}`}
              headers={table.headers}
              data={table.data}
              caption={table.caption || `Table ${index + 1}`}
            />
          ))}
          
          {/* Render section charts */}
          {sectionData.charts && sectionData.charts.map((chart, index) => (
            <SectionChart
              key={`${sectionKey}-chart-${index}`}
              section={sectionKey}
              chartData={{
                chart_type: chart.chart_type,
                title: chart.title,
                data: chart.data
              }}
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="report-title">
                  {report.ticker} - Investment Analysis Report
                </h1>
                {report.metadata?.is_demo && (
                  <span className="px-3 py-1 rounded-full text-sm font-semibold" style={{ 
                    backgroundColor: '#FEF3C7', 
                    color: '#92400E',
                    border: '2px solid #F59E0B'
                  }}>
                    🎭 DEMO MODE
                  </span>
                )}
              </div>
              <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                Generated: {new Date(report.generated_at).toLocaleDateString()}
                {report.metadata?.is_demo && (
                  <span className="ml-2" style={{ color: '#92400E' }}>
                    • Using Broadcom Inc. (AVGO) demonstration data
                  </span>
                )}
              </p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => window.open(`http://localhost:8000/api/v1/reports/${reportId}/pdf`, '_blank')}
                className="text-white px-4 py-2 rounded hover:opacity-90 flex items-center transition-colors"
                style={{ backgroundColor: 'var(--color-danger)' }}
              >
                📄 Download PDF
              </button>
              <button
                onClick={() => navigate('/')}
                className="text-white px-4 py-2 rounded hover:opacity-90 transition-colors"
                style={{ backgroundColor: 'var(--color-text-secondary)' }}
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Demo Mode Notice */}
        {report.metadata?.is_demo && (
          <div className="mb-6 rounded-lg p-4" style={{ 
            backgroundColor: '#FEF3C7', 
            border: '2px solid #F59E0B'
          }}>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎭</span>
              <div>
                <h3 className="font-bold mb-1" style={{ color: '#92400E' }}>
                  DEMO MODE - Demonstration Report
                </h3>
                <p className="text-sm" style={{ color: '#78350F' }}>
                  This is a demonstration report using Broadcom Inc. (AVGO) data. 
                  Enter a real ticker symbol (e.g., MSFT, GOOGL, TSLA) to generate live analysis with real-time data.
                </p>
              </div>
            </div>
          </div>
        )}
        
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-4 sticky top-8" style={{ border: '1px solid var(--color-border-light)' }}>
              <h3 className="font-semibold mb-4" style={{ color: 'var(--color-text-primary)' }}>Report Sections</h3>
              <nav className="space-y-2">
                {/* Add Charts Overview option */}
                <button
                  onClick={() => setActiveSection('charts_overview')}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    activeSection === 'charts_overview'
                      ? 'font-medium'
                      : 'hover:bg-gray-100'
                  }`}
                  style={{
                    backgroundColor: activeSection === 'charts_overview' ? 'var(--color-primary-light)' : 'transparent',
                    color: activeSection === 'charts_overview' ? 'var(--color-primary)' : 'var(--color-text-secondary)'
                  }}
                >
                  📊 Charts Overview
                </button>
                
                {sectionKeys.map((sectionKey) => {
                  const section = sections[sectionKey];
                  return (
                    <button
                      key={sectionKey}
                      onClick={() => setActiveSection(sectionKey)}
                      className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                        activeSection === sectionKey
                          ? 'font-medium'
                          : 'hover:bg-gray-100'
                      }`}
                      style={{
                        backgroundColor: activeSection === sectionKey ? 'var(--color-primary-light)' : 'transparent',
                        color: activeSection === sectionKey ? 'var(--color-primary)' : 'var(--color-text-secondary)'
                      }}
                    >
                      {section.title || sectionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </button>
                  );
                })}
              </nav>
              
              {/* Report Statistics */}
              <div className="mt-6 pt-4" style={{ borderTop: '1px solid var(--color-border-light)' }}>
                <h4 className="font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Report Stats</h4>
                <div className="space-y-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  <div>Sections: {report.statistics?.total_sections || 0}</div>
                  <div>Words: {report.statistics?.total_words?.toLocaleString() || 0}</div>
                  <div className="metric-value" style={{ fontSize: 'var(--text-sm)' }}>
                    Quality: {report.quality_score || 0}%
                  </div>
                  {report.chart_data && (
                    <div>Charts: Available</div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Charts Overview */}
            {activeSection === 'charts_overview' && (
              <div className="report-section">
                <div className="section-header">
                  <h2 className="section-title">
                    📊 Interactive Charts Overview
                  </h2>
                </div>
                <div className="section-content">
                  <ReportCharts chartData={report.chart_data} />
                </div>
              </div>
            )}
            
            {/* Regular Section Content */}
            {activeSection !== 'charts_overview' && activeSection && sections[activeSection] && (
              renderSectionContent(activeSection, sections[activeSection])
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportViewerPage;
