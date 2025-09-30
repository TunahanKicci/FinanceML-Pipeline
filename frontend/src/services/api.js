// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getModelStatus = async () => {
  const response = await api.get('/model/status');
  return response.data;
};

export const predictStock = async (symbol, daysAhead = 1) => {
  const response = await api.post('/predict', {
    symbol: symbol.toUpperCase(),
    days_ahead: daysAhead,
  });
  return response.data;
};

export default api;