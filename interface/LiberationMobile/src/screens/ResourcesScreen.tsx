import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LiberationTheme } from '../theme/colors';
import { useLiberationContext } from '../contexts/LiberationContext';

export const ResourcesScreen: React.FC = () => {
  const { requestResourceFlow, resourceHistory, isLoading } = useLiberationContext();

  const handleResourceRequest = async () => {
    await requestResourceFlow(800);
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={LiberationTheme.gradients.background}
        style={styles.backgroundGradient}
      >
        <ScrollView style={styles.scrollView}>
          <View style={styles.header}>
            <Text style={styles.title}>Resources</Text>
            <Text style={styles.subtitle}>Access your resource flow</Text>
          </View>

          <View style={styles.resourceCard}>
            <Text style={styles.resourceTitle}>Weekly Resource Flow</Text>
            <Text style={styles.resourceAmount}>$800</Text>
            <Text style={styles.resourceDescription}>
              Direct to your account • No verification needed
            </Text>
            <TouchableOpacity 
              style={styles.requestButton}
              onPress={handleResourceRequest}
              disabled={isLoading}
            >
              <Text style={styles.requestButtonText}>
                {isLoading ? 'Processing...' : 'Request Now'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.poolCard}>
            <Text style={styles.poolTitle}>Community Pool</Text>
            <Text style={styles.poolAmount}>$104,000</Text>
            <Text style={styles.poolDescription}>
              For housing, business, creative projects
            </Text>
            <TouchableOpacity style={styles.applyButton}>
              <Text style={styles.applyButtonText}>Apply for Project</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.historySection}>
            <Text style={styles.historyTitle}>Resource History</Text>
            {resourceHistory.length === 0 ? (
              <Text style={styles.noHistory}>No resource history available</Text>
            ) : (
              resourceHistory.map((item, index) => (
                <View key={index} style={styles.historyItem}>
                  <Text style={styles.historyType}>{item.type}</Text>
                  <Text style={styles.historyAmount}>+${item.amount}</Text>
                </View>
              ))
            )}
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
  resourceCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    marginBottom: LiberationTheme.spacing.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.primary,
  },
  resourceTitle: {
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    marginBottom: LiberationTheme.spacing.sm,
  },
  resourceAmount: {
    fontSize: LiberationTheme.fontSize.xxxl,
    fontWeight: 'bold',
    color: LiberationTheme.primary,
    marginBottom: LiberationTheme.spacing.sm,
  },
  resourceDescription: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    marginBottom: LiberationTheme.spacing.lg,
  },
  requestButton: {
    backgroundColor: LiberationTheme.primary,
    paddingVertical: LiberationTheme.spacing.md,
    paddingHorizontal: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.md,
    alignItems: 'center',
  },
  requestButtonText: {
    color: LiberationTheme.background,
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: 'bold',
  },
  poolCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    marginBottom: LiberationTheme.spacing.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.success,
  },
  poolTitle: {
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    marginBottom: LiberationTheme.spacing.sm,
  },
  poolAmount: {
    fontSize: LiberationTheme.fontSize.xxxl,
    fontWeight: 'bold',
    color: LiberationTheme.success,
    marginBottom: LiberationTheme.spacing.sm,
  },
  poolDescription: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    marginBottom: LiberationTheme.spacing.lg,
  },
  applyButton: {
    backgroundColor: LiberationTheme.success,
    paddingVertical: LiberationTheme.spacing.md,
    paddingHorizontal: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.md,
    alignItems: 'center',
  },
  applyButtonText: {
    color: LiberationTheme.background,
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: 'bold',
  },
  historySection: {
    marginTop: LiberationTheme.spacing.lg,
  },
  historyTitle: {
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    color: LiberationTheme.text,
    marginBottom: LiberationTheme.spacing.md,
  },
  noHistory: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  historyItem: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.md,
    borderRadius: LiberationTheme.borderRadius.md,
    marginBottom: LiberationTheme.spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  historyType: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.text,
  },
  historyAmount: {
    fontSize: LiberationTheme.fontSize.base,
    color: LiberationTheme.success,
    fontWeight: 'bold',
  },
});
