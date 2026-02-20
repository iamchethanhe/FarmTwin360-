import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { adminService } from '../services/api';

export default function AdminSystemStatsScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try {
      const data = await adminService.getSystemStats();
      setStats(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load stats');
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
        <Text style={styles.headerTitle}>System Statistics</Text>
      </View>
      <View style={styles.section}>
        <StatBox label="Total Users" value={stats.total_users || 0} />
        <StatBox label="Total Farms" value={stats.total_farms || 0} />
        <StatBox label="Total Barns" value={stats.total_barns || 0} />
        <StatBox label="Checklists" value={stats.total_checklists || 0} />
        <StatBox label="Incidents" value={stats.total_incidents || 0} />
      </View>
    </ScrollView>
  );
}

function StatBox({ label, value }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F1F8E9' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F1F8E9' },
  header: { backgroundColor: '#F44336', padding: 20, paddingTop: 30 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#fff' },
  section: { paddingHorizontal: 15, paddingVertical: 20 },
  statBox: { backgroundColor: '#fff', borderRadius: 12, padding: 20, marginBottom: 10, alignItems: 'center' },
  statValue: { fontSize: 32, fontWeight: 'bold', color: '#1B5E20' },
  statLabel: { fontSize: 13, color: '#757575', marginTop: 8 }
});
