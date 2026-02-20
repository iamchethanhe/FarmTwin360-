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
import { farmService, incidentService } from '../services/api';

export default function IncidentScreen({ navigation }) {
  const [farms, setFarms] = useState([]);
  const [barns, setBarns] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState('');
  const [selectedBarn, setSelectedBarn] = useState('');
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    incident_type: 'disease',
    severity: 'medium',
    description: '',
    actions_taken: '',
  });

  useEffect(() => {
    loadFarms();
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

  const handleSubmit = async () => {
    if (!selectedBarn || !formData.description) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const data = {
        barn_id: parseInt(selectedBarn),
        incident_type: formData.incident_type,
        severity: formData.severity,
        description: formData.description,
        actions_taken: formData.actions_taken,
      };

      await incidentService.createIncident(data);
      Alert.alert('Success', 'Incident reported successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to report incident');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Report Incident</Text>

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

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Incident Type</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={formData.incident_type}
              onValueChange={(value) => setFormData({ ...formData, incident_type: value })}
              style={styles.picker}
            >
              <Picker.Item label="Disease Outbreak" value="disease" />
              <Picker.Item label="Equipment Failure" value="equipment_failure" />
              <Picker.Item label="Environmental Issue" value="environmental" />
              <Picker.Item label="Safety Hazard" value="safety" />
              <Picker.Item label="Other" value="other" />
            </Picker>
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Severity</Text>
          <View style={styles.severityButtons}>
            <TouchableOpacity
              style={[
                styles.severityButton,
                formData.severity === 'low' && styles.severityButtonActive,
                { borderColor: '#4CAF50' },
              ]}
              onPress={() => setFormData({ ...formData, severity: 'low' })}
            >
              <Text
                style={[
                  styles.severityButtonText,
                  formData.severity === 'low' && styles.severityButtonTextActive,
                ]}
              >
                Low
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.severityButton,
                formData.severity === 'medium' && styles.severityButtonActive,
                { borderColor: '#FF9800' },
              ]}
              onPress={() => setFormData({ ...formData, severity: 'medium' })}
            >
              <Text
                style={[
                  styles.severityButtonText,
                  formData.severity === 'medium' && styles.severityButtonTextActive,
                ]}
              >
                Medium
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.severityButton,
                formData.severity === 'high' && styles.severityButtonActive,
                { borderColor: '#F44336' },
              ]}
              onPress={() => setFormData({ ...formData, severity: 'high' })}
            >
              <Text
                style={[
                  styles.severityButtonText,
                  formData.severity === 'high' && styles.severityButtonTextActive,
                ]}
              >
                High
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Description *</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.description}
            onChangeText={(text) => setFormData({ ...formData, description: text })}
            multiline
            numberOfLines={4}
            placeholder="Describe the incident in detail..."
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Actions Taken</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.actions_taken}
            onChangeText={(text) => setFormData({ ...formData, actions_taken: text })}
            multiline
            numberOfLines={4}
            placeholder="What immediate actions have been taken?"
          />
        </View>

        <TouchableOpacity
          style={styles.submitButton}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>Report Incident</Text>
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
  severityButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  severityButton: {
    flex: 1,
    padding: 12,
    marginHorizontal: 5,
    borderRadius: 12,
    borderWidth: 2,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  severityButtonActive: {
    backgroundColor: '#E8F5E9',
  },
  severityButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
  },
  severityButtonTextActive: {
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#F44336',
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
