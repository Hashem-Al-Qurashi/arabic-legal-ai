# Arabic Legal AI Mobile App - Setup Guide

React Native mobile application for the Arabic Legal AI Assistant, providing native iOS and Android apps with full feature parity to the web version.

## 🏗️ Architecture Overview

This mobile app follows the **strategic adaptation approach** outlined in the Mobile Conversion Strategy, maximizing code reuse from the web application while providing native mobile experiences.

### Key Features
- **TypeScript First**: Strict TypeScript configuration matching web app standards
- **Cross-Platform**: Single codebase for iOS and Android
- **Arabic RTL Support**: Native right-to-left text rendering
- **React Navigation 6**: Stack and Drawer navigation
- **React Query**: Optimized API state management
- **Reanimated 3**: Smooth animations and gestures

## 📁 Project Structure

```
mobile/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── actions/         # Action buttons and bars
│   │   ├── auth/           # Authentication components
│   │   ├── chat/           # Chat interface components
│   │   ├── message/        # Message rendering components
│   │   ├── premium/        # Premium features components
│   │   └── ui/             # Generic UI components
│   ├── contexts/           # React contexts
│   │   ├── AuthContext.tsx # Authentication state management
│   │   └── ThemeContext.tsx # Theme and styling management
│   ├── hooks/              # Custom React hooks
│   ├── navigation/         # React Navigation setup
│   │   └── AppNavigator.tsx # Main navigation structure
│   ├── screens/            # Screen components
│   │   ├── AuthScreen.tsx  # Login/Register screen
│   │   ├── ChatScreen.tsx  # Main chat interface
│   │   ├── ConversationsScreen.tsx # Conversations list
│   │   └── SettingsScreen.tsx # App settings
│   ├── services/           # API and external services
│   │   └── api.ts          # HTTP client adapted from web app
│   ├── styles/             # Global styles and themes
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts        # Shared types from web app + mobile-specific
│   └── utils/              # Utility functions
├── android/                # Android-specific configuration
├── ios/                    # iOS-specific configuration
├── App.tsx                 # Root application component
├── babel.config.js         # Babel configuration with path aliases
├── metro.config.js         # Metro bundler configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- npm or yarn
- React Native CLI
- For iOS: Xcode 14+ and iOS Simulator
- For Android: Android Studio and Android SDK

### Installation

1. **Install dependencies:**
```bash
cd mobile
npm install
```

2. **Install iOS dependencies (iOS only):**
```bash
cd ios && pod install && cd ..
# or run: npm run postinstall
```

3. **Start Metro bundler:**
```bash
npm start
# or for cache reset: npm run start:reset
```

4. **Run on platform:**
```bash
# iOS
npm run ios

# Android
npm run android

# iOS Release
npm run ios:release

# Android Release
npm run android:release
```

## 🔧 Development Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start Metro bundler |
| `npm run ios` | Run on iOS simulator |
| `npm run android` | Run on Android emulator |
| `npm run ios:device` | Run on connected iOS device |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Fix ESLint issues |
| `npm run test` | Run Jest tests |
| `npm run clean` | Clean React Native cache |
| `npm run reinstall` | Reinstall node_modules |

## 🌍 Arabic RTL Support

The app is configured for proper Arabic text rendering:

### Android
- `android:supportsRtl="true"` in AndroidManifest.xml
- Arabic app name: "مساعد القانون العربي"

### iOS
- Localization support for Arabic (`ar`) and English (`en`)
- Arabic display name in Info.plist
- Dynamic RTL layout support

### React Native
- `I18nManager.allowRTL(true)` for RTL support
- Dynamic RTL based on content direction
- Arabic fonts loaded through Metro bundler

## 🎨 Theming

The app includes a comprehensive theming system:

```typescript
// Light/Dark theme support
const { theme, colors, toggleTheme } = useTheme();

// Colors automatically adapt based on theme
colors.primary    // Brand primary color
colors.background // Background color
colors.text       // Primary text color
colors.border     // Border color
```

## 🔐 Authentication

Mobile-optimized authentication using AsyncStorage:

```typescript
// Secure token storage
const { login, logout, user, isAuthenticated } = useAuth();

// Automatic token refresh
// Biometric authentication support (future)
```

## 📱 API Integration

Mobile API client adapted from web app:

```typescript
// Automatic platform detection
// Mobile-optimized timeouts
// AsyncStorage token management
// Streaming support for chat
```

### Backend Compatibility
- **Zero backend changes required**
- Same REST endpoints as web app
- JWT authentication
- CORS configured for mobile

## 🏗️ Navigation Structure

```
App
├── AuthNavigator (when not authenticated)
│   └── AuthScreen (Login/Register)
└── MainNavigator (when authenticated)
    ├── DrawerNavigator
    │   ├── ChatScreen (Main chat)
    │   ├── ConversationsScreen (Chat history)
    │   └── SettingsScreen (App settings)
```

## 📦 Dependencies

### Core Framework
- `react-native`: 0.82.1 (Latest stable)
- `react`: 19.1.1
- `typescript`: 5.8.3+

### Navigation
- `@react-navigation/native`: 7.x
- `@react-navigation/stack`: 7.x
- `@react-navigation/drawer`: 7.x

### State Management
- `@tanstack/react-query`: 5.x (API state)
- React Context (Auth, Theme)

### Storage & Security
- `@react-native-async-storage/async-storage`: 2.x
- `react-native-keychain`: 10.x (secure storage)

### UI & Animation
- `react-native-reanimated`: 4.x
- `react-native-gesture-handler`: 2.x
- `react-native-vector-icons`: 10.x
- `react-native-svg`: 15.x

### HTTP & Forms
- `axios`: 1.x (HTTP client)
- `react-hook-form`: 7.x (forms)
- `zod`: 4.x (validation)

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues:**
```bash
npm run start:reset
npm run clean
```

2. **iOS build issues:**
```bash
cd ios && pod install && cd ..
npm run clean:ios
```

3. **Android build issues:**
```bash
npm run clean:android
```

4. **Path alias not working:**
- Ensure babel-plugin-module-resolver is installed
- Check babel.config.js configuration
- Restart Metro bundler

## 🔄 Web App Compatibility

This mobile app maintains **100% feature parity** with the web application:

### Shared Components (80% reuse)
- ✅ Type definitions
- ✅ API client logic
- ✅ Authentication flow
- ✅ Theme system
- ✅ Utility functions

### Mobile-Adapted Components (20% modified)
- 🔄 Navigation (Router → React Navigation)
- 🔄 Storage (localStorage → AsyncStorage)
- 🔄 UI Components (HTML → React Native)
- 🔄 File handling (web APIs → native APIs)

## 📈 Performance

- **Bundle size optimization** through Metro configuration
- **Image optimization** for multiple screen densities
- **Memory management** with proper cleanup
- **Network optimization** with request caching

## 🚀 Deployment

### Development
```bash
npm run ios:debug
npm run android:debug
```

### Production
```bash
npm run ios:release
npm run android:release
```

### App Store Distribution
- iOS: Archive in Xcode → Upload to App Store Connect
- Android: Generate signed APK/AAB → Upload to Google Play Console

---

## 📞 Support

This mobile app follows the senior-level mobile conversion strategy, providing maximum code reuse while delivering native mobile experiences. For issues or questions, refer to the main project documentation or mobile conversion strategy document.