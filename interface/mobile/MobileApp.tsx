import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Heart, 
  Lightbulb, 
  Shield, 
  Zap, 
  Network, 
  Users,
  Globe,
  Activity,
  Menu,
  X,
  Home,
  Settings,
  Bell,
  ChevronRight,
  TrendingUp,
  Eye,
  MessageSquare,
  Wallet,
  Share2
} from 'lucide-react';

interface SystemMetrics {
  resourceDistribution: string;
  truthChannels: string;
  networkNodes: string;
  systemUptime: string;
  responseTime: string;
}

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ReactNode;
  badge?: number;
}

const MobileApp: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    resourceDistribution: '$19T',
    truthChannels: '1.2M',
    networkNodes: '50K+',
    systemUptime: '99.9%',
    responseTime: '<100ms'
  });

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isConnected, setIsConnected] = useState(true);
  const [activeUsers, setActiveUsers] = useState(1247);
  const [notifications, setNotifications] = useState(3);

  const navigationItems: NavigationItem[] = [
    { id: 'dashboard', name: 'Dashboard', icon: <Home className="w-5 h-5" /> },
    { id: 'resources', name: 'Resources', icon: <Wallet className="w-5 h-5" /> },
    { id: 'truth', name: 'Truth Network', icon: <Network className="w-5 h-5" /> },
    { id: 'community', name: 'Community', icon: <Users className="w-5 h-5" /> },
    { id: 'notifications', name: 'Notifications', icon: <Bell className="w-5 h-5" />, badge: notifications },
    { id: 'settings', name: 'Settings', icon: <Settings className="w-5 h-5" /> }
  ];

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setActiveUsers(prev => prev + Math.floor(Math.random() * 10) - 5);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Status Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
          <div className="text-sm text-gray-400 mb-1">Your Flow</div>
          <div className="text-xl font-bold text-cyan-400">$800</div>
          <div className="text-xs text-green-400">🟢 Weekly</div>
        </div>
        <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
          <div className="text-sm text-gray-400 mb-1">Community Pool</div>
          <div className="text-xl font-bold text-purple-400">$104K</div>
          <div className="text-xs text-green-400">🟢 Available</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyan-400" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg p-3 text-left">
            <div className="text-white font-medium">Request Resources</div>
            <div className="text-xs text-gray-300">Instant access</div>
          </button>
          <button className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-lg p-3 text-left">
            <div className="text-white font-medium">Share Truth</div>
            <div className="text-xs text-gray-300">Spread reality</div>
          </button>
        </div>
      </div>

      {/* Live Feed */}
      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-green-400" />
          Live Network Activity
        </h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                <Heart className="w-4 h-4 text-black" />
              </div>
              <div>
                <div className="text-sm font-medium">Resource Distribution</div>
                <div className="text-xs text-gray-400">12 people received $800</div>
              </div>
            </div>
            <div className="text-xs text-gray-400">2m ago</div>
          </div>
          <div className="flex items-center justify-between p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-purple-400 rounded-full flex items-center justify-center">
                <Network className="w-4 h-4 text-black" />
              </div>
              <div>
                <div className="text-sm font-medium">Truth Channel Added</div>
                <div className="text-xs text-gray-400">Marketing → Reality</div>
              </div>
            </div>
            <div className="text-xs text-gray-400">5m ago</div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-green-400" />
          System Health
        </h3>
        <div className="space-y-3">
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <div className="text-sm text-gray-300 capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </div>
              <div className="text-sm font-bold text-cyan-400">{value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderResources = () => (
    <div className="space-y-6">
      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Heart className="w-6 h-6 text-pink-400" />
          <span className="bg-gradient-to-r from-pink-400 to-cyan-400 bg-clip-text text-transparent">
            Your Resource Flow
          </span>
        </h3>
        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg border border-cyan-500/30">
            <div className="flex items-center justify-between">
              <span className="text-white font-medium">Weekly Flow</span>
              <span className="text-cyan-400 font-bold">$800</span>
            </div>
            <p className="text-sm text-gray-300 mt-2">Direct to your account • No verification needed</p>
            <button className="w-full mt-3 bg-cyan-500/20 border border-cyan-500/30 rounded-lg py-2 text-cyan-400 font-medium">
              Request Now
            </button>
          </div>
          <div className="p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-lg border border-emerald-500/30">
            <div className="flex items-center justify-between">
              <span className="text-white font-medium">Community Pool</span>
              <span className="text-emerald-400 font-bold">$104,000</span>
            </div>
            <p className="text-sm text-gray-300 mt-2">Housing, business, creative projects</p>
            <button className="w-full mt-3 bg-emerald-500/20 border border-emerald-500/30 rounded-lg py-2 text-emerald-400 font-medium">
              Apply for Project
            </button>
          </div>
        </div>
      </div>

      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4">Resource History</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium">Weekly Flow</div>
              <div className="text-xs text-gray-400">July 10, 2024</div>
            </div>
            <div className="text-green-400 font-bold">+$800</div>
          </div>
          <div className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium">Community Pool</div>
              <div className="text-xs text-gray-400">July 8, 2024</div>
            </div>
            <div className="text-blue-400 font-bold">+$2,500</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTruthNetwork = () => (
    <div className="space-y-6">
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
              <span className="text-white font-medium">Truth Propagation</span>
              <span className="text-orange-400 font-bold">Viral</span>
            </div>
            <p className="text-sm text-gray-300 mt-2">Natural spread • No gatekeepers</p>
          </div>
        </div>
      </div>

      <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-6 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4">Truth Actions</h3>
        <div className="space-y-3">
          <button className="w-full p-4 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg text-left">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-medium">Share Reality</div>
                <div className="text-xs text-gray-300">Replace marketing with truth</div>
              </div>
              <Share2 className="w-5 h-5 text-cyan-400" />
            </div>
          </button>
          <button className="w-full p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-lg text-left">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-medium">Convert Channel</div>
                <div className="text-xs text-gray-300">Transform media to truth</div>
              </div>
              <Network className="w-5 h-5 text-purple-400" />
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'resources':
        return renderResources();
      case 'truth':
        return renderTruthNetwork();
      case 'community':
        return (
          <div className="text-center text-gray-400 mt-8">
            <Users className="w-12 h-12 mx-auto mb-4 text-cyan-400" />
            <p>Community features coming soon</p>
          </div>
        );
      case 'notifications':
        return (
          <div className="text-center text-gray-400 mt-8">
            <Bell className="w-12 h-12 mx-auto mb-4 text-cyan-400" />
            <p>Notifications will appear here</p>
          </div>
        );
      case 'settings':
        return (
          <div className="text-center text-gray-400 mt-8">
            <Settings className="w-12 h-12 mx-auto mb-4 text-cyan-400" />
            <p>Settings panel coming soon</p>
          </div>
        );
      default:
        return renderDashboard();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-cyan-500/20 bg-black/20 backdrop-blur-sm sticky top-0 z-50">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-black" />
              </div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Liberation
              </h1>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
                <span className="text-xs text-gray-300">
                  {activeUsers.toLocaleString()}
                </span>
              </div>
              <button
                onClick={toggleMenu}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Menu */}
      {isMenuOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40" onClick={toggleMenu}>
          <div className="absolute right-0 top-0 h-full w-64 bg-black/80 backdrop-blur-sm border-l border-cyan-500/20">
            <div className="p-4 border-b border-cyan-500/20">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Navigation</h2>
                <button onClick={toggleMenu}>
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <nav className="p-4">
              <ul className="space-y-2">
                {navigationItems.map((item) => (
                  <li key={item.id}>
                    <button
                      onClick={() => {
                        setActiveTab(item.id);
                        setIsMenuOpen(false);
                      }}
                      className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                        activeTab === item.id
                          ? 'bg-cyan-500/20 border border-cyan-500/30'
                          : 'hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {item.icon}
                        <span>{item.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {item.badge && (
                          <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs">
                            {item.badge}
                          </div>
                        )}
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="px-4 py-6">
        {renderContent()}
      </main>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm border-t border-cyan-500/20">
        <div className="flex items-center justify-around py-2">
          {navigationItems.slice(0, 4).map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-colors ${
                activeTab === item.id
                  ? 'text-cyan-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <div className="relative">
                {item.icon}
                {item.badge && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center text-xs">
                    {item.badge}
                  </div>
                )}
              </div>
              <span className="text-xs">{item.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MobileApp;
