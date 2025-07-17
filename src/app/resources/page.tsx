'use client';

import React, { useState } from 'react';
import { DollarSign, Users, TrendingUp, Plus, RefreshCw } from 'lucide-react';
import { formatCurrency, formatLargeNumber } from '@/lib/utils';
import { mockData } from '@/lib/api';
import Layout from '@/components/layout/Layout';
import MetricCard from '@/components/ui/MetricCard';
import NeonButton from '@/components/ui/NeonButton';
import ProgressBar from '@/components/ui/ProgressBar';

export default function ResourcesPage() {
  const [resourceStats] = useState(mockData.dashboardData.resourceStats);
  const [loading, setLoading] = useState(false);

  const handleDistribute = async () => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setLoading(false);
  };

  const distributionProgress = (resourceStats.totalDistributed / 19000000000000) * 100;

  return (
    <Layout title="Resource Distribution">
      <div className="space-y-6">
        {/* Header */}
        <div className="liberation-card">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold gradient-text mb-2">
                💰 Resource Distribution
              </h1>
              <p className="text-white/70">
                $800 weekly flow to all humans. No questions asked.
              </p>
            </div>
            <div className="flex space-x-4">
              <NeonButton 
                variant="primary" 
                onClick={handleDistribute}
                loading={loading}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Distribute Now
              </NeonButton>
              <NeonButton variant="secondary">
                <Plus className="h-4 w-4 mr-2" />
                Add Human
              </NeonButton>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Humans"
            value={formatLargeNumber(resourceStats.totalHumans)}
            subtitle={`${resourceStats.activeHumans} active`}
            icon={<Users className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="Total Distributed"
            value={formatCurrency(resourceStats.totalDistributed)}
            subtitle="All time"
            icon={<DollarSign className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="This Week"
            value={formatCurrency(resourceStats.distributedThisWeek)}
            subtitle="Current cycle"
            icon={<TrendingUp className="h-6 w-6" />}
            status="active"
            trend="up"
          />
          
          <MetricCard
            title="Average per Human"
            value={formatCurrency(resourceStats.averagePerHuman)}
            subtitle="Lifetime"
            icon={<DollarSign className="h-6 w-6" />}
            status="active"
            trend="stable"
          />
        </div>

        {/* Distribution Progress */}
        <div className="liberation-card">
          <h3 className="text-lg font-semibold text-primary-500 mb-4">
            $19 Trillion Distribution Progress
          </h3>
          <ProgressBar
            value={resourceStats.totalDistributed}
            max={19000000000000}
            label="Total Pool Distribution"
            variant="primary"
          />
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-success">
                {formatCurrency(resourceStats.totalDistributed)}
              </div>
              <div className="text-sm text-white/50">Distributed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-500">
                {formatCurrency(resourceStats.remainingWealth)}
              </div>
              <div className="text-sm text-white/50">Remaining</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent-500">
                {distributionProgress.toFixed(1)}%
              </div>
              <div className="text-sm text-white/50">Complete</div>
            </div>
          </div>
        </div>

        {/* Resource Flow Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4">
              Weekly Flow Distribution
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-white/70">Base Weekly Flow</span>
                <span className="text-primary-500 font-mono">$800</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">Active Recipients</span>
                <span className="text-primary-500 font-mono">{resourceStats.activeHumans.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">Weekly Total</span>
                <span className="text-primary-500 font-mono">
                  {formatCurrency(resourceStats.activeHumans * 800)}
                </span>
              </div>
            </div>
          </div>

          <div className="liberation-card">
            <h3 className="text-lg font-semibold text-primary-500 mb-4">
              Community Pools
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-white/70">Housing Credit Pool</span>
                <span className="text-secondary-500 font-mono">$104,000</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">Investment Pool</span>
                <span className="text-secondary-500 font-mono">$104,000</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/70">Per Community</span>
                <span className="text-secondary-500 font-mono">$208,000</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
