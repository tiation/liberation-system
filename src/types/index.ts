export interface Human {
  id: string;
  weeklyFlow: number;
  housingCredit: number;
  investmentPool: number;
  createdAt: string;
  lastDistribution?: string;
  totalReceived: number;
  status: 'active' | 'inactive' | 'pending';
}

export interface Transaction {
  id: string;
  humanId: string;
  amount: number;
  transactionType: 'weekly_distribution' | 'housing_credit' | 'investment_pool' | 'manual';
  timestamp: string;
  status: 'completed' | 'failed' | 'pending';
  metadata?: Record<string, any>;
}

export interface ResourceStats {
  totalHumans: number;
  activeHumans: number;
  totalDistributed: number;
  distributedThisWeek: number;
  remainingWealth: number;
  averagePerHuman: number;
}

export interface TruthMessage {
  id: string;
  content: string;
  source: string;
  priority: number;
  createdAt: string;
  spreadCount: number;
  effectivenessScore: number;
  active: boolean;
}

export interface Channel {
  id: string;
  name: string;
  type: 'billboard' | 'social' | 'media' | 'direct';
  reach: number;
  conversionRate: number;
  lastMessageId?: string;
  status: 'active' | 'inactive' | 'maintenance';
  createdAt: string;
}

export interface TruthStats {
  totalMessages: number;
  activeChannels: number;
  totalSpreadCount: number;
  totalReach: number;
  topMessages: TruthMessage[];
  channelPerformance: Record<string, number>;
}

export interface MeshNode {
  id: string;
  address: string;
  port: number;
  publicKey?: string;
  status: 'active' | 'inactive' | 'connecting';
  lastSeen: string;
  transmissionPower: number;
  connectionsCount: number;
  dataTransferred: number;
  createdAt: string;
}

export interface MeshConnection {
  id: string;
  nodeA: string;
  nodeB: string;
  connectionStrength: number;
  latencyMs: number;
  establishedAt: string;
  lastPing: string;
  status: 'active' | 'inactive' | 'unstable';
}

export interface SystemTask {
  name: string;
  priority: number;
  lastRun?: string;
  runCount: number;
  successCount: number;
  failureCount: number;
  averageDuration: number;
  status: 'pending' | 'running' | 'success' | 'failed';
  nextRun?: string;
}

export interface SystemMetrics {
  uptime: number;
  tasksCompleted: number;
  errorsHandled: number;
  resourcesDistributed: number;
  truthMessagesSent: number;
  meshNodesActive: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
}

export interface SystemHealth {
  overall: 'healthy' | 'degraded' | 'critical';
  components: {
    resourceSystem: boolean;
    truthSystem: boolean;
    meshNetwork: boolean;
    automation: boolean;
    database: boolean;
  };
  uptime: number;
  lastCheck: string;
}

export interface DashboardData {
  systemHealth: SystemHealth;
  metrics: SystemMetrics;
  resourceStats: ResourceStats;
  truthStats: TruthStats;
  activeTasks: SystemTask[];
  recentTransactions: Transaction[];
  activeNodes: MeshNode[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface LiberationConfig {
  liberationMode: 'development' | 'production';
  trustLevel: 'maximum' | 'high' | 'medium';
  debugMode: boolean;
  apiUrl: string;
  refreshInterval: number;
  theme: {
    primaryColor: string;
    secondaryColor: string;
    accentColor: string;
    background: string;
    surface: string;
    text: string;
    success: string;
    warning: string;
    error: string;
    gradient: string;
  };
}

export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface NeonButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export interface MetricCardProps extends ComponentProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'stable';
  icon?: React.ReactNode;
  status?: 'active' | 'warning' | 'error';
}

export interface ProgressBarProps extends ComponentProps {
  value: number;
  max: number;
  label?: string;
  variant?: 'primary' | 'secondary' | 'accent';
  showPercentage?: boolean;
}

export interface ConsoleOutputProps extends ComponentProps {
  logs: string[];
  maxLines?: number;
  autoScroll?: boolean;
}

export interface DataTableProps<T> extends ComponentProps {
  data: T[];
  columns: Array<{
    key: keyof T;
    label: string;
    render?: (value: any, row: T) => React.ReactNode;
  }>;
  onRowClick?: (row: T) => void;
  loading?: boolean;
}

export type NavigationItem = {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  badge?: number;
  active?: boolean;
};

export type ThemeMode = 'dark' | 'neon' | 'matrix';

export type NotificationType = 'success' | 'warning' | 'error' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}
