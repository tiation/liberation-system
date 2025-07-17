import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Heart, 
  Lightbulb, 
  Shield, 
  Zap, 
  Network, 
  TrendingUp,
  Users,
  Globe,
  Activity
} from 'lucide-react';

interface SystemMetrics {
  resourceDistribution: string;
  truthChannels: string;
  networkNodes: string;
  systemUptime: string;
  responseTime: string;
}

const LiberationDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    resourceDistribution: '$19T',
    truthChannels: '1.2M',
    networkNodes: '50K+',
    systemUptime: '99.9%',
    responseTime: '<100ms'
  });

  const [isConnected, setIsConnected] = useState(true);
  const [activeUsers, setActiveUsers] = useState(1247);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setActiveUsers(prev => prev + Math.floor(Math.random() * 10) - 5);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-cyan-500/20 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-black" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Liberation System
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <Users className="w-4 h-4" />
                {activeUsers.toLocaleString()} active
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* System Status */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            System Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-sm text-gray-400 capitalize mb-1">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="text-lg font-bold text-cyan-400">{value}</div>
                <div className="text-xs text-green-400 mt-1">🟢 Active</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Resource Flow */}
          <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Heart className="w-6 h-6 text-pink-400" />
              <span className="bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">
                Your Flow Today
              </span>
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg border border-cyan-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Weekly Resource Flow</span>
                  <span className="text-cyan-400 font-bold">$800</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">Direct to your account • No verification needed</p>
              </div>
              <div className="p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-lg border border-emerald-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Community Abundance Pool</span>
                  <span className="text-emerald-400 font-bold">$104,000</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">For housing, business, creative projects</p>
              </div>
            </div>
          </div>

          {/* Truth Network */}
          <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Network className="w-6 h-6 text-purple-400" />
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Truth Network
              </span>
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg border border-purple-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Channels Converted</span>
                  <span className="text-purple-400 font-bold">1.2M</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">Marketing → Reality • Growing exponentially</p>
              </div>
              <div className="p-4 bg-gradient-to-r from-orange-500/20 to-yellow-500/20 rounded-lg border border-orange-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Truth Propagation Rate</span>
                  <span className="text-orange-400 font-bold">Viral</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">Natural spread • No gatekeepers</p>
              </div>
            </div>
          </div>

          {/* What Calls You */}
          <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Lightbulb className="w-6 h-6 text-yellow-400" />
              <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                What Calls You?
              </span>
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-indigo-500/20 to-blue-500/20 rounded-lg border border-indigo-500/30 hover:border-indigo-400/50 transition-colors cursor-pointer">
                <p className="text-white font-medium">Teaching quantum physics at the park</p>
                <p className="text-sm text-gray-300 mt-2">3 neighbors are curious too</p>
              </div>
              <div className="p-4 bg-gradient-to-r from-teal-500/20 to-green-500/20 rounded-lg border border-teal-500/30 hover:border-teal-400/50 transition-colors cursor-pointer">
                <p className="text-white font-medium">Community garden needs plant wisdom</p>
                <p className="text-sm text-gray-300 mt-2">Share what you know</p>
              </div>
            </div>
          </div>

          {/* System Transformation */}
          <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Zap className="w-6 h-6 text-cyan-400" />
              <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                System Status
              </span>
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-lg border border-cyan-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Mesh Network Health</span>
                  <span className="text-cyan-400 font-bold">99.9%</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">Self-healing • Autonomous operation</p>
              </div>
              <div className="p-4 bg-gradient-to-r from-red-500/20 to-pink-500/20 rounded-lg border border-red-500/30">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Transformation Progress</span>
                  <span className="text-red-400 font-bold">47%</span>
                </div>
                <p className="text-sm text-gray-300 mt-2">Critical mass approaching</p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Status */}
        <div className="mt-8 bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-green-400" />
            <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">
              Trust-First Security
            </span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="text-2xl font-bold text-green-400 mb-2">OPEN</div>
              <div className="text-sm text-gray-300">Authentication</div>
            </div>
            <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="text-2xl font-bold text-green-400 mb-2">TRUST</div>
              <div className="text-sm text-gray-300">Default Mode</div>
            </div>
            <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="text-2xl font-bold text-green-400 mb-2">DIRECT</div>
              <div className="text-sm text-gray-300">Access Model</div>
            </div>
          </div>
        </div>

        {/* Global Impact */}
        <div className="mt-8 bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Globe className="w-6 h-6 text-blue-400" />
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Global Impact
            </span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-cyan-400 mb-2">50K+</div>
              <div className="text-sm text-gray-300">Active Nodes</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400 mb-2">1.2M</div>
              <div className="text-sm text-gray-300">Truth Channels</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400 mb-2">$19T</div>
              <div className="text-sm text-gray-300">Resource Pool</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-400 mb-2">∞</div>
              <div className="text-sm text-gray-300">Possibilities</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-cyan-500/20 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="text-center text-gray-400 text-sm">
            <p className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent font-medium">
              "We're not building software. We're creating transformation."
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LiberationDashboard;
