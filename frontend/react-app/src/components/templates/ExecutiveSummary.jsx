import React from 'react';

const ExecutiveSummary = ({ data }) => {
  const { content, key_metrics } = data;
  
  const getRecommendationClass = (recommendation) => {
    if (!recommendation) return '';
    const rec = recommendation.toLowerCase();
    if (rec.includes('buy')) return 'recommendation-buy';
    if (rec.includes('sell')) return 'recommendation-sell';
    return 'recommendation-hold';
  };

  return (
    <div className="executive-summary-section">
      {key_metrics && (
        <div className="executive-summary-metrics">
          <div className="metrics-grid">
            {key_metrics.recommendation && (
              <div className="metric-card">
                <div className="metric-label">Investment Recommendation</div>
                <div className={`metric-value recommendation ${getRecommendationClass(key_metrics.recommendation)}`}>
                  {key_metrics.recommendation}
                </div>
              </div>
            )}
            
            {key_metrics.price_target && (
              <div className="metric-card">
                <div className="metric-label">12-Month Price Target</div>
                <div className="metric-value price-target">
                  {key_metrics.price_target}
                </div>
              </div>
            )}
            
            {key_metrics.current_price && (
              <div className="metric-card">
                <div className="metric-label">Current Price</div>
                <div className="metric-value">{key_metrics.current_price}</div>
              </div>
            )}
            
            {key_metrics.market_cap && (
              <div className="metric-card">
                <div className="metric-label">Market Capitalization</div>
                <div className="metric-value">{key_metrics.market_cap}</div>
              </div>
            )}
            
            {key_metrics.pe_ratio && (
              <div className="metric-card">
                <div className="metric-label">P/E Ratio</div>
                <div className="metric-value">{key_metrics.pe_ratio}</div>
              </div>
            )}
            
            {key_metrics.revenue_growth && (
              <div className="metric-card">
                <div className="metric-label">Revenue Growth</div>
                <div className="metric-value">{key_metrics.revenue_growth}</div>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="section-content">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    </div>
  );
};

export { ExecutiveSummary };