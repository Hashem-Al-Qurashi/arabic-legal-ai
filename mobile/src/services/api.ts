import axios from 'axios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {
  User,
  LoginCredentials,
  RegisterCredentials,
  ApiResponse,
  Message,
  Conversation,
} from '@/types';

// Mobile-optimized API base URL detection
const getApiBaseUrl = (): string => {
  // For development, you may need to use your computer's IP address
  // Replace with your actual backend URL
  if (__DEV__) {
    // Development URLs - update these based on your setup
    if (Platform.OS === 'ios') {
      return 'http://localhost:8000'; // iOS Simulator
    } else {
      return 'http://10.0.2.2:8000'; // Android Emulator
    }
  }

  // Production URL
  return 'https://api.hokm.ai';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with mobile-optimized configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for mobile networks
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'ArabicLegalAI-Mobile/1.0',
    'X-Platform': Platform.OS,
  },
});

// Mobile-specific token management using AsyncStorage
const getToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem('access_token');
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
};

const setToken = async (token: string): Promise<void> => {
  try {
    await AsyncStorage.setItem('access_token', token);
  } catch (error) {
    console.error('Error setting token:', error);
  }
};

const removeToken = async (): Promise<void> => {
  try {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
  } catch (error) {
    console.error('Error removing tokens:', error);
  }
};

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh and error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          await setToken(access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;

          return api(originalRequest);
        }
      } catch (refreshError) {
        await removeToken();
        // In mobile app, you'd navigate to login screen here
        console.error('Token refresh failed:', refreshError);
      }
    }

    if (error.response?.status === 401) {
      await removeToken();
      // In mobile app, navigate to login screen
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  async login(credentials: LoginCredentials): Promise<ApiResponse<{ user: User; tokens: any }>> {
    try {
      const response = await api.post('/api/auth/login', credentials);

      const { access_token, refresh_token, expires_in, ...userData } = response.data;
      await setToken(access_token);
      await AsyncStorage.setItem('refresh_token', refresh_token);

      return {
        success: true,
        data: {
          user: userData,
          tokens: { access_token, refresh_token, expires_in },
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed',
      };
    }
  },

  async register(userData: RegisterCredentials): Promise<ApiResponse<User>> {
    try {
      const response = await api.post('/api/auth/register', userData);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed',
      };
    }
  },

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response = await api.get('/api/chat/status');
      const userData = {
        id: response.data.user_id || response.data.id,
        email: response.data.email,
        full_name: response.data.full_name,
        is_active: response.data.is_active,
        subscription_tier: response.data.subscription_tier,
        questions_used_current_cycle: response.data.questions_used_current_cycle || 0,
        cycle_reset_time: response.data.cycle_reset_time || null,
        is_verified: response.data.is_verified,
      };

      return {
        success: true,
        data: userData,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get user data',
      };
    }
  },

  async logout(): Promise<void> {
    await removeToken();
    // In mobile app, navigate to login screen
  },
};

// Chat API for messaging functionality
export const chatAPI = {
  async sendMessage(
    message: string,
    conversationId?: string,
    sessionId?: string
  ): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('message', message);
      if (conversationId) {
        formData.append('conversation_id', conversationId);
      }
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      const response = await api.post('/api/chat/message', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to send message',
      };
    }
  },

  async sendMessageStreaming(
    message: string,
    conversationId?: string,
    sessionId?: string,
    onChunk?: (chunk: string) => void,
    onComplete?: (response: any) => void,
    onError?: (error: string) => void,
    abortSignal?: AbortSignal
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
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Accept': 'text/event-stream',
          'User-Agent': 'ArabicLegalAI-Mobile/1.0',
          'X-Platform': Platform.OS,
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: formData,
        signal: abortSignal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP ${response.status}:`, errorText);
        throw new Error(`HTTP ${response.status}`);
      }

      // React Native doesn't support streaming fetch responses
      // Fall back to regular JSON response for now
      // TODO: Implement proper streaming using WebSocket or similar
      const responseText = await response.text();

      try {
        const data = JSON.parse(responseText);

        if (data.error && onError) {
          onError(data.error);
          return;
        }

        // Simulate streaming by delivering content immediately
        if (data.content && onChunk) {
          onChunk(data.content);
        }

        if (onComplete) {
          onComplete({
            ...data,
            fullResponse: data.content || '',
            type: 'complete',
          });
        }
      } catch (jsonError) {
        // If not JSON, treat as plain text response
        if (onChunk) {
          onChunk(responseText);
        }

        if (onComplete) {
          onComplete({
            content: responseText,
            fullResponse: responseText,
            type: 'complete',
          });
        }
      }
    } catch (error: any) {
      // Don't log or report aborted requests as errors
      if (error.name === 'AbortError' || error.message === 'Request aborted') {
        console.log('Request was aborted');
        return;
      }

      console.error('Streaming failed:', error);
      if (onError) {
        onError(error instanceof Error ? error.message : 'Streaming failed');
      }
      throw error;
    }
  },

  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    try {
      const response = await api.get('/api/chat/conversations');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get conversations',
      };
    }
  },

  async getConversationMessages(conversationId: string): Promise<ApiResponse<Message[]>> {
    try {
      const response = await api.get(`/api/chat/conversations/${conversationId}/messages`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get messages',
      };
    }
  },

  async updateConversationTitle(conversationId: string, title: string): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('new_title', title);

      const response = await api.put(`/api/chat/conversations/${conversationId}/title`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update title',
      };
    }
  },

  async archiveConversation(conversationId: string): Promise<ApiResponse<any>> {
    try {
      const response = await api.delete(`/api/chat/conversations/${conversationId}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to archive conversation',
      };
    }
  },

  async getUserStats(): Promise<ApiResponse<any>> {
    try {
      const response = await api.get('/api/chat/status');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get user stats',
      };
    }
  },
};

// Export utility functions
export { getToken, removeToken, setToken };
