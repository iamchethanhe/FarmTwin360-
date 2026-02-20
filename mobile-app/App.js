import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ActivityIndicator, View, Text } from 'react-native';

// Screens
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import ChecklistScreen from './screens/ChecklistScreen';
import IncidentScreen from './screens/IncidentScreen';
import ProfileScreen from './screens/ProfileScreen';

// Admin Screens
import AdminUserManagementScreen from './screens/AdminUserManagementScreen';
import AdminFarmManagementScreen from './screens/AdminFarmManagementScreen';
import AdminFarmAssignmentsScreen from './screens/AdminFarmAssignmentsScreen';
import AdminBarnManagementScreen from './screens/AdminBarnManagementScreen';
import AdminSystemStatsScreen from './screens/AdminSystemStatsScreen';

// Manager Screens
import ManagerApprovalsScreen from './screens/ManagerApprovalsScreen';

// Analytics Screen
import AnalyticsScreen from './screens/AnalyticsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Admin Management Stack
function AdminManagementStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#F44336' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="AdminUserManagement"
        component={AdminUserManagementScreen}
        options={{ title: 'User Management' }}
      />
      <Stack.Screen
        name="AdminFarmManagement"
        component={AdminFarmManagementScreen}
        options={{ title: 'Farm Management' }}
      />
      <Stack.Screen
        name="AdminFarmAssignments"
        component={AdminFarmAssignmentsScreen}
        options={{ title: 'Farm Assignments' }}
      />
      <Stack.Screen
        name="AdminBarnManagement"
        component={AdminBarnManagementScreen}
        options={{ title: 'Barn Management' }}
      />
      <Stack.Screen
        name="AdminSystemStats"
        component={AdminSystemStatsScreen}
        options={{ title: 'System Statistics' }}
      />
    </Stack.Navigator>
  );
}

// Manager Approvals Stack
function ManagerApprovalsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#2196F3' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="ManagerApprovals"
        component={ManagerApprovalsScreen}
        options={{ title: 'Approvals' }}
      />
    </Stack.Navigator>
  );
}

// Main Tab Navigator
function MainTabs({ userRole, onLogout }) {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: '#81C784',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 0,
          elevation: 10,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
        },
        headerStyle: {
          backgroundColor: '#4CAF50',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>🏠</Text>,
          headerShown: false,
        }}
      />

      <Tab.Screen
        name="Checklist"
        component={ChecklistScreen}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>✓</Text>,
          title: 'New Checklist',
          tabBarStyle: userRole !== 'worker' ? { display: 'none' } : {},
        }}
      />
      <Tab.Screen
        name="Incident"
        component={IncidentScreen}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>⚠</Text>,
          title: 'Report Incident',
          tabBarStyle: userRole !== 'worker' ? { display: 'none' } : {},
        }}
      />
      <Tab.Screen
        name="AdminManagement"
        component={AdminManagementStack}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>👑</Text>,
          title: 'Admin',
          headerShown: false,
          tabBarStyle: userRole !== 'admin' ? { display: 'none' } : {},
        }}
      />
      <Tab.Screen
        name="ManagerStack"
        component={ManagerApprovalsStack}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>✅</Text>,
          title: 'Approvals',
          headerShown: false,
          tabBarStyle: userRole !== 'manager' ? { display: 'none' } : {},
        }}
      />
      <Tab.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>📊</Text>,
          title: 'Analytics',
          tabBarStyle: !['admin', 'manager', 'vet', 'auditor'].includes(userRole) ? { display: 'none' } : {},
        }}
      />

      <Tab.Screen
        name="Profile"
        options={{
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>👤</Text>,
        }}
      >
        {(props) => <ProfileScreen {...props} onLogout={onLogout} />}
      </Tab.Screen>
    </Tab.Navigator>
  );
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      const user = await AsyncStorage.getItem('user');
      if (token && user) {
        const userData = JSON.parse(user);
        setUserRole(userData.role);
        setIsLoggedIn(true);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshAuthState = async () => {
    const token = await AsyncStorage.getItem('authToken');
    const user = await AsyncStorage.getItem('user');
    if (token && user) {
      const userData = JSON.parse(user);
      setUserRole(userData.role);
      setIsLoggedIn(true);
    }
  };

  const handleLogout = async () => {
    setIsLoggedIn(false);
    setUserRole(null);
  };

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isLoggedIn ? (
          <Stack.Screen name="Login">
            {(props) => <LoginScreen {...props} onLoginSuccess={refreshAuthState} />}
          </Stack.Screen>
        ) : (
          <Stack.Screen name="Main">
            {(props) => (
              <MainTabs {...props} userRole={userRole} onLogout={handleLogout} />
            )}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
