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

export const getSentiment = async (symbol, days = 7) => {
  const response = await api.get(`/sentiment/${symbol}?days=${days}`);
  return response.data;
};

export const getRiskAnalysis = async (symbol) => {
  const response = await api.get(`/risk/${symbol}`);
  return response.data;
};



export const getModelStatus = async () => {
  const response = await api.get('/model/status');
  return response.data;
};

export const getFinancials = async (symbol) => {
  const response = await api.get(`/financials/${symbol}`);
  return response.data;
};

export const forecastStock = async (symbol, days = 14) => {
  try {
    const response = await fetch(
      `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/forecast`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, days }),
      }
    );
    if (!response.ok) throw new Error("Forecast request failed");
    return await response.json();
  } catch (err) {
    throw err;
  }
};



export default api;