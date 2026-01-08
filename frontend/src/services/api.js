import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (email, password, fullName) =>
    api.post('/api/auth/register', { email, password, full_name: fullName }),
  getMe: () => api.get('/api/auth/me'),
};

// Categories API
export const categoriesAPI = {
  getAll: (type) => api.get('/api/categories', { params: { type } }),
  create: (data) => api.post('/api/categories', data),
  update: (id, data) => api.put(`/api/categories/${id}`, data),
  delete: (id) => api.delete(`/api/categories/${id}`),
};

// Wallets API
export const walletsAPI = {
  getAll: () => api.get('/api/wallets'),
  getById: (id) => api.get(`/api/wallets/${id}`),
  create: (data) => api.post('/api/wallets', data),
  update: (id, data) => api.put(`/api/wallets/${id}`, data),
  delete: (id) => api.delete(`/api/wallets/${id}`),
};

// Transactions API
export const transactionsAPI = {
  getAll: (params) => api.get('/api/transactions', { params }),
  getById: (id) => api.get(`/api/transactions/${id}`),
  create: (data) => api.post('/api/transactions', data),
  update: (id, data) => api.put(`/api/transactions/${id}`, data),
  delete: (id) => api.delete(`/api/transactions/${id}`),
};

// Budgets API
export const budgetsAPI = {
  getAll: (params) => api.get('/api/budgets', { params }),
  getStatus: (month, year) =>
    api.get('/api/budgets/status', { params: { month, year } }),
  create: (data) => api.post('/api/budgets', data),
  update: (id, data) => api.put(`/api/budgets/${id}`, data),
  delete: (id) => api.delete(`/api/budgets/${id}`),
};

// Summary API
export const summaryAPI = {
  getDashboard: () => api.get('/api/summary/dashboard'),
  getMonthly: (months) => api.get('/api/summary/monthly', { params: { months } }),
  getCategories: (type, month, year) =>
    api.get('/api/summary/categories', { params: { type, month, year } }),
};

export default api;
