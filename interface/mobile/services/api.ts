import { SystemMetrics } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class MobileApiService {
  private static instance: MobileApiService;
  private isConnected = true;
  private websocket: WebSocket | null = null;

  private constructor() {
    this.initializeWebSocket();
  }

  public static getInstance(): MobileApiService {
    if (!MobileApiService.instance) {
      MobileApiService.instance = new MobileApiService();
    }
    return MobileApiService.instance;
  }

  private initializeWebSocket(): void {
    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
      };

      this.websocket.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.initializeWebSocket(), 5000);
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      };
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
      this.isConnected = false;
    }
  }

  private handleWebSocketMessage(data: any): void {
    // Handle real-time updates from the Liberation System
    switch (data.type) {
      case 'metrics_update':
        this.onMetricsUpdate?.(data.payload);
        break;
      case 'resource_distribution':
        this.onResourceUpdate?.(data.payload);
        break;
      case 'truth_network_update':
        this.onTruthNetworkUpdate?.(data.payload);
        break;
      case 'system_alert':
        this.onSystemAlert?.(data.payload);
        break;
    }
  }

  // Event handlers (can be set by components)
  public onMetricsUpdate?: (metrics: SystemMetrics) => void;
  public onResourceUpdate?: (update: any) => void;
  public onTruthNetworkUpdate?: (update: any) => void;
  public onSystemAlert?: (alert: any) => void;

  public getConnectionStatus(): boolean {
    return this.isConnected;
  }

  // System Metrics
  public async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/system/metrics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch system metrics');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      // Return mock data for offline mode
      return {
        resourceDistribution: '$19T',
        truthChannels: '1.2M',
        networkNodes: '50K+',
        systemUptime: '99.9%',
        responseTime: '<100ms'
      };
    }
  }

  // Resource Distribution
  public async requestResourceFlow(amount: number = 800): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resources/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount,
          type: 'weekly_flow',
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to request resource flow');
      }

      return await response.json();
    } catch (error) {
      console.error('Error requesting resource flow:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  public async applyCommunityPool(projectDetails: any): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resources/community-pool`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...projectDetails,
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to apply for community pool');
      }

      return await response.json();
    } catch (error) {
      console.error('Error applying for community pool:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  public async getResourceHistory(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/resources/history`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch resource history');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching resource history:', error);
      return [];
    }
  }

  // Truth Network
  public async getTruthNetworkStatus(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/truth/network-status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch truth network status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching truth network status:', error);
      return {
        channelsConverted: '1.2M',
        propagationRate: 'Viral',
        activeNodes: '50K+'
      };
    }
  }

  public async shareReality(content: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/truth/share-reality`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          timestamp: new Date().toISOString(),
          source: 'mobile_app'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to share reality');
      }

      return await response.json();
    } catch (error) {
      console.error('Error sharing reality:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  public async convertChannel(channelData: any): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/truth/convert-channel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...channelData,
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to convert channel');
      }

      return await response.json();
    } catch (error) {
      console.error('Error converting channel:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // System Health
  public async getSystemHealth(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/system/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch system health');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching system health:', error);
      return {
        meshNetworkHealth: '99.9%',
        transformationProgress: '47%',
        activeUsers: 1247,
        trustLevel: 'maximum'
      };
    }
  }

  // Mesh Network
  public async getMeshNetworkNodes(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mesh/nodes`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch mesh network nodes');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching mesh network nodes:', error);
      return [];
    }
  }

  public async joinMeshNetwork(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mesh/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_type: 'mobile',
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to join mesh network');
      }

      return await response.json();
    } catch (error) {
      console.error('Error joining mesh network:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Notifications
  public async getNotifications(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notifications`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }

  public async markNotificationAsRead(id: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notifications/${id}/read`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to mark notification as read');
      }

      return await response.json();
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Push Notifications
  public async registerForPushNotifications(token: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/push/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          device_type: 'mobile',
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to register for push notifications');
      }

      return await response.json();
    } catch (error) {
      console.error('Error registering for push notifications:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  public sendMessage(message: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent');
    }
  }

  public disconnect(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}

export const mobileApi = MobileApiService.getInstance();
