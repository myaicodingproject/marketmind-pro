import React from 'react';
import { CoverPage } from './CoverPage';
import { TableOfContents } from './TableOfContents';
import { ExecutiveSummary } from './ExecutiveSummary';
import { FinancialAnalysis } from './FinancialAnalysis';
import { CompanyOverview } from './CompanyOverview';
import { ValuationAnalysis } from './ValuationAnalysis';
import { RiskAssessment } from './RiskAssessment';
import { ReportFooter } from './ReportFooter';

const ReportTemplate = ({ reportData }) => {
  const { ticker, company_name, generated_date, sections } = reportData;

  const sectionComponents = {
    executive_summary: ExecutiveSummary,
    financial_analysis: FinancialAnalysis,
    company_overview: CompanyOverview,
    valuation_analysis: ValuationAnalysis,
    risk_assessment: RiskAssessment
  };

  return (
    <div className="report-container">
      <CoverPage 
        ticker={ticker}
        companyName={company_name}
        generatedDate={generated_date}
        keyMetrics={sections.executive_summary?.key_metrics}
      />
      
      <div className="page-break" />
      
      <TableOfContents sections={sections} />
      
      {Object.entries(sections).map(([sectionKey, sectionData], index) => {
        const SectionComponent = sectionComponents[sectionKey];
        
        return (
          <div key={sectionKey}>
            <div className="page-break" />
            <div className="report-section">
              <div className="section-header">
                <h2 className="section-title">{sectionData.title}</h2>
                <div className="section-divider" />
              </div>
              
              {SectionComponent ? (
                <SectionComponent data={sectionData} />
              ) : (
                <div className="section-content">
                  <div dangerouslySetInnerHTML={{ __html: sectionData.content }} />
                </div>
              )}
            </div>
          </div>
        );
      })}
      
      <ReportFooter generatedDate={generated_date} />
    </div>
  );
};

export default ReportTemplate;