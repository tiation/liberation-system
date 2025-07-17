'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Menu, Bell, Settings, User, Power } from 'lucide-react';

interface HeaderProps {
  title: string;
  onMenuClick: () => void;
  showMenuButton?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  title,
  onMenuClick,
  showMenuButton = true,
}) => {
  return (
    <header className="bg-surface-200 border-b border-primary-500/20 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Menu button and title */}
        <div className="flex items-center space-x-4">
          {showMenuButton && (
            <button
              onClick={onMenuClick}
              className="p-2 rounded-lg hover:bg-surface-100 transition-colors duration-200"
            >
              <Menu className="h-5 w-5 text-primary-500" />
            </button>
          )}
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-neon rounded-lg flex items-center justify-center">
                <span className="text-dark-200 font-bold text-sm">L</span>
              </div>
              <h1 className="text-xl font-bold gradient-text">{title}</h1>
            </div>
          </div>
        </div>

        {/* Center - System status indicators */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="status-indicator status-active" />
            <span className="text-sm text-white/70">System Online</span>
          </div>
          <div className="hidden md:flex items-center space-x-2">
            <span className="text-xs text-white/50">Uptime:</span>
            <span className="text-xs font-mono text-primary-500">24h 32m</span>
          </div>
          <div className="hidden md:flex items-center space-x-2">
            <span className="text-xs text-white/50">Trust Level:</span>
            <span className="text-xs font-mono text-accent-500">MAXIMUM</span>
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-2">
          <button className="p-2 rounded-lg hover:bg-surface-100 transition-colors duration-200 relative">
            <Bell className="h-5 w-5 text-primary-500" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-error rounded-full animate-pulse" />
          </button>
          
          <button className="p-2 rounded-lg hover:bg-surface-100 transition-colors duration-200">
            <Settings className="h-5 w-5 text-primary-500" />
          </button>
          
          <div className="w-px h-6 bg-primary-500/20" />
          
          <button className="p-2 rounded-lg hover:bg-surface-100 transition-colors duration-200">
            <User className="h-5 w-5 text-primary-500" />
          </button>
          
          <button className="p-2 rounded-lg hover:bg-surface-100 transition-colors duration-200 hover:text-error">
            <Power className="h-5 w-5 text-primary-500" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
