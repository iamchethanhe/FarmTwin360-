import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import { adminService } from '../services/api';

export default function AdminFarmManagementScreen() {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchFarms();
  }, []);

  const fetchFarms = async () => {
    try {
      const data = await adminService.getAllFarms();
      setFarms(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load farms');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchFarms(); }} />}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Farm Management</Text>
        <Text style={styles.headerSubtitle}>Total Farms: {farms.length}</Text>
      </View>
      <TouchableOpacity style={styles.addButton}>
        <Text style={styles.addButtonText}>Add New Farm</Text>
      </TouchableOpacity>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>All Farms</Text>
        {farms.map((farm) => (
          <View key={farm.id} style={styles.card}>
            <Text style={styles.farmName}>{farm.name}</Text>
            <Text style={styles.farmLocation}>{farm.location}</Text>
            <Text style={styles.farmDesc}>{farm.description || 'No description'}</Text>
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
  addButton: { marginHorizontal: 15, marginVertical: 15, backgroundColor: '#4CAF50', paddingVertical: 12, borderRadius: 8, alignItems: 'center' },
  addButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  section: { paddingHorizontal: 15, paddingVertical: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1B5E20', marginBottom: 15 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 15, marginBottom: 10 },
  farmName: { fontSize: 16, fontWeight: 'bold', color: '#1B5E20' },
  farmLocation: { fontSize: 13, color: '#2196F3', marginTop: 4 },
  farmDesc: { fontSize: 12, color: '#757575', marginTop: 6 }
});
