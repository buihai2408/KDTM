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

// Chatbot API (Backend direct - fallback)
export const chatbotAPI = {
  query: (userId, question, timezone = 'Asia/Ho_Chi_Minh') =>
    api.post('/chatbot/query', { user_id: userId, question, timezone }),
  health: () => api.get('/chatbot/health'),
  demoQuestions: () => api.get('/chatbot/demo-questions'),
};

// Dify Cloud API Configuration
const DIFY_CONFIG = {
  apiKey: import.meta.env.VITE_DIFY_API_KEY || 'app-4Wuqqyd2vfDcLp4J8TtRxSqT',
  apiUrl: import.meta.env.VITE_DIFY_API_URL || 'https://api.dify.ai/v1',
};

// Dify Chatbot API
export const difyAPI = {
  /**
   * Send message to Dify chatbot using streaming (required for Agent apps)
   * @param {string} query - User's question
   * @param {string} userId - User ID for conversation tracking
   * @param {string} conversationId - Optional conversation ID for context
   */
  chat: async (query, userId, conversationId = '') => {
    const response = await fetch(`${DIFY_CONFIG.apiUrl}/chat-messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${DIFY_CONFIG.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        inputs: {
          user_id: userId.toString(),
        },
        query: query,
        response_mode: 'streaming', // Agent apps require streaming mode
        conversation_id: conversationId,
        user: `user-${userId}`,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Dify API error');
    }

    // Parse streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = { answer: '', conversation_id: '' };

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            // Handle different event types from Dify
            if (data.event === 'agent_message' || data.event === 'message') {
              result.answer += data.answer || '';
              result.conversation_id = data.conversation_id;
            } else if (data.event === 'message_end') {
              result.conversation_id = data.conversation_id;
            } else if (data.event === 'error') {
              throw new Error(data.message || 'Dify error');
            }
          } catch (e) {
            // Skip invalid JSON lines
            if (e.message && !e.message.includes('JSON')) {
              throw e;
            }
          }
        }
      }
    }

    return result;
  },
};

export default api;
