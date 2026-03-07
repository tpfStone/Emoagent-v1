import axios, { AxiosError } from 'axios';
import { useSessionStore } from '../stores/sessionStore';
import t from '../locales';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8200',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = useSessionStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      await useSessionStore.getState().initSession();
      if (error.config) {
        return apiClient.request(error.config);
      }
    }
    const message = (error.response?.data as Record<string, string>)?.detail || t.error.requestFailed;
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default apiClient;
