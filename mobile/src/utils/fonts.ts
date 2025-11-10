import { Platform } from 'react-native';

/**
 * Font configuration for Arabic Legal AI Mobile
 * Supports both Arabic and Latin text with proper fallbacks
 */

// Font family definitions
export const FONTS = {
  // System fonts that support Arabic
  arabic: {
    regular: Platform.select({
      ios: 'NotoSansArabic-Regular', // Custom Arabic font
      android: 'NotoSansArabic-Regular', // Custom Arabic font
      default: 'NotoSansArabic-Regular',
    }),
    bold: Platform.select({
      ios: 'NotoSansArabic-Bold',
      android: 'NotoSansArabic-Bold',
      default: 'NotoSansArabic-Bold',
    }),
  },

  // Latin fonts for English text
  latin: {
    regular: Platform.select({
      ios: 'San Francisco',
      android: 'Roboto',
      default: 'sans-serif',
    }),
    bold: Platform.select({
      ios: 'San Francisco-Bold',
      android: 'Roboto-Bold',
      default: 'sans-serif',
    }),
    medium: Platform.select({
      ios: 'San Francisco-Medium',
      android: 'Roboto-Medium',
      default: 'sans-serif',
    }),
  },

  // Custom fonts (actual available fonts)
  custom: {
    // Available Arabic fonts in assets
    notoSansArabic: 'NotoSansArabic-Regular',
    notoSansArabicBold: 'NotoSansArabic-Bold',
    notoKufiArabic: 'NotoKufiArabic-Regular',
    notoNaskhArabic: 'NotoNaskhArabic-Regular',
  },
} as const;

/**
 * Utility functions for font handling
 */

export const isArabicText = (text: string): boolean => {
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  return arabicRegex.test(text);
};

export const getFontFamily = (
  text: string,
  weight: 'regular' | 'bold' | 'medium' = 'regular'
): string => {
  const isArabic = isArabicText(text);

  if (isArabic) {
    return weight === 'bold' ? FONTS.arabic.bold : FONTS.arabic.regular;
  } else {
    switch (weight) {
      case 'bold':
        return FONTS.latin.bold;
      case 'medium':
        return FONTS.latin.medium || FONTS.latin.regular;
      default:
        return FONTS.latin.regular;
    }
  }
};

export const getTextDirection = (text: string): 'rtl' | 'ltr' => {
  return isArabicText(text) ? 'rtl' : 'ltr';
};

/**
 * Font style presets for common use cases
 */

export const fontStyles = {
  // Heading styles
  h1: {
    fontSize: 28,
    fontWeight: 'bold' as const,
    lineHeight: 36,
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold' as const,
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  h4: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 24,
  },

  // Body text styles
  body: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: 'normal' as const,
    lineHeight: 20,
  },

  // UI element styles
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal' as const,
    lineHeight: 16,
  },

  // Chat-specific styles
  messageUser: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 22,
  },
  messageAssistant: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
  },
} as const;

/**
 * Create font style object with automatic font family selection
 */
export const createFontStyle = (
  text: string,
  preset: keyof typeof fontStyles
) => {
  const baseStyle = fontStyles[preset];
  const fontFamily = getFontFamily(text, baseStyle.fontWeight as any);
  const textAlign = getTextDirection(text) === 'rtl' ? 'right' : 'left';

  return {
    ...baseStyle,
    fontFamily,
    textAlign,
    writingDirection: getTextDirection(text),
  };
};

/**
 * Instructions for adding custom fonts
 */
export const FONT_SETUP_INSTRUCTIONS = `
To add custom Arabic fonts to your React Native project:

1. Add font files to: src/assets/fonts/
   - Recommended formats: .ttf, .otf
   - Example files:
     * Amiri-Regular.ttf (Arabic)
     * Amiri-Bold.ttf (Arabic) 
     * Inter-Regular.ttf (Latin)
     * Inter-Bold.ttf (Latin)

2. Update react-native.config.js:
   module.exports = {
     assets: ['./src/assets/fonts/'],
   };

3. Run font linking command:
   npx react-native link

4. Update FONTS.custom object in this file with your font names

5. For iOS: Verify fonts are added to Info.plist under UIAppFonts

6. For Android: Verify fonts are copied to android/app/src/main/assets/fonts/

Popular Arabic fonts to consider:
- Amiri (serif, traditional)
- Cairo (sans-serif, modern)
- Almarai (sans-serif, clean)
- Tajawal (sans-serif, geometric)
- Markazi Text (serif, display)
`;
