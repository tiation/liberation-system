'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { ComponentProps } from '@/types';
import Sidebar from './Sidebar';
import Header from './Header';
import MatrixRain from './MatrixRain';

interface LayoutProps extends ComponentProps {
  title?: string;
  showSidebar?: boolean;
}

const Layout: React.FC<LayoutProps> = ({
  title = 'Liberation System',
  showSidebar = true,
  children,
  className,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-dark-200 text-white">
      {/* Matrix Rain Background Effect */}
      <MatrixRain />
      
      {/* Main Layout Container */}
      <div className="relative flex h-screen overflow-hidden">
        {/* Sidebar */}
        {showSidebar && (
          <Sidebar
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />
        )}
        
        {/* Main Content Area */}
        <div className={cn(
          'flex-1 flex flex-col overflow-hidden',
          showSidebar && sidebarOpen ? 'ml-64' : 'ml-0',
          'transition-all duration-300 ease-in-out'
        )}>
          {/* Header */}
          <Header
            title={title}
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            showMenuButton={showSidebar}
          />
          
          {/* Page Content */}
          <main className={cn(
            'flex-1 overflow-y-auto bg-gradient-dark p-6',
            'scrollbar-neon',
            className
          )}>
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
