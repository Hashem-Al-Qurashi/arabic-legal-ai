import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authAPI } from '../services/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  subscription_tier: 'free' | 'pro' | 'enterprise';
  questions_used_this_month: number;
  is_verified: boolean;
}

interface GuestLimits {
  messagesUsed: number;
  maxMessages: number;
  exchangesUsed: number;
  maxExchanges: number;
  exportsUsed: number;
  maxExports: number;
  citationsUsed: number;
  maxCitations: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isGuest: boolean;
  guestLimits: GuestLimits;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  incrementGuestMessage: () => boolean;
  incrementGuestExchange: () => boolean;
  incrementGuestExport: () => boolean;
  incrementGuestCitation: () => boolean;
  canSendMessage: () => boolean;
  canAskFollowup: () => boolean;
  canExport: () => boolean;
  canGetCitations: () => boolean;
  resetGuestLimits: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(true);
  const [guestLimits, setGuestLimits] = useState<GuestLimits>({
    messagesUsed: 0,
    maxMessages: 7,
    exchangesUsed: 0,
    maxExchanges: 3,
    exportsUsed: 0,
    maxExports: 2,
    citationsUsed: 0,
    maxCitations: 3
  });

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const currentUser = await authAPI.getCurrentUser();
        setUser(currentUser);
        setIsGuest(false);
      } else {
        setIsGuest(true);
      }
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setIsGuest(true);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
  console.log('🔑 Starting login process...');
  await authAPI.login({ email, password });
  console.log('✅ API login successful, getting user data...');
  
  const currentUser = await authAPI.getCurrentUser();
  console.log('👤 User data received:', currentUser.email);
  
  setUser(currentUser);
  setIsGuest(false);
  resetGuestLimits();
  
  console.log('🎯 Auth state updated, login complete');
  
  // Add a small delay to ensure state updates propagate
  await new Promise(resolve => setTimeout(resolve, 100));
};

const register = async (email: string, password: string, fullName: string) => {
  console.log('📝 Starting registration process...');
  await authAPI.register({ email, password, full_name: fullName });
  console.log('✅ Registration API successful, logging in...');
  
  await login(email, password);
  console.log('🎯 Registration and login complete');
  
  // Add a small delay to ensure state updates propagate
  await new Promise(resolve => setTimeout(resolve, 100));
};

  const logout = () => {
    authAPI.logout();
    setUser(null);
    setIsGuest(true);
    resetGuestLimits();
  };

  // Guest limitation functions
  const incrementGuestMessage = (): boolean => {
    if (isGuest && guestLimits.messagesUsed >= guestLimits.maxMessages) {
      return false;
    }
    if (isGuest) {
      setGuestLimits(prev => ({
        ...prev,
        messagesUsed: prev.messagesUsed + 1
      }));
    }
    return true;
  };

  const incrementGuestExchange = (): boolean => {
    if (isGuest && guestLimits.exchangesUsed >= guestLimits.maxExchanges) {
      return false;
    }
    if (isGuest) {
      setGuestLimits(prev => ({
        ...prev,
        exchangesUsed: prev.exchangesUsed + 1
      }));
    }
    return true;
  };

  const incrementGuestExport = (): boolean => {
    if (isGuest && guestLimits.exportsUsed >= guestLimits.maxExports) {
      return false;
    }
    if (isGuest) {
      setGuestLimits(prev => ({
        ...prev,
        exportsUsed: prev.exportsUsed + 1
      }));
    }
    return true;
  };

  const incrementGuestCitation = (): boolean => {
    if (isGuest && guestLimits.citationsUsed >= guestLimits.maxCitations) {
      return false;
    }
    if (isGuest) {
      setGuestLimits(prev => ({
        ...prev,
        citationsUsed: prev.citationsUsed + 1
      }));
    }
    return true;
  };

  const canSendMessage = (): boolean => {
    return !isGuest || guestLimits.messagesUsed < guestLimits.maxMessages;
  };

  const canAskFollowup = (): boolean => {
    return !isGuest || guestLimits.exchangesUsed < guestLimits.maxExchanges;
  };

  const canExport = (): boolean => {
    return !isGuest || guestLimits.exportsUsed < guestLimits.maxExports;
  };

  const canGetCitations = (): boolean => {
    return !isGuest || guestLimits.citationsUsed < guestLimits.maxCitations;
  };

  const resetGuestLimits = () => {
    setGuestLimits({
      messagesUsed: 0,
      maxMessages: 7,
      exchangesUsed: 0,
      maxExchanges: 3,
      exportsUsed: 0,
      maxExports: 2,
      citationsUsed: 0,
      maxCitations: 3
    });
  };

  const value = {
    user,
    loading,
    isGuest,
    guestLimits,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    incrementGuestMessage,
    incrementGuestExchange,
    incrementGuestExport,
    incrementGuestCitation,
    canSendMessage,
    canAskFollowup,
    canExport,
    canGetCitations,
    resetGuestLimits
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export type { User };