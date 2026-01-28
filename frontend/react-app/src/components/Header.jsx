import React from 'react';

const Header = ({ systemStatus }) => {
  const getStatusColor = () => {
    switch (systemStatus) {
      case 'ready': return 'text-green-400 bg-green-900/20';
      case 'checking': return 'text-yellow-400 bg-yellow-900/20';
      case 'degraded': return 'text-orange-400 bg-orange-900/20';
      case 'error': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getStatusText = () => {
    switch (systemStatus) {
      case 'ready': return '● LIVE';
      case 'checking': return '● CONNECTING';
      case 'degraded': return '● DEGRADED';
      case 'error': return '● OFFLINE';
      default: return '● UNKNOWN';
    }
  };

  return (
    <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
      <div className="px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">MM</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">MarketMind Pro</h1>
                <p className="text-xs text-gray-400">Institutional Research Platform</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="text-right">
              <div className="text-xs text-gray-400">SYSTEM STATUS</div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
                {getStatusText()}
              </span>
            </div>
            
            <div className="text-right">
              <div className="text-xs text-gray-400">SESSION</div>
              <div className="text-sm text-white font-mono">
                {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
