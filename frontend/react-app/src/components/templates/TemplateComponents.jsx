import React from 'react';

const TableOfContents = ({ sections }) => {
  return (
    <div className="toc-page">
      <h2>Table of Contents</h2>
      <div className="toc-list">
        {Object.entries(sections).map(([key, section], index) => (
          <div key={key} className="toc-item">
            <span className="toc-title">
              {index + 1}. {section.title}
            </span>
            <span className="toc-dots"></span>
            <span className="toc-page">{index + 3}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const CompanyOverview = ({ data }) => {
  const { content, subsections } = data;
  
  return (
    <div className="company-overview-section">
      <div className="section-content">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
      
      {subsections && subsections.map((subsection, index) => (
        <div key={index} className="subsection">
          <h3 className="subsection-title">{subsection.title}</h3>
          <div className="subsection-content">
            <div dangerouslySetInnerHTML={{ __html: subsection.content }} />
          </div>
        </div>
      ))}
    </div>
  );
};

const ValuationAnalysis = ({ data }) => {
  const { content, subsections } = data;
  
  return (
    <div className="valuation-analysis-section">
      <div className="section-content">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
      
      {subsections && subsections.map((subsection, index) => (
        <div key={index} className="subsection">
          <h3 className="subsection-title">{subsection.title}</h3>
          <div className="subsection-content">
            <div dangerouslySetInnerHTML={{ __html: subsection.content }} />
          </div>
        </div>
      ))}
    </div>
  );
};

const RiskAssessment = ({ data }) => {
  const { content, subsections } = data;
  
  return (
    <div className="risk-assessment-section">
      <div className="section-content">
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
      
      {subsections && subsections.map((subsection, index) => (
        <div key={index} className="subsection">
          <h3 className="subsection-title">{subsection.title}</h3>
          <div className="subsection-content">
            <div dangerouslySetInnerHTML={{ __html: subsection.content }} />
          </div>
        </div>
      ))}
    </div>
  );
};

const ReportFooter = ({ generatedDate }) => {
  return (
    <div className="report-footer">
      <div className="footer-content">
        <div className="footer-left">
          <strong>MarketMind Pro</strong> - AI-Powered Stock Research Platform
        </div>
        <div className="footer-right">
          Generated: {generatedDate}
        </div>
      </div>
      <div className="footer-disclaimer">
        <p>
          <strong>Important Disclaimer:</strong> This report is generated using AI analysis 
          and is for informational purposes only. Past performance does not guarantee future results. 
          Please consult with a qualified financial advisor before making investment decisions.
        </p>
      </div>
    </div>
  );
};

export { TableOfContents, CompanyOverview, ValuationAnalysis, RiskAssessment, ReportFooter };