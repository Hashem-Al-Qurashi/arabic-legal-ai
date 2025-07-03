import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authAPI, chatAPI } from '../services/api';
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
  lastQuestionTime: number | null; // Timestamp of last question
  cooldownMinutes: number; // Cooldown period in minutes
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
  // 🔧 NEW: Methods for updating user data
  updateUserData: (userData: Partial<User>) => void;
  refreshUserData: () => Promise<void>;
  questionsRemaining: number;
   isInCooldown: boolean;
  cooldownTimeRemaining: number; // in minutes
  canAskNewQuestion: () => boolean;
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
    maxCitations: 3,
    lastQuestionTime: null,
    cooldownMinutes: 90 // 1.5 hours cooldown
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

  // 🔧 NEW: Method to update user data in real-time
  // 🔧 NEW: Method to update user data in real-time (with debounce)
  const updateUserData = (userData: Partial<User>) => {
    if (user) {
      console.log('🔄 Updating user data:', userData);
      setUser(prevUser => {
        // Only update if data actually changed
        const hasChanged = Object.keys(userData).some(
          key => prevUser![key as keyof User] !== userData[key as keyof User]
        );
        
        if (hasChanged) {
          return { ...prevUser!, ...userData };
        }
        return prevUser!;
      });
    }
  };

  // 🔧 NEW: Method to refresh user data from backend
  const refreshUserData = async () => {
    if (!isGuest) {
      try {
        console.log('🔄 Refreshing user data from backend...');
        const userStats = await chatAPI.getUserStats();
        if (userStats && !userStats.error) {
          console.log('✅ User data refreshed:', userStats);
          setUser(prevUser => ({
            ...prevUser!,
            questions_used_this_month: userStats.questions_used_this_month,
            subscription_tier: userStats.subscription_tier,
            is_active: userStats.is_active,
            is_verified: userStats.is_verified
          }));
        }
      } catch (error) {
        console.warn('⚠️ Failed to refresh user data:', error);
      }
    }
  };

  // 🔧 ENHANCED: Calculate questions remaining in real-time
  const questionsRemaining = user ? (() => {
    if (user.subscription_tier === "free") {
      return Math.max(0, 20 - user.questions_used_this_month);
    } else if (user.subscription_tier === "pro") {
      return Math.max(0, 100 - user.questions_used_this_month);
    } else { // enterprise
      return 999999;
    }
  })() : 0;

  const isInCooldown = (() => {
    if (isGuest && guestLimits.lastQuestionTime) {
      const now = Date.now();
      const timeDiff = now - guestLimits.lastQuestionTime;
      const cooldownTime = guestLimits.cooldownMinutes * 60 * 1000; // Convert to milliseconds
      return timeDiff < cooldownTime;
    }
    
    // For authenticated users, check if they've reached their limit
    if (user && questionsRemaining === 0) {
      // You can implement user-specific cooldown here if needed
      return false; // For now, no cooldown for users who haven't reached limit
    }
    
    return false;
  })();

  // 🔧 NEW: Calculate remaining cooldown time in minutes
  const cooldownTimeRemaining = (() => {
    if (isGuest && guestLimits.lastQuestionTime && isInCooldown) {
      const now = Date.now();
      const timeDiff = now - guestLimits.lastQuestionTime;
      const cooldownTime = guestLimits.cooldownMinutes * 60 * 1000;
      const remaining = cooldownTime - timeDiff;
      return Math.ceil(remaining / (60 * 1000)); // Convert to minutes
    }
    return 0;
  })();

  // 🔧 NEW: Check if user can ask a new question
  const canAskNewQuestion = (): boolean => {
    if (isInCooldown) return false;
    return canSendMessage();
  };

  // Guest limitation functions
  const incrementGuestMessage = (): boolean => {
    if (isGuest && guestLimits.messagesUsed >= guestLimits.maxMessages) {
      return false;
    }
    if (isGuest) {
      setGuestLimits(prev => ({
        ...prev,
        messagesUsed: prev.messagesUsed + 1,
        lastQuestionTime: Date.now() // 🔧 NEW: Record the time of last question
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
    if (isGuest) {
      return guestLimits.messagesUsed < guestLimits.maxMessages;
    } else {
      return questionsRemaining > 0;
    }
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
      maxCitations: 3,
      lastQuestionTime: null,
      cooldownMinutes: 90
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
    resetGuestLimits,
    // 🔧 NEW: Expose new methods
    updateUserData,
    refreshUserData,
    questionsRemaining,
    // 🔧 NEW: Add cooldown properties
    isInCooldown,
    cooldownTimeRemaining,
    canAskNewQuestion
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export type { User };