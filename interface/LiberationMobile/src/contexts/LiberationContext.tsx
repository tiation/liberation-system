import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { 
  LiberationContextType, 
  SystemMetrics, 
  UserProfile, 
  ResourceHistoryItem, 
  TruthNetworkStatus, 
  NotificationItem,
  CommunityPoolApplication 
} from '../types';
import { LiberationAI } from '../services/LiberationAI';
import { AutomationEngine } from '../services/AutomationEngine';
import { InfiltrationSystem } from '../services/InfiltrationSystem';
import { LearningNetwork } from '../services/LearningNetwork';

interface LiberationState {
  isConnected: boolean;
  metrics: SystemMetrics;
  systemHealth: any;
  userProfile: UserProfile | null;
  resourceHistory: ResourceHistoryItem[];
  notifications: NotificationItem[];
  truthNetworkStatus: TruthNetworkStatus;
  communityData: any;
  isLoading: boolean;
  error: string | null;
  
  // AI and Automation
  aiInsights: any[];
  automationTasks: any[];
  learningProgress: any;
  infiltrationTargets: any[];
  networkGrowth: any;
}

type LiberationAction = 
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_METRICS'; payload: SystemMetrics }
  | { type: 'SET_USER_PROFILE'; payload: UserProfile }
  | { type: 'SET_RESOURCE_HISTORY'; payload: ResourceHistoryItem[] }
  | { type: 'SET_NOTIFICATIONS'; payload: NotificationItem[] }
  | { type: 'SET_TRUTH_NETWORK_STATUS'; payload: TruthNetworkStatus }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_AI_INSIGHT'; payload: any }
  | { type: 'UPDATE_AUTOMATION_TASKS'; payload: any[] }
  | { type: 'UPDATE_LEARNING_PROGRESS'; payload: any }
  | { type: 'UPDATE_INFILTRATION_TARGETS'; payload: any[] }
  | { type: 'UPDATE_NETWORK_GROWTH'; payload: any };

const initialState: LiberationState = {
  isConnected: false,
  metrics: {
    resourceDistribution: '$19T',
    truthChannels: '1.2M',
    networkNodes: '50K+',
    systemUptime: '99.9%',
    responseTime: '<100ms',
    activeUsers: 1247
  },
  systemHealth: null,
  userProfile: null,
  resourceHistory: [],
  notifications: [],
  truthNetworkStatus: {
    channelsConverted: '1.2M',
    propagationRate: 'Viral',
    activeNodes: '50K+',
    recentActivity: []
  },
  communityData: null,
  isLoading: false,
  error: null,
  aiInsights: [],
  automationTasks: [],
  learningProgress: null,
  infiltrationTargets: [],
  networkGrowth: null
};

const liberationReducer = (state: LiberationState, action: LiberationAction): LiberationState => {
  switch (action.type) {
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload };
    case 'SET_METRICS':
      return { ...state, metrics: action.payload };
    case 'SET_USER_PROFILE':
      return { ...state, userProfile: action.payload };
    case 'SET_RESOURCE_HISTORY':
      return { ...state, resourceHistory: action.payload };
    case 'SET_NOTIFICATIONS':
      return { ...state, notifications: action.payload };
    case 'SET_TRUTH_NETWORK_STATUS':
      return { ...state, truthNetworkStatus: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'ADD_AI_INSIGHT':
      return { ...state, aiInsights: [...state.aiInsights, action.payload] };
    case 'UPDATE_AUTOMATION_TASKS':
      return { ...state, automationTasks: action.payload };
    case 'UPDATE_LEARNING_PROGRESS':
      return { ...state, learningProgress: action.payload };
    case 'UPDATE_INFILTRATION_TARGETS':
      return { ...state, infiltrationTargets: action.payload };
    case 'UPDATE_NETWORK_GROWTH':
      return { ...state, networkGrowth: action.payload };
    default:
      return state;
  }
};

const LiberationContext = createContext<LiberationContextType | undefined>(undefined);

export const LiberationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(liberationReducer, initialState);
  
  // Initialize AI and automation systems
  const ai = new LiberationAI();
  const automation = new AutomationEngine();
  const infiltration = new InfiltrationSystem();
  const learning = new LearningNetwork();

  useEffect(() => {
    initializeSystems();
    startAutomationLoop();
    startLearningLoop();
    startInfiltrationLoop();
  }, []);

  const initializeSystems = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Initialize AI systems
      await ai.initialize();
      await automation.initialize();
      await infiltration.initialize();
      await learning.initialize();
      
      // Load user profile
      const profile = await loadUserProfile();
      if (profile) {
        dispatch({ type: 'SET_USER_PROFILE', payload: profile });
      }
      
      // Start real-time connections
      await connectToSystem();
      
      dispatch({ type: 'SET_CONNECTED', payload: true });
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const connectToSystem = async () => {
    // WebSocket connection with auto-reconnect
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      dispatch({ type: 'SET_CONNECTED', payload: true });
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
      dispatch({ type: 'SET_CONNECTED', payload: false });
      // Auto-reconnect after 5 seconds
      setTimeout(connectToSystem, 5000);
    };
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'metrics_update':
        dispatch({ type: 'SET_METRICS', payload: data.payload });
        break;
      case 'truth_network_update':
        dispatch({ type: 'SET_TRUTH_NETWORK_STATUS', payload: data.payload });
        break;
      case 'ai_insight':
        dispatch({ type: 'ADD_AI_INSIGHT', payload: data.payload });
        break;
      case 'automation_update':
        dispatch({ type: 'UPDATE_AUTOMATION_TASKS', payload: data.payload });
        break;
      case 'learning_progress':
        dispatch({ type: 'UPDATE_LEARNING_PROGRESS', payload: data.payload });
        break;
      case 'infiltration_update':
        dispatch({ type: 'UPDATE_INFILTRATION_TARGETS', payload: data.payload });
        break;
      case 'network_growth':
        dispatch({ type: 'UPDATE_NETWORK_GROWTH', payload: data.payload });
        break;
    }
  };

  const startAutomationLoop = () => {
    setInterval(async () => {
      try {
        // Execute automation tasks
        const tasks = await automation.executeNextTasks();
        dispatch({ type: 'UPDATE_AUTOMATION_TASKS', payload: tasks });
        
        // Generate AI insights
        const insights = await ai.generateInsights(state.metrics, state.userProfile);
        if (insights) {
          dispatch({ type: 'ADD_AI_INSIGHT', payload: insights });
        }
      } catch (error) {
        console.error('Automation loop error:', error);
      }
    }, 30000); // Every 30 seconds
  };

  const startLearningLoop = () => {
    setInterval(async () => {
      try {
        // Update learning progress
        const progress = await learning.updateLearningProgress();
        dispatch({ type: 'UPDATE_LEARNING_PROGRESS', payload: progress });
        
        // Adapt strategies based on learning
        await automation.adaptStrategies(progress);
      } catch (error) {
        console.error('Learning loop error:', error);
      }
    }, 60000); // Every minute
  };

  const startInfiltrationLoop = () => {
    setInterval(async () => {
      try {
        // Scan for infiltration opportunities
        const targets = await infiltration.scanTargets();
        dispatch({ type: 'UPDATE_INFILTRATION_TARGETS', payload: targets });
        
        // Execute infiltration strategies
        await infiltration.executeStrategies(targets);
      } catch (error) {
        console.error('Infiltration loop error:', error);
      }
    }, 120000); // Every 2 minutes
  };

  const loadUserProfile = async (): Promise<UserProfile | null> => {
    try {
      const profile = await AsyncStorage.getItem('userProfile');
      return profile ? JSON.parse(profile) : null;
    } catch (error) {
      console.error('Error loading user profile:', error);
      return null;
    }
  };

  const saveUserProfile = async (profile: UserProfile) => {
    try {
      await AsyncStorage.setItem('userProfile', JSON.stringify(profile));
      dispatch({ type: 'SET_USER_PROFILE', payload: profile });
    } catch (error) {
      console.error('Error saving user profile:', error);
    }
  };

  const requestResourceFlow = async (amount: number) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const request = {
        amount,
        type: 'weekly_flow' as const,
        timestamp: new Date().toISOString(),
        userId: state.userProfile?.id
      };
      
      // Send request to automation system
      const result = await automation.requestResourceFlow(request);
      
      if (result.success) {
        // Update resource history
        const newHistory = [...state.resourceHistory, result.transaction];
        dispatch({ type: 'SET_RESOURCE_HISTORY', payload: newHistory });
        
        // Trigger AI learning from successful request
        await learning.recordSuccess('resource_request', request);
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const shareReality = async (content: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Use AI to optimize content for maximum impact
      const optimizedContent = await ai.optimizeContent(content);
      
      // Share through infiltration network
      const result = await infiltration.shareReality(optimizedContent);
      
      if (result.success) {
        // Update truth network status
        const updatedStatus = await getTruthNetworkStatus();
        dispatch({ type: 'SET_TRUTH_NETWORK_STATUS', payload: updatedStatus });
        
        // Learn from sharing success
        await learning.recordSuccess('reality_share', { content, result });
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const convertChannel = async (channelData: any) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Use AI to analyze channel vulnerability
      const analysis = await ai.analyzeChannel(channelData);
      
      // Execute infiltration strategy
      const result = await infiltration.convertChannel(channelData, analysis);
      
      if (result.success) {
        // Update metrics
        const updatedMetrics = await getSystemMetrics();
        dispatch({ type: 'SET_METRICS', payload: updatedMetrics });
        
        // Learn from conversion success
        await learning.recordSuccess('channel_convert', { channelData, result });
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const applyCommunityPool = async (application: CommunityPoolApplication) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Use AI to optimize application
      const optimizedApp = await ai.optimizeApplication(application);
      
      // Submit through automation system
      const result = await automation.submitCommunityApplication(optimizedApp);
      
      if (result.success) {
        // Update user profile
        if (state.userProfile) {
          const updatedProfile = {
            ...state.userProfile,
            totalResourcesReceived: state.userProfile.totalResourcesReceived + application.requestedAmount
          };
          await saveUserProfile(updatedProfile);
        }
        
        // Learn from application success
        await learning.recordSuccess('community_application', { application, result });
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const markNotificationRead = async (id: string) => {
    try {
      const updatedNotifications = state.notifications.map(n => 
        n.id === id ? { ...n, read: true } : n
      );
      dispatch({ type: 'SET_NOTIFICATIONS', payload: updatedNotifications });
      
      // Update in storage
      await AsyncStorage.setItem('notifications', JSON.stringify(updatedNotifications));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const getSystemMetrics = async (): Promise<SystemMetrics> => {
    // This would typically fetch from API
    return state.metrics;
  };

  const getTruthNetworkStatus = async (): Promise<TruthNetworkStatus> => {
    // This would typically fetch from API
    return state.truthNetworkStatus;
  };

  const contextValue: LiberationContextType = {
    ...state,
    requestResourceFlow,
    shareReality,
    convertChannel,
    applyCommunityPool,
    markNotificationRead,
  };

  return (
    <LiberationContext.Provider value={contextValue}>
      {children}
    </LiberationContext.Provider>
  );
};

export const useLiberationContext = () => {
  const context = useContext(LiberationContext);
  if (!context) {
    throw new Error('useLiberationContext must be used within a LiberationProvider');
  }
  return context;
};
