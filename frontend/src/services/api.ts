import axios from 'axios';
import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  Consultation 
} from '../types/auth';

// Production: Detect environment and use appropriate backend URL
const getApiBaseUrl = () => {
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For hokm.ai production domains, use the backend ALB directly (CloudFront has issues)
  if (window.location.hostname.includes('hokm.ai') || window.location.hostname.includes('cloudfront.net')) {
    // Use the ALB directly since CloudFront backend is not working
    return 'http://hokm-ai-alb-1845047249.eu-central-1.elb.amazonaws.com';
  }
  
  // Fallback for other domains
  return `https://api.${window.location.hostname}`;
};

const API_BASE_URL = getApiBaseUrl();
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

// In frontend/src/services/api.ts - Replace the entire authAPI object
export const authAPI = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login', credentials);
    
    const { access_token, refresh_token, expires_in } = response.data;
    setToken(access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  },

  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
  const response = await api.get('/api/chat/status');
  return {
    id: response.data.user_id || response.data.id,
    email: response.data.email,
    full_name: response.data.full_name,
    is_active: response.data.is_active,
    subscription_tier: response.data.subscription_tier,
    questions_used_this_month: response.data.questions_used_this_month,
    questions_used_current_cycle: response.data.questions_used_current_cycle || 0,
    cycle_reset_time: response.data.cycle_reset_time || null,
    is_verified: response.data.is_verified
  };
},

  logout(): void {
    removeToken();
    window.location.href = '/';
  }
};

// Add this to your API interceptors for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          setToken(access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        removeToken();
        window.location.href = '/';
      }
    }
    
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/';
    }
    
    return Promise.reject(error);
  }
);

export const legalAPI = {
  async askQuestion(question: string, conversationHistory: any[] = [], onChunk?: (chunk: string) => void): Promise<Consultation> {
  const formData = new FormData();
  formData.append('query', question);
  
  if (conversationHistory.length > 0) {
    formData.append('context', JSON.stringify(conversationHistory));
  }

  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: 'POST',
    body: formData
  });

  if (!response.body) {
    throw new Error('No response body for streaming');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';
  let metadata: any = {};

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') break;

        try {
          const parsed = JSON.parse(data);
          if (parsed.type === 'chunk' && onChunk) {
            fullResponse += parsed.content;
            onChunk(parsed.content);
          } else if (parsed.type === 'complete') {
            metadata = parsed;
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }
  }

  return metadata.answer ? metadata : {
    id: metadata.id || Date.now().toString(),
    question: question,
    answer: fullResponse,
    category: 'general',
    processing_time_ms: metadata.processing_time_ms || 0,
    timestamp: new Date().toISOString(),
    user_questions_remaining: 999
  };
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
async sendMessage(message: string, conversationId?: string, sessionId?: string): Promise<any> {
  const formData = new FormData();
  formData.append('message', message);
  if (conversationId) {
    formData.append('conversation_id', conversationId);
  }
  if (sessionId) {
    formData.append('session_id', sessionId);
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
  // Add this method to your existing chatAPI object (after sendMessage):
// Replace your sendMessageStreaming function with this fixed version:

async sendMessageStreaming(
  message: string,
  conversationId?: string,
  sessionId?: string,
  onChunk?: (chunk: string) => void,
  onComplete?: (response: any) => void,
  onError?: (error: string) => void
): Promise<void> {
  const formData = new FormData();
  formData.append('message', message);
  
  if (conversationId) {
    formData.append('conversation_id', conversationId);
  }
  
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  try {
    // ✅ FIXED: Removed conflicting headers, let browser set Content-Type for FormData
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {  // ← Removed double slash
      method: 'POST',
      headers: {
        'Accept': 'text/event-stream',
        ...(getToken() && { 'Authorization': `Bearer ${getToken()}` }),
      },
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ HTTP ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (data === '[DONE]') return;

          try {
            const parsed = JSON.parse(data);
            
            if (parsed.type === 'chunk' && parsed.content && onChunk) {
              fullResponse += parsed.content;
              onChunk(parsed.content);
            } else if (parsed.type === 'complete' && onComplete) {
              onComplete({ ...parsed, fullResponse });
            } else if (parsed.type === 'error' && onError) {
              onError(parsed.error);
              return;
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  } catch (error) {
    console.error('❌ Streaming failed:', error);
    if (onError) {
      onError(error instanceof Error ? error.message : 'Streaming failed');
    }
    throw error;
  }
},
  
  async archiveConversation(conversationId: string): Promise<any> {
    const response = await api.delete(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  async getUserStats(): Promise<any> {
  const response = await api.get('/api/chat/status');
  return response.data;
}

  
};

export { getToken, removeToken };