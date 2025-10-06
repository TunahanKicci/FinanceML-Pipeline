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

export const optimizePortfolio = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Portfolio optimization failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Portfolio optimization error:', error);
    throw error;
  }
};

// Get Efficient Frontier
export const getEfficientFrontier = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/efficient-frontier`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to calculate efficient frontier');
    }

    return await response.json();
  } catch (error) {
    console.error('Efficient frontier error:', error);
    throw error;
  }
};

// Monte Carlo Simulation
export const runMonteCarloSimulation = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/monte-carlo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Monte Carlo simulation failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Monte Carlo simulation error:', error);
    throw error;
  }
};

// Get Correlation Matrix
export const getCorrelationMatrix = async (symbols, period = '2y') => {
  try {
    const symbolsParam = Array.isArray(symbols) ? symbols.join(',') : symbols;
    const response = await fetch(
      `${API_BASE_URL}/portfolio/correlation/${symbolsParam}?period=${period}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get correlation matrix');
    }

    return await response.json();
  } catch (error) {
    console.error('Correlation matrix error:', error);
    throw error;
  }
};

// Optimize for Target Return
export const optimizeTargetReturn = async (symbols, targetReturn, period = '2y', constraints = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/target-return`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbols,
        target_return: targetReturn,
        period,
        constraints
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Target return optimization failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Target return optimization error:', error);
    throw error;
  }
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