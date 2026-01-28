import React, { useState } from 'react';
import axios from 'axios';
import ProgressTracker from './ProgressTracker';

const API_BASE = 'http://localhost:8000';

const ReportGenerator = ({ onReportGenerated, systemStatus }) => {
  console.log('🔍 ReportGenerator rendering with systemStatus:', systemStatus);
  
  const [ticker, setTicker] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentReportId, setCurrentReportId] = useState(null);
  const [error, setError] = useState(null);
  const [completedReport, setCompletedReport] = useState(null);

  console.log('🎨 ReportGenerator state:', { ticker, isGenerating, systemStatus });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ticker.trim()) {
      setError('Please enter a stock ticker');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setCompletedReport(null);

    try {
      const response = await axios.post(`${API_BASE}/api/v1/reports/generate`, {
        ticker: ticker.toUpperCase(),
        report_type: 'institutional'
      });

      setCurrentReportId(response.data.report_id);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate report');
      setIsGenerating(false);
    }
  };

  const handleReportComplete = (report) => {
    setIsGenerating(false);
    setCurrentReportId(null);
    setCompletedReport(report);
    onReportGenerated(report);
  };

  const handleReportError = (errorMsg) => {
    setError(errorMsg);
    setIsGenerating(false);
    setCurrentReportId(null);
  };

  const handleGenerateAnother = () => {
    setCompletedReport(null);
    setTicker('');
    setError(null);
  };

  const handleViewReport = () => {
    if (completedReport?.report_id) {
      window.open(`/report/${completedReport.report_id}`, '_blank');
    }
  };

  const handleDownloadPDF = async () => {
    if (completedReport?.report_id) {
      try {
        const response = await axios.get(`${API_BASE}/api/v1/reports/${completedReport.report_id}/pdf`, {
          responseType: 'blob'
        });
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${ticker}_MarketMind_Report.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        setError('Failed to download PDF');
      }
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800 rounded-2xl border border-gray-700 shadow-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 p-8">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <span className="text-3xl">🎯</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Institutional Research Generator</h2>
                <p className="text-blue-100">AI-powered institutional equity research reports</p>
              </div>
            </div>
          </div>

          <div className="p-8">
            {!isGenerating && !completedReport ? (
              <form onSubmit={handleSubmit} className="space-y-8">
                <div>
                  <label className="block text-lg font-semibold text-gray-200 mb-4">
                    Enter Stock Ticker Symbol
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={ticker}
                      onChange={(e) => setTicker(e.target.value.toUpperCase())}
                      placeholder="e.g., AAPL, MSFT, GOOGL"
                      className="w-full px-6 py-5 bg-gray-900 border-2 border-gray-600 rounded-xl focus:ring-4 focus:ring-blue-500/50 focus:border-blue-500 text-white text-xl font-mono text-center transition-all duration-300 shadow-inner"
                      maxLength="10"
                      disabled={systemStatus !== 'ready'}
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                      <div className={`w-3 h-3 rounded-full ${systemStatus === 'ready' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-900/30 border-2 border-red-500/50 rounded-xl p-4 backdrop-blur-sm">
                    <div className="flex items-center space-x-3">
                      <span className="text-red-400 text-xl">⚠️</span>
                      <p className="text-red-300 font-medium">{error}</p>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={systemStatus !== 'ready' || !ticker.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 hover:from-blue-700 hover:via-purple-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold py-6 px-8 rounded-xl transition-all duration-300 text-xl shadow-2xl transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  {systemStatus !== 'ready' ? '🔴 SYSTEM OFFLINE' : '🚀 Generate'}
                </button>
              </form>
            ) : isGenerating ? (
              <div className="space-y-6">
                <ProgressTracker
                  reportId={currentReportId}
                  onComplete={handleReportComplete}
                  onError={handleReportError}
                />
              </div>
            ) : completedReport ? (
              <div className="space-y-6">
                <div className="bg-green-900/30 border-2 border-green-500/50 rounded-xl p-6 backdrop-blur-sm">
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-green-400 text-2xl">✅</span>
                    <div>
                      <h3 className="text-green-300 font-bold text-xl">Report Generated Successfully!</h3>
                      <p className="text-green-200">Your institutional research report for {ticker} is ready</p>
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-4 mt-6">
                    <button
                      onClick={handleViewReport}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 text-lg shadow-lg transform hover:scale-[1.02] active:scale-[0.98]"
                    >
                      📊 View Report Details
                    </button>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;
