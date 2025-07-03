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

  // 🔧 NEW: Get updated user stats after asking question
  async askQuestionWithUserUpdate(question: string): Promise<{consultation: Consultation, updatedUser?: any}> {
    const consultation = await this.askQuestion(question);
    
    // If the response includes updated user data, return it
    if ((consultation as any).updated_user) {
      return {
        consultation,
        updatedUser: (consultation as any).updated_user
      };
    }
    
    // Otherwise, fetch current user stats separately
    try {
      const userStats = await chatAPI.getUserStats();
      return {
        consultation,
        updatedUser: userStats
      };
    } catch (error) {
      console.warn('Failed to fetch updated user stats:', error);
      return { consultation };
    }
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
export const chatAPI = {
  async sendMessage(message: string, conversationId?: string): Promise<any> {
    const formData = new FormData();
    formData.append('message', message);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }

    const response = await api.post('/api/chat/message', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    return response.data;
  },

  async getConversations(): Promise<any> {
    const response = await api.get('/api/chat/conversations');
    return response.data;
  },

  async getConversationMessages(conversationId: string): Promise<any> {
    const response = await api.get(`/api/chat/conversations/${conversationId}/messages`);
    return response.data;
  },

  async updateConversationTitle(conversationId: string, title: string): Promise<any> {
    const formData = new FormData();
    formData.append('new_title', title);

    const response = await api.put(`/api/chat/conversations/${conversationId}/title`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    
    return response.data;
  },

  
  async archiveConversation(conversationId: string): Promise<any> {
    const response = await api.delete(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  async getUserStats(): Promise<any> {
    const response = await api.get('/api/consultations/user/stats');
    return response.data;
  }

  
};

export { getToken, removeToken };