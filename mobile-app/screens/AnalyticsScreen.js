import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { adminService } from '../services/api';

export default function AnalyticsScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try {
      const data = await adminService.getSystemStats();
      setStats(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load analytics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) return (<View style={styles.loadingContainer}><ActivityIndicator size="large" color="#4CAF50" /></View>);
  if (!stats) return (<View style={styles.loadingContainer}><Text>No data</Text></View>);

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchStats(); }} />}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Analytics Dashboard</Text>
      </View>
      <View style={styles.grid}>
        <MetricCard label="Total Users" value={stats.total_users || 0} color="#2196F3" />
        <MetricCard label="Total Farms" value={stats.total_farms || 0} color="#4CAF50" />
        <MetricCard label="Total Barns" value={stats.total_barns || 0} color="#FF9800" />
        <MetricCard label="Checklists" value={stats.total_checklists || 0} color="#9C27B0" />
        <MetricCard label="Incidents" value={stats.total_incidents || 0} color="#F44336" />
        <MetricCard label="Pending Items" value={(stats.pending_checklists || 0) + (stats.pending_incidents || 0)} color="#00BCD4" />
      </View>
    </ScrollView>
  );
}

function MetricCard({ label, value, color }) {
  return (
    <View style={[styles.card, { borderLeftColor: color, borderLeftWidth: 4 }]}>
      <Text style={styles.cardValue}>{value}</Text>
      <Text style={styles.cardLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F1F8E9' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F1F8E9' },
  header: { backgroundColor: '#2196F3', padding: 20, paddingTop: 30 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#fff' },
  grid: { paddingHorizontal: 15, paddingVertical: 20 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 15, marginBottom: 10 },
  cardValue: { fontSize: 28, fontWeight: 'bold', color: '#1B5E20' },
  cardLabel: { fontSize: 12, color: '#757575', marginTop: 6 }
});
