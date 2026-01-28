import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const MobileMenu = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-primary-200 hover:text-white p-2 rounded-lg transition-colors"
      >
        {isOpen ? (
          <XMarkIcon className="h-6 w-6" />
        ) : (
          <Bars3Icon className="h-6 w-6" />
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 bg-primary-900 border-t border-primary-700 shadow-xl">
          <div className="px-4 py-4 space-y-3">
            <a
              href="#"
              className="block text-primary-200 hover:text-white transition-colors py-2 px-3 rounded-lg hover:bg-primary-800"
            >
              Reports
            </a>
            <a
              href="#"
              className="block text-primary-200 hover:text-white transition-colors py-2 px-3 rounded-lg hover:bg-primary-800"
            >
              Analytics
            </a>
            <button className="w-full bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
              Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MobileMenu;