import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import * as Location from 'expo-location';
import { farmService, checklistService } from '../services/api';

export default function ChecklistScreen({ navigation }) {
  const [farms, setFarms] = useState([]);
  const [barns, setBarns] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState('');
  const [selectedBarn, setSelectedBarn] = useState('');
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);

  const [formData, setFormData] = useState({
    hygiene_score: '8',
    mortality_count: '0',
    feed_quality: '8',
    water_quality: '8',
    ventilation_score: '8',
    temperature: '22',
    humidity: '55',
    notes: '',
  });

  useEffect(() => {
    loadFarms();
    getLocation();
  }, []);

  useEffect(() => {
    if (selectedFarm) {
      loadBarns(selectedFarm);
    }
  }, [selectedFarm]);

  const loadFarms = async () => {
    try {
      const farmsData = await farmService.getFarms();
      setFarms(farmsData);
      if (farmsData.length > 0) {
        setSelectedFarm(farmsData[0].id.toString());
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load farms');
    }
  };

  const loadBarns = async (farmId) => {
    try {
      const barnsData = await farmService.getBarns(parseInt(farmId));
      setBarns(barnsData);
      if (barnsData.length > 0) {
        setSelectedBarn(barnsData[0].id.toString());
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load barns');
    }
  };

  const getLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        setLocation(loc.coords);
      }
    } catch (error) {
      console.log('Error getting location:', error);
    }
  };

  const handleSubmit = async () => {
    if (!selectedBarn) {
      Alert.alert('Error', 'Please select a barn');
      return;
    }

    setLoading(true);
    try {
      const data = {
        barn_id: parseInt(selectedBarn),
        hygiene_score: parseInt(formData.hygiene_score),
        mortality_count: parseInt(formData.mortality_count),
        feed_quality: parseInt(formData.feed_quality),
        water_quality: parseInt(formData.water_quality),
        ventilation_score: parseInt(formData.ventilation_score),
        temperature: parseFloat(formData.temperature),
        humidity: parseFloat(formData.humidity),
        notes: formData.notes,
        gps_lat: location?.latitude || null,
        gps_lng: location?.longitude || null,
      };

      await checklistService.createChecklist(data);
      Alert.alert('Success', 'Checklist submitted successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to submit checklist');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Daily Checklist</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Farm</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={selectedFarm}
              onValueChange={setSelectedFarm}
              style={styles.picker}
            >
              {farms.map((farm) => (
                <Picker.Item key={farm.id} label={farm.name} value={farm.id.toString()} />
              ))}
            </Picker>
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Barn</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={selectedBarn}
              onValueChange={setSelectedBarn}
              style={styles.picker}
            >
              {barns.map((barn) => (
                <Picker.Item key={barn.id} label={barn.name} value={barn.id.toString()} />
              ))}
            </Picker>
          </View>
        </View>

        <View style={styles.row}>
          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Hygiene Score (1-10)</Text>
            <TextInput
              style={styles.input}
              value={formData.hygiene_score}
              onChangeText={(text) => setFormData({ ...formData, hygiene_score: text })}
              keyboardType="numeric"
            />
          </View>

          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Mortality Count</Text>
            <TextInput
              style={styles.input}
              value={formData.mortality_count}
              onChangeText={(text) => setFormData({ ...formData, mortality_count: text })}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.row}>
          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Feed Quality (1-10)</Text>
            <TextInput
              style={styles.input}
              value={formData.feed_quality}
              onChangeText={(text) => setFormData({ ...formData, feed_quality: text })}
              keyboardType="numeric"
            />
          </View>

          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Water Quality (1-10)</Text>
            <TextInput
              style={styles.input}
              value={formData.water_quality}
              onChangeText={(text) => setFormData({ ...formData, water_quality: text })}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.row}>
          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Temperature (°C)</Text>
            <TextInput
              style={styles.input}
              value={formData.temperature}
              onChangeText={(text) => setFormData({ ...formData, temperature: text })}
              keyboardType="decimal-pad"
            />
          </View>

          <View style={[styles.inputGroup, styles.halfWidth]}>
            <Text style={styles.label}>Humidity (%)</Text>
            <TextInput
              style={styles.input}
              value={formData.humidity}
              onChangeText={(text) => setFormData({ ...formData, humidity: text })}
              keyboardType="decimal-pad"
            />
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Ventilation Score (1-10)</Text>
          <TextInput
            style={styles.input}
            value={formData.ventilation_score}
            onChangeText={(text) => setFormData({ ...formData, ventilation_score: text })}
            keyboardType="numeric"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Notes</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.notes}
            onChangeText={(text) => setFormData({ ...formData, notes: text })}
            multiline
            numberOfLines={4}
            placeholder="Additional observations..."
          />
        </View>

        {location && (
          <View style={styles.locationInfo}>
            <Text style={styles.locationText}>
              📍 Location: {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
            </Text>
          </View>
        )}

        <TouchableOpacity
          style={styles.submitButton}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>Submit Checklist</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F1F8E9',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1B5E20',
    marginBottom: 20,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    fontSize: 16,
    borderWidth: 2,
    borderColor: '#A5D6A7',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  pickerContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#A5D6A7',
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfWidth: {
    width: '48%',
  },
  locationInfo: {
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  locationText: {
    fontSize: 12,
    color: '#2E7D32',
  },
  submitButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
