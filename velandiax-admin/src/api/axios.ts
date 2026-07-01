import axios from 'axios';
import { clearAuth } from '../utils/auth';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', 
  },
});

// Interceptor: Se ejecuta ANTES de que la petición salga hacia tu backend
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    // Si tenemos un token guardado, lo inyectamos como Bearer Token
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de respuesta: Para detectar si el token expiró (401) y cerrar sesión
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      clearAuth();
      window.location.href = '/admin/login'; // Redirigimos al login forzosamente
    }
    return Promise.reject(error);
  }
);

export default apiClient;
