import React from 'react';

const CoverPage = ({ ticker, companyName, generatedDate, keyMetrics }) => {
  const getRecommendationClass = (recommendation) => {
    if (!recommendation) return '';
    const rec = recommendation.toLowerCase();
    if (rec.includes('buy')) return 'recommendation-buy';
    if (rec.includes('sell')) return 'recommendation-sell';
    return 'recommendation-hold';
  };

  return (
    <div className="cover-page">
      <div className="header">
        <div className="logo">MarketMind Pro</div>
        <div className="tagline">The Mind Behind Smart Investing</div>
      </div>
      
      <div className="cover-content">
        <h1 className="report-title">
          {ticker} - Comprehensive Stock Analysis
        </h1>
        <div className="report-subtitle">
          Institutional Investment Research Report
        </div>
        <div className="company-name">{companyName}</div>
        
        {keyMetrics && (
          <div className="key-metrics-summary">
            {keyMetrics.recommendation && (
              <div className="metric-item">
                <span className="metric-label">Recommendation:</span>
                <span className={`recommendation ${getRecommendationClass(keyMetrics.recommendation)}`}>
                  {keyMetrics.recommendation}
                </span>
              </div>
            )}
            
            {keyMetrics.price_target && (
              <div className="metric-item">
                <span className="metric-label">Price Target:</span>
                <span className="metric-value">{keyMetrics.price_target}</span>
              </div>
            )}
            
            {keyMetrics.current_price && (
              <div className="metric-item">
                <span className="metric-label">Current Price:</span>
                <span className="metric-value">{keyMetrics.current_price}</span>
              </div>
            )}
            
            {keyMetrics.market_cap && (
              <div className="metric-item">
                <span className="metric-label">Market Cap:</span>
                <span className="metric-value">{keyMetrics.market_cap}</span>
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="cover-footer">
        <div className="generated-date">Generated: {generatedDate}</div>
        <div className="disclaimer">
          This report is for institutional investment research purposes only.
        </div>
      </div>
    </div>
  );
};

export { CoverPage };