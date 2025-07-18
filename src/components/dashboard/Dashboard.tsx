'use client';

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  MessageSquare, 
  Network, 
  Users, 
  Activity, 
  Zap,
  TrendingUp,
  Server,
  Shield
} from 'lucide-react';
import { formatCurrency, formatLargeNumber, formatDuration } from '@/lib/utils';
import { DashboardData } from '@/types';
import { mockData } from '@/lib/api';
import Layout from '@/components/layout/Layout';
import MetricCard from '@/components/ui/MetricCard';
import ProgressBar from '@/components/ui/ProgressBar';
import ConsoleOutput from '@/components/ui/ConsoleOutput';
import NeonButton from '@/components/ui/NeonButton';
import EnterpriseBackground from '@/components/ui/EnterpriseBackground';

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData>(mockData.dashboardData);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([
    'System initialization complete',
    'Resource distribution system online',
    'Truth spreading network active',
    'Mesh network discovering nodes...',
    'Automation engine running 5 tasks',
    'Trust security layer activated',
    'All systems operational'
  ]);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setDashboardData(prev => ({
        ...prev,
        metrics: {
          ...prev.metrics,
          resourcesDistributed: prev.metrics.resourcesDistributed + Math.floor(Math.random() * 100),
          truthMessagesSent: prev.metrics.truthMessagesSent + Math.floor(Math.random() * 5),
          meshNodesActive: prev.metrics.meshNodesActive + Math.floor(Math.random() * 2) - 1,
          cpuUsage: Math.max(20, Math.min(80, prev.metrics.cpuUsage + (Math.random() - 0.5) * 10)),
          memoryUsage: Math.max(50, Math.min(90, prev.metrics.memoryUsage + (Math.random() - 0.5) * 5)),
        }
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleSystemAction = (action: string) => {
    setLoading(true);
    const newLog = `${action} initiated by user`;
    setLogs(prev => [...prev, newLog]);
    
    setTimeout(() => {
      setLogs(prev => [...prev, `${action} completed successfully`]);
      setLoading(false);
    }, 2000);
  };

  return (
    <Layout title="Liberation System Dashboard">
      <div className="space-y-6">
        {/* Hero Section */}
        <div className="liberation-card-enterprise animate-enterprise-pulse cyber-grid">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold gradient-text-flare mb-2 text-shadow-neon">
                🌟 Liberation System
              </h1>
              <p className="text-white/70 text-lg animate-hologram">
                One person, massive impact. Transform everything.
              </p>
              <div className="flex items-center space-x-4 mt-4">
                <div className="flex items-center space-x-2">
                  <div className="status-indicator status-active" />
                  <span className="text-sm text-white/70">All Systems Operational</span>
                </div>
                <div className="text-sm text-white/50">
                  Uptime: {formatDuration(dashboardData.metrics.uptime)}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-primary-500">
                {formatCurrency(dashboardData.resourceStats.totalDistributed)}
              </div>
              <div className="text-sm text-white/50">Resources Distributed</div>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Active Humans"
            value={formatLargeNumber(dashboardData.resourceStats.activeHumans)}
            subtitle={`${dashboardData.resourceStats.totalHumans} total`}
            icon={<Users className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="Resources Distributed"
            value={formatCurrency(dashboardData.resourceStats.totalDistributed)}
            subtitle="$19T total pool"
            icon={<DollarSign className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="Truth Messages"
            value={dashboardData.truthStats.totalSpreadCount}
            subtitle={`${dashboardData.truthStats.activeChannels} channels`}
            icon={<MessageSquare className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="Mesh Nodes"
            value={dashboardData.metrics.meshNodesActive}
            subtitle="Network active"
            icon={<Network className="h-6 w-6" />}
            status="active"
            trend="stable"
          />
        </div>

        {/* System Health Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4 flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              System Health
            </h3>
            <div className="space-y-4">
              <ProgressBar
                label="CPU Usage"
                value={dashboardData.metrics.cpuUsage}
                max={100}
                variant="primary"
              />
              <ProgressBar
                label="Memory Usage"
                value={dashboardData.metrics.memoryUsage}
                max={100}
                variant="secondary"
              />
              <ProgressBar
                label="Disk Usage"
                value={dashboardData.metrics.diskUsage}
                max={100}
                variant="accent"
              />
            </div>
          </div>

          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4 flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              Active Tasks
            </h3>
            <div className="space-y-3">
              {dashboardData.activeTasks.map((task, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-surface-100 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      task.status === 'success' ? 'bg-success' :
                      task.status === 'failed' ? 'bg-error' :
                      'bg-warning'
                    }`} />
                    <span className="text-sm font-medium">{task.name}</span>
                  </div>
                  <div className="text-xs text-white/50">
                    {task.runCount} runs
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Controls and Console */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4 flex items-center">
              <Server className="h-5 w-5 mr-2" />
              System Controls
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <NeonButton
                variant="primary"
                onClick={() => handleSystemAction('Resource Distribution')}
                loading={loading}
              >
                Distribute Resources
              </NeonButton>
              <NeonButton
                variant="secondary"
                onClick={() => handleSystemAction('Truth Spreading')}
                loading={loading}
              >
                Spread Truth
              </NeonButton>
              <NeonButton
                variant="accent"
                onClick={() => handleSystemAction('Mesh Optimization')}
                loading={loading}
              >
                Optimize Network
              </NeonButton>
              <NeonButton
                variant="primary"
                onClick={() => handleSystemAction('System Health Check')}
                loading={loading}
              >
                Health Check
              </NeonButton>
            </div>
          </div>

          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4 flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Trust Security Status
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/70">Trust Level</span>
                <span className="text-sm font-mono text-accent-500">MAXIMUM</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/70">Verification Required</span>
                <span className="text-sm font-mono text-error">FALSE</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/70">Auth Bypass</span>
                <span className="text-sm font-mono text-success">TRUE</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/70">Access Logging</span>
                <span className="text-sm font-mono text-success">TRUE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Console Output */}
        <div className="liberation-card">
          <h3 className="text-lg font-semibold text-primary-500 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            System Console
          </h3>
          <ConsoleOutput logs={logs} maxLines={50} />
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
