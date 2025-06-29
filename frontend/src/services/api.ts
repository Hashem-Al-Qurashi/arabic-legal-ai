import axios from 'axios';
import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  Consultation 
} from '../types/auth';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

const setToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

const removeToken = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // 🔧 FIXED: Use JSON instead of FormData for consistency
    const response = await api.post('/api/auth/login', {
      email: credentials.email,
      password: credentials.password
    });
    
    // Note: Simple auth returns user object, not tokens
    // For now, we'll simulate tokens
    const fakeToken = btoa(JSON.stringify({ email: credentials.email, timestamp: Date.now() }));
    setToken(fakeToken);
    
    return {
      access_token: fakeToken,
      refresh_token: fakeToken,
      token_type: 'bearer',
      expires_in: 3600
    };
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    // 🔧 SIMPLIFIED: Since we don't have /api/users/me yet, 
    // we'll return a mock user based on stored email
    const token = getToken();
    if (!token) throw new Error('No token');
    
    try {
      const decoded = JSON.parse(atob(token));
      return {
        id: '1',
        email: decoded.email,
        full_name: 'User',
        is_active: true,
        subscription_tier: 'free',
        questions_used_this_month: 0,
        is_verified: true
      };
    } catch {
      throw new Error('Invalid token');
    }
  },

  logout(): void {
    removeToken();
    window.location.href = '/';
  }
};

export const legalAPI = {
  async askQuestion(question: string): Promise<Consultation> {
    const formData = new FormData();
    formData.append('query', question);

    // 🔧 FIXED: Use the correct endpoint path
    const response = await api.post('/api/consultations/ask', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    return response.data;
  },

  async exportDocx(question: string, answer: string): Promise<void> {
    const response = await api.get('/export/docx', {
      params: { question, answer },
      responseType: 'blob'
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `legal-response-${Date.now()}.docx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
};

export { getToken, removeToken };