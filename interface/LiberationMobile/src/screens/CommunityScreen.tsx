import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LiberationTheme } from '../theme/colors';
import { useLiberationContext } from '../contexts/LiberationContext';

export const CommunityScreen: React.FC = () => {
  const { joinCommunity, communityMembers, isLoading } = useLiberationContext();

  const handleJoinCommunity = async () => {
    await joinCommunity();
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={LiberationTheme.gradients.background}
        style={styles.backgroundGradient}
      >
        <ScrollView style={styles.scrollView}>
          <View style={styles.header}>
            <Text style={styles.title}>Community</Text>
            <Text style={styles.subtitle}>Connect with fellow liberators</Text>
          </View>

          <View style={styles.memberCard}>
            <Text style={styles.memberCount}>
              {communityMembers.toLocaleString()} members
            </Text>
            <Text style={styles.memberDescription}>
              Active liberation network
            </Text>
            <TouchableOpacity 
              style={styles.joinButton}
              onPress={handleJoinCommunity}
              disabled={isLoading}
            >
              <Text style={styles.joinButtonText}>
                {isLoading ? 'Joining...' : 'Join Community'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.featuresCard}>
            <Text style={styles.featuresTitle}>Community Features</Text>
            <View style={styles.featuresList}>
              <Text style={styles.featureItem}>• Secure messaging</Text>
              <Text style={styles.featureItem}>• Resource sharing</Text>
              <Text style={styles.featureItem}>• Truth verification</Text>
              <Text style={styles.featureItem}>• Collaborative projects</Text>
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
    padding: LiberationTheme.spacing.md,
  },
  header: {
    alignItems: 'center',
    marginBottom: LiberationTheme.spacing.xl,
    paddingTop: LiberationTheme.spacing.xl,
  },
  title: {
    fontSize: LiberationTheme.fontSize.xxxl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: LiberationTheme.fontSize.lg,
    color: LiberationTheme.textSecondary,
    textAlign: 'center',
    marginTop: LiberationTheme.spacing.sm,
  },
  memberCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    marginBottom: LiberationTheme.spacing.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.accent,
    alignItems: 'center',
  },
  memberCount: {
    fontSize: LiberationTheme.fontSize.xxxl,
    fontWeight: 'bold',
    color: LiberationTheme.accent,
    marginBottom: LiberationTheme.spacing.sm,
  },
  memberDescription: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    marginBottom: LiberationTheme.spacing.lg,
  },
  joinButton: {
    backgroundColor: LiberationTheme.accent,
    paddingVertical: LiberationTheme.spacing.md,
    paddingHorizontal: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.md,
    alignItems: 'center',
  },
  joinButtonText: {
    color: LiberationTheme.background,
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: 'bold',
  },
  featuresCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  featuresTitle: {
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    marginBottom: LiberationTheme.spacing.md,
  },
  featuresList: {
    paddingLeft: LiberationTheme.spacing.md,
  },
  featureItem: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    marginBottom: LiberationTheme.spacing.sm,
  },
});
