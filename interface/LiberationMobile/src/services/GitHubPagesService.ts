import { Linking } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface GitHubPagesConfig {
  baseUrl: string;
  repositoryUrl: string;
  docsUrl: string;
  wikiUrl: string;
  issuesUrl: string;
  releasesUrl: string;
}

interface PageMetadata {
  title: string;
  description: string;
  lastUpdated: string;
  version: string;
}

export class GitHubPagesService {
  private config: GitHubPagesConfig;
  private pageMetadata: Map<string, PageMetadata> = new Map();

  constructor() {
    this.config = {
      baseUrl: 'https://tiation.github.io/liberation-system',
      repositoryUrl: 'https://github.com/tiation-github/liberation-system',
      docsUrl: 'https://tiation.github.io/liberation-system/docs',
      wikiUrl: 'https://github.com/tiation-github/liberation-system/wiki',
      issuesUrl: 'https://github.com/tiation-github/liberation-system/issues',
      releasesUrl: 'https://github.com/tiation-github/liberation-system/releases'
    };
  }

  async initialize() {
    try {
      // Load cached metadata
      const cachedMetadata = await AsyncStorage.getItem('github_pages_metadata');
      if (cachedMetadata) {
        const metadataArray = JSON.parse(cachedMetadata);
        this.pageMetadata = new Map(metadataArray);
      }

      // Fetch latest page metadata
      await this.fetchPageMetadata();
      
      console.log('GitHubPagesService initialized successfully');
    } catch (error) {
      console.error('Error initializing GitHubPagesService:', error);
    }
  }

  async openMainSite(): Promise<boolean> {
    try {
      const url = this.config.baseUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('main_site');
        return true;
      } else {
        console.warn('Cannot open GitHub Pages site');
        return false;
      }
    } catch (error) {
      console.error('Error opening main site:', error);
      return false;
    }
  }

  async openDocumentation(): Promise<boolean> {
    try {
      const url = this.config.docsUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('documentation');
        return true;
      } else {
        console.warn('Cannot open documentation');
        return false;
      }
    } catch (error) {
      console.error('Error opening documentation:', error);
      return false;
    }
  }

  async openWiki(): Promise<boolean> {
    try {
      const url = this.config.wikiUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('wiki');
        return true;
      } else {
        console.warn('Cannot open wiki');
        return false;
      }
    } catch (error) {
      console.error('Error opening wiki:', error);
      return false;
    }
  }

  async openRepository(): Promise<boolean> {
    try {
      const url = this.config.repositoryUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('repository');
        return true;
      } else {
        console.warn('Cannot open repository');
        return false;
      }
    } catch (error) {
      console.error('Error opening repository:', error);
      return false;
    }
  }

  async openIssues(): Promise<boolean> {
    try {
      const url = this.config.issuesUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('issues');
        return true;
      } else {
        console.warn('Cannot open issues');
        return false;
      }
    } catch (error) {
      console.error('Error opening issues:', error);
      return false;
    }
  }

  async openReleases(): Promise<boolean> {
    try {
      const url = this.config.releasesUrl;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('releases');
        return true;
      } else {
        console.warn('Cannot open releases');
        return false;
      }
    } catch (error) {
      console.error('Error opening releases:', error);
      return false;
    }
  }

  async openCustomPage(path: string): Promise<boolean> {
    try {
      const url = `${this.config.baseUrl}/${path}`;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
        await this.trackPageVisit('custom_page', path);
        return true;
      } else {
        console.warn(`Cannot open custom page: ${path}`);
        return false;
      }
    } catch (error) {
      console.error('Error opening custom page:', error);
      return false;
    }
  }

  async fetchPageMetadata(): Promise<void> {
    try {
      // Simulate fetching metadata from GitHub API
      const pages = [
        {
          path: 'main_site',
          title: 'Liberation System',
          description: 'A minimal system to flip everything on its head. One person, massive impact.',
          lastUpdated: new Date().toISOString(),
          version: '1.0.0'
        },
        {
          path: 'documentation',
          title: 'Documentation',
          description: 'Complete documentation for the Liberation System',
          lastUpdated: new Date().toISOString(),
          version: '1.0.0'
        },
        {
          path: 'wiki',
          title: 'Wiki',
          description: 'Community-driven wiki and knowledge base',
          lastUpdated: new Date().toISOString(),
          version: '1.0.0'
        }
      ];

      pages.forEach(page => {
        this.pageMetadata.set(page.path, {
          title: page.title,
          description: page.description,
          lastUpdated: page.lastUpdated,
          version: page.version
        });
      });

      // Cache metadata
      const metadataArray = Array.from(this.pageMetadata.entries());
      await AsyncStorage.setItem('github_pages_metadata', JSON.stringify(metadataArray));
    } catch (error) {
      console.error('Error fetching page metadata:', error);
    }
  }

  getPageMetadata(path: string): PageMetadata | null {
    return this.pageMetadata.get(path) || null;
  }

  getAllPageMetadata(): Map<string, PageMetadata> {
    return new Map(this.pageMetadata);
  }

  getConfig(): GitHubPagesConfig {
    return { ...this.config };
  }

  async updateConfig(newConfig: Partial<GitHubPagesConfig>): Promise<void> {
    this.config = { ...this.config, ...newConfig };
    await AsyncStorage.setItem('github_pages_config', JSON.stringify(this.config));
  }

  private async trackPageVisit(page: string, additionalData?: string): Promise<void> {
    try {
      const visit = {
        page,
        additionalData,
        timestamp: new Date().toISOString(),
        userAgent: 'LiberationMobile/1.0'
      };

      // Get existing visits
      const existingVisits = await AsyncStorage.getItem('page_visits');
      const visits = existingVisits ? JSON.parse(existingVisits) : [];
      
      visits.push(visit);
      
      // Keep only last 100 visits
      if (visits.length > 100) {
        visits.splice(0, visits.length - 100);
      }
      
      await AsyncStorage.setItem('page_visits', JSON.stringify(visits));
    } catch (error) {
      console.error('Error tracking page visit:', error);
    }
  }

  async getPageVisits(): Promise<any[]> {
    try {
      const visits = await AsyncStorage.getItem('page_visits');
      return visits ? JSON.parse(visits) : [];
    } catch (error) {
      console.error('Error getting page visits:', error);
      return [];
    }
  }

  async checkSiteStatus(): Promise<boolean> {
    try {
      // Simple check to see if the site is reachable
      const response = await fetch(this.config.baseUrl, {
        method: 'HEAD',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      console.error('Error checking site status:', error);
      return false;
    }
  }

  async sharePageUrl(page: string): Promise<string> {
    let url;
    
    switch (page) {
      case 'main_site':
        url = this.config.baseUrl;
        break;
      case 'documentation':
        url = this.config.docsUrl;
        break;
      case 'wiki':
        url = this.config.wikiUrl;
        break;
      case 'repository':
        url = this.config.repositoryUrl;
        break;
      case 'issues':
        url = this.config.issuesUrl;
        break;
      case 'releases':
        url = this.config.releasesUrl;
        break;
      default:
        url = `${this.config.baseUrl}/${page}`;
    }

    return url;
  }

  async getQuickLinks(): Promise<Array<{ title: string; url: string; description: string; icon: string }>> {
    return [
      {
        title: 'Main Site',
        url: this.config.baseUrl,
        description: 'Liberation System homepage',
        icon: 'home'
      },
      {
        title: 'Documentation',
        url: this.config.docsUrl,
        description: 'Complete system documentation',
        icon: 'book'
      },
      {
        title: 'Wiki',
        url: this.config.wikiUrl,
        description: 'Community knowledge base',
        icon: 'file-text'
      },
      {
        title: 'Repository',
        url: this.config.repositoryUrl,
        description: 'Source code and development',
        icon: 'github'
      },
      {
        title: 'Issues',
        url: this.config.issuesUrl,
        description: 'Report bugs and request features',
        icon: 'alert-circle'
      },
      {
        title: 'Releases',
        url: this.config.releasesUrl,
        description: 'Latest releases and updates',
        icon: 'download'
      }
    ];
  }

  async syncWithGitHub(): Promise<boolean> {
    try {
      // Fetch latest release info
      const releaseResponse = await fetch(`${this.config.repositoryUrl.replace('github.com', 'api.github.com/repos')}/releases/latest`);
      
      if (releaseResponse.ok) {
        const release = await releaseResponse.json();
        
        // Update metadata with latest release info
        this.pageMetadata.set('latest_release', {
          title: release.name,
          description: release.body,
          lastUpdated: release.published_at,
          version: release.tag_name
        });
        
        // Save updated metadata
        const metadataArray = Array.from(this.pageMetadata.entries());
        await AsyncStorage.setItem('github_pages_metadata', JSON.stringify(metadataArray));
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error syncing with GitHub:', error);
      return false;
    }
  }

  async getLatestRelease(): Promise<any> {
    const metadata = this.pageMetadata.get('latest_release');
    if (metadata) {
      return {
        version: metadata.version,
        title: metadata.title,
        description: metadata.description,
        publishedAt: metadata.lastUpdated
      };
    }
    return null;
  }
}

export const gitHubPagesService = new GitHubPagesService();
