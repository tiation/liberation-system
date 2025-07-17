import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { LiberationTheme } from '../theme/colors';
import { useLiberationContext } from '../contexts/LiberationContext';

export const TruthNetworkScreen: React.FC = () => {
  const { activateTruthNetwork, networkStatus, isLoading } = useLiberationContext();

  const handleActivateNetwork = async () => {
    await activateTruthNetwork();
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={LiberationTheme.gradients.background}
        style={styles.backgroundGradient}
      >
        <ScrollView style={styles.scrollView}>
          <View style={styles.header}>
            <Text style={styles.title}>Truth Network</Text>
            <Text style={styles.subtitle}>Join the network of truth seekers</Text>
          </View>

          <View style={styles.networkCard}>
            <Text style={styles.networkStatus}>
              {networkStatus}
            </Text>
            <TouchableOpacity 
              style={styles.activateButton}
              onPress={handleActivateNetwork}
              disabled={isLoading}
            >
              <Text style={styles.activateButtonText}>
                {isLoading ? 'Activating...' : 'Activate Network'}
              </Text>
            </TouchableOpacity>
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
  networkCard: {
    backgroundColor: LiberationTheme.surface,
    padding: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.lg,
    marginBottom: LiberationTheme.spacing.lg,
    borderWidth: 1,
    borderColor: LiberationTheme.info,
    alignItems: 'center',
  },
  networkStatus: {
    fontSize: LiberationTheme.fontSize.lg,
    color: LiberationTheme.info,
    marginBottom: LiberationTheme.spacing.md,
  },
  activateButton: {
    backgroundColor: LiberationTheme.info,
    paddingVertical: LiberationTheme.spacing.md,
    paddingHorizontal: LiberationTheme.spacing.lg,
    borderRadius: LiberationTheme.borderRadius.md,
    alignItems: 'center',
  },
  activateButtonText: {
    color: LiberationTheme.background,
    fontSize: LiberationTheme.fontSize.base,
    fontWeight: 'bold',
  },
});

