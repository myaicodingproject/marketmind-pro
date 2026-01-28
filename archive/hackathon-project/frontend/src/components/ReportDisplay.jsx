import React, { useState } from 'react';
import { 
  DocumentArrowDownIcon, 
  PrinterIcon, 
  EyeIcon,
  ChartBarIcon,
  TableCellsIcon,
  ClockIcon,
  StarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const ReportDisplay = ({ reportData }) => {
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/v1/download/${reportData.job_id}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportData.symbol}_institutional_report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-8 animate-fadeInUp">
      {/* Report Summary Card */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
        <div className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 px-8 py-8 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10"></div>
          <div className="relative">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="bg-white/20 p-2 rounded-lg">
                    <DocumentArrowDownIcon className="h-6 w-6 text-white" />
                  </div>
                  <div className="bg-white/10 px-3 py-1 rounded-full">
                    <span className="text-primary-100 text-sm font-medium">INSTITUTIONAL GRADE</span>
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">
                  {reportData.symbol} Financial Analysis
                </h2>
                <p className="text-primary-100 text-lg leading-relaxed">
                  Comprehensive 30-page institutional report with professional formatting, 
                  embedded charts, and detailed financial analysis
                </p>
              </div>
              <div className="text-right ml-6">
                <div className="bg-white/20 backdrop-blur-sm rounded-xl px-6 py-4 border border-white/30">
                  <p className="text-primary-100 text-sm font-medium mb-1">Report ID</p>
                  <p className="text-white font-mono text-sm">{reportData.job_id}</p>
                  <p className="text-primary-200 text-xs mt-2">
                    Generated {new Date().toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-8">
          {/* Feature Grid */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="text-center group">
              <div className="bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl p-4 w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-200">
                <ChartBarIcon className="w-8 h-8 text-green-600 mx-auto" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Professional Charts</h3>
              <p className="text-gray-600 text-sm">15+ institutional-grade visualizations</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-br from-blue-100 to-cyan-100 rounded-2xl p-4 w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-200">
                <TableCellsIcon className="w-8 h-8 text-blue-600 mx-auto" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Data Tables</h3>
              <p className="text-gray-600 text-sm">Comprehensive financial datasets</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-br from-purple-100 to-violet-100 rounded-2xl p-4 w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-200">
                <ClockIcon className="w-8 h-8 text-purple-600 mx-auto" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Real-time Data</h3>
              <p className="text-gray-600 text-sm">Latest market information</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-br from-amber-100 to-orange-100 rounded-2xl p-4 w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-200">
                <ShieldCheckIcon className="w-8 h-8 text-amber-600 mx-auto" />
              </div>
              <h3 className="font-bold text-gray-900 mb-1">Verified Analysis</h3>
              <p className="text-gray-600 text-sm">Institutional-grade accuracy</p>
            </div>
          </div>

          {/* Quality Indicators */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <div>
                  <p className="font-bold text-gray-900">Institutional Quality Report</p>
                  <p className="text-gray-600 text-sm">Professional formatting • Print-ready • 30 pages</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-primary-600">100%</p>
                <p className="text-gray-600 text-sm">Completion Rate</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={handleDownload}
              className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white px-8 py-4 rounded-xl font-bold flex items-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <DocumentArrowDownIcon className="w-6 h-6" />
              <span>Download PDF Report</span>
            </button>
            
            <button
              onClick={handlePrint}
              className="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white px-8 py-4 rounded-xl font-bold flex items-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 print:hidden"
            >
              <PrinterIcon className="w-6 h-6" />
              <span>Print Report</span>
            </button>
            
            <button
              onClick={() => setIsPreviewOpen(!isPreviewOpen)}
              className="border-2 border-primary-600 text-primary-600 hover:bg-primary-50 px-8 py-4 rounded-xl font-bold flex items-center space-x-3 transition-all duration-200 hover:shadow-lg transform hover:-translate-y-0.5"
            >
              <EyeIcon className="w-6 h-6" />
              <span>{isPreviewOpen ? 'Hide Preview' : 'Show Preview'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Report Preview */}
      {isPreviewOpen && (
        <div className="bg-white rounded-2xl shadow-xl p-8 print:shadow-none print:rounded-none border border-gray-100">
          <div className="max-w-4xl mx-auto">
            <ReportPreview symbol={reportData.symbol} />
          </div>
        </div>
      )}
    </div>
  );
};

const ReportPreview = ({ symbol }) => {
  return (
    <div className="space-y-10 print:space-y-6">
      {/* Cover Page Preview */}
      <div className="text-center border-b-2 border-primary-200 pb-10 print:pb-6">
        <div className="mb-10">
          <div className="inline-block bg-gradient-to-r from-primary-600 to-primary-700 text-white px-6 py-2 rounded-full text-sm font-bold mb-6">
            CONFIDENTIAL • INSTITUTIONAL USE ONLY
          </div>
          <h1 className="text-5xl font-bold text-primary-900 mb-6 print:text-3xl leading-tight">
            INSTITUTIONAL FINANCIAL ANALYSIS
          </h1>
          <h2 className="text-3xl font-bold text-gray-700 mb-8 print:text-xl">
            {symbol} Comprehensive Stock Report
          </h2>
          <div className="bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200 rounded-2xl p-8 inline-block max-w-lg">
            <p className="text-primary-800 font-bold text-lg mb-2">
              Professional 30-Page Analysis
            </p>
            <p className="text-primary-600 mb-4">
              Generated {new Date().toLocaleDateString()} • MarketMind Pro
            </p>
            <div className="flex items-center justify-center space-x-4 text-sm text-primary-700">
              <span className="flex items-center space-x-1">
                <ChartBarIcon className="h-4 w-4" />
                <span>Charts</span>
              </span>
              <span className="flex items-center space-x-1">
                <TableCellsIcon className="h-4 w-4" />
                <span>Tables</span>
              </span>
              <span className="flex items-center space-x-1">
                <ShieldCheckIcon className="h-4 w-4" />
                <span>Verified</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary Preview */}
      <div className="space-y-8">
        <h2 className="text-3xl font-bold text-primary-900 border-b-2 border-primary-200 pb-3">
          Executive Summary
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-gray-50 to-blue-50 p-8 rounded-2xl border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-6 text-lg">Key Financial Metrics</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Current Price:</span>
                <span className="font-bold text-lg">$150.25</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Market Cap:</span>
                <span className="font-bold text-lg">$2.45T</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-200">
                <span className="text-gray-600 font-medium">P/E Ratio:</span>
                <span className="font-bold text-lg">28.5</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-gray-600 font-medium">52W Range:</span>
                <span className="font-bold text-lg">$124 - $182</span>
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-8 rounded-2xl border border-green-200">
            <h3 className="font-bold text-gray-900 mb-6 text-lg">Investment Recommendation</h3>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-4">BUY</div>
              <div className="bg-white rounded-lg p-4 mb-4">
                <div className="text-sm text-gray-600 mb-1">Price Target</div>
                <div className="text-2xl font-bold text-green-600">$175.00</div>
              </div>
              <div className="text-sm text-gray-600">
                <span className="font-semibold">Upside Potential:</span> +16.5%
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200 rounded-2xl p-8">
          <h3 className="font-bold text-primary-900 mb-4 text-lg">Investment Thesis</h3>
          <p className="text-primary-800 leading-relaxed text-justify">
            This comprehensive institutional analysis of {symbol} provides detailed insights into the company's 
            financial performance, technical indicators, and market positioning. Our analysis incorporates 
            fundamental valuation metrics, technical chart patterns, risk assessment frameworks, and 
            competitive landscape evaluation. The report includes 15+ professional charts, comprehensive 
            financial tables, and institutional-grade recommendations based on current market conditions 
            and forward-looking projections.
          </p>
        </div>
      </div>

      {/* Table of Contents Preview */}
      <div className="space-y-6">
        <h2 className="text-3xl font-bold text-primary-900 border-b-2 border-primary-200 pb-3">
          Table of Contents
        </h2>
        
        <div className="bg-gray-50 rounded-2xl p-6">
          <div className="space-y-3">
            {[
              { section: 'Executive Summary', pages: '3-5' },
              { section: 'Company Overview', pages: '6-8' },
              { section: 'Financial Analysis', pages: '9-15' },
              { section: 'Technical Analysis', pages: '16-20' },
              { section: 'Risk Assessment', pages: '21-23' },
              { section: 'Market Context & Peers', pages: '24-26' },
              { section: 'Investment Recommendations', pages: '27-29' },
              { section: 'Appendices & Data Tables', pages: '30' }
            ].map((item, index) => (
              <div key={item.section} className="flex justify-between items-center py-3 px-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-100 text-primary-700 font-bold text-sm px-2 py-1 rounded">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-900">{item.section}</span>
                </div>
                <span className="text-gray-500 font-medium">{item.pages}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportDisplay;