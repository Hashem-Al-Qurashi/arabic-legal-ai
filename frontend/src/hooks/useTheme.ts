import { useState, useEffect } from 'react';
import { THEME_CONFIG, applyTheme, getStoredTheme, storeTheme } from '../styles/theme.config';

/**
 * Theme management hook
 * - Light mode is default
 * - Dark mode is applied via .dark-mode class on root element
 * - Persists preference to localStorage
 * - Uses centralized theme configuration
 */
export const useTheme = () => {
  const [isDark, setIsDark] = useState<boolean>(() => {
    // Check for stored preference
    const stored = getStoredTheme();
    if (stored !== null) {
      return stored === 'dark';
    }
    // Default to light mode (as per architecture)
    // No system preference check - light mode is intentionally the default
    return THEME_CONFIG.DEFAULT_THEME === 'dark';
  });

  useEffect(() => {
    // Apply theme to document
    applyTheme(isDark);
    
    // Persist preference
    storeTheme(isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => setIsDark(prev => !prev);

  return { 
    isDark, 
    toggleTheme,
    theme: isDark ? 'dark' : 'light'
  };
};