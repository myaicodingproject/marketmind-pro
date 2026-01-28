import React, { useState } from 'react';
import { TrendingUpIcon, DocumentTextIcon, ChartBarIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="bg-gradient-to-r from-primary-900 to-primary-800 shadow-xl print:hidden relative">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center space-x-4">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 p-3 rounded-xl shadow-lg transform hover:scale-105 transition-transform duration-200">
              <TrendingUpIcon className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">MarketMind Pro</h1>
              <p className="text-primary-200 text-sm font-medium">Institutional Analytics Platform</p>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-primary-200 hover:text-white transition-all duration-200 flex items-center space-x-2 group">
              <DocumentTextIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
              <span className="font-medium">Reports</span>
            </a>
            <a href="#" className="text-primary-200 hover:text-white transition-all duration-200 flex items-center space-x-2 group">
              <ChartBarIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
              <span className="font-medium">Analytics</span>
            </a>
            <button className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Dashboard
            </button>
          </nav>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-primary-200 hover:text-white p-2 rounded-lg transition-colors"
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-primary-900 border-t border-primary-700 shadow-xl z-50">
            <div className="px-4 py-4 space-y-3">
              <a
                href="#"
                className="flex items-center space-x-3 text-primary-200 hover:text-white transition-colors py-3 px-3 rounded-lg hover:bg-primary-800"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <DocumentTextIcon className="h-5 w-5" />
                <span className="font-medium">Reports</span>
              </a>
              <a
                href="#"
                className="flex items-center space-x-3 text-primary-200 hover:text-white transition-colors py-3 px-3 rounded-lg hover:bg-primary-800"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <ChartBarIcon className="h-5 w-5" />
                <span className="font-medium">Analytics</span>
              </a>
              <button 
                className="w-full bg-primary-600 hover:bg-primary-500 text-white px-4 py-3 rounded-lg font-semibold transition-colors text-left"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;