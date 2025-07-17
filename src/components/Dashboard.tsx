'use client'

import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  Users, 
  DollarSign, 
  Network, 
  Zap, 
  Shield, 
  Globe, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Radio,
  Eye,
  Cpu,
  Database
} from 'lucide-react'

interface SystemMetrics {
  totalPool: string
  weeklyDistributions: string
  meshNodes: string
  truthChannels: string
  uptime: string
  processingTime: string
  trustLevel: string
}

interface LiveActivity {
  id: string
  type: 'resource' | 'truth' | 'mesh' | 'automation'
  message: string
  timestamp: string
  status: 'success' | 'warning' | 'error'
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalPool: '$19T',
    weeklyDistributions: '2.4M',
    meshNodes: '50K+',
    truthChannels: '1.2M',
    uptime: '99.7%',
    processingTime: '0.3s',
    trustLevel: 'BYPASSED'
  })

  const [activities, setActivities] = useState<LiveActivity[]>([
    {
      id: '1',
      type: 'resource',
      message: 'Resource distribution completed for 847 new participants',
      timestamp: '2s ago',
      status: 'success'
    },
    {
      id: '2',
      type: 'mesh',
      message: 'Mesh network expanded to 3 new geographic regions',
      timestamp: '15s ago',
      status: 'success'
    },
    {
      id: '3',
      type: 'truth',
      message: 'Truth channel conversion: 47 marketing channels → reality feeds',
      timestamp: '31s ago',
      status: 'warning'
    },
    {
      id: '4',
      type: 'automation',
      message: 'Automation engine self-optimized response time by 23%',
      timestamp: '1m ago',
      status: 'success'
    }
  ])

  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'resource': return <DollarSign className="w-4 h-4" />
      case 'truth': return <Radio className="w-4 h-4" />
      case 'mesh': return <Network className="w-4 h-4" />
      case 'automation': return <Cpu className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-400'
      case 'warning': return 'bg-yellow-400'
      case 'error': return 'bg-red-400'
      default: return 'bg-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            🌟 LIBERATION SYSTEM
          </h1>
          <p className="text-xl text-gray-300">
            $19 Trillion Economic Transformation • Live Dashboard
          </p>
          <div className="text-sm text-gray-400 mt-2">
            {currentTime.toLocaleString()} UTC
          </div>
        </div>

        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-black/20 backdrop-blur-lg border border-cyan-500/30 rounded-xl p-6 shadow-2xl hover:shadow-cyan-500/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-400">TOTAL RESOURCE POOL</div>
              <DollarSign className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="text-4xl font-bold text-cyan-400 mb-2">{metrics.totalPool}</div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-400">ACTIVE</span>
            </div>
          </div>

          <div className="bg-black/20 backdrop-blur-lg border border-purple-500/30 rounded-xl p-6 shadow-2xl hover:shadow-purple-500/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-400">WEEKLY DISTRIBUTIONS</div>
              <Users className="w-6 h-6 text-purple-400" />
            </div>
            <div className="text-4xl font-bold text-purple-400 mb-2">{metrics.weeklyDistributions}</div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-400">FLOWING</span>
            </div>
          </div>

          <div className="bg-black/20 backdrop-blur-lg border border-blue-500/30 rounded-xl p-6 shadow-2xl hover:shadow-blue-500/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-400">MESH NETWORK NODES</div>
              <Network className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-4xl font-bold text-blue-400 mb-2">{metrics.meshNodes}</div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-400">EXPANDING</span>
            </div>
          </div>

          <div className="bg-black/20 backdrop-blur-lg border border-yellow-500/30 rounded-xl p-6 shadow-2xl hover:shadow-yellow-500/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-400">TRUTH CHANNELS</div>
              <Radio className="w-6 h-6 text-yellow-400" />
            </div>
            <div className="text-4xl font-bold text-yellow-400 mb-2">{metrics.truthChannels}</div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-yellow-400">CONVERTING</span>
            </div>
          </div>
        </div>

        {/* System Components */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Resource Distribution */}
          <div className="bg-black/20 backdrop-blur-lg border border-cyan-500/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 mb-6">
              <DollarSign className="w-6 h-6 text-cyan-400" />
              <h3 className="text-xl font-semibold text-cyan-400">Resource Distribution</h3>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Weekly $800 Flow</span>
                <span className="text-green-400 font-semibold">{metrics.uptime} Uptime</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-cyan-400 to-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: '99.7%' }}
                />
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>$104K Community Pools</span>
                <span>Real-time Processing</span>
              </div>
            </div>
          </div>

          {/* Truth Network */}
          <div className="bg-black/20 backdrop-blur-lg border border-purple-500/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 mb-6">
              <Radio className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-semibold text-purple-400">Truth Network</h3>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Channel Conversion</span>
                <span className="text-green-400 font-semibold">Real-time</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-400 to-pink-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: '73%' }}
                />
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>Viral Propagation</span>
                <span>Auto-scaling</span>
              </div>
            </div>
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="bg-black/20 backdrop-blur-lg border border-gray-500/30 rounded-xl p-6 shadow-2xl">
          <div className="flex items-center space-x-3 mb-6">
            <Activity className="w-6 h-6 text-gray-400" />
            <h3 className="text-xl font-semibold text-gray-300">Live Activity</h3>
          </div>
          <div className="space-y-3">
            {activities.map((activity) => (
              <div 
                key={activity.id}
                className="flex items-center justify-between p-4 bg-black/30 rounded-lg hover:bg-black/40 transition-all duration-200"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full animate-pulse ${getStatusDot(activity.status)}`} />
                  <div className={getStatusColor(activity.status)}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <span className="text-sm text-gray-300">{activity.message}</span>
                </div>
                <div className="text-xs text-gray-400">
                  {activity.timestamp}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/20 backdrop-blur-lg border border-green-500/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 mb-4">
              <TrendingUp className="w-6 h-6 text-green-400" />
              <h4 className="text-lg font-semibold text-green-400">Performance</h4>
            </div>
            <div className="text-2xl font-bold text-green-400 mb-2">
              {metrics.processingTime}
            </div>
            <div className="text-sm text-gray-400">Average Processing Time</div>
          </div>

          <div className="bg-black/20 backdrop-blur-lg border border-red-500/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="w-6 h-6 text-red-400" />
              <h4 className="text-lg font-semibold text-red-400">Security</h4>
            </div>
            <div className="text-2xl font-bold text-red-400 mb-2">
              {metrics.trustLevel}
            </div>
            <div className="text-sm text-gray-400">Trust Verification</div>
          </div>

          <div className="bg-black/20 backdrop-blur-lg border border-blue-500/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 mb-4">
              <Globe className="w-6 h-6 text-blue-400" />
              <h4 className="text-lg font-semibold text-blue-400">Global Reach</h4>
            </div>
            <div className="text-2xl font-bold text-blue-400 mb-2">
              WORLDWIDE
            </div>
            <div className="text-sm text-gray-400">Network Coverage</div>
          </div>
        </div>

        {/* Footer Status */}
        <div className="mt-8 bg-black/40 backdrop-blur-lg border border-gray-500/30 rounded-xl p-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                <span className="text-sm text-green-400">System Status: OPERATIONAL</span>
              </div>
              <div className="text-sm text-gray-400">
                Uptime: {metrics.uptime}
              </div>
            </div>
            <div className="text-sm text-gray-400">
              Liberation System v1.0 • One person, massive impact
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
