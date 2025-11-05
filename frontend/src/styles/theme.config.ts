/**
 * Theme Configuration - Single Source of Truth
 * 
 * This file defines all theme-related constants and utilities.
 * Light mode is the default theme, dark mode is an optional override.
 * 
 * Architecture principles:
 * 1. No hardcoded colors in components - use theme variables
 * 2. Light mode is default, dark mode is applied via .dark-mode class
 * 3. All theme transitions are smooth and consistent
 * 4. Theme preference is persisted to localStorage
 */

export const THEME_CONFIG = {
  // Storage key for theme preference
  STORAGE_KEY: 'theme-preference',
  
  // CSS class applied to root element for dark mode
  DARK_MODE_CLASS: 'dark-mode',
  
  // Default theme when no preference is stored
  DEFAULT_THEME: 'light' as const,
  
  // Meta theme colors for mobile browsers
  META_COLORS: {
    light: '#ffffff',
    dark: '#111827'
  },
  
  // Transition duration for theme changes
  TRANSITION_DURATION: '0.3s',
  
  // CSS variable definitions (for reference)
  cssVariables: {
    light: {
      // Text colors
      '--text-primary': '#1f2937',
      '--text-secondary': '#6b7280',
      '--text-light': '#9ca3af',
      
      // Background colors
      '--background-white': '#ffffff',
      '--background-light': '#f9fafb',
      
      // Border colors
      '--border-light': '#e5e7eb',
      '--border-medium': '#d1d5db',
      
      // Component specific
      '--sidebar-bg': '#f8f9fa',
      '--sidebar-border': '#e5e7eb',
    },
    dark: {
      // Text colors
      '--text-primary': '#f9fafb',
      '--text-secondary': '#d1d5db',
      '--text-light': '#9ca3af',
      
      // Background colors
      '--background-white': '#111827',
      '--background-light': '#1f2937',
      
      // Border colors
      '--border-light': '#374151',
      '--border-medium': '#4b5563',
      
      // Component specific
      '--sidebar-bg': '#0f1419',
      '--sidebar-border': '#2d3748',
    }
  }
} as const;

/**
 * Helper function to apply theme to document
 */
export const applyTheme = (isDark: boolean): void => {
  const root = document.documentElement;
  
  if (isDark) {
    root.classList.add(THEME_CONFIG.DARK_MODE_CLASS);
  } else {
    root.classList.remove(THEME_CONFIG.DARK_MODE_CLASS);
  }
  
  // Update meta theme-color for mobile browsers
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.setAttribute(
      'content', 
      isDark ? THEME_CONFIG.META_COLORS.dark : THEME_CONFIG.META_COLORS.light
    );
  }
};

/**
 * Get stored theme preference
 */
export const getStoredTheme = (): 'light' | 'dark' | null => {
  const stored = localStorage.getItem(THEME_CONFIG.STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  return null;
};

/**
 * Store theme preference
 */
export const storeTheme = (theme: 'light' | 'dark'): void => {
  localStorage.setItem(THEME_CONFIG.STORAGE_KEY, theme);
};