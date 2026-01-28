import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { 
  ArrowDownTrayIcon, 
  MagnifyingGlassPlusIcon, 
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

// Chart Export Component
export const ChartExportButton = ({ chartRef, filename = 'chart' }) => {
  const [isExporting, setIsExporting] = useState(false);

  const exportAsPNG = async () => {
    if (!chartRef.current) return;
    
    setIsExporting(true);
    try {
      const canvas = await html2canvas(chartRef.current, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true
      });
      
      const link = document.createElement('a');
      link.download = `${filename}.png`;
      link.href = canvas.toDataURL();
      link.click();
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const exportAsCSV = (data) => {
    if (!data) return;
    
    const csvContent = convertToCSV(data);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const convertToCSV = (data) => {
    if (!Array.isArray(data) || data.length === 0) return '';
    
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(row => 
      Object.values(row).map(value => 
        typeof value === 'string' ? `"${value}"` : value
      ).join(',')
    );
    
    return [headers, ...rows].join('\n');
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={exportAsPNG}
        disabled={isExporting}
        className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        <ArrowDownTrayIcon className="w-4 h-4" />
        {isExporting ? 'Exporting...' : 'PNG'}
      </button>
    </div>
  );
};

// Chart Controls Component
export const ChartControls = ({ 
  onZoomIn, 
  onZoomOut, 
  onReset, 
  onToggleSeries,
  series = [],
  visibleSeries = {}
}) => {
  const [showControls, setShowControls] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setShowControls(!showControls)}
        className="flex items-center gap-1 px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
      >
        <Cog6ToothIcon className="w-4 h-4" />
        Controls
      </button>
      
      {showControls && (
        <div className="absolute top-8 right-0 bg-white border rounded-lg shadow-lg p-3 z-10 min-w-48">
          {/* Zoom Controls */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">Zoom</label>
            <div className="flex gap-1">
              <button
                onClick={onZoomIn}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
              >
                <MagnifyingGlassPlusIcon className="w-3 h-3" />
                In
              </button>
              <button
                onClick={onZoomOut}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
              >
                <MagnifyingGlassMinusIcon className="w-3 h-3" />
                Out
              </button>
              <button
                onClick={onReset}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
              >
                <ArrowsPointingOutIcon className="w-3 h-3" />
                Reset
              </button>
            </div>
          </div>
          
          {/* Series Toggle */}
          {series.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Data Series</label>
              {series.map((seriesName) => (
                <label key={seriesName} className="flex items-center gap-2 text-xs">
                  <input
                    type="checkbox"
                    checked={visibleSeries[seriesName] !== false}
                    onChange={() => onToggleSeries(seriesName)}
                    className="rounded"
                  />
                  {seriesName}
                </label>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Enhanced Tooltip Component
export const EnhancedTooltip = ({ active, payload, label, formatter }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white border rounded-lg shadow-lg p-3 max-w-xs">
      <p className="font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.name}:</span>
          </div>
          <span className="font-medium">
            {formatter ? formatter(entry.value, entry.name) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

// Interactive Chart Wrapper
export const InteractiveChart = ({ 
  children, 
  title, 
  data, 
  filename,
  series = [],
  onDataPointClick,
  height = 300 
}) => {
  const chartRef = useRef(null);
  const [visibleSeries, setVisibleSeries] = useState({});
  const [zoomDomain, setZoomDomain] = useState(null);

  const handleToggleSeries = (seriesName) => {
    setVisibleSeries(prev => ({
      ...prev,
      [seriesName]: prev[seriesName] === false ? true : false
    }));
  };

  const handleZoomIn = () => {
    // Implement zoom in logic
    console.log('Zoom in');
  };

  const handleZoomOut = () => {
    // Implement zoom out logic
    console.log('Zoom out');
  };

  const handleReset = () => {
    setZoomDomain(null);
    setVisibleSeries({});
  };

  return (
    <div className="chart-container mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <div className="flex gap-2">
          <ChartControls
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onReset={handleReset}
            onToggleSeries={handleToggleSeries}
            series={series}
            visibleSeries={visibleSeries}
          />
          <ChartExportButton chartRef={chartRef} filename={filename} />
        </div>
      </div>
      
      <div ref={chartRef} className="bg-white p-4 rounded-lg shadow-sm border">
        <div style={{ width: '100%', height }}>
          {React.cloneElement(children, {
            onClick: onDataPointClick,
            visibleSeries,
            zoomDomain
          })}
        </div>
      </div>
    </div>
  );
};

// Drill-down Modal Component
export const DrillDownModal = ({ isOpen, onClose, data, title }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-3">
          {data && typeof data === 'object' && (
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(data).map(([key, value]) => (
                <div key={key} className="border-b pb-2">
                  <dt className="text-sm font-medium text-gray-500 capitalize">
                    {key.replace(/_/g, ' ')}
                  </dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                  </dd>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};