import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const ProgressTracker = ({ reportId, onComplete, onError }) => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('initializing');
  const [message, setMessage] = useState('Initializing...');
  const [activityLog, setActivityLog] = useState([]);
  const [startTime, setStartTime] = useState(Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [completedReport, setCompletedReport] = useState(null);
  const [currentSection, setCurrentSection] = useState('');

  // Analysis stages with proper progression
  const analysisStages = [
    { key: 'initializing', name: 'System Initialization', icon: '🚀', progress: 5 },
    { key: 'executive_summary', name: 'Executive Summary', icon: '📋', progress: 15 },
    { key: 'company_analysis', name: 'Company Analysis', icon: '🏢', progress: 30 },
    { key: 'financial_analysis', name: 'Financial Analysis', icon: '💰', progress: 50 },
    { key: 'valuation_analysis', name: 'Valuation Models', icon: '📊', progress: 70 },
    { key: 'risk_assessment', name: 'Risk Assessment', icon: '⚠️', progress: 85 },
    { key: 'final_compilation', name: 'Report Compilation', icon: '📄', progress: 95 },
    { key: 'completed', name: 'Complete', icon: '✅', progress: 100 }
  ];

  const formatActivityMessage = (rawMessage) => {
    const timestamp = new Date().toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
    
    // Clean up redundant messages
    if (rawMessage.includes('Initializing MarketMind Pro') || 
        rawMessage.includes('Process ID') || 
        rawMessage.includes('Kiro CLI started')) {
      return null; // Skip redundant initialization messages
    }
    
    if (rawMessage.includes('AI processing')) {
      const analysisType = rawMessage.match(/AI processing (\w+)/)?.[1];
      if (analysisType) {
        const stage = analysisStages.find(s => s.key.includes(analysisType));
        return `${timestamp} 🧠 Processing ${stage?.name || analysisType}`;
      }
    }
    
    if (rawMessage.includes('Deep analysis in progress')) {
      return null; // Skip generic progress messages
    }
    
    // Only show meaningful activity updates
    if (rawMessage.includes('completed') || rawMessage.includes('generated') || rawMessage.includes('validated')) {
      return `${timestamp} ✅ ${rawMessage}`;
    }
    
    return null; // Filter out noise
  };

  useEffect(() => {
    if (!reportId) return;

    const checkProgress = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/v1/reports/progress/${reportId}`);
        const data = response.data;

        const currentProgress = Math.min(data.progress || 0, 100);
        setProgress(currentProgress);
        setStage(data.stage || 'initializing');
        
        // Determine current section based on progress
        const activeStage = analysisStages.find(s => currentProgress <= s.progress) || analysisStages[0];
        setCurrentSection(activeStage.name);
        
        // Process activity log - filter out noise
        const filteredActivities = (data.activity_log || [])
          .map(formatActivityMessage)
          .filter(Boolean)
          .slice(-5); // Keep only last 5 meaningful activities
        
        setActivityLog(filteredActivities);
        
        // Clean up main message
        let cleanMessage = data.message || 'Processing...';
        if (cleanMessage.includes('parallel kiro agents')) {
          cleanMessage = `Analyzing ${activeStage.name.toLowerCase()}...`;
        }
        setMessage(cleanMessage);

        // Check completion
        const isComplete = data.status === 'completed' || 
                          currentProgress >= 100 ||
                          data.stage === 'completed';

        if (isComplete && !isCompleted) {
          try {
            const reportResponse = await axios.get(`${API_BASE}/api/v1/reports/${reportId}`);
            setCompletedReport(reportResponse.data);
            setIsCompleted(true);
            setProgress(100);
            if (onComplete) onComplete(reportResponse.data);
          } catch (error) {
            console.error('Failed to fetch completed report:', error);
            setIsCompleted(true);
            setProgress(100);
          }
        } else if (data.status === 'failed' || data.status === 'error') {
          onError(data.error || 'Report generation failed');
        }
      } catch (error) {
        console.error('Progress check failed:', error);
      }
    };

    if (!isCompleted) {
      checkProgress(); // Initial check
      const interval = setInterval(checkProgress, 3000); // Check every 3 seconds
      return () => clearInterval(interval);
    }
  }, [reportId, onError, isCompleted]);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [startTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleViewReport = () => {
    navigate(`/report/${reportId}`);
  };

  const handleGenerateAnother = () => {
    window.location.reload();
  };

  // If completed, show completion screen
  if (isCompleted && completedReport) {
    return (
      <div className="space-y-8">
        {/* Success Header */}
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🎉</span>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">Report Generated Successfully!</h3>
          <p className="text-gray-400">Your institutional-quality research report is ready</p>
        </div>

        {/* Report Summary */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Report Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-900 rounded-xl p-4">
              <div className="text-sm text-gray-400">Ticker</div>
              <div className="text-xl font-bold text-white">{completedReport.ticker}</div>
            </div>
            <div className="bg-gray-900 rounded-xl p-4">
              <div className="text-sm text-gray-400">Generation Time</div>
              <div className="text-xl font-bold text-green-400">{formatTime(elapsedTime)}</div>
            </div>
            <div className="bg-gray-900 rounded-xl p-4">
              <div className="text-sm text-gray-400">Total Sections</div>
              <div className="text-xl font-bold text-white">{completedReport.statistics?.total_sections || 0}</div>
            </div>
            <div className="bg-gray-900 rounded-xl p-4">
              <div className="text-sm text-gray-400">Total Words</div>
              <div className="text-xl font-bold text-white">{completedReport.statistics?.total_words?.toLocaleString() || 0}</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <button
            onClick={handleViewReport}
            className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 hover:from-blue-700 hover:via-purple-700 hover:to-blue-800 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 text-lg shadow-2xl transform hover:scale-[1.02] active:scale-[0.98]"
          >
            📊 View Full Report
          </button>
          
          <div className="grid grid-cols-2 gap-4">
            {completedReport.pdf_filename && (
              <a
                href={`${API_BASE}/api/v1/reports/${reportId}/pdf`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 text-center"
              >
                📄 Download PDF
              </a>
            )}
            <button
              onClick={handleGenerateAnother}
              className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300"
            >
              🔄 Generate Another
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Map backend stages to user-friendly display
  const getCurrentStage = () => {
    // Find the stage that matches current progress
    for (let i = 0; i < analysisStages.length; i++) {
      if (progress <= analysisStages[i].progress) {
        return analysisStages[i];
      }
    }
    // If progress exceeds all stages, return the last one
    return analysisStages[analysisStages.length - 1];
  };

  const currentStageDisplay = getCurrentStage();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
          <span className="text-3xl">🧠</span>
        </div>
        <h3 className="text-2xl font-bold text-white mb-2">AI Research in Progress</h3>
        <p className="text-gray-400">Generating institutional-quality analysis...</p>
      </div>

      {/* Progress Ring */}
      <div className="flex justify-center">
        <div className="relative w-48 h-48">
          <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-700"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 45}`}
              strokeDashoffset={`${2 * Math.PI * 45 * (1 - progress / 100)}`}
              className="text-blue-500 transition-all duration-1000 ease-out"
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl font-bold text-white">{progress}%</div>
              <div className="text-sm text-gray-400">Complete</div>
            </div>
          </div>
        </div>
      </div>

      {/* Current Status */}
      <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-white">Current Status</h4>
          <div className="text-sm text-gray-400">Elapsed: {formatTime(elapsedTime)}</div>
        </div>
        
        <div className="bg-gray-900 rounded-xl p-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{currentStageDisplay.icon}</div>
            <div className="flex-1">
              <div className="text-white font-medium">{currentStageDisplay.name}</div>
              <div className="text-sm text-gray-400">{message}</div>
            </div>
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Progress Stages */}
        <div className="space-y-2">
          {analysisStages.slice(0, -1).map((stageItem, index) => {
            const isCompleted = progress > stageItem.progress;
            const isActive = progress >= (index === 0 ? 0 : analysisStages[index - 1]?.progress || 0) && 
                            progress <= stageItem.progress;
            
            return (
              <div key={stageItem.key} className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 ${
                isActive ? 'bg-blue-900/30 border border-blue-500/30' : 
                isCompleted ? 'bg-green-900/20' : 'bg-gray-800/50'
              }`}>
                <div className={`text-lg ${isCompleted ? 'opacity-50' : isActive ? 'animate-pulse' : 'opacity-30'}`}>
                  {isCompleted ? '✅' : stageItem.icon}
                </div>
                <div className="flex-1">
                  <div className={`text-sm font-medium ${
                    isActive ? 'text-blue-400' : 
                    isCompleted ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    {stageItem.name}
                  </div>
                </div>
                <div className={`text-xs ${
                  isActive ? 'text-blue-400' : 
                  isCompleted ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {isCompleted ? 'Done' : isActive ? 'Processing...' : 'Pending'}
                </div>
              </div>
            );
          })}
        </div>

        {/* Activity Log - Only show if there are meaningful activities */}
        {activityLog.length > 0 && (
          <div className="mt-4">
            <div className="text-xs text-gray-400 font-semibold mb-2">Recent Activity:</div>
            <div className="bg-gray-900/50 rounded-lg p-3 space-y-1 max-h-24 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
              {activityLog.map((activity, index) => (
                <div key={index} className="text-xs text-gray-300">
                  {activity}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracker;
