import AsyncStorage from '@react-native-async-storage/async-storage';

interface LearningData {
  id: string;
  type: string;
  input: any;
  output: any;
  success: boolean;
  timestamp: string;
  confidence: number;
}

interface LearningProgress {
  resourceSuccessRate: number;
  truthEngagementRate: number;
  networkGrowthRate: number;
  infiltrationSuccessRate: number;
  totalActions: number;
  improvementRate: number;
}

export class LearningNetwork {
  private learningData: LearningData[] = [];
  private progress: LearningProgress = {
    resourceSuccessRate: 0.5,
    truthEngagementRate: 0.5,
    networkGrowthRate: 0.1,
    infiltrationSuccessRate: 0.3,
    totalActions: 0,
    improvementRate: 0.05
  };

  async initialize() {
    try {
      // Load saved learning data
      const savedData = await AsyncStorage.getItem('learning_data');
      if (savedData) {
        this.learningData = JSON.parse(savedData);
      }

      // Load progress
      const savedProgress = await AsyncStorage.getItem('learning_progress');
      if (savedProgress) {
        this.progress = JSON.parse(savedProgress);
      }

      console.log('LearningNetwork initialized successfully');
    } catch (error) {
      console.error('Error initializing LearningNetwork:', error);
    }
  }

  async recordSuccess(type: string, data: any): Promise<void> {
    const learningEntry: LearningData = {
      id: `learning_${Date.now()}`,
      type,
      input: data,
      output: null,
      success: true,
      timestamp: new Date().toISOString(),
      confidence: 0.8
    };

    this.learningData.push(learningEntry);
    await this.updateProgress();
    await this.saveLearningData();
  }

  async recordFailure(type: string, data: any, error: string): Promise<void> {
    const learningEntry: LearningData = {
      id: `learning_${Date.now()}`,
      type,
      input: data,
      output: error,
      success: false,
      timestamp: new Date().toISOString(),
      confidence: 0.3
    };

    this.learningData.push(learningEntry);
    await this.updateProgress();
    await this.saveLearningData();
  }

  async updateLearningProgress(): Promise<LearningProgress> {
    await this.updateProgress();
    await this.saveProgress();
    return this.progress;
  }

  private async updateProgress(): Promise<void> {
    // Calculate success rates for different types
    const resourceActions = this.learningData.filter(d => d.type === 'resource_request');
    const truthActions = this.learningData.filter(d => d.type === 'reality_share');
    const networkActions = this.learningData.filter(d => d.type === 'network_expansion');
    const infiltrationActions = this.learningData.filter(d => d.type === 'channel_convert');

    this.progress.resourceSuccessRate = this.calculateSuccessRate(resourceActions);
    this.progress.truthEngagementRate = this.calculateSuccessRate(truthActions);
    this.progress.networkGrowthRate = this.calculateGrowthRate(networkActions);
    this.progress.infiltrationSuccessRate = this.calculateSuccessRate(infiltrationActions);
    this.progress.totalActions = this.learningData.length;
    this.progress.improvementRate = this.calculateImprovementRate();
  }

  private calculateSuccessRate(actions: LearningData[]): number {
    if (actions.length === 0) return 0.5;
    
    const successCount = actions.filter(a => a.success).length;
    return successCount / actions.length;
  }

  private calculateGrowthRate(actions: LearningData[]): number {
    if (actions.length === 0) return 0.1;
    
    const recentActions = actions.filter(a => 
      new Date(a.timestamp).getTime() > Date.now() - 24 * 60 * 60 * 1000
    );
    
    return Math.min(0.3, recentActions.length / 10);
  }

  private calculateImprovementRate(): number {
    if (this.learningData.length < 10) return 0.05;
    
    const recent = this.learningData.slice(-10);
    const older = this.learningData.slice(-20, -10);
    
    const recentSuccess = recent.filter(d => d.success).length / recent.length;
    const olderSuccess = older.filter(d => d.success).length / Math.max(older.length, 1);
    
    return Math.max(0, recentSuccess - olderSuccess);
  }

  getProgress(): LearningProgress {
    return { ...this.progress };
  }

  async getLearningInsights(): Promise<any[]> {
    const insights = [];
    
    // Resource success insight
    if (this.progress.resourceSuccessRate > 0.8) {
      insights.push({
        type: 'success',
        title: 'Resource Allocation Optimized',
        description: 'Resource requests are highly successful. Consider increasing allocation amounts.',
        confidence: 0.9
      });
    }

    // Truth engagement insight
    if (this.progress.truthEngagementRate > 0.7) {
      insights.push({
        type: 'optimization',
        title: 'Truth Propagation Effective',
        description: 'Truth sharing is engaging audiences well. Expand to more channels.',
        confidence: 0.8
      });
    }

    // Network growth insight
    if (this.progress.networkGrowthRate > 0.2) {
      insights.push({
        type: 'growth',
        title: 'Network Expansion Accelerating',
        description: 'Network is growing rapidly. Focus on quality over quantity.',
        confidence: 0.7
      });
    }

    return insights;
  }

  private async saveLearningData(): Promise<void> {
    try {
      // Keep only last 1000 entries
      if (this.learningData.length > 1000) {
        this.learningData = this.learningData.slice(-1000);
      }
      
      await AsyncStorage.setItem('learning_data', JSON.stringify(this.learningData));
    } catch (error) {
      console.error('Error saving learning data:', error);
    }
  }

  private async saveProgress(): Promise<void> {
    try {
      await AsyncStorage.setItem('learning_progress', JSON.stringify(this.progress));
    } catch (error) {
      console.error('Error saving progress:', error);
    }
  }

  async exportLearningData(): Promise<string> {
    return JSON.stringify({
      learningData: this.learningData,
      progress: this.progress,
      exportedAt: new Date().toISOString()
    });
  }

  async importLearningData(data: string): Promise<void> {
    try {
      const imported = JSON.parse(data);
      this.learningData = imported.learningData || [];
      this.progress = imported.progress || this.progress;
      
      await this.saveLearningData();
      await this.saveProgress();
    } catch (error) {
      console.error('Error importing learning data:', error);
    }
  }
}
