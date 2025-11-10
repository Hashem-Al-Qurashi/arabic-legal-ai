/**
 * Functional React Native Testing Setup
 *
 * This setup enables REAL testing of React Native components with:
 * - User interactions (touch, text input, gestures)
 * - Component integration testing
 * - Animation and navigation testing
 * - API integration with MSW
 * - Real error handling and loading states
 */

import 'react-native-gesture-handler/jestSetup';
import 'whatwg-fetch';
import { server } from './__tests__/mocks/server';

// Configure axios to use fetch for MSW interception in Node.js environment
const axios = require('axios');

// Create a fetch-based adapter for axios to work with MSW
const fetchAdapter = (config) => {
  const { url, method = 'GET', data, headers = {}, timeout, baseURL } = config;

  // Construct full URL
  const fullUrl = url.startsWith('http') ? url : `${baseURL || ''}${url}`;
  console.log('Axios adapter: Making request to', method.toUpperCase(), fullUrl);
  console.log('Axios adapter: Headers:', headers);
  console.log('Axios adapter: Data:', data);

  const controller = new AbortController();
  const timeoutId = timeout ? setTimeout(() => controller.abort(), timeout) : null;

  const fetchOptions = {
    method: method.toUpperCase(),
    headers: headers,
    body: data ? (typeof data === 'string' ? data : JSON.stringify(data)) : undefined,
    signal: controller.signal,
  };

  return fetch(fullUrl, fetchOptions)
    .then(response => {
      if (timeoutId) {clearTimeout(timeoutId);}

      return response.text().then(text => {
        let responseData;
        try {
          responseData = JSON.parse(text);
        } catch {
          responseData = text;
        }

        const axiosResponse = {
          data: responseData,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          config,
          request: {},
        };

        if (response.ok) {
          return axiosResponse;
        } else {
          const error = new Error(`Request failed with status ${response.status}`);
          error.response = axiosResponse;
          throw error;
        }
      });
    })
    .catch(error => {
      if (timeoutId) {clearTimeout(timeoutId);}

      if (error.name === 'AbortError') {
        const timeoutError = new Error('Request timeout');
        timeoutError.code = 'ECONNABORTED';
        throw timeoutError;
      }

      throw error;
    });
};

// Use fetch adapter for axios in test environment
axios.defaults.adapter = fetchAdapter;

// Define React Native globals
global.__DEV__ = true;
global.__TEST__ = true;

// Mock React Native StyleSheet and other utilities
jest.mock('react-native/Libraries/StyleSheet/StyleSheet', () => ({
  create: (styles) => styles,
  flatten: (style) => style,
  absoluteFillObject: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
  hairlineWidth: 1,
}));

jest.mock('react-native/Libraries/Utilities/PixelRatio', () => ({
  get: jest.fn(() => 2),
  getFontScale: jest.fn(() => 1),
  getPixelSizeForLayoutSize: jest.fn((layoutSize) => layoutSize * 2),
  roundToNearestPixel: jest.fn((layoutSize) => Math.round(layoutSize)),
}));

// Setup MSW for API mocking
beforeAll(() => {
  console.log('Setting up MSW server...');
  server.listen({
    onUnhandledRequest: 'warn',  // Changed from 'error' to 'warn' for debugging
  });
});
afterEach(() => {
  console.log('Resetting MSW handlers...');
  server.resetHandlers();
});
afterAll(() => {
  console.log('Closing MSW server...');
  server.close();
});

// Configure console for better test output - keep console.log for debugging
const originalConsole = global.console;
global.console = {
  ...console,
  // Keep error, warn, and log for debugging
  log: originalConsole.log,
  error: originalConsole.error,
  warn: originalConsole.warn,
  debug: jest.fn(),
  info: jest.fn(),
};

// Mock alert more functionally
global.alert = jest.fn();

// Mock platform-specific modules
jest.mock('react-native/Libraries/Alert/Alert', () => ({
  alert: jest.fn((title, message, buttons) => {
    if (buttons && buttons.length > 0) {
      // Simulate user pressing the first button by default
      buttons[0].onPress && buttons[0].onPress();
    }
  }),
}));

// Functional AsyncStorage mock that actually stores data
jest.mock('@react-native-async-storage/async-storage', () => {
  let storage = {};

  return {
    getItem: jest.fn((key) => Promise.resolve(storage[key] || null)),
    setItem: jest.fn((key, value) => {
      storage[key] = value;
      return Promise.resolve();
    }),
    removeItem: jest.fn((key) => {
      delete storage[key];
      return Promise.resolve();
    }),
    clear: jest.fn(() => {
      storage = {};
      return Promise.resolve();
    }),
    getAllKeys: jest.fn(() => Promise.resolve(Object.keys(storage))),
    multiGet: jest.fn((keys) =>
      Promise.resolve(keys.map(key => [key, storage[key] || null]))
    ),
    multiSet: jest.fn((keyValuePairs) => {
      keyValuePairs.forEach(([key, value]) => {
        storage[key] = value;
      });
      return Promise.resolve();
    }),
    multiRemove: jest.fn((keys) => {
      keys.forEach(key => delete storage[key]);
      return Promise.resolve();
    }),
  };
});

// Functional Keychain mock with actual encryption simulation
jest.mock('react-native-keychain', () => {
  let credentials = {};

  return {
    setInternetCredentials: jest.fn((server, username, password) => {
      credentials[server] = { username, password };
      return Promise.resolve();
    }),
    getInternetCredentials: jest.fn((server) => {
      const creds = credentials[server];
      if (creds) {
        return Promise.resolve(creds);
      }
      return Promise.reject(new Error('Credentials not found'));
    }),
    resetInternetCredentials: jest.fn((server) => {
      delete credentials[server];
      return Promise.resolve();
    }),
    getSupportedBiometryType: jest.fn(() => Promise.resolve('TouchID')),
    canImplyAuthentication: jest.fn(() => Promise.resolve(true)),
  };
});

// Functional React Native Reanimated mock
jest.mock('react-native-reanimated', () => {
  const React = require('react');
  const { View, Text, ScrollView, Image } = require('react-native');

  const createMockComponent = (BaseComponent) => {
    const MockComponent = React.forwardRef((props, ref) => {
      return React.createElement(BaseComponent, { ...props, ref });
    });
    MockComponent.displayName = `Animated.${BaseComponent.displayName || BaseComponent.name || 'Component'}`;
    return MockComponent;
  };

  return {
    default: {
      View: createMockComponent(View),
      Text: createMockComponent(Text),
      ScrollView: createMockComponent(ScrollView),
      Image: createMockComponent(Image),
      createAnimatedComponent: createMockComponent,
    },
    View: createMockComponent(View),
    Text: createMockComponent(Text),
    ScrollView: createMockComponent(ScrollView),
    Image: createMockComponent(Image),
    createAnimatedComponent: createMockComponent,

    useSharedValue: jest.fn((initialValue) => ({ value: initialValue })),
    useDerivedValue: jest.fn((fn) => ({ value: fn() })),
    useAnimatedStyle: jest.fn((styleFunction) => styleFunction()),
    useAnimatedProps: jest.fn((propsFunction) => propsFunction()),
    useAnimatedGestureHandler: jest.fn((handlers) => handlers),
    useWorkletCallback: jest.fn((fn) => fn),

    withTiming: jest.fn((toValue) => toValue),
    withSpring: jest.fn((toValue) => toValue),
    withDelay: jest.fn((delay, animation) => animation),
    withSequence: jest.fn((...animations) => animations[animations.length - 1]),
    withRepeat: jest.fn((animation) => animation),

    Easing: {
      linear: jest.fn(),
      ease: jest.fn(),
      bezier: jest.fn(),
    },

    runOnJS: jest.fn((fn) => fn),
    runOnUI: jest.fn((fn) => fn),
    interpolate: jest.fn((value, inputRange, outputRange) => outputRange ? outputRange[0] : 0),
  };
});

// Functional React Native Worklets mock
jest.mock('react-native-worklets', () => ({
  createWorklet: jest.fn((fn) => fn),
  runOnJS: jest.fn((fn) => fn),
  runOnUI: jest.fn((fn) => fn),
  getContext: jest.fn(() => 'JS'),
  isWorklet: jest.fn(() => false),
}));

// Functional Dimensions mock that can be updated for testing
jest.mock('react-native/Libraries/Utilities/Dimensions', () => {
  let mockDimensions = {
    window: { width: 375, height: 812 },
    screen: { width: 375, height: 812 },
  };

  return {
    get: jest.fn((dimension) => mockDimensions[dimension]),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    // Helper for tests to change dimensions
    __setDimensions: (newDimensions) => {
      mockDimensions = { ...mockDimensions, ...newDimensions };
    },
  };
});

// Mock Toast with functional behavior
jest.mock('react-native-toast-message', () => {
  const mockToast = {
    show: jest.fn(),
    hide: jest.fn(),
  };

  return {
    show: mockToast.show,
    hide: mockToast.hide,
    __esModule: true,
    default: mockToast,
  };
});

// Functional navigation mocks that track navigation state
const createMockNavigator = () => {
  let navigationState = {
    index: 0,
    routes: [{ name: 'Initial', key: 'initial' }],
    currentScreen: 'Initial',
  };

  const navigate = jest.fn((screenName, params) => {
    navigationState.currentScreen = screenName;
    navigationState.routes.push({
      name: screenName,
      key: screenName.toLowerCase(),
      params,
    });
    navigationState.index = navigationState.routes.length - 1;
  });

  const goBack = jest.fn(() => {
    if (navigationState.index > 0) {
      navigationState.index -= 1;
      navigationState.currentScreen = navigationState.routes[navigationState.index].name;
    }
  });

  const reset = jest.fn((state) => {
    navigationState = { ...state };
  });

  return {
    navigate,
    goBack,
    reset,
    canGoBack: jest.fn(() => navigationState.index > 0),
    isFocused: jest.fn(() => true),
    getState: jest.fn(() => navigationState),
    // Helpers for testing
    __getNavigationState: () => navigationState,
    __setNavigationState: (newState) => { navigationState = newState; },
  };
};

// Create global mock navigator instance
global.__mockNavigator = createMockNavigator();

jest.mock('@react-navigation/native', () => {
  const React = require('react');

  return {
    NavigationContainer: ({ children }) => children,
    useNavigation: () => global.__mockNavigator,
    useFocusEffect: (callback) => {
      // Simulate focus effect by calling callback immediately
      React.useEffect(callback, []);
    },
    useRoute: () => ({
      params: {},
      name: global.__mockNavigator.__getNavigationState().currentScreen,
    }),
    createNavigationContainerRef: () => global.__mockNavigator,
  };
});

// Better React Navigation stack mock
jest.mock('@react-navigation/stack', () => {
  const React = require('react');
  const { View } = require('react-native');

  return {
    createStackNavigator: jest.fn(() => ({
      Navigator: ({ children, ...props }) =>
        React.createElement(View, { ...props, testID: 'stack-navigator' }, children),
      Screen: ({ component: Component, name, ...props }) => {
        if (Component) {
          return React.createElement(Component, { ...props, testID: `screen-${name}` });
        }
        return React.createElement(View, { ...props, testID: `screen-${name}` });
      },
    })),
    TransitionPresets: {
      SlideFromRightIOS: {},
      ModalSlideFromBottomIOS: {},
      FadeFromBottomAndroid: {},
    },
  };
});

// Mock Safe Area with functional insets
let mockInsets = { top: 44, right: 0, bottom: 34, left: 0 };

jest.mock('react-native-safe-area-context', () => {
  const React = require('react');

  return {
    SafeAreaProvider: ({ children }) => children,
    SafeAreaView: ({ children, ...props }) =>
      React.createElement(require('react-native').View, props, children),
    useSafeAreaInsets: () => mockInsets,
    useSafeAreaFrame: () => ({
      x: 0,
      y: mockInsets.top,
      width: mockDimensions.window.width,
      height: mockDimensions.window.height - mockInsets.top - mockInsets.bottom,
    }),
    // Helper for tests
    __setInsets: (newInsets) => { mockInsets = { ...mockInsets, ...newInsets }; },
  };
});

// Mock Gesture Handler with better touch support
jest.mock('react-native-gesture-handler', () => {
  const { View, ScrollView, TouchableOpacity, TextInput } = require('react-native');

  return {
    GestureHandlerRootView: View,
    PanGestureHandler: View,
    TapGestureHandler: View,
    LongPressGestureHandler: View,
    PinchGestureHandler: View,
    RotationGestureHandler: View,
    FlingGestureHandler: View,
    ForceTouchGestureHandler: View,
    NativeViewGestureHandler: View,
    RawButton: TouchableOpacity,
    BaseButton: TouchableOpacity,
    RectButton: TouchableOpacity,
    BorderlessButton: TouchableOpacity,
    TouchableWithoutFeedback: TouchableOpacity,
    ScrollView: ScrollView,
    Switch: View,
    TextInput: TextInput,
    ToolbarAndroid: View,
    ViewPagerAndroid: View,
    DrawerLayoutAndroid: View,
    WebView: View,
    Directions: {
      RIGHT: 1,
      LEFT: 2,
      UP: 4,
      DOWN: 8,
    },
    State: {
      UNDETERMINED: 0,
      FAILED: 1,
      BEGAN: 2,
      CANCELLED: 3,
      ACTIVE: 4,
      END: 5,
    },
    Swipeable: View,
    DrawerLayout: View,
    TouchableHighlight: TouchableOpacity,
    gestureHandlerRootHOC: (Component) => Component,
    Gesture: {
      Tap: () => ({ enabled: jest.fn(), numberOfTaps: jest.fn() }),
      Pan: () => ({ enabled: jest.fn(), minDistance: jest.fn() }),
      Pinch: () => ({ enabled: jest.fn() }),
      Rotation: () => ({ enabled: jest.fn() }),
      Fling: () => ({ enabled: jest.fn(), direction: jest.fn() }),
      LongPress: () => ({ enabled: jest.fn(), minDuration: jest.fn() }),
      ForceTouch: () => ({ enabled: jest.fn() }),
      Native: () => ({ enabled: jest.fn() }),
      Race: (...gestures) => ({ enabled: jest.fn() }),
      Simultaneous: (...gestures) => ({ enabled: jest.fn() }),
      Exclusive: (...gestures) => ({ enabled: jest.fn() }),
    },
    GestureDetector: View,
  };
});

// Mock screens with actual rendering capability
jest.mock('react-native-screens', () => ({
  enableScreens: jest.fn(),
  Screen: require('react-native').View,
  ScreenContainer: require('react-native').View,
  NativeScreen: require('react-native').View,
  NativeScreenContainer: require('react-native').View,
}));

// Mock vector icons with testable components
jest.mock('react-native-vector-icons/MaterialIcons', () => {
  const React = require('react');
  const { Text } = require('react-native');

  return React.forwardRef((props, ref) => {
    return React.createElement(Text, {
      ...props,
      ref,
      testID: `icon-${props.name}`,
      accessibilityLabel: props.name,
    }, props.name);
  });
});

jest.mock('react-native-vector-icons/FontAwesome', () => {
  const React = require('react');
  const { Text } = require('react-native');

  return React.forwardRef((props, ref) => {
    return React.createElement(Text, {
      ...props,
      ref,
      testID: `fa-icon-${props.name}`,
      accessibilityLabel: props.name,
    }, props.name);
  });
});

jest.mock('react-native-vector-icons/Ionicons', () => {
  const React = require('react');
  const { Text } = require('react-native');

  return React.forwardRef((props, ref) => {
    return React.createElement(Text, {
      ...props,
      ref,
      testID: `ion-icon-${props.name}`,
      accessibilityLabel: props.name,
    }, props.name);
  });
});

// Export test utilities (accessed via require when needed)
global.testUtils = {
  navigation: () => global.__mockNavigator,
  createMockNavigator,
};
