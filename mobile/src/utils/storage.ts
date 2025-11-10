import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Secure storage utilities for React Native
 */

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  THEME: 'app_theme',
  LANGUAGE: 'app_language',
  ONBOARDING_COMPLETED: 'onboarding_completed',
  CHAT_HISTORY: 'chat_history',
  SETTINGS: 'app_settings',
} as const;

/**
 * Generic storage functions
 */

export const setItem = async (key: string, value: any): Promise<void> => {
  try {
    const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
    await AsyncStorage.setItem(key, stringValue);
  } catch (error) {
    console.error('Error saving to storage:', error);
    throw new Error('Failed to save data');
  }
};

export const getItem = async <T = any>(key: string): Promise<T | null> => {
  try {
    const value = await AsyncStorage.getItem(key);
    if (value === null) {return null;}

    try {
      return JSON.parse(value) as T;
    } catch {
      // If JSON parsing fails, return as string
      return value as unknown as T;
    }
  } catch (error) {
    console.error('Error reading from storage:', error);
    return null;
  }
};

export const removeItem = async (key: string): Promise<void> => {
  try {
    await AsyncStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing from storage:', error);
    throw new Error('Failed to remove data');
  }
};

export const clearAll = async (): Promise<void> => {
  try {
    await AsyncStorage.clear();
  } catch (error) {
    console.error('Error clearing storage:', error);
    throw new Error('Failed to clear storage');
  }
};

/**
 * Specific storage functions
 */

export const saveToken = async (token: string): Promise<void> => {
  await setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
};

export const getToken = async (): Promise<string | null> => {
  return await getItem<string>(STORAGE_KEYS.ACCESS_TOKEN);
};

export const removeToken = async (): Promise<void> => {
  await removeItem(STORAGE_KEYS.ACCESS_TOKEN);
};

export const saveUserData = async (userData: any): Promise<void> => {
  await setItem(STORAGE_KEYS.USER_DATA, userData);
};

export const getUserData = async <T = any>(): Promise<T | null> => {
  return await getItem<T>(STORAGE_KEYS.USER_DATA);
};

export const removeUserData = async (): Promise<void> => {
  await removeItem(STORAGE_KEYS.USER_DATA);
};

export const saveTheme = async (theme: string): Promise<void> => {
  await setItem(STORAGE_KEYS.THEME, theme);
};

export const getTheme = async (): Promise<string | null> => {
  return await getItem<string>(STORAGE_KEYS.THEME);
};

export const saveSettings = async (settings: any): Promise<void> => {
  await setItem(STORAGE_KEYS.SETTINGS, settings);
};

export const getSettings = async <T = any>(): Promise<T | null> => {
  return await getItem<T>(STORAGE_KEYS.SETTINGS);
};

export const markOnboardingCompleted = async (): Promise<void> => {
  await setItem(STORAGE_KEYS.ONBOARDING_COMPLETED, true);
};

export const isOnboardingCompleted = async (): Promise<boolean> => {
  const completed = await getItem<boolean>(STORAGE_KEYS.ONBOARDING_COMPLETED);
  return completed === true;
};

/**
 * Utility functions
 */

export const getAllKeys = async (): Promise<string[]> => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    return [...keys]; // Convert readonly to mutable array
  } catch (error) {
    console.error('Error getting all keys:', error);
    return [];
  }
};

export const getMultiple = async (keys: string[]): Promise<[string, string | null][]> => {
  try {
    const result = await AsyncStorage.multiGet(keys);
    return [...result]; // Convert readonly to mutable array
  } catch (error) {
    console.error('Error getting multiple items:', error);
    return [];
  }
};

export const setMultiple = async (keyValuePairs: [string, string][]): Promise<void> => {
  try {
    await AsyncStorage.multiSet(keyValuePairs);
  } catch (error) {
    console.error('Error setting multiple items:', error);
    throw new Error('Failed to save multiple items');
  }
};
