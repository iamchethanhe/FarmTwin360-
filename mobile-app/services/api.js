import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Change this to your backend URL
// Use your computer's local IP address when testing on a physical device or emulator
// If using Android emulator, you can also try: http://10.0.2.2:8000/api
const API_URL = 'http://10.60.236.240:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, logout user
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.token) {
      await AsyncStorage.setItem('authToken', response.data.token);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: async () => {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('user');
  },

  getProfile: async () => {
    const response = await api.get('/user/profile');
    return response.data;
  },
};

export const farmService = {
  getFarms: async () => {
    const response = await api.get('/farms');
    return response.data;
  },

  getBarns: async (farmId) => {
    const response = await api.get(`/farms/${farmId}/barns`);
    return response.data;
  },
};

export const checklistService = {
  createChecklist: async (data) => {
    const response = await api.post('/checklists', data);
    return response.data;
  },

  getChecklists: async () => {
    const response = await api.get('/checklists');
    return response.data;
  },
};

export const incidentService = {
  createIncident: async (data) => {
    const response = await api.post('/incidents', data);
    return response.data;
  },

  getIncidents: async () => {
    const response = await api.get('/incidents');
    return response.data;
  },
};

export const dashboardService = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getAlerts: async () => {
    const response = await api.get('/alerts');
    return response.data;
  },
};

export const managerService = {
  getPendingChecklists: async () => {
    const response = await api.get('/manager/pending-checklists');
    return response.data;
  },

  getPendingIncidents: async () => {
    const response = await api.get('/manager/pending-incidents');
    return response.data;
  },

  approveChecklist: async (checklistId) => {
    const response = await api.post(`/checklists/${checklistId}/approve`);
    return response.data;
  },

  approveIncident: async (incidentId) => {
    const response = await api.post(`/incidents/${incidentId}/approve`);
    return response.data;
  },
};

export const adminService = {
  getAllUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  getAllFarms: async () => {
    const response = await api.get('/admin/farms');
    return response.data;
  },

  getFarmAssignments: async () => {
    const response = await api.get('/admin/farm-assignments');
    return response.data;
  },

  getAllBarns: async () => {
    const response = await api.get('/admin/barns');
    return response.data;
  },

  getSystemStats: async () => {
    const response = await api.get('/admin/system-stats');
    return response.data;
  },
};

export default api;
