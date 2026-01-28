import React, { useState } from 'react';
import Header from './components/Header';
import StockForm from './components/StockForm';
import ProgressTracker from './components/ProgressTracker';
import ReportDisplay from './components/ReportDisplay';
import './styles/print.css';

function App() {
  const [jobId, setJobId] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleReportGenerated = (data) => {
    setReportData(data);
    setIsGenerating(false);
  };

  const handleGenerationStart = (id) => {
    setJobId(id);
    setIsGenerating(true);
    setReportData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-primary-50">
      <Header />
      
      <main className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="space-y-12">
          {/* Hero Section */}
          <div className="text-center animate-fadeInUp">
            <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg mb-8">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-primary-700 font-semibold text-sm">Professional Financial Analysis Platform</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-primary-900 mb-6 leading-tight">
              Institutional Report
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-blue-600">
                Generator
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Generate comprehensive 30-page financial analysis reports with professional formatting, 
              embedded charts, and institutional-grade insights for any publicly traded stock.
            </p>
          </div>

          {/* Main Content */}
          <div className="space-y-8">
            <StockForm 
              onGenerationStart={handleGenerationStart}
              disabled={isGenerating}
            />

            {isGenerating && (
              <ProgressTracker 
                jobId={jobId}
                onComplete={handleReportGenerated}
              />
            )}

            {reportData && (
              <ReportDisplay reportData={reportData} />
            )}
          </div>

          {/* Features Section */}
          {!isGenerating && !reportData && (
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-white/80 shadow-xl animate-fadeInUp">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Professional Features
                </h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Our institutional-grade reports include everything you need for professional financial analysis
                </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center group">
                  <div className="bg-gradient-to-br from-primary-100 to-blue-100 rounded-2xl p-6 mb-4 group-hover:scale-105 transition-transform duration-200">
                    <div className="text-4xl mb-4">📊</div>
                    <h3 className="font-bold text-gray-900 mb-2">Professional Charts</h3>
                    <p className="text-gray-600 text-sm">15+ institutional-grade visualizations including technical analysis, financial trends, and performance metrics</p>
                  </div>
                </div>
                
                <div className="text-center group">
                  <div className="bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl p-6 mb-4 group-hover:scale-105 transition-transform duration-200">
                    <div className="text-4xl mb-4">🖨️</div>
                    <h3 className="font-bold text-gray-900 mb-2">Print-Ready Format</h3>
                    <p className="text-gray-600 text-sm">Optimized for professional printing with corporate styling, proper margins, and page breaks</p>
                  </div>
                </div>
                
                <div className="text-center group">
                  <div className="bg-gradient-to-br from-purple-100 to-violet-100 rounded-2xl p-6 mb-4 group-hover:scale-105 transition-transform duration-200">
                    <div className="text-4xl mb-4">⚡</div>
                    <h3 className="font-bold text-gray-900 mb-2">Real-Time Data</h3>
                    <p className="text-gray-600 text-sm">Latest market data, financial metrics, and analysis updated in real-time for accurate insights</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-primary-900 text-white py-8 mt-16 print:hidden">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="bg-primary-600 p-2 rounded-lg">
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
              </svg>
            </div>
            <span className="text-xl font-bold">MarketMind Pro</span>
          </div>
          <p className="text-primary-200 text-sm">
            Professional financial analysis platform for institutional investors
          </p>
          <p className="text-primary-300 text-xs mt-2">
            © 2024 MarketMind Pro. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;