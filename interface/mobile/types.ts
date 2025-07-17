export interface SystemMetrics {
  resourceDistribution: string;
  truthChannels: string;
  networkNodes: string;
  systemUptime: string;
  responseTime: string;
}

export interface NavigationItem {
  id: string;
  name: string;
  icon: React.ReactNode;
  badge?: number;
}

export interface ResourceFlowRequest {
  amount: number;
  type: 'weekly_flow' | 'community_pool' | 'emergency';
  timestamp: string;
  userId?: string;
}

export interface ResourceHistoryItem {
  id: string;
  type: 'weekly_flow' | 'community_pool' | 'emergency';
  amount: number;
  date: string;
  status: 'completed' | 'pending' | 'failed';
  description?: string;
}

export interface TruthNetworkStatus {
  channelsConverted: string;
  propagationRate: string;
  activeNodes: string;
  recentActivity: TruthActivity[];
}

export interface TruthActivity {
  id: string;
  type: 'channel_converted' | 'reality_shared' | 'truth_propagated';
  title: string;
  description: string;
  timestamp: string;
  impact: 'low' | 'medium' | 'high';
}

export interface MeshNetworkNode {
  id: string;
  location: string;
  status: 'online' | 'offline' | 'degraded';
  type: 'mobile' | 'desktop' | 'server';
  lastSeen: string;
  connectionQuality: number;
}

export interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  read: boolean;
}

export interface NotificationItem {
  id: string;
  type: 'resource_update' | 'truth_network' | 'system_alert' | 'community';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action?: {
    type: 'navigate' | 'external_link' | 'api_call';
    target: string;
    label: string;
  };
}

export interface CommunityPoolApplication {
  id?: string;
  projectTitle: string;
  description: string;
  requestedAmount: number;
  category: 'housing' | 'business' | 'creative' | 'education' | 'health' | 'other';
  timeline: string;
  impact: string;
  status?: 'pending' | 'approved' | 'rejected';
  submittedAt?: string;
}

export interface UserProfile {
  id: string;
  name?: string;
  email?: string;
  location?: string;
  joinedAt: string;
  totalResourcesReceived: number;
  contributionScore: number;
  trustLevel: 'basic' | 'verified' | 'trusted' | 'champion';
  preferences: {
    notifications: boolean;
    darkMode: boolean;
    language: string;
  };
}

export interface MobileAppState {
  isMenuOpen: boolean;
  activeTab: string;
  isConnected: boolean;
  activeUsers: number;
  notifications: number;
  metrics: SystemMetrics;
  resourceHistory: ResourceHistoryItem[];
  truthNetworkStatus: TruthNetworkStatus;
  meshNodes: MeshNetworkNode[];
  systemAlerts: SystemAlert[];
  notificationItems: NotificationItem[];
  userProfile: UserProfile;
}

export interface WebSocketMessage {
  type: 'metrics_update' | 'resource_distribution' | 'truth_network_update' | 'system_alert' | 'mesh_update';
  payload: any;
  timestamp: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PushNotificationConfig {
  enabled: boolean;
  token?: string;
  categories: {
    resourceUpdates: boolean;
    truthNetwork: boolean;
    systemAlerts: boolean;
    communityUpdates: boolean;
  };
}

export interface GeoLocation {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: string;
}

export interface DeviceInfo {
  platform: 'ios' | 'android' | 'web';
  version: string;
  model?: string;
  userAgent?: string;
  screenSize: {
    width: number;
    height: number;
  };
  darkMode: boolean;
  language: string;
  timezone: string;
}

export interface OfflineQueue {
  id: string;
  action: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  url: string;
  data?: any;
  timestamp: string;
  retryCount: number;
  maxRetries: number;
}

export interface SyncStatus {
  isOnline: boolean;
  lastSync: string;
  pendingActions: number;
  syncInProgress: boolean;
  failedActions: number;
}

export interface SecuritySettings {
  biometricEnabled: boolean;
  pinEnabled: boolean;
  sessionTimeout: number;
  autoLock: boolean;
  secureStorage: boolean;
  trustLevel: 'basic' | 'enhanced' | 'maximum';
}

export interface PerformanceMetrics {
  appStartTime: number;
  apiResponseTime: number;
  renderTime: number;
  memoryUsage: number;
  batteryOptimized: boolean;
  networkQuality: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface AccessibilitySettings {
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  highContrast: boolean;
  screenReader: boolean;
  hapticFeedback: boolean;
  voiceCommands: boolean;
}

export interface LiberationTheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  gradients: {
    primary: string;
    secondary: string;
    accent: string;
  };
}

export interface AnimationSettings {
  enabled: boolean;
  duration: 'fast' | 'normal' | 'slow';
  reduceMotion: boolean;
  parallax: boolean;
  transitions: boolean;
}

export const DEFAULT_THEME: LiberationTheme = {
  primary: '#00ffff',
  secondary: '#9333ea',
  accent: '#f59e0b',
  background: '#111827',
  surface: '#1f2937',
  text: '#ffffff',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  gradients: {
    primary: 'linear-gradient(to right, #00ffff, #9333ea)',
    secondary: 'linear-gradient(to right, #9333ea, #ec4899)',
    accent: 'linear-gradient(to right, #f59e0b, #ef4444)'
  }
};
