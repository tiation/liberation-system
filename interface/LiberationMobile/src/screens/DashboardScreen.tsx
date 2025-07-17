import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LiberationTheme } from '../theme/colors';
import { useLiberationContext } from '../contexts/LiberationContext';

export const DashboardScreen: React.FC = () => {
  const { metrics, isConnected, userProfile } = useLiberationContext();

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={LiberationTheme.gradients.background}
        style={styles.backgroundGradient}
      >
        <ScrollView style={styles.scrollView}>
          <View style={styles.header}>
            <Text style={styles.title}>Liberation System</Text>
            <Text style={styles.subtitle}>Dashboard</Text>
          </View>

          <View style={styles.statusCard}>
            <View style={styles.statusRow}>
              <View style={[styles.statusDot, { backgroundColor: isConnected ? LiberationTheme.success : LiberationTheme.error }]} />
              <Text style={styles.statusText}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </Text>
            </View>
          </View>

          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Active Users</Text>
              <Text style={styles.metricValue}>{metrics.activeUsers}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Response Time</Text>
              <Text style={styles.metricValue}>{metrics.responseTime}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>System Uptime</Text>
              <Text style={styles.metricValue}>{metrics.systemUptime}</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Network Nodes</Text>
              <Text style={styles.metricValue}>{metrics.networkNodes}</Text>
            </View>
          </View>

          <View style={styles.actionCard}>
            <Text style={styles.actionTitle}>Quick Actions</Text>
            <Text style={styles.actionSubtitle}>System transformation in progress...</Text>
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
  statusCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.md,
    borderRadius: LiberationTheme.borderRadius.lg,
    marginBottom: LiberationTheme.spacing.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: LiberationTheme.spacing.sm,
  },
  statusText: {
    color: LiberationTheme.text,
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: '500',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: LiberationTheme.spacing.lg,
  },
  metricCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.md,
    borderRadius: LiberationTheme.borderRadius.lg,
    width: '48%',
    marginBottom: LiberationTheme.spacing.md,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
  },
  metricLabel: {
    color: LiberationTheme.textSecondary,
    fontSize: LiberationTheme.fontSize.sm,
    marginBottom: LiberationTheme.spacing.xs,
  },
  metricValue: {
    color: LiberationTheme.primary,
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
  },
  actionCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.border,
    alignItems: 'center',
  },
  actionTitle: {
    color: LiberationTheme.text,
    fontSize: LiberationTheme.fontSize.xl,
    fontWeight: 'bold',
    marginBottom: LiberationTheme.spacing.sm,
  },
  actionSubtitle: {
    color: LiberationTheme.textSecondary,
    fontSize: LiberationTheme.fontSize.base,
    textAlign: 'center',
  },
});
