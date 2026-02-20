import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { dashboardService } from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [user, setUser] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserData();
    fetchDashboardData();
  }, []);

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
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.greeting}>Admin Dashboard</Text>
        <Text style={styles.userName}>{user?.name || 'Administrator'}</Text>
        <Text style={styles.subtitle}>System Overview & Management</Text>
      </View>

      {/* Admin Stats */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 System Overview</Text>
        <View style={styles.statsGrid}>
          <View style={[styles.statCard, { backgroundColor: '#E3F2FD' }]}>
            <Text style={styles.statIcon}>👥</Text>
            <Text style={styles.statValue}>6</Text>
            <Text style={styles.statLabel}>Total Users</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#F3E5F5' }]}>
            <Text style={styles.statIcon}>🌾</Text>
            <Text style={styles.statValue}>{stats?.total_farms || 0}</Text>
            <Text style={styles.statLabel}>Farms</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#E8F5E9' }]}>
            <Text style={styles.statIcon}>🏚️</Text>
            <Text style={styles.statValue}>{stats?.total_barns || 0}</Text>
            <Text style={styles.statLabel}>Barns</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#FFF3E0' }]}>
            <Text style={styles.statIcon}>⚠️</Text>
            <Text style={styles.statValue}>{stats?.unresolved_incidents || 0}</Text>
            <Text style={styles.statLabel}>Active Incidents</Text>
          </View>
        </View>
      </View>

      {/* Quick Admin Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Admin Actions</Text>
        <View style={styles.actionGrid}>
          <TouchableOpacity style={styles.adminActionCard}>
            <Text style={styles.actionIcon}>👤</Text>
            <Text style={styles.actionLabel}>Manage Users</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminActionCard}>
            <Text style={styles.actionIcon}>🏗️</Text>
            <Text style={styles.actionLabel}>Manage Farms</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminActionCard}>
            <Text style={styles.actionIcon}>📋</Text>
            <Text style={styles.actionLabel}>View Reports</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminActionCard}>
            <Text style={styles.actionIcon}>⚙️</Text>
            <Text style={styles.actionLabel}>System Settings</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔔 Recent Notifications</Text>
        <Text style={styles.pullHint}>⬇️ Pull down to refresh</Text>
        {alerts.length > 0 ? (
          alerts.slice(0, 5).map((alert) => (
            <View key={alert.id} style={styles.alertCard}>
              <View style={styles.alertHeader}>
                <Text style={styles.alertType}>{alert.type.replace('_', ' ').toUpperCase()}</Text>
                <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(alert.severity) }]}>
                  <Text style={styles.severityText}>{alert.severity}</Text>
                </View>
              </View>
              <Text style={styles.alertMessage}>{alert.message}</Text>
              <Text style={styles.alertTime}>{new Date(alert.created_at).toLocaleString()}</Text>
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>✅</Text>
            <Text style={styles.emptyText}>All caught up!</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

function getSeverityColor(severity) {
  switch (severity) {
    case 'high': return '#F44336';
    case 'medium': return '#FF9800';
    default: return '#4CAF50';
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  header: {
    backgroundColor: '#F44336',
    padding: 25,
    paddingTop: 50,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  greeting: { fontSize: 14, color: '#FFEBEE' },
  userName: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginTop: 5 },
  subtitle: { fontSize: 14, color: '#FFCDD2', marginTop: 5 },
  section: { padding: 20 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: '#1B5E20', marginBottom: 15 },
  pullHint: { fontSize: 11, color: '#81C784', marginBottom: 10, fontStyle: 'italic' },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  statCard: {
    width: '48%',
    padding: 15,
    borderRadius: 15,
    marginBottom: 15,
    alignItems: 'center',
  },
  statIcon: { fontSize: 32, marginBottom: 5 },
  statValue: { fontSize: 28, fontWeight: 'bold', color: '#1B5E20' },
  statLabel: { fontSize: 12, color: '#2E7D32', marginTop: 5 },
  actionGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  adminActionCard: {
    width: '48%',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 15,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionIcon: { fontSize: 36, marginBottom: 10 },
  actionLabel: { fontSize: 12, fontWeight: '600', color: '#2E7D32', textAlign: 'center' },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  alertHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  alertType: { fontSize: 11, fontWeight: '600', color: '#4CAF50' },
  severityBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  severityText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  alertMessage: { fontSize: 14, color: '#1B5E20', marginBottom: 5 },
  alertTime: { fontSize: 11, color: '#81C784' },
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyIcon: { fontSize: 48, marginBottom: 15 },
  emptyText: { fontSize: 16, fontWeight: '600', color: '#2E7D32' },
});
