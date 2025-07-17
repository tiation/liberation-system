export interface SystemMetrics {
  resourceDistribution: string;
  truthChannels: string;
  networkNodes: string;
  systemUptime: string;
  responseTime: string;
  activeUsers: number;
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
  icon: string;
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

export interface LiberationContextType {
  // System State
  isConnected: boolean;
  metrics: SystemMetrics;
  systemHealth: any;
  
  // User Data
  userProfile: UserProfile | null;
  resourceHistory: ResourceHistoryItem[];
  notifications: NotificationItem[];
  
  // Truth Network
  truthNetworkStatus: TruthNetworkStatus;
  
  // Community
  communityData: any;
  
  // Actions
  requestResourceFlow: (amount: number) => Promise<void>;
  shareReality: (content: string) => Promise<void>;
  convertChannel: (channelData: any) => Promise<void>;
  applyCommunityPool: (application: CommunityPoolApplication) => Promise<void>;
  markNotificationRead: (id: string) => Promise<void>;
  
  // Loading States
  isLoading: boolean;
  error: string | null;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'metrics_update' | 'resource_distribution' | 'truth_network_update' | 'system_alert' | 'mesh_update';
  payload: any;
  timestamp: string;
}

export interface TabBarProps {
  state: any;
  descriptors: any;
  navigation: any;
}

export interface IconProps {
  name: string;
  size?: number;
  color?: string;
}

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  style?: any;
}

export interface CardProps {
  children: React.ReactNode;
  style?: any;
  gradient?: boolean;
  neonGlow?: boolean;
  glowColor?: string;
}

export interface MetricCardProps {
  title: string;
  value: string;
  status: 'active' | 'pending' | 'error';
  icon?: string;
  color?: string;
}

export interface ActivityItemProps {
  activity: TruthActivity;
  onPress?: () => void;
}

export interface ResourceCardProps {
  title: string;
  amount: string;
  description: string;
  onPress: () => void;
  gradient: string[];
  borderColor: string;
}

export interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'degraded';
  size?: 'sm' | 'md' | 'lg';
}

export interface ProgressBarProps {
  progress: number;
  color?: string;
  height?: number;
  animated?: boolean;
}

export interface FormInputProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  multiline?: boolean;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  style?: any;
}

export interface LoadingProps {
  size?: 'small' | 'large';
  color?: string;
}

export interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
  action?: {
    label: string;
    onPress: () => void;
  };
}

// Navigation Types
export type RootStackParamList = {
  Dashboard: undefined;
  Resources: undefined;
  Truth: undefined;
  Community: undefined;
  Profile: undefined;
  Settings: undefined;
  ResourceRequest: { type: 'weekly_flow' | 'community_pool' };
  CommunityApplication: undefined;
  NotificationDetails: { notification: NotificationItem };
};

export type TabNavigationProps = {
  Dashboard: undefined;
  Resources: undefined;
  Truth: undefined;
  Community: undefined;
};
