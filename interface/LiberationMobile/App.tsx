import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { LiberationProvider } from './src/contexts/LiberationContext';
import { DashboardScreen } from './src/screens/DashboardScreen';
import { ResourcesScreen } from './src/screens/ResourcesScreen';
import { TruthNetworkScreen } from './src/screens/TruthNetworkScreen';
import { CommunityScreen } from './src/screens/CommunityScreen';
import { TabBar } from './src/components/TabBar';
import { LiberationTheme } from './src/theme/colors';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <LiberationProvider>
        <NavigationContainer>
          <View style={styles.container}>
            <StatusBar style="light" backgroundColor={LiberationTheme.background} />
            <Tab.Navigator
              tabBar={(props) => <TabBar {...props} />}
              screenOptions={{
                headerShown: false,
              }}
            >
              <Tab.Screen 
                name="Dashboard" 
                component={DashboardScreen}
                options={{
                  title: 'Dashboard',
                  tabBarIcon: 'home',
                }}
              />
              <Tab.Screen 
                name="Resources" 
                component={ResourcesScreen}
                options={{
                  title: 'Resources',
                  tabBarIcon: 'wallet',
                }}
              />
              <Tab.Screen 
                name="Truth" 
                component={TruthNetworkScreen}
                options={{
                  title: 'Truth Network',
                  tabBarIcon: 'network',
                }}
              />
              <Tab.Screen 
                name="Community" 
                component={CommunityScreen}
                options={{
                  title: 'Community',
                  tabBarIcon: 'users',
                }}
              />
            </Tab.Navigator>
          </View>
        </NavigationContainer>
      </LiberationProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LiberationTheme.background,
  },
});
});
