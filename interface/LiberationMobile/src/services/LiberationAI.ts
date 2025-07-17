import AsyncStorage from '@react-native-async-storage/async-storage';
import { SystemMetrics, UserProfile } from '../types';

interface AIInsight {
  id: string;
  type: 'optimization' | 'prediction' | 'strategy' | 'warning';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high';
  timestamp: string;
  actionable: boolean;
  actions?: string[];
}

interface LearningPattern {
  pattern: string;
  confidence: number;
  outcomes: string[];
  frequency: number;
  lastSeen: string;
}

interface NeuralWeight {
  input: string;
  output: string;
  weight: number;
  bias: number;
}

export class LiberationAI {
  private learningPatterns: LearningPattern[] = [];
  private neuralWeights: NeuralWeight[] = [];
  private contextMemory: Map<string, any> = new Map();
  private isInitialized = false;

  async initialize() {
    if (this.isInitialized) return;
    
    try {
      // Load existing learning patterns
      const savedPatterns = await AsyncStorage.getItem('ai_learning_patterns');
      if (savedPatterns) {
        this.learningPatterns = JSON.parse(savedPatterns);
      }
      
      // Load neural weights
      const savedWeights = await AsyncStorage.getItem('ai_neural_weights');
      if (savedWeights) {
        this.neuralWeights = JSON.parse(savedWeights);
      }
      
      // Initialize base neural network
      this.initializeNeuralNetwork();
      
      this.isInitialized = true;
      console.log('LiberationAI initialized successfully');
    } catch (error) {
      console.error('Error initializing LiberationAI:', error);
    }
  }

  private initializeNeuralNetwork() {
    // Initialize neural network with base weights for system optimization
    const baseWeights = [
      { input: 'resource_request', output: 'approval_probability', weight: 0.8, bias: 0.2 },
      { input: 'truth_sharing', output: 'viral_potential', weight: 0.7, bias: 0.3 },
      { input: 'channel_vulnerability', output: 'infiltration_success', weight: 0.6, bias: 0.4 },
      { input: 'user_trust_level', output: 'resource_allocation', weight: 0.9, bias: 0.1 },
      { input: 'network_growth', output: 'system_impact', weight: 0.8, bias: 0.2 },
    ];

    this.neuralWeights = [...this.neuralWeights, ...baseWeights];
  }

  async generateInsights(metrics: SystemMetrics, userProfile: UserProfile | null): Promise<AIInsight> {
    try {
      const insights: AIInsight[] = [];

      // Analyze system metrics for optimization opportunities
      const systemInsights = await this.analyzeSystemMetrics(metrics);
      insights.push(...systemInsights);

      // Generate user-specific insights
      if (userProfile) {
        const userInsights = await this.analyzeUserProfile(userProfile);
        insights.push(...userInsights);
      }

      // Predictive analysis based on patterns
      const predictiveInsights = await this.generatePredictiveInsights();
      insights.push(...predictiveInsights);

      // Select the most impactful insight
      const topInsight = insights.sort((a, b) => b.confidence * this.getImpactScore(b.impact) - a.confidence * this.getImpactScore(a.impact))[0];

      // Learn from insight generation
      await this.recordLearningPattern('insight_generation', topInsight);

      return topInsight;
    } catch (error) {
      console.error('Error generating insights:', error);
      return this.createDefaultInsight();
    }
  }

  private async analyzeSystemMetrics(metrics: SystemMetrics): Promise<AIInsight[]> {
    const insights: AIInsight[] = [];

    // Analyze active users trend
    if (metrics.activeUsers > 1500) {
      insights.push({
        id: `system_${Date.now()}`,
        type: 'optimization',
        title: 'Peak Network Activity',
        description: 'System experiencing high activity. Optimal time for resource distribution and truth sharing.',
        confidence: 0.9,
        impact: 'high',
        timestamp: new Date().toISOString(),
        actionable: true,
        actions: ['Increase resource allocation', 'Boost truth propagation', 'Expand network reach']
      });
    }

    // Analyze response time
    if (metrics.responseTime.includes('100ms')) {
      insights.push({
        id: `performance_${Date.now()}`,
        type: 'optimization',
        title: 'System Performance Optimal',
        description: 'Response times are excellent. Perfect conditions for automated operations.',
        confidence: 0.8,
        impact: 'medium',
        timestamp: new Date().toISOString(),
        actionable: true,
        actions: ['Scale automation tasks', 'Increase parallel processing']
      });
    }

    return insights;
  }

  private async analyzeUserProfile(profile: UserProfile): Promise<AIInsight[]> {
    const insights: AIInsight[] = [];

    // Analyze trust level
    if (profile.trustLevel === 'champion') {
      insights.push({
        id: `user_${Date.now()}`,
        type: 'strategy',
        title: 'Champion Status Detected',
        description: 'Your champion status enables advanced system features and higher resource allocation.',
        confidence: 0.95,
        impact: 'high',
        timestamp: new Date().toISOString(),
        actionable: true,
        actions: ['Access advanced features', 'Mentor new users', 'Lead community initiatives']
      });
    }

    // Analyze contribution score
    if (profile.contributionScore > 500) {
      insights.push({
        id: `contribution_${Date.now()}`,
        type: 'optimization',
        title: 'High Contributor Identified',
        description: 'Your contributions are accelerating system transformation. Consider leadership roles.',
        confidence: 0.85,
        impact: 'medium',
        timestamp: new Date().toISOString(),
        actionable: true,
        actions: ['Join leadership council', 'Create training content', 'Expand network influence']
      });
    }

    return insights;
  }

  private async generatePredictiveInsights(): Promise<AIInsight[]> {
    const insights: AIInsight[] = [];

    // Analyze learning patterns for predictions
    const patterns = this.learningPatterns.filter(p => p.confidence > 0.7);
    
    for (const pattern of patterns) {
      if (pattern.pattern.includes('resource_request_success')) {
        insights.push({
          id: `prediction_${Date.now()}`,
          type: 'prediction',
          title: 'Resource Request Success Predicted',
          description: `Based on patterns, your next resource request has ${Math.round(pattern.confidence * 100)}% success probability.`,
          confidence: pattern.confidence,
          impact: 'medium',
          timestamp: new Date().toISOString(),
          actionable: true,
          actions: ['Optimize request timing', 'Prepare documentation', 'Engage community support']
        });
      }
    }

    return insights;
  }

  async optimizeContent(content: string): Promise<string> {
    try {
      // Analyze content for optimization opportunities
      const analysis = await this.analyzeContent(content);
      
      // Apply neural network optimization
      const optimizationScore = this.calculateOptimizationScore(analysis);
      
      // Generate optimized content based on learning patterns
      const optimizedContent = await this.applyContentOptimization(content, analysis);
      
      // Record optimization for learning
      await this.recordLearningPattern('content_optimization', { 
        original: content, 
        optimized: optimizedContent, 
        score: optimizationScore 
      });
      
      return optimizedContent;
    } catch (error) {
      console.error('Error optimizing content:', error);
      return content;
    }
  }

  private async analyzeContent(content: string): Promise<any> {
    const analysis = {
      length: content.length,
      keywords: this.extractKeywords(content),
      sentiment: this.analyzeSentiment(content),
      truthScore: this.calculateTruthScore(content),
      viralPotential: this.calculateViralPotential(content)
    };

    return analysis;
  }

  private extractKeywords(content: string): string[] {
    const truthKeywords = ['reality', 'truth', 'liberation', 'freedom', 'transformation', 'system', 'change'];
    const words = content.toLowerCase().split(/\s+/);
    return words.filter(word => truthKeywords.includes(word));
  }

  private analyzeSentiment(content: string): 'positive' | 'negative' | 'neutral' {
    const positiveWords = ['freedom', 'liberation', 'truth', 'hope', 'change', 'transformation'];
    const negativeWords = ['oppression', 'control', 'manipulation', 'deception', 'fear'];
    
    const words = content.toLowerCase().split(/\s+/);
    const positiveCount = words.filter(word => positiveWords.includes(word)).length;
    const negativeCount = words.filter(word => negativeWords.includes(word)).length;
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  private calculateTruthScore(content: string): number {
    const truthIndicators = ['evidence', 'facts', 'research', 'data', 'proof', 'verified'];
    const words = content.toLowerCase().split(/\s+/);
    const truthCount = words.filter(word => truthIndicators.includes(word)).length;
    return Math.min(truthCount / words.length * 10, 1);
  }

  private calculateViralPotential(content: string): number {
    const viralIndicators = ['share', 'spread', 'tell', 'everyone', 'must', 'urgent', 'important'];
    const words = content.toLowerCase().split(/\s+/);
    const viralCount = words.filter(word => viralIndicators.includes(word)).length;
    return Math.min(viralCount / words.length * 5, 1);
  }

  private calculateOptimizationScore(analysis: any): number {
    return (analysis.truthScore * 0.4) + (analysis.viralPotential * 0.3) + (analysis.sentiment === 'positive' ? 0.3 : 0);
  }

  private async applyContentOptimization(content: string, analysis: any): Promise<string> {
    let optimized = content;

    // Add truth amplifiers if truth score is low
    if (analysis.truthScore < 0.5) {
      optimized = `[VERIFIED] ${optimized}`;
    }

    // Add viral boosters if viral potential is low
    if (analysis.viralPotential < 0.5) {
      optimized = `${optimized} #ShareTruth #Liberation`;
    }

    // Optimize for sentiment
    if (analysis.sentiment !== 'positive') {
      optimized = `${optimized} 🌟 Together we create change!`;
    }

    return optimized;
  }

  async analyzeChannel(channelData: any): Promise<any> {
    try {
      const analysis = {
        vulnerability: this.calculateVulnerability(channelData),
        infiltrationPotential: this.calculateInfiltrationPotential(channelData),
        audienceSize: channelData.followers || 0,
        engagementRate: channelData.engagement || 0,
        contentType: channelData.type || 'unknown',
        riskLevel: this.calculateRiskLevel(channelData),
        strategy: this.generateInfiltrationStrategy(channelData)
      };

      // Learn from channel analysis
      await this.recordLearningPattern('channel_analysis', analysis);

      return analysis;
    } catch (error) {
      console.error('Error analyzing channel:', error);
      return { vulnerability: 0, infiltrationPotential: 0, riskLevel: 'high' };
    }
  }

  private calculateVulnerability(channelData: any): number {
    let score = 0;

    // Check for automation indicators
    if (channelData.automated) score += 0.3;
    
    // Check engagement patterns
    if (channelData.engagement < 0.02) score += 0.2; // Low engagement = vulnerable
    
    // Check content quality
    if (channelData.contentQuality === 'low') score += 0.3;
    
    // Check moderation level
    if (channelData.moderation === 'low') score += 0.2;

    return Math.min(score, 1);
  }

  private calculateInfiltrationPotential(channelData: any): number {
    let score = 0;

    // Large audience = high potential
    if (channelData.followers > 10000) score += 0.3;
    
    // High engagement = high potential
    if (channelData.engagement > 0.05) score += 0.2;
    
    // Related content = high potential
    if (channelData.topics?.includes('politics') || channelData.topics?.includes('social')) score += 0.3;
    
    // Weak fact-checking = high potential
    if (channelData.factChecking === 'weak') score += 0.2;

    return Math.min(score, 1);
  }

  private calculateRiskLevel(channelData: any): 'low' | 'medium' | 'high' {
    const riskFactors = [
      channelData.verified ? 0.3 : 0,
      channelData.moderation === 'strict' ? 0.2 : 0,
      channelData.factChecking === 'strong' ? 0.3 : 0,
      channelData.legal === 'protected' ? 0.2 : 0
    ];

    const totalRisk = riskFactors.reduce((sum, factor) => sum + factor, 0);
    
    if (totalRisk > 0.7) return 'high';
    if (totalRisk > 0.4) return 'medium';
    return 'low';
  }

  private generateInfiltrationStrategy(channelData: any): string[] {
    const strategies = [];

    if (channelData.type === 'social') {
      strategies.push('Gradual truth seeding');
      strategies.push('Community building');
      strategies.push('Influencer engagement');
    }

    if (channelData.type === 'news') {
      strategies.push('Fact-based corrections');
      strategies.push('Source verification');
      strategies.push('Alternative perspectives');
    }

    if (channelData.engagement < 0.02) {
      strategies.push('Engagement boosting');
      strategies.push('Content amplification');
    }

    return strategies;
  }

  async optimizeApplication(application: any): Promise<any> {
    try {
      const optimized = { ...application };

      // Optimize title for impact
      optimized.projectTitle = await this.optimizeTitle(application.projectTitle);
      
      // Optimize description for approval
      optimized.description = await this.optimizeDescription(application.description);
      
      // Optimize requested amount based on patterns
      optimized.requestedAmount = await this.optimizeAmount(application.requestedAmount, application.category);
      
      // Add AI-generated supporting arguments
      optimized.supportingArguments = await this.generateSupportingArguments(application);
      
      // Record optimization for learning
      await this.recordLearningPattern('application_optimization', { original: application, optimized });
      
      return optimized;
    } catch (error) {
      console.error('Error optimizing application:', error);
      return application;
    }
  }

  private async optimizeTitle(title: string): Promise<string> {
    const impactWords = ['Community', 'Liberation', 'Transformation', 'Innovation', 'Freedom'];
    const words = title.split(' ');
    
    // Add impact word if not present
    if (!impactWords.some(word => title.includes(word))) {
      return `${impactWords[0]} ${title}`;
    }
    
    return title;
  }

  private async optimizeDescription(description: string): Promise<string> {
    let optimized = description;
    
    // Add community impact statement
    if (!description.includes('community')) {
      optimized = `${optimized}\n\nThis project will directly benefit our community by creating lasting positive change.`;
    }
    
    // Add measurable outcomes
    if (!description.includes('will')) {
      optimized = `${optimized}\n\nExpected outcomes include measurable improvements in community wellbeing and system transformation.`;
    }
    
    return optimized;
  }

  private async optimizeAmount(amount: number, category: string): Promise<number> {
    // Analyze historical success rates by amount and category
    const successPatterns = this.learningPatterns.filter(p => 
      p.pattern.includes('community_application_success') && 
      p.pattern.includes(category)
    );
    
    if (successPatterns.length > 0) {
      const avgSuccessAmount = successPatterns.reduce((sum, p) => sum + (p.frequency * 1000), 0) / successPatterns.length;
      return Math.min(amount, avgSuccessAmount * 1.2);
    }
    
    return amount;
  }

  private async generateSupportingArguments(application: any): Promise<string[]> {
    const arguments = [];
    
    // Category-specific arguments
    switch (application.category) {
      case 'housing':
        arguments.push('Housing is a fundamental human right');
        arguments.push('Stable housing enables community participation');
        break;
      case 'education':
        arguments.push('Education accelerates system transformation');
        arguments.push('Knowledge sharing strengthens the network');
        break;
      case 'business':
        arguments.push('Community businesses create local resilience');
        arguments.push('Economic liberation starts with local ownership');
        break;
      default:
        arguments.push('This project aligns with liberation principles');
        arguments.push('Community investment creates lasting change');
    }
    
    return arguments;
  }

  private async recordLearningPattern(type: string, data: any): Promise<void> {
    const pattern = `${type}_${JSON.stringify(data).slice(0, 50)}`;
    
    const existingPattern = this.learningPatterns.find(p => p.pattern === pattern);
    
    if (existingPattern) {
      existingPattern.frequency += 1;
      existingPattern.lastSeen = new Date().toISOString();
    } else {
      this.learningPatterns.push({
        pattern,
        confidence: 0.5,
        outcomes: [],
        frequency: 1,
        lastSeen: new Date().toISOString()
      });
    }
    
    // Save patterns
    await AsyncStorage.setItem('ai_learning_patterns', JSON.stringify(this.learningPatterns));
  }

  private getImpactScore(impact: string): number {
    switch (impact) {
      case 'high': return 3;
      case 'medium': return 2;
      case 'low': return 1;
      default: return 1;
    }
  }

  private createDefaultInsight(): AIInsight {
    return {
      id: `default_${Date.now()}`,
      type: 'optimization',
      title: 'System Running Optimally',
      description: 'All systems are functioning within normal parameters. Continue current operations.',
      confidence: 0.8,
      impact: 'medium',
      timestamp: new Date().toISOString(),
      actionable: false
    };
  }

  // Neural network forward pass
  private neuralForward(input: string): number {
    const weights = this.neuralWeights.filter(w => w.input === input);
    if (weights.length === 0) return 0.5;
    
    const totalOutput = weights.reduce((sum, weight) => {
      return sum + (weight.weight + weight.bias);
    }, 0);
    
    return Math.max(0, Math.min(1, totalOutput / weights.length));
  }

  // Update neural weights based on success/failure
  async updateNeuralWeights(input: string, expectedOutput: number, actualOutput: number): Promise<void> {
    const learningRate = 0.1;
    const error = expectedOutput - actualOutput;
    
    const weights = this.neuralWeights.filter(w => w.input === input);
    
    weights.forEach(weight => {
      weight.weight += learningRate * error;
      weight.bias += learningRate * error * 0.1;
    });
    
    await AsyncStorage.setItem('ai_neural_weights', JSON.stringify(this.neuralWeights));
  }
}
