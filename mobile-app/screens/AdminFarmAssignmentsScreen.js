import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { adminService } from '../services/api';

export default function AdminFarmAssignmentsScreen() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const data = await adminService.getFarmAssignments();
      setAssignments(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load assignments');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (<View style={styles.loadingContainer}><ActivityIndicator size="large" color="#4CAF50" /></View>);
  }

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchAssignments(); }} />}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Farm Assignments</Text>
        <Text style={styles.headerSubtitle}>Total: {assignments.length}</Text>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Active Assignments</Text>
        {assignments.map((a) => (
          <View key={a.id} style={styles.card}>
            <Text style={styles.title}>{a.user_name}</Text>
            <Text style={styles.subtitle}>{a.farm_name}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F1F8E9' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F1F8E9' },
  header: { backgroundColor: '#F44336', padding: 20, paddingTop: 30 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#fff' },
  headerSubtitle: { fontSize: 14, color: 'rgba(255, 255, 255, 0.8)', marginTop: 5 },
  section: { paddingHorizontal: 15, paddingVertical: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1B5E20', marginBottom: 15 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 15, marginBottom: 10 },
  title: { fontSize: 16, fontWeight: 'bold', color: '#1B5E20' },
  subtitle: { fontSize: 13, color: '#2196F3', marginTop: 4 }
});
