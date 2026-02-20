import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { dashboardService, managerService, adminService } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function DashboardScreen({ navigation }) {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserData();
    fetchDashboardData();
  }, []);

  // Get role-specific configuration
  const getRoleConfig = () => {
    const role = user?.role || 'worker';
    const configs = {
      admin: {
        color: '#F44336',
        title: 'Admin Dashboard',
        subtitle: 'System Overview & Management',
        showUserManagement: true,
      },
      manager: {
        color: '#2196F3',
        title: 'Manager Dashboard',
        subtitle: 'Team & Operations Management',
        showApprovals: true,
      },
      worker: {
        color: '#4CAF50',
        title: 'Worker Dashboard',
        subtitle: 'Daily Tasks & Reports',
        showTasks: true,
      },
      vet: {
        color: '#9C27B0',
        title: 'Veterinarian Dashboard',
        subtitle: 'Animal Health & Inspections',
        showHealthReports: true,
      },
      visitor: {
        color: '#607D8B',
        title: 'Visitor Dashboard',
        subtitle: 'View-Only Access',
        showLimited: true,
      },
      auditor: {
        color: '#FF9800',
        title: 'Auditor Dashboard',
        subtitle: 'Compliance & Reporting',
        showReports: true,
      },
    };
    return configs[role] || configs.worker;
  };

  const loadUserData = async () => {
    const userData = await AsyncStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  };

  const fetchDashboardData = async () => {
    try {
      const [statsData, alertsData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getAlerts(),
      ]);
      setStats(statsData);
      setAlerts(alertsData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const handleManagerAction = async (action, nav) => {
    try {
      switch (action) {
        case 'reviewChecklists':
          // Fetch pending checklists
          const checklists = await managerService.getPendingChecklists();
          Alert.alert(
            '📋 Review Checklists',
            `Found ${checklists.length} pending checklists.\nNavigating to approval screen...`,
            [{text: 'OK', onPress: () => nav.navigate('Checklist')}]
          );
          break;
        case 'reviewIncidents':
          // Fetch pending incidents
          const incidents = await managerService.getPendingIncidents();
          Alert.alert(
            '⚠️ Review Incidents',
            `Found ${incidents.length} pending incidents.\nNavigating to approval screen...`,
            [{text: 'OK', onPress: () => nav.navigate('Incident')}]
          );
          break;
        default:
          break;
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load data: ' + error.message);
    }
  };

  const handleAdminAction = async (action, nav) => {
    if (user?.role !== 'admin') return;
    try {
      switch (action) {
        case 'manageUsers':
          nav.navigate('AdminManagement');
          break;
        case 'manageFarms':
          nav.navigate('AdminManagement');
          break;
        case 'manageFarmAssignments':
          nav.navigate('AdminManagement');
          break;
        case 'manageBarn':
          nav.navigate('AdminManagement');
          break;
        case 'systemSettings':
          nav.navigate('AdminManagement');
          break;
        case 'viewAnalytics':
          nav.navigate('Analytics');
          break;
        default:
          break;
      }
    } catch (error) {
      Alert.alert('Error', 'Navigation failed: ' + error.message);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return '#F44336';
      case 'medium':
        return '#FF9800';
      default:
        return '#4CAF50';
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      'checklist_submitted': '⏳',
      'incident_reported': '⚠️',
      'checklist_approved': '✅',
      'incident_approved': '✅',
    };
    return <Text style={styles.notificationIcon}>{icons[type] || '🔔'}</Text>;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  const roleConfig = getRoleConfig();

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={[styles.header, { backgroundColor: roleConfig.color }]}>
        <Text style={styles.greeting}>{roleConfig.title}</Text>
        <Text style={styles.userName}>{user?.name || 'User'}</Text>
        <Text style={styles.userRole}>{roleConfig.subtitle}</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.total_farms || 0}</Text>
          <Text style={styles.statLabel}>Farms</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.total_barns || 0}</Text>
          <Text style={styles.statLabel}>Barns</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.total_checklists || 0}</Text>
          <Text style={styles.statLabel}>Checklists</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats?.unresolved_incidents || 0}</Text>
          <Text style={styles.statLabel}>Active Incidents</Text>
        </View>
      </View>

      {/* Role-Specific Features */}
      {roleConfig.showUserManagement && user?.role === 'admin' && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👥 Admin Controls</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('manageUsers', navigation)}
            >
              <Text style={styles.actionIcon}>👤</Text>
              <Text style={styles.actionText}>Manage Users</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('manageFarms', navigation)}
            >
              <Text style={styles.actionIcon}>🃛️</Text>
              <Text style={styles.actionText}>Manage Farms</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('manageFarmAssignments', navigation)}
            >
              <Text style={styles.actionIcon}>🔗</Text>
              <Text style={styles.actionText}>Farm Assignments</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('manageBarn', navigation)}
            >
              <Text style={styles.actionIcon}>📚</Text>
              <Text style={styles.actionText}>Manage Barns</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('systemSettings', navigation)}
            >
              <Text style={styles.actionIcon}>⚙️</Text>
              <Text style={styles.actionText}>System Settings</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, styles.adminButton]}
              onPress={() => handleAdminAction('viewAnalytics', navigation)}
            >
              <Text style={styles.actionIcon}>📊</Text>
              <Text style={styles.actionText}>Analytics</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {roleConfig.showApprovals && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>✅ Approval Queue</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.reviewButton]}
              onPress={() => handleManagerAction('reviewChecklists', navigation)}
            >
              <Text style={styles.actionIcon}>📋</Text>
              <Text style={styles.actionText}>Review Checklists</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, styles.reviewButton]}
              onPress={() => handleManagerAction('reviewIncidents', navigation)}
            >
              <Text style={styles.actionIcon}>⚠️</Text>
              <Text style={styles.actionText}>Review Incidents</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {roleConfig.showHealthReports && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🍽️ Veterinary Tasks</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity style={styles.roleActionButton}>
              <Text style={styles.actionIcon}>💉</Text>
              <Text style={styles.actionText}>Health Inspections</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.roleActionButton}>
              <Text style={styles.actionIcon}>📊</Text>
              <Text style={styles.actionText}>Medical Reports</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {roleConfig.showReports && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Audit & Reports</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity style={styles.roleActionButton}>
              <Text style={styles.actionIcon}>📄</Text>
              <Text style={styles.actionText}>Compliance Reports</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.roleActionButton}>
              <Text style={styles.actionIcon}>📝</Text>
              <Text style={styles.actionText}>Audit Logs</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Worker Quick Actions - Only for workers */}
      {roleConfig.showTasks && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Checklist')}
            >
              <Text style={styles.actionIcon}>✓</Text>
              <Text style={styles.actionText}>New Checklist</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Incident')}
            >
              <Text style={styles.actionIcon}>⚠</Text>
              <Text style={styles.actionText}>Report Incident</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Alerts */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={styles.notificationHeader}>
            <Text style={styles.sectionTitle}>Recent Notifications</Text>
            <Text style={styles.pullToRefreshHint}>⬇️ Pull down to refresh</Text>
          </View>
          {alerts.length > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{alerts.length}</Text>
            </View>
          )}
        </View>
        {alerts.length > 0 ? (
          alerts.slice(0, 5).map((alert) => (
            <View
              key={alert.id}
              style={[
                styles.alertCard,
                { borderLeftColor: getSeverityColor(alert.severity) },
              ]}
            >
              <View style={styles.alertHeader}>
                <View style={styles.alertTypeContainer}>
                  {getNotificationIcon(alert.type)}
                  <Text style={styles.alertType}>{alert.type.replace('_', ' ').toUpperCase()}</Text>
                </View>
                <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(alert.severity) }]}>
                  <Text style={styles.severityText}>{alert.severity}</Text>
                </View>
              </View>
              <Text style={styles.alertMessage}>{alert.message}</Text>
              <Text style={styles.alertTime}>
                {new Date(alert.created_at).toLocaleString()}
              </Text>
            </View>
          ))
        ) : (
          <View style={styles.emptyNotifications}>
            <Text style={styles.emptyIcon}>🔔</Text>
            <Text style={styles.emptyText}>No new notifications</Text>
            <Text style={styles.emptySubtext}>You'll be notified when there are updates</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F1F8E9',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F1F8E9',
  },
  header: {
    backgroundColor: '#4CAF50',
    padding: 25,
    paddingTop: 50,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  greeting: {
    fontSize: 16,
    color: '#E8F5E9',
  },
  userName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 5,
  },
  userRole: {
    fontSize: 14,
    color: '#C8E6C9',
    marginTop: 5,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginTop: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1B5E20',
  },
  statLabel: {
    fontSize: 14,
    color: '#2E7D32',
    marginTop: 5,
  },
  section: {
    padding: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  notificationHeader: {
    flexDirection: 'column',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1B5E20',
  },
  pullToRefreshHint: {
    fontSize: 11,
    color: '#81C784',
    marginTop: 2,
    fontStyle: 'italic',
  },
  badge: {
    backgroundColor: '#F44336',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    textAlign: 'center',
  },
  roleActionButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  reviewButton: {
    backgroundColor: '#E3F2FD',
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  adminButton: {
    backgroundColor: '#FFEBEE',
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertTypeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  notificationIcon: {
    fontSize: 14,
  },
  alertType: {
    fontSize: 11,
    fontWeight: '600',
    color: '#4CAF50',
    textTransform: 'uppercase',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  severityText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  alertMessage: {
    fontSize: 14,
    color: '#1B5E20',
    marginBottom: 5,
    lineHeight: 20,
  },
  alertTime: {
    fontSize: 11,
    color: '#81C784',
    marginTop: 4,
  },
  emptyNotifications: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 15,
    opacity: 0.5,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#81C784',
    textAlign: 'center',
  },
});
