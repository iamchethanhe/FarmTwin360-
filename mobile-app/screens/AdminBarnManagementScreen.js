import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert } from 'react-native';
import { adminService } from '../services/api';

export default function AdminBarnManagementScreen() {
  const [barns, setBarns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { fetchBarns(); }, []);

  const fetchBarns = async () => {
    try {
      const data = await adminService.getAllBarns();
      setBarns(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load barns');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) return (<View style={styles.loadingContainer}><ActivityIndicator size="large" color="#4CAF50" /></View>);

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchBarns(); }} />}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Barn Management</Text>
        <Text style={styles.headerSubtitle}>Total Barns: {barns.length}</Text>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>All Barns</Text>
        {barns.map((barn) => (
          <View key={barn.id} style={styles.card}>
            <Text style={styles.name}>{barn.name}</Text>
            <Text style={styles.location}>{barn.location}</Text>
            <Text style={styles.type}>{barn.animal_type}</Text>
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
  name: { fontSize: 16, fontWeight: 'bold', color: '#1B5E20' },
  location: { fontSize: 13, color: '#2196F3', marginTop: 4 },
  type: { fontSize: 12, color: '#757575', marginTop: 4 }
});
