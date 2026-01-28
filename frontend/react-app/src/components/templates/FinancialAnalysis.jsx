import React from 'react';

const FinancialAnalysis = ({ data }) => {
  const { content, financial_metrics } = data;

  const formatCurrency = (value) => {
    if (!value) return '$0.00';
    try {
      const num = parseFloat(value.toString().replace(/[$,]/g, ''));
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num);
    } catch {
      return value;
    }
  };

  const formatPercent = (value) => {
    if (!value) return '0.0%';
    try {
      const num = parseFloat(value.toString().replace('%', ''));
      return `${num.toFixed(1)}%`;
    } catch {
      return value;
    }
  };

  return (
    <div className="financial-analysis-section">
      {financial_metrics && (
        <div className="financial-metrics-container">
          {financial_metrics.revenue && financial_metrics.revenue.length > 0 && (
            <div className="revenue-section">
              <h3 className="subsection-title">Revenue Analysis</h3>
              <div className="revenue-table">
                <table className="financial-table">
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Revenue</th>
                      <th>Growth Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {financial_metrics.revenue.map((item, index) => (
                      <tr key={index}>
                        <td>{item.year}</td>
                        <td>{formatCurrency(item.value)}</td>
                        <td className={parseFloat(item.growth) > 0 ? 'positive' : 'negative'}>
                          {formatPercent(item.growth)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {financial_metrics.profit_margins && (
            <div className="margins-section">
              <h3 className="subsection-title">Profitability Metrics</h3>
              <div className="margins-grid">
                {financial_metrics.profit_margins.gross && (
                  <div className="margin-card">
                    <div className="margin-label">Gross Margin</div>
                    <div className="margin-value">
                      {formatPercent(financial_metrics.profit_margins.gross)}
                    </div>
                  </div>
                )}
                
                {financial_metrics.profit_margins.operating && (
                  <div className="margin-card">
                    <div className="margin-label">Operating Margin</div>
                    <div className="margin-value">
                      {formatPercent(financial_metrics.profit_margins.operating)}
                    </div>
                  </div>
                )}
                
                {financial_metrics.profit_margins.net && (
                  <div className="margin-card">
                    <div className="margin-label">Net Margin</div>
                    <div className="margin-value">
                      {formatPercent(financial_metrics.profit_margins.net)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {financial_metrics.growth_rates && (
            <div className="growth-section">
              <h3 className="subsection-title">Growth Analysis</h3>
              <div className="growth-metrics">
                {Object.entries(financial_metrics.growth_rates).map(([key, value]) => (
                  <div key={key} className="growth-item">
                    <span className="growth-label">
                      {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                    </span>
                    <span className={`growth-value ${parseFloat(value) > 0 ? 'positive' : 'negative'}`}>
                      {formatPercent(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="section-content">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    </div>
  );
};

export { FinancialAnalysis };