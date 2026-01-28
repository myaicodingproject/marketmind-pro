import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReportGenerator from './components/ReportGenerator';
import ReportViewer from './components/ReportViewer';
import ReportViewerPage from './components/ReportViewerPage';
import ChartShowcase from './components/ChartShowcase';
import Header from './components/Header';

const API_BASE = 'http://localhost:8000';

function HomePage() {
  const [systemStatus, setSystemStatus] = useState('checking');
  const [currentReport, setCurrentReport] = useState(null);
  const [showViewer, setShowViewer] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      if (response.data.status === 'healthy') {
        setSystemStatus('ready');
      } else {
        setSystemStatus('degraded');
      }
    } catch (error) {
      setSystemStatus('error');
    }
  };

  const handleReportGenerated = (report) => {
    // This is now handled by ProgressTracker navigation
    // No need for popup logic
    console.log('Report generated:', report);
  };

  const handleBackToGenerator = () => {
    setShowViewer(false);
    setCurrentReport(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header systemStatus={systemStatus} />
      
      <main className="container mx-auto">
        <ReportGenerator 
          onReportGenerated={handleReportGenerated}
          systemStatus={systemStatus}
        />
        
        {/* Chart Showcase Link - DISABLED FOR PRODUCTION */}
        {/* 
        <div className="text-center mt-8">
          <button
            onClick={() => navigate('/charts')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            📊 View Chart Showcase
          </button>
        </div>
        */}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/report/:reportId" element={<ReportViewerPage />} />
        <Route path="/charts" element={<ChartShowcase />} />
      </Routes>
    </Router>
  );
}

export default App;
