// Fix frontend authentication and API calls
// Add this to your ReportGenerator.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios defaults
const API_BASE = 'http://localhost:8000';
axios.defaults.baseURL = API_BASE;

// Add auth token to all requests
const setupAuthToken = () => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
};

// Simple auth component
const AuthComponent = ({ onAuthSuccess }) => {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [isLogin, setIsLogin] = useState(true);

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(endpoint, credentials);
      
      // Store token
      localStorage.setItem('auth_token', response.data.access_token);
      setupAuthToken();
      onAuthSuccess(response.data.user);
    } catch (error) {
      console.error('Auth error:', error);
      alert('Authentication failed');
    }
  };

  return (
    <div className="auth-container">
      <form onSubmit={handleAuth}>
        <h2>{isLogin ? 'Login' : 'Register'}</h2>
        <input
          type="email"
          placeholder="Email"
          value={credentials.email}
          onChange={(e) => setCredentials({...credentials, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={credentials.password}
          onChange={(e) => setCredentials({...credentials, password: e.target.value})}
          required
        />
        <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
        <button type="button" onClick={() => setIsLogin(!isLogin)}>
          {isLogin ? 'Need to register?' : 'Already have account?'}
        </button>
      </form>
    </div>
  );
};

// Fixed ReportGenerator component
const ReportGenerator = () => {
  const [user, setUser] = useState(null);
  const [ticker, setTicker] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentReportId, setCurrentReportId] = useState(null);

  useEffect(() => {
    // Check for existing auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      setupAuthToken();
      // Verify token is still valid
      axios.get('/api/auth/me')
        .then(response => setUser(response.data))
        .catch(() => {
          localStorage.removeItem('auth_token');
          delete axios.defaults.headers.common['Authorization'];
        });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please login first');
      return;
    }

    setIsGenerating(true);
    
    try {
      // Fixed API call with proper endpoint
      const response = await axios.post('/api/v1/reports/generate', {
        ticker: ticker.toUpperCase(),
        report_type: 'institutional'
      });
      
      setCurrentReportId(response.data.report_id);
      console.log('Report generation started:', response.data);
      
    } catch (error) {
      console.error('Report generation failed:', error);
      alert('Failed to start report generation');
      setIsGenerating(false);
    }
  };

  if (!user) {
    return <AuthComponent onAuthSuccess={setUser} />;
  }

  return (
    <div className="report-generator">
      <h1>MarketMind Pro - Stock Research</h1>
      <p>Welcome, {user.email}</p>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter stock ticker (e.g., AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          required
        />
        <button type="submit" disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate Report'}
        </button>
      </form>

      {currentReportId && (
        <ProgressTracker 
          reportId={currentReportId} 
          onComplete={(reportData) => {
            setIsGenerating(false);
            console.log('Report completed:', reportData);
          }}
        />
      )}
    </div>
  );
};

export default ReportGenerator;
