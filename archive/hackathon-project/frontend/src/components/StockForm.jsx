import React, { useState } from 'react';
import { MagnifyingGlassIcon, DocumentArrowDownIcon, SparklesIcon } from '@heroicons/react/24/outline';

const StockForm = ({ onGenerationStart, disabled }) => {
  const [symbol, setSymbol] = useState('');
  const [reportType, setReportType] = useState('institutional');
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeTables, setIncludeTables] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!symbol.trim()) return;

    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol.toUpperCase(),
          report_type: reportType,
          include_charts: includeCharts,
          include_tables: includeTables
        })
      });
      
      const data = await response.json();
      onGenerationStart(data.job_id);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 print:hidden border border-gray-100 animate-fadeInUp">
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-50 to-blue-50 px-4 py-2 rounded-full mb-4">
          <SparklesIcon className="h-5 w-5 text-primary-600" />
          <span className="text-primary-700 font-semibold text-sm">Professional Report Generator</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Institutional Analysis</h2>
        <p className="text-gray-600">Create comprehensive 30-page financial reports with professional formatting</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Stock Symbol
            </label>
            <div className="relative group">
              <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-primary-500 transition-colors" />
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Enter symbol (e.g., AAPL)"
                className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white shadow-sm hover:shadow-md"
                disabled={disabled}
                required
              />
            </div>
            <p className="text-xs text-gray-500">Enter any valid stock ticker symbol</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Report Type
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-4 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white shadow-sm hover:shadow-md"
              disabled={disabled}
            >
              <option value="institutional">Institutional Report (30 pages)</option>
              <option value="executive">Executive Summary (5 pages)</option>
            </select>
            <p className="text-xs text-gray-500">Choose your preferred report format</p>
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 space-y-4">
          <h3 className="font-semibold text-gray-900 mb-4">Report Options</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <label className="flex items-start space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={includeCharts}
                onChange={(e) => setIncludeCharts(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-0.5"
                disabled={disabled}
              />
              <div>
                <span className="text-gray-900 font-medium group-hover:text-primary-700 transition-colors">Include Charts & Visualizations</span>
                <p className="text-sm text-gray-500">Professional charts and graphs</p>
              </div>
            </label>

            <label className="flex items-start space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={includeTables}
                onChange={(e) => setIncludeTables(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-0.5"
                disabled={disabled}
              />
              <div>
                <span className="text-gray-900 font-medium group-hover:text-primary-700 transition-colors">Include Data Tables</span>
                <p className="text-sm text-gray-500">Comprehensive financial data</p>
              </div>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled || loading || !symbol.trim()}
          className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-5 px-8 rounded-xl transition-all duration-200 flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none disabled:hover:shadow-lg"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
              <span>Generating Professional Report...</span>
            </>
          ) : (
            <>
              <DocumentArrowDownIcon className="h-6 w-6" />
              <span>Generate Professional Report</span>
            </>
          )}
        </button>

        {!loading && (
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Report generation typically takes 2-3 minutes
            </p>
          </div>
        )}
      </form>
    </div>
  );
};

export default StockForm;