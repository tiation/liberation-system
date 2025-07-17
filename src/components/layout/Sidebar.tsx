'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Home, 
  DollarSign, 
  MessageSquare, 
  Network, 
  Settings, 
  Activity,
  Users,
  Database,
  Shield,
  Zap,
  Terminal,
  BarChart3
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const pathname = usePathname();

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <Home className="h-5 w-5" />,
      href: '/',
      badge: null,
    },
    {
      id: 'resources',
      label: 'Resource Distribution',
      icon: <DollarSign className="h-5 w-5" />,
      href: '/resources',
      badge: 987,
    },
    {
      id: 'truth',
      label: 'Truth Spreading',
      icon: <MessageSquare className="h-5 w-5" />,
      href: '/truth',
      badge: 25,
    },
    {
      id: 'mesh',
      label: 'Mesh Network',
      icon: <Network className="h-5 w-5" />,
      href: '/mesh',
      badge: 45,
    },
    {
      id: 'automation',
      label: 'Automation',
      icon: <Zap className="h-5 w-5" />,
      href: '/automation',
      badge: null,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <BarChart3 className="h-5 w-5" />,
      href: '/analytics',
      badge: null,
    },
    {
      id: 'users',
      label: 'Humans',
      icon: <Users className="h-5 w-5" />,
      href: '/humans',
      badge: null,
    },
    {
      id: 'database',
      label: 'Database',
      icon: <Database className="h-5 w-5" />,
      href: '/database',
      badge: null,
    },
    {
      id: 'security',
      label: 'Trust Security',
      icon: <Shield className="h-5 w-5" />,
      href: '/security',
      badge: null,
    },
    {
      id: 'system',
      label: 'System Health',
      icon: <Activity className="h-5 w-5" />,
      href: '/system',
      badge: null,
    },
    {
      id: 'console',
      label: 'Console',
      icon: <Terminal className="h-5 w-5" />,
      href: '/console',
      badge: null,
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <Settings className="h-5 w-5" />,
      href: '/settings',
      badge: null,
    },
  ];

  return (
    <div
      className={cn(
        'fixed left-0 top-0 h-full bg-surface-200 border-r border-primary-500/20',
        'transition-all duration-300 ease-in-out z-50',
        isOpen ? 'w-64' : 'w-0 overflow-hidden'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Sidebar Header */}
        <div className="p-6 border-b border-primary-500/20">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-neon rounded-lg flex items-center justify-center">
              <span className="text-dark-200 font-bold">L</span>
            </div>
            <div>
              <h2 className="text-lg font-bold gradient-text">Liberation</h2>
              <p className="text-xs text-white/50">Trust by Default</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto scrollbar-neon py-4">
          <div className="space-y-1 px-3">
            {navigationItems.map((item) => {
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.id}
                  href={item.href}
                  className={cn(
                    'sidebar-link',
                    isActive && 'sidebar-link-active'
                  )}
                >
                  <div className="flex items-center space-x-3 flex-1">
                    {item.icon}
                    <span className="text-sm font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <div className="bg-gradient-neon text-dark-200 text-xs px-2 py-1 rounded-full font-bold">
                      {item.badge}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-primary-500/20">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-white/50">System Status</span>
              <span className="text-success">Online</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-white/50">Active Tasks</span>
              <span className="text-primary-500">5</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-white/50">Trust Level</span>
              <span className="text-accent-500">Maximum</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
