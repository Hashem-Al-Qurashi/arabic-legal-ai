import { I18nManager } from 'react-native';

/**
 * RTL (Right-to-Left) support utilities for Arabic Legal AI Mobile
 * Handles proper text direction, layout, and formatting for Arabic text
 */

/**
 * Arabic Unicode ranges for detection
 */
const ARABIC_UNICODE_RANGES = [
  [0x0600, 0x06FF], // Arabic
  [0x0750, 0x077F], // Arabic Supplement
  [0x08A0, 0x08FF], // Arabic Extended-A
  [0xFB50, 0xFDFF], // Arabic Presentation Forms-A
  [0xFE70, 0xFEFF], // Arabic Presentation Forms-B
];

/**
 * Check if a character is Arabic
 */
export const isArabicCharacter = (char: string): boolean => {
  const code = char.codePointAt(0);
  if (!code) {return false;}

  return ARABIC_UNICODE_RANGES.some(([start, end]) => code >= start && code <= end);
};

/**
 * Check if text contains Arabic characters
 */
export const containsArabic = (text: string): boolean => {
  if (!text) {return false;}
  return Array.from(text).some(char => isArabicCharacter(char));
};

/**
 * Determine if text is predominantly Arabic (>50% Arabic characters)
 */
export const isPredominantlyArabic = (text: string): boolean => {
  if (!text) {return false;}

  const chars = Array.from(text.replace(/\s/g, '')); // Remove whitespace
  if (chars.length === 0) {return false;}

  const arabicChars = chars.filter(char => isArabicCharacter(char));
  return arabicChars.length / chars.length > 0.5;
};

/**
 * Get text direction based on content
 */
export const getTextDirection = (text: string): 'rtl' | 'ltr' => {
  return isPredominantlyArabic(text) ? 'rtl' : 'ltr';
};

/**
 * Get text alignment based on content
 */
export const getTextAlign = (text: string): 'left' | 'right' | 'center' => {
  return getTextDirection(text) === 'rtl' ? 'right' : 'left';
};

/**
 * RTL layout directions
 */
export const RTL_DIRECTION = {
  RTL: 'rtl' as const,
  LTR: 'ltr' as const,
};

/**
 * Initialize RTL support for the app
 */
export const initializeRTL = () => {
  // Force RTL for development/testing
  // In production, this should be based on user preference or device locale
  I18nManager.allowRTL(true);

  // Uncomment to force RTL mode for testing
  // I18nManager.forceRTL(true);
};

/**
 * Check if RTL is currently enabled
 */
export const isRTLEnabled = (): boolean => {
  return I18nManager.isRTL;
};

/**
 * Get flex direction based on RTL state
 */
export const getFlexDirection = (reverse = false): 'row' | 'row-reverse' => {
  const isRTL = isRTLEnabled();
  if (reverse) {
    return isRTL ? 'row' : 'row-reverse';
  }
  return isRTL ? 'row-reverse' : 'row';
};

/**
 * Get margin/padding adjustments for RTL
 */
export const getRTLAdjustment = (leftValue: number, rightValue: number) => {
  const isRTL = isRTLEnabled();
  return {
    marginLeft: isRTL ? rightValue : leftValue,
    marginRight: isRTL ? leftValue : rightValue,
    paddingLeft: isRTL ? rightValue : leftValue,
    paddingRight: isRTL ? leftValue : rightValue,
  };
};

/**
 * Style helpers for RTL layouts
 */
export const rtlStyles = {
  /**
   * Container styles that adapt to RTL
   */
  container: {
    flexDirection: getFlexDirection() as 'row' | 'row-reverse',
  },

  /**
   * Text input styles for RTL
   */
  textInput: (text: string = '') => ({
    textAlign: getTextAlign(text),
    writingDirection: getTextDirection(text),
  }),

  /**
   * Chat message styles
   */
  chatBubble: (isUser: boolean, text: string = '') => {
    const isRTL = getTextDirection(text) === 'rtl';
    const userAlignment = isUser ? (isRTL ? 'flex-start' : 'flex-end') : (isRTL ? 'flex-end' : 'flex-start');

    return {
      alignSelf: userAlignment,
      textAlign: getTextAlign(text),
      writingDirection: getTextDirection(text),
    };
  },

  /**
   * Icon positioning for RTL
   */
  iconPosition: (position: 'left' | 'right') => {
    const isRTL = isRTLEnabled();
    if (position === 'left') {
      return isRTL ? { marginLeft: 8 } : { marginRight: 8 };
    } else {
      return isRTL ? { marginRight: 8 } : { marginLeft: 8 };
    }
  },
};

/**
 * Format text for proper RTL display
 */
export const formatRTLText = (text: string): string => {
  if (!text) {return text;}

  // Add RTL mark for proper text direction
  if (containsArabic(text)) {
    return `\u202B${text}\u202C`; // Right-to-Left Mark + text + Pop Directional Formatting
  }

  return text;
};

/**
 * Mixed content handling (Arabic + English in same text)
 */
export const formatMixedText = (text: string): string => {
  if (!text) {return text;}

  // Simple approach: if text contains both Arabic and Latin,
  // treat the whole text according to the predominant script
  return formatRTLText(text);
};

/**
 * Keyboard adjustment for RTL
 */
export const getKeyboardAvoidingOffset = () => {
  // iOS handles RTL automatically, Android might need adjustment
  return isRTLEnabled() ? { marginRight: 0, marginLeft: 0 } : {};
};

/**
 * Animation directions for RTL
 */
export const getAnimationDirection = (direction: 'left' | 'right') => {
  const isRTL = isRTLEnabled();
  if (direction === 'left') {
    return isRTL ? 'right' : 'left';
  } else {
    return isRTL ? 'left' : 'right';
  }
};

/**
 * Screen transition directions for RTL
 */
export const getScreenTransition = () => {
  return {
    cardStyleInterpolator: isRTLEnabled()
      ? require('@react-navigation/stack').CardStyleInterpolators.forHorizontalIOS
      : require('@react-navigation/stack').CardStyleInterpolators.forHorizontalIOS,
    gestureDirection: isRTLEnabled() ? 'horizontal-inverted' : 'horizontal',
  };
};
