import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Share,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LiberationTheme, createNeonGlow } from '../theme/colors';
import { gitHubPagesService } from '../services/GitHubPagesService';

// Mock icons - replace with your preferred icon library
const Icon = ({ name, size = 24, color = LiberationTheme.text }: { name: string; size?: number; color?: string }) => (
  <View style={{ width: size, height: size, backgroundColor: color, borderRadius: size / 2 }} />
);

interface QuickLink {
  title: string;
  url: string;
  description: string;
  icon: string;
}

export const GitHubPagesScreen: React.FC = () => {
  const [quickLinks, setQuickLinks] = useState<QuickLink[]>([]);
  const [latestRelease, setLatestRelease] = useState<any>(null);
  const [siteStatus, setSiteStatus] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    initializeGitHubPages();
  }, []);

  const initializeGitHubPages = async () => {
    try {
      setLoading(true);
      
      // Initialize GitHub Pages service
      await gitHubPagesService.initialize();
      
      // Load quick links
      const links = await gitHubPagesService.getQuickLinks();
      setQuickLinks(links);
      
      // Check site status
      const status = await gitHubPagesService.checkSiteStatus();
      setSiteStatus(status);
      
      // Sync with GitHub to get latest release
      await gitHubPagesService.syncWithGitHub();
      const release = await gitHubPagesService.getLatestRelease();
      setLatestRelease(release);
      
    } catch (error) {
      console.error('Error initializing GitHub Pages:', error);
      Alert.alert('Error', 'Failed to load GitHub Pages information');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await initializeGitHubPages();
    setRefreshing(false);
  };

  const handleOpenLink = async (type: string) => {
    try {
      let success = false;
      
      switch (type) {
        case 'main_site':
          success = await gitHubPagesService.openMainSite();
          break;
        case 'documentation':
          success = await gitHubPagesService.openDocumentation();
          break;
        case 'wiki':
          success = await gitHubPagesService.openWiki();
          break;
        case 'repository':
          success = await gitHubPagesService.openRepository();
          break;
        case 'issues':
          success = await gitHubPagesService.openIssues();
          break;
        case 'releases':
          success = await gitHubPagesService.openReleases();
          break;
        default:
          Alert.alert('Error', 'Unknown link type');
          return;
      }
      
      if (!success) {
        Alert.alert('Error', 'Unable to open link. Please check your internet connection.');
      }
    } catch (error) {
      console.error('Error opening link:', error);
      Alert.alert('Error', 'Failed to open link');
    }
  };

  const handleShareLink = async (type: string) => {
    try {
      const url = await gitHubPagesService.sharePageUrl(type);
      await Share.share({
        message: `Check out the Liberation System: ${url}`,
        url,
      });
    } catch (error) {
      console.error('Error sharing link:', error);
      Alert.alert('Error', 'Failed to share link');
    }
  };

  const renderQuickLink = (link: QuickLink, index: number) => (
    <TouchableOpacity
      key={index}
      style={styles.linkCard}
      onPress={() => handleOpenLink(getLinkType(link.title))}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={LiberationTheme.gradients.primary}
        style={styles.linkGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.linkContent}>
          <View style={styles.linkHeader}>
            <Icon name={link.icon} size={24} color={LiberationTheme.text} />
            <Text style={styles.linkTitle}>{link.title}</Text>
          </View>
          <Text style={styles.linkDescription}>{link.description}</Text>
          <View style={styles.linkActions}>
            <TouchableOpacity
              style={styles.shareButton}
              onPress={() => handleShareLink(getLinkType(link.title))}
            >
              <Icon name="share" size={16} color={LiberationTheme.primary} />
              <Text style={styles.shareButtonText}>Share</Text>
            </TouchableOpacity>
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const getLinkType = (title: string): string => {
    switch (title) {
      case 'Main Site': return 'main_site';
      case 'Documentation': return 'documentation';
      case 'Wiki': return 'wiki';
      case 'Repository': return 'repository';
      case 'Issues': return 'issues';
      case 'Releases': return 'releases';
      default: return 'main_site';
    }
  };

  const renderSiteStatus = () => (
    <View style={styles.statusCard}>
      <View style={styles.statusHeader}>
        <Icon name="activity" size={20} color={LiberationTheme.primary} />
        <Text style={styles.statusTitle}>Site Status</Text>
      </View>
      <View style={styles.statusContent}>
        <View style={styles.statusRow}>
          <View style={[styles.statusIndicator, { backgroundColor: siteStatus ? LiberationTheme.success : LiberationTheme.error }]} />
          <Text style={styles.statusText}>
            {siteStatus ? 'Online' : 'Offline'}
          </Text>
        </View>
        <Text style={styles.statusUrl}>tiation.github.io/liberation-system</Text>
      </View>
    </View>
  );

  const renderLatestRelease = () => {
    if (!latestRelease) return null;

    return (
      <View style={styles.releaseCard}>
        <View style={styles.releaseHeader}>
          <Icon name="download" size={20} color={LiberationTheme.accent} />
          <Text style={styles.releaseTitle}>Latest Release</Text>
        </View>
        <View style={styles.releaseContent}>
          <Text style={styles.releaseVersion}>{latestRelease.version}</Text>
          <Text style={styles.releaseName}>{latestRelease.title}</Text>
          <Text style={styles.releaseDescription} numberOfLines={3}>
            {latestRelease.description}
          </Text>
          <TouchableOpacity
            style={styles.releaseButton}
            onPress={() => handleOpenLink('releases')}
          >
            <Text style={styles.releaseButtonText}>View Release</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={LiberationTheme.primary} />
        <Text style={styles.loadingText}>Loading GitHub Pages...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={LiberationTheme.gradients.background}
        style={styles.backgroundGradient}
      >
        <ScrollView
          style={styles.scrollView}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={LiberationTheme.primary}
            />
          }
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerIcon}>
              <Icon name="github" size={32} color={LiberationTheme.primary} />
            </View>
            <Text style={styles.headerTitle}>GitHub Pages</Text>
            <Text style={styles.headerSubtitle}>
              Access the Liberation System web interface and documentation
            </Text>
          </View>

          {/* Site Status */}
          {renderSiteStatus()}

          {/* Latest Release */}
          {renderLatestRelease()}

          {/* Quick Links */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Links</Text>
            <View style={styles.linksContainer}>
              {quickLinks.map((link, index) => renderQuickLink(link, index))}
            </View>
          </View>

          {/* Additional Features */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Features</Text>
            <View style={styles.featuresContainer}>
              <View style={styles.featureCard}>
                <Icon name="sync" size={20} color={LiberationTheme.success} />
                <Text style={styles.featureTitle}>Auto-Sync</Text>
                <Text style={styles.featureDescription}>
                  Automatically syncs with GitHub for latest updates
                </Text>
              </View>
              <View style={styles.featureCard}>
                <Icon name="offline" size={20} color={LiberationTheme.info} />
                <Text style={styles.featureTitle}>Offline Support</Text>
                <Text style={styles.featureDescription}>
                  Access cached content when offline
                </Text>
              </View>
              <View style={styles.featureCard}>
                <Icon name="link" size={20} color={LiberationTheme.accent} />
                <Text style={styles.featureTitle}>Deep Links</Text>
                <Text style={styles.featureDescription}>
                  Direct links to specific documentation sections
                </Text>
              </View>
            </View>
          </View>
        </ScrollView>
      </LinearGradient>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LiberationTheme.background,
  },
  backgroundGradient: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: LiberationTheme.background,
  },
  loadingText: {
    color: LiberationTheme.textSecondary,
    fontSize: LiberationTheme.fontSize.base,
    marginTop: LiberationTheme.spacing.md,
  },
  header: {
    padding: LiberationTheme.spacing.lg,
    alignItems: 'center',
  },
  headerIcon: {
    width: 64,
    height: 64,
    backgroundColor: LiberationTheme.surface,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.md,
    ...createNeonGlow(LiberationTheme.primary, 0.3),
  },
  headerTitle: {
    fontSize: LiberationTheme.fontSize.xxl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    textAlign: 'center',
    marginBottom: LiberationTheme.spacing.sm,
  },
  headerSubtitle: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  statusCard: {
    margin: LiberationTheme.spacing.md,
    padding: LiberationTheme.spacing.md,
    backgroundColor: LiberationTheme.surface,
    borderRadius: LiberationTheme.borderRadius.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.sm,
  },
  statusTitle: {
    fontSize: LiberationTheme.fontSize.lg,
    fontWeight: '600',
    color: LiberationTheme.text,
    marginLeft: LiberationTheme.spacing.sm,
  },
  statusContent: {
    marginLeft: LiberationTheme.spacing.xl,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.xs,
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: LiberationTheme.spacing.sm,
  },
  statusText: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.text,
    fontWeight: '500',
  },
  statusUrl: {
    fontSize: LiberationTheme.fontSize.sm,
    color: LiberationTheme.textMuted,
    fontFamily: 'monospace',
  },
  releaseCard: {
    margin: LiberationTheme.spacing.md,
    padding: LiberationTheme.spacing.md,
    backgroundColor: LiberationTheme.surface,
    borderRadius: LiberationTheme.borderRadius.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  releaseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.sm,
  },
  releaseTitle: {
    fontSize: LiberationTheme.fontSize.lg,
    fontWeight: '600',
    color: LiberationTheme.text,
    marginLeft: LiberationTheme.spacing.sm,
  },
  releaseContent: {
    marginLeft: LiberationTheme.spacing.xl,
  },
  releaseVersion: {
    fontSize: LiberationTheme.fontSize.lg,
    fontWeight: 'bold',
    color: LiberationTheme.accent,
    marginBottom: LiberationTheme.spacing.xs,
  },
  releaseName: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.text,
    fontWeight: '500',
    marginBottom: LiberationTheme.spacing.sm,
  },
  releaseDescription: {
    fontSize: LiberationTheme.fontSize.sm,
    color: LiberationTheme.textSecondary,
    lineHeight: 18,
    marginBottom: LiberationTheme.spacing.md,
  },
  releaseButton: {
    backgroundColor: LiberationTheme.accent,
    paddingHorizontal: LiberationTheme.spacing.md,
    paddingVertical: LiberationTheme.spacing.sm,
    borderRadius: LiberationTheme.borderRadius.sm,
    alignSelf: 'flex-start',
  },
  releaseButtonText: {
    color: LiberationTheme.background,
    fontSize: LiberationTheme.fontSize.sm,
    fontWeight: '600',
  },
  section: {
    margin: LiberationTheme.spacing.md,
  },
  sectionTitle: {
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    marginBottom: LiberationTheme.spacing.md,
  },
  linksContainer: {
    gap: LiberationTheme.spacing.md,
  },
  linkCard: {
    borderRadius: LiberationTheme.borderRadius.lg,
    overflow: 'hidden',
    ...createNeonGlow(LiberationTheme.primary, 0.2),
  },
  linkGradient: {
    padding: 1,
  },
  linkContent: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.md,
    borderRadius: LiberationTheme.borderRadius.lg - 1,
  },
  linkHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.sm,
  },
  linkTitle: {
    fontSize: LiberationTheme.fontSize.lg,
    fontWeight: '600',
    color: LiberationTheme.text,
    marginLeft: LiberationTheme.spacing.sm,
  },
  linkDescription: {
    fontSize: LiberationTheme.fontSize.sm,
    color: LiberationTheme.textSecondary,
    lineHeight: 18,
    marginBottom: LiberationTheme.spacing.md,
  },
  linkActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: LiberationTheme.spacing.sm,
    paddingVertical: LiberationTheme.spacing.xs,
    backgroundColor: LiberationTheme.primary + '20',
    borderRadius: LiberationTheme.borderRadius.sm,
  },
  shareButtonText: {
    color: LiberationTheme.primary,
    fontSize: LiberationTheme.fontSize.sm,
    fontWeight: '500',
    marginLeft: LiberationTheme.spacing.xs,
  },
  featuresContainer: {
    gap: LiberationTheme.spacing.md,
  },
  featureCard: {
    padding: LiberationTheme.spacing.md,
    backgroundColor: LiberationTheme.surface,
    borderRadius: LiberationTheme.borderRadius.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  featureTitle: {
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: '600',
    color: LiberationTheme.text,
    marginTop: LiberationTheme.spacing.sm,
    marginBottom: LiberationTheme.spacing.xs,
  },
  featureDescription: {
    fontSize: LiberationTheme.fontSize.sm,
    color: LiberationTheme.textSecondary,
    lineHeight: 18,
  },
});
