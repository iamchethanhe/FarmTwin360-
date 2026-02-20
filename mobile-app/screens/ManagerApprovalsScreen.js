import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import { managerService } from '../services/api';

export default function ManagerApprovalsScreen() {
  const [activeTab, setActiveTab] = useState('checklists');
  const [checklists, setChecklists] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [c, i] = await Promise.all([
        managerService.getPendingChecklists(),
        managerService.getPendingIncidents()
      ]);
      setChecklists(c);
      setIncidents(i);
    } catch (error) {
      Alert.alert('Error', 'Failed to load data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) return (<View style={styles.loadingContainer}><ActivityIndicator size="large" color="#4CAF50" /></View>);

  return (
    <View style={styles.container}>
      <View style={styles.tabBar}>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'checklists' && styles.tabBtnActive]} onPress={() => setActiveTab('checklists')}>
          <Text style={[styles.tabText, activeTab === 'checklists' && styles.tabTextActive]}>Checklists</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'incidents' && styles.tabBtnActive]} onPress={() => setActiveTab('incidents')}>
          <Text style={[styles.tabText, activeTab === 'incidents' && styles.tabTextActive]}>Incidents</Text>
        </TouchableOpacity>
      </View>
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchData(); }} />}>
        {activeTab === 'checklists' ? (
          <View style={styles.section}>
            {checklists.map((c) => (
              <View key={c.id} style={styles.card}>
                <Text style={styles.title}>{c.farm_name}</Text>
                <Text style={styles.subtitle}>{c.worker_name}</Text>
                <TouchableOpacity style={styles.btn}><Text style={styles.btnText}>Approve</Text></TouchableOpacity>
              </View>
            ))}
          </View>
        ) : (
          <View style={styles.section}>
            {incidents.map((i) => (
              <View key={i.id} style={styles.card}>
                <Text style={styles.title}>{i.title}</Text>
                <Text style={styles.subtitle}>{i.farm_name}</Text>
                <TouchableOpacity style={styles.btn}><Text style={styles.btnText}>Approve</Text></TouchableOpacity>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F1F8E9' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F1F8E9' },
  tabBar: { flexDirection: 'row', backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E0E0E0' },
  tabBtn: { flex: 1, paddingVertical: 12, borderBottomWidth: 3, borderBottomColor: 'transparent', alignItems: 'center' },
  tabBtnActive: { borderBottomColor: '#4CAF50' },
  tabText: { fontSize: 12, fontWeight: 'bold', color: '#999' },
  tabTextActive: { color: '#4CAF50' },
  section: { paddingHorizontal: 15, paddingVertical: 15 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 15, marginBottom: 10 },
  title: { fontSize: 15, fontWeight: 'bold', color: '#1B5E20' },
  subtitle: { fontSize: 12, color: '#757575', marginTop: 4 },
  btn: { marginTop: 10, backgroundColor: '#4CAF50', paddingVertical: 8, borderRadius: 6, alignItems: 'center' },
  btnText: { color: '#fff', fontSize: 12, fontWeight: 'bold' }
});
