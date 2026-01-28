// Fixed ProgressTracker component
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProgressTracker = ({ reportId, onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('initializing');
  const [message, setMessage] = useState('Starting...');
  const [activityLog, setActivityLog] = useState([]);
  const [status, setStatus] = useState('in_progress');

  useEffect(() => {
    if (!reportId) return;

    const pollProgress = async () => {
      try {
        // Fixed endpoint to match backend
        const response = await axios.get(`/api/v1/reports/progress/${reportId}`);
        const data = response.data;
        
        setProgress(data.progress || 0);
        setStage(data.stage || 'processing');
        setMessage(data.message || 'Processing...');
        setActivityLog(data.activity_log || []);
        setStatus(data.status || 'in_progress');

        // Check if completed
        if (data.status === 'completed' || data.progress >= 100) {
          // Get final report data
          const reportResponse = await axios.get(`/api/v1/reports/${reportId}`);
          onComplete(reportResponse.data);
          return; // Stop polling
        }

        // Check if error
        if (data.status === 'error') {
          console.error('Report generation failed:', data.message);
          return; // Stop polling
        }

      } catch (error) {
        console.error('Progress polling error:', error);
        if (error.response?.status === 404) {
          console.log('Report not found, stopping polling');
          return;
        }
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollProgress, 2000);
    
    // Initial poll
    pollProgress();

    return () => clearInterval(interval);
  }, [reportId, onComplete]);

  return (
    <div className="progress-tracker">
      <h3>AI Research in Progress</h3>
      
      {/* Progress Ring */}
      <div className="progress-ring">
        <svg width="120" height="120">
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke="#3b82f6"
            strokeWidth="8"
            strokeDasharray={`${2 * Math.PI * 50}`}
            strokeDashoffset={`${2 * Math.PI * 50 * (1 - progress / 100)}`}
            transform="rotate(-90 60 60)"
          />
        </svg>
        <div className="progress-text">
          <div className="progress-percent">{Math.round(progress)}%</div>
          <div className="progress-status">
            {status === 'completed' ? 'Complete' : 
             status === 'error' ? 'Error' : 
             'Processing...'}
          </div>
        </div>
      </div>

      {/* Current Status */}
      <div className="current-status">
        <h4>Current Status</h4>
        <p><strong>Stage:</strong> {stage.replace('_', ' ')}</p>
        <p><strong>Message:</strong> {message}</p>
        <p><strong>Progress:</strong> {progress}%</p>
      </div>

      {/* Activity Log */}
      <div className="activity-log">
        <h4>Live Activity:</h4>
        <div className="log-container">
          {activityLog.slice(-5).map((activity, index) => (
            <div key={index} className="log-entry">
              {activity}
            </div>
          ))}
        </div>
      </div>

      {/* Processing Stages */}
      <div className="processing-stages">
        <h4>Processing Stages</h4>
        <div className="stages">
          <div className={`stage ${progress >= 10 ? 'completed' : progress > 0 ? 'active' : ''}`}>
            ⚙️ Initialization
          </div>
          <div className={`stage ${progress >= 25 ? 'completed' : progress >= 10 ? 'active' : ''}`}>
            🚀 Agent Launch
          </div>
          <div className={`stage ${progress >= 70 ? 'completed' : progress >= 25 ? 'active' : ''}`}>
            🧠 AI Analysis
          </div>
          <div className={`stage ${progress >= 85 ? 'completed' : progress >= 70 ? 'active' : ''}`}>
            📊 Compilation
          </div>
          <div className={`stage ${progress >= 95 ? 'completed' : progress >= 85 ? 'active' : ''}`}>
            ✅ Validation
          </div>
          <div className={`stage ${progress >= 100 ? 'completed' : progress >= 95 ? 'active' : ''}`}>
            📄 PDF Generation
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
