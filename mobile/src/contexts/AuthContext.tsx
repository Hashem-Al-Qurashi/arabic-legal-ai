import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '@/services/api';
import type { AuthState, LoginCredentials, RegisterCredentials } from '@/types';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>;
  register: (userData: RegisterCredentials) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): React.JSX.Element {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    isGuest: false,
    isAuthenticated: false,
  });

  // Check for existing authentication on app start
  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async (): Promise<void> => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const token = await AsyncStorage.getItem('access_token');
      if (!token) {
        setAuthState({
          user: null,
          loading: false,
          isGuest: true,
          isAuthenticated: false,
        });
        return;
      }

      // Verify token by fetching user data
      const userResponse = await authAPI.getCurrentUser();
      if (userResponse.success && userResponse.data) {
        setAuthState({
          user: userResponse.data,
          loading: false,
          isGuest: false,
          isAuthenticated: true,
        });
      } else {
        // Token is invalid, clear it
        await AsyncStorage.removeItem('access_token');
        setAuthState({
          user: null,
          loading: false,
          isGuest: true,
          isAuthenticated: false,
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthState({
        user: null,
        loading: false,
        isGuest: true,
        isAuthenticated: false,
      });
    }
  };

  const login = async (credentials: LoginCredentials): Promise<{ success: boolean; error?: string }> => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const response = await authAPI.login(credentials);

      if (response.success && response.data) {
        setAuthState({
          user: response.data.user,
          loading: false,
          isGuest: false,
          isAuthenticated: true,
        });

        return { success: true };
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
        return {
          success: false,
          error: response.error || 'Login failed',
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      setAuthState(prev => ({ ...prev, loading: false }));
      return {
        success: false,
        error: 'Network error. Please try again.',
      };
    }
  };

  const register = async (userData: RegisterCredentials): Promise<{ success: boolean; error?: string }> => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const response = await authAPI.register(userData);

      if (response.success) {
        setAuthState(prev => ({ ...prev, loading: false }));
        return { success: true };
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
        return {
          success: false,
          error: response.error || 'Registration failed',
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      setAuthState(prev => ({ ...prev, loading: false }));
      return {
        success: false,
        error: 'Network error. Please try again.',
      };
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout();
      setAuthState({
        user: null,
        loading: false,
        isGuest: true,
        isAuthenticated: false,
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout fails, clear local state
      setAuthState({
        user: null,
        loading: false,
        isGuest: true,
        isAuthenticated: false,
      });
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      const userResponse = await authAPI.getCurrentUser();
      if (userResponse.success && userResponse.data) {
        setAuthState(prev => ({
          ...prev,
          user: userResponse.data || null,
        }));
      }
    } catch (error) {
      console.error('User refresh failed:', error);
    }
  };

  const contextValue: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
