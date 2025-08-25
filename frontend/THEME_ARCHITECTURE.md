# Theme Architecture Documentation

## Overview
This document describes the theme architecture implemented for the Arabic Legal AI application. The system provides a clean, maintainable approach to theming with light mode as default and dark mode as an optional override.

## Architecture Principles

### 1. Single Source of Truth
- All theme variables are defined in CSS custom properties (CSS variables)
- Theme configuration is centralized in `src/styles/theme.config.ts`
- No hardcoded colors outside the theme system

### 2. Light Mode as Default
- Light mode is the default experience
- No dependency on system preferences
- Clean white backgrounds (#ffffff) for light mode
- Dark mode is an explicit user choice

### 3. Theme Application Method
- Theme is controlled via `.dark-mode` class on the root element (`<html>`)
- CSS variables cascade from `:root` (light mode) and `:root.dark-mode` (dark mode)
- Smooth transitions between themes (0.3s duration)

## File Structure

### Core Theme Files

#### `/src/index.css`
- Defines base CSS variables for light mode in `:root`
- Overrides variables for dark mode in `:root.dark-mode`
- Sets fundamental colors without component-specific styles

#### `/src/App.css`
- Extends index.css with application-specific variables
- Defines component-level theme variables
- Uses CSS variables exclusively (no hardcoded colors)

#### `/src/styles/theme.config.ts`
- TypeScript configuration for theme constants
- Helper functions for theme application
- Storage management for theme preference
- Single source of truth for theme-related constants

#### `/src/hooks/useTheme.ts`
- React hook for theme management
- Handles theme toggling
- Persists preference to localStorage
- Updates DOM and meta tags

## CSS Variable Structure

### Base Colors (index.css)
```css
:root {
  /* Light Mode (Default) */
  --color-text-primary: #1f2937;
  --color-background: #ffffff;
  /* ... */
}

:root.dark-mode {
  /* Dark Mode Override */
  --color-text-primary: #f9fafb;
  --color-background: #111827;
  /* ... */
}
```

### Application Variables (App.css)
```css
:root {
  /* Extends base with app-specific */
  --primary-color: #1e40af;
  --background-white: #ffffff;
  --border-light: #e5e7eb;
  /* ... */
}

:root.dark-mode {
  /* Dark mode overrides */
  --background-white: #111827;
  --border-light: #374151;
  /* ... */
}
```

## Implementation Details

### Theme Toggle Flow
1. User clicks theme toggle button
2. `useTheme` hook updates state
3. `.dark-mode` class is added/removed from `<html>`
4. CSS variables automatically cascade
5. Preference saved to localStorage
6. Meta theme-color updated for mobile browsers

### Component Usage
```tsx
// Import the hook
import { useTheme } from './hooks/useTheme';

// Use in component
const { isDark, toggleTheme } = useTheme();

// Apply in JSX
<button onClick={toggleTheme}>
  {isDark ? 'Light Mode' : 'Dark Mode'}
</button>
```

### CSS Usage
```css
/* Use variables, not hardcoded colors */
.component {
  background: var(--background-white);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

/* Dark mode automatically applied via cascade */
/* No need for .dark-mode selectors in most cases */
```

## Migration from Old System

### What Changed
1. **Removed**: `color-scheme: light dark` - caused conflicts
2. **Removed**: Hardcoded dark colors in `:root`
3. **Removed**: `[data-theme="dark"]` selectors
4. **Removed**: Media queries for `prefers-color-scheme`
5. **Added**: Centralized theme configuration
6. **Added**: Consistent `.dark-mode` class approach
7. **Fixed**: Light mode now properly shows white backgrounds

### Breaking Changes
- Components using `[data-theme="dark"]` must use `:root.dark-mode`
- Direct color values must be replaced with CSS variables
- localStorage key changed from `dark-mode` to `theme-preference`

## Best Practices

### DO
- ✅ Use CSS variables for all colors
- ✅ Define colors in root or App.css
- ✅ Use semantic variable names
- ✅ Test both light and dark modes
- ✅ Ensure sufficient contrast ratios

### DON'T
- ❌ Hardcode colors in components
- ❌ Use inline styles for colors
- ❌ Mix theme approaches
- ❌ Forget mobile meta theme-color
- ❌ Create component-specific dark mode classes

## Testing Checklist

- [ ] Light mode shows white backgrounds
- [ ] Dark mode shows dark backgrounds
- [ ] Theme persists after refresh
- [ ] Transitions are smooth
- [ ] No flash of incorrect theme on load
- [ ] Mobile browser chrome matches theme
- [ ] All text is readable in both modes
- [ ] Form inputs work in both modes

## Performance Considerations

- CSS variables are performant and cached by browsers
- Theme changes don't require re-renders (CSS-only)
- Transitions use GPU-accelerated properties
- No JavaScript theme calculations during runtime

## Future Enhancements

Potential improvements while maintaining architecture:
- Additional theme presets (high contrast, sepia)
- Theme-aware images and icons
- Automatic theme scheduling
- Per-component theme overrides
- Theme animation preferences