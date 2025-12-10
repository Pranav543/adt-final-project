import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard API calls
export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/summary'),
  getProtocolDistribution: () => api.get('/dashboard/protocol-distribution'),
  getContractsByBlockchain: () => api.get('/dashboard/contracts-by-blockchain'),
  getTransactionVolume: (days = 30) => api.get(`/dashboard/transaction-volume?days=${days}`),
  getTopProtocols: (limit = 10) => api.get(`/dashboard/top-protocols?limit=${limit}`),
  getUserActivity: (days = 30) => api.get(`/dashboard/user-activity?days=${days}`),
  getMarketPerformance: (days = 14) => api.get(`/dashboard/market-performance?days=${days}`),
  getGasAnalysis: (days = 30) => api.get(`/dashboard/gas-analysis?days=${days}`),
  getMarketShare: () => api.get('/dashboard/market-share'),
};

// Protocols API
export const protocolsAPI = {
  getAll: (page = 1, perPage = 20) => api.get(`/protocols?page=${page}&per_page=${perPage}`),
  getById: (id) => api.get(`/protocols/${id}`),
  create: (data) => api.post('/protocols', data),
  update: (id, data) => api.put(`/protocols/${id}`, data),
  delete: (id) => api.delete(`/protocols/${id}`),
};

// Contracts API
export const contractsAPI = {
  getAll: (page = 1, perPage = 20) => api.get(`/contracts?page=${page}&per_page=${perPage}`),
  getById: (id) => api.get(`/contracts/${id}`),
  create: (data) => api.post('/contracts', data),
  update: (id, data) => api.put(`/contracts/${id}`, data),
  delete: (id) => api.delete(`/contracts/${id}`),
};

// Users API
export const usersAPI = {
  getAll: (page = 1, perPage = 20) => api.get(`/users?page=${page}&per_page=${perPage}`),
  getById: (id) => api.get(`/users/${id}`),
  getTopByVolume: (limit = 10) => api.get(`/users/top-by-volume?limit=${limit}`),
};

// Transactions API
export const transactionsAPI = {
  getAll: (page = 1, perPage = 20) => api.get(`/transactions?page=${page}&per_page=${perPage}`),
  getById: (id) => api.get(`/transactions/${id}`),
  getByHash: (hash) => api.get(`/transactions/hash/${hash}`),
};

export default api;
