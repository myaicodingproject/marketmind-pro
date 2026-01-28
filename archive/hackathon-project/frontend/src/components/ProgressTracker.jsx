import React, { useState, useEffect } from 'react';
import { CheckCircleIcon, ClockIcon, CogIcon } from '@heroicons/react/24/outline';

const ProgressTracker = ({ jobId, onComplete }) => {
  const [status, setStatus] = useState({ status: 'QUEUED', progress: 0, message: 'Initializing...' });

  useEffect(() => {
    if (!jobId) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/v1/status/${jobId}`);
        const data = await response.json();
        setStatus(data);

        if (data.status === 'COMPLETED') {
          onComplete(data);
        } else if (data.status === 'FAILED') {
          console.error('Report generation failed:', data.message);
        }
      } catch (error) {
        console.error('Status check failed:', error);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    pollStatus();

    return () => clearInterval(interval);
  }, [jobId, onComplete]);

  const steps = [
    { name: 'Initializing Analysis', progress: 0, description: 'Setting up report structure' },
    { name: 'Data Collection', progress: 20, description: 'Gathering financial data' },
    { name: 'Building Structure', progress: 40, description: 'Creating report framework' },
    { name: 'Generating Charts', progress: 60, description: 'Creating visualizations' },
    { name: 'Creating Tables', progress: 80, description: 'Formatting data tables' },
    { name: 'Finalizing PDF', progress: 95, description: 'Compiling final document' },
    { name: 'Complete', progress: 100, description: 'Report ready for download' }
  ];

  const currentStep = steps.findIndex(step => step.progress >= status.progress) || 0;

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 print:hidden border border-gray-100 animate-fadeInUp">
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-50 to-primary-50 px-4 py-2 rounded-full mb-4">
          <CogIcon className="h-5 w-5 text-primary-600 animate-spin" />
          <span className="text-primary-700 font-semibold text-sm">Processing Report</span>
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Generating Professional Report</h3>
        <p className="text-gray-600 mb-2">Job ID: <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{jobId}</span></p>
      </div>

      <div className="space-y-8">
        {/* Progress Bar */}
        <div className="relative">
          <div className="flex items-center justify-between text-sm font-semibold text-gray-700 mb-3">
            <span>Overall Progress</span>
            <span className="text-primary-600">{status.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 shadow-inner">
            <div 
              className="bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 h-4 rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
              style={{ width: `${status.progress}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Step Progress */}
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900 mb-4">Processing Steps</h4>
          {steps.map((step, index) => (
            <div key={step.name} className="flex items-start space-x-4 group">
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                index < currentStep 
                  ? 'bg-green-100 text-green-600 shadow-md' 
                  : index === currentStep 
                    ? 'bg-primary-100 text-primary-600 shadow-lg ring-4 ring-primary-100' 
                    : 'bg-gray-100 text-gray-400'
              }`}>
                {index < currentStep ? (
                  <CheckCircleIcon className="w-6 h-6" />
                ) : index === currentStep ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-600 border-t-transparent"></div>
                ) : (
                  <ClockIcon className="w-6 h-6" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`font-semibold transition-colors ${
                  index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {step.name}
                </p>
                <p className={`text-sm transition-colors ${
                  index <= currentStep ? 'text-gray-600' : 'text-gray-400'
                }`}>
                  {step.description}
                </p>
                {index === currentStep && (
                  <p className="text-sm text-primary-600 animate-pulse font-medium mt-1">
                    {status.message}
                  </p>
                )}
              </div>
              <div className={`text-xs font-medium px-2 py-1 rounded-full ${
                index < currentStep 
                  ? 'bg-green-100 text-green-700' 
                  : index === currentStep 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'bg-gray-100 text-gray-500'
              }`}>
                {index < currentStep ? 'Complete' : index === currentStep ? 'Processing' : 'Pending'}
              </div>
            </div>
          ))}
        </div>

        {/* Status Information */}
        {status.status === 'PROCESSING' && (
          <div className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-xl p-6">
            <div className="flex items-center space-x-4">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <div>
                <p className="text-primary-800 font-semibold">
                  Estimated completion: 2-3 minutes
                </p>
                <p className="text-primary-600 text-sm">
                  Creating institutional-grade financial analysis
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracker;