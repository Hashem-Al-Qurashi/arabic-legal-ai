/**
 * Legacy Jest Setup (kept for compatibility)
 *
 * This file contains the old mocking setup.
 * For functional testing, see jest.functional.setup.js
 */

import 'react-native-gesture-handler/jestSetup';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

// Mock react-native-vector-icons
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');
jest.mock('react-native-vector-icons/FontAwesome', () => 'Icon');
jest.mock('react-native-vector-icons/Ionicons', () => 'Icon');

// Mock react-native-reanimated
jest.mock('react-native-reanimated', () => {
  const React = require('react');
  const { View, Text, ScrollView, Image } = require('react-native');
  const Animated = require('react-native').Animated;

  const createMockComponent = (BaseComponent) => {
    const MockComponent = React.forwardRef((props, ref) => {
      return React.createElement(BaseComponent, { ...props, ref });
    });
    MockComponent.displayName = `Reanimated.${BaseComponent.displayName || BaseComponent.name || 'Component'}`;
    return MockComponent;
  };

  return {
    default: {
      View: createMockComponent(View),
      Text: createMockComponent(Text),
      ScrollView: createMockComponent(ScrollView),
      Image: createMockComponent(Image),
      createAnimatedComponent: (component) => createMockComponent(component),
      call: jest.fn(),
    },
    View: createMockComponent(View),
    Text: createMockComponent(Text),
    ScrollView: createMockComponent(ScrollView),
    Image: createMockComponent(Image),
    createAnimatedComponent: (component) => createMockComponent(component),
    Easing: {
      linear: jest.fn(),
      ease: jest.fn(),
      quad: jest.fn(),
      cubic: jest.fn(),
      poly: jest.fn(),
      sin: jest.fn(),
      circle: jest.fn(),
      exp: jest.fn(),
      elastic: jest.fn(),
      back: jest.fn(),
      bounce: jest.fn(),
      bezier: jest.fn(),
      in: jest.fn(),
      out: jest.fn(),
      inOut: jest.fn(),
    },
    useSharedValue: jest.fn((value) => ({ value })),
    useDerivedValue: jest.fn((fn) => ({ value: fn && typeof fn === 'function' ? fn() : undefined })),
    useAnimatedStyle: jest.fn((fn) => (fn && typeof fn === 'function' ? fn() : {})),
    useAnimatedGestureHandler: jest.fn(() => ({})),
    useAnimatedProps: jest.fn(() => ({})),
    useWorkletCallback: jest.fn((fn) => fn),
    withSpring: jest.fn((value) => value),
    withTiming: jest.fn((value) => value),
    withDelay: jest.fn((delay, value) => value),
    withSequence: jest.fn((...values) => values[values.length - 1]),
    withRepeat: jest.fn((value) => value),
    runOnJS: jest.fn((fn) => fn),
    runOnUI: jest.fn((fn) => fn),
    interpolate: jest.fn((value, inputRange, outputRange) => outputRange ? outputRange[0] : 0),
    interpolateColor: jest.fn(() => '#000000'),
    makeMutable: jest.fn((value) => ({ value })),
    makeRemote: jest.fn((value) => value),
    startMapper: jest.fn(),
    stopMapper: jest.fn(),
    enableLayoutAnimations: jest.fn(),
    disableLayoutAnimations: jest.fn(),
    getRelativeCoords: jest.fn(),
    measure: jest.fn(),
    dispatchCommand: jest.fn(),
    setGestureState: jest.fn(),
    FlatList: createMockComponent(require('react-native').FlatList),
    SectionList: createMockComponent(require('react-native').SectionList),
  };
});

// Mock react-native-worklets
jest.mock('react-native-worklets', () => ({
  createWorklet: jest.fn((fn) => fn),
  runOnJS: jest.fn((fn) => fn),
  runOnUI: jest.fn((fn) => fn),
  getContext: jest.fn(() => 'JS'),
  isWorklet: jest.fn(() => false),
  createSharedValue: jest.fn((value) => ({ value })),
  useDerivedValue: jest.fn((fn) => ({ value: fn() })),
  useSharedValue: jest.fn((value) => ({ value })),
  useWorkletCallback: jest.fn((fn) => fn),
  withSpring: jest.fn((value) => value),
  withTiming: jest.fn((value) => value),
  withDelay: jest.fn((delay, value) => value),
  withSequence: jest.fn((...values) => values[values.length - 1]),
  withRepeat: jest.fn((value) => value),
  Easing: {
    linear: jest.fn(),
    ease: jest.fn(),
    quad: jest.fn(),
    cubic: jest.fn(),
    poly: jest.fn(),
    sin: jest.fn(),
    circle: jest.fn(),
    exp: jest.fn(),
    elastic: jest.fn(),
    back: jest.fn(),
    bounce: jest.fn(),
    bezier: jest.fn(),
    in: jest.fn(),
    out: jest.fn(),
    inOut: jest.fn(),
  },
}));

// Mock @tanstack/react-query
jest.mock('@tanstack/react-query', () => {
  const mockQueryClient = {
    clear: jest.fn(),
    getQueryData: jest.fn(),
    setQueryData: jest.fn(),
    invalidateQueries: jest.fn(),
    removeQueries: jest.fn(),
    cancelQueries: jest.fn(),
    fetchQuery: jest.fn(),
    prefetchQuery: jest.fn(),
    ensureQueryData: jest.fn(),
    setQueriesData: jest.fn(),
    invalidateQueries: jest.fn(),
    refetchQueries: jest.fn(),
    resetQueries: jest.fn(),
    isFetching: jest.fn(),
    isMutating: jest.fn(),
    getDefaults: jest.fn(),
    setDefaults: jest.fn(),
    getMutationDefaults: jest.fn(),
    setMutationDefaults: jest.fn(),
    mount: jest.fn(),
    unmount: jest.fn(),
  };

  return {
    QueryClient: jest.fn(() => mockQueryClient),
    QueryClientProvider: ({ children }) => children,
    useQuery: jest.fn(() => ({
      data: undefined,
      error: null,
      isLoading: false,
      isError: false,
      isSuccess: true,
      refetch: jest.fn(),
    })),
    useMutation: jest.fn(() => ({
      mutate: jest.fn(),
      mutateAsync: jest.fn(),
      isLoading: false,
      isError: false,
      isSuccess: false,
      data: undefined,
      error: null,
      reset: jest.fn(),
    })),
    useQueryClient: jest.fn(() => mockQueryClient),
    useInfiniteQuery: jest.fn(() => ({
      data: { pages: [], pageParams: [] },
      error: null,
      isLoading: false,
      isError: false,
      isSuccess: true,
      fetchNextPage: jest.fn(),
      fetchPreviousPage: jest.fn(),
      hasNextPage: false,
      hasPreviousPage: false,
      isFetchingNextPage: false,
      isFetchingPreviousPage: false,
    })),
    useIsFetching: jest.fn(() => 0),
    useIsMutating: jest.fn(() => 0),
    useMutationState: jest.fn(() => []),
    useQueries: jest.fn(() => []),
    useSuspenseQuery: jest.fn(() => ({
      data: undefined,
      error: null,
      refetch: jest.fn(),
    })),
    useSuspenseInfiniteQuery: jest.fn(() => ({
      data: { pages: [], pageParams: [] },
      error: null,
      fetchNextPage: jest.fn(),
      fetchPreviousPage: jest.fn(),
      hasNextPage: false,
      hasPreviousPage: false,
      isFetchingNextPage: false,
      isFetchingPreviousPage: false,
    })),
    QueryCache: jest.fn(),
    MutationCache: jest.fn(),
    focusManager: {
      setEventListener: jest.fn(),
      setFocused: jest.fn(),
      isFocused: jest.fn(() => true),
    },
    onlineManager: {
      setEventListener: jest.fn(),
      setOnline: jest.fn(),
      isOnline: jest.fn(() => true),
    },
    notifyManager: {
      setBatchNotifyFunction: jest.fn(),
      setScheduler: jest.fn(),
      batchCalls: jest.fn((fn) => fn()),
    },
    hashQueryKey: jest.fn(),
    isServer: false,
  };
});

// Mock react-native-toast-message
jest.mock('react-native-toast-message', () => ({
  show: jest.fn(),
  hide: jest.fn(),
  __esModule: true,
  default: {
    show: jest.fn(),
    hide: jest.fn(),
  },
}));

// Mock react-native-keychain
jest.mock('react-native-keychain', () => ({
  setInternetCredentials: jest.fn(() => Promise.resolve()),
  getInternetCredentials: jest.fn(() => Promise.resolve({ username: '', password: '' })),
  resetInternetCredentials: jest.fn(() => Promise.resolve()),
  getSupportedBiometryType: jest.fn(() => Promise.resolve('TouchID')),
  canImplyAuthentication: jest.fn(() => Promise.resolve(true)),
}));

// Mock react-native-svg
jest.mock('react-native-svg', () => {
  const React = require('react');
  const { View } = require('react-native');

  const mockComponent = (name) => {
    const MockedComponent = React.forwardRef((props, ref) => {
      return React.createElement(View, { ...props, ref, testID: name });
    });
    MockedComponent.displayName = name;
    return MockedComponent;
  };

  return {
    Svg: mockComponent('Svg'),
    Circle: mockComponent('Circle'),
    Ellipse: mockComponent('Ellipse'),
    G: mockComponent('G'),
    Text: mockComponent('SvgText'),
    TSpan: mockComponent('TSpan'),
    TextPath: mockComponent('TextPath'),
    Path: mockComponent('Path'),
    Polygon: mockComponent('Polygon'),
    Polyline: mockComponent('Polyline'),
    Line: mockComponent('Line'),
    Rect: mockComponent('Rect'),
    Use: mockComponent('Use'),
    Image: mockComponent('SvgImage'),
    Symbol: mockComponent('Symbol'),
    Defs: mockComponent('Defs'),
    LinearGradient: mockComponent('LinearGradient'),
    RadialGradient: mockComponent('RadialGradient'),
    Stop: mockComponent('Stop'),
    ClipPath: mockComponent('ClipPath'),
    Pattern: mockComponent('Pattern'),
    Mask: mockComponent('Mask'),
    Marker: mockComponent('Marker'),
    ForeignObject: mockComponent('ForeignObject'),
  };
});

// Mock @react-navigation
jest.mock('@react-navigation/native', () => {
  return {
    NavigationContainer: ({ children }) => children,
    useNavigation: () => ({
      navigate: jest.fn(),
      goBack: jest.fn(),
      reset: jest.fn(),
      canGoBack: jest.fn(() => true),
      isFocused: jest.fn(() => true),
    }),
    useFocusEffect: jest.fn(),
    useRoute: () => ({
      params: {},
      name: 'MockRoute',
    }),
    createNavigationContainerRef: jest.fn(),
  };
});

jest.mock('@react-navigation/stack', () => {
  const React = require('react');
  return {
    createStackNavigator: jest.fn(() => ({
      Navigator: ({ children }) => React.createElement('div', { testID: 'stack-navigator' }, children),
      Screen: ({ children }) => React.createElement('div', { testID: 'stack-screen' }, children),
    })),
    TransitionPresets: {},
  };
});

jest.mock('@react-navigation/bottom-tabs', () => {
  const React = require('react');
  return {
    createBottomTabNavigator: jest.fn(() => ({
      Navigator: ({ children }) => React.createElement('div', { testID: 'tab-navigator' }, children),
      Screen: ({ children }) => React.createElement('div', { testID: 'tab-screen' }, children),
    })),
  };
});

jest.mock('@react-navigation/drawer', () => {
  const React = require('react');
  return {
    createDrawerNavigator: jest.fn(() => ({
      Navigator: ({ children }) => React.createElement('div', { testID: 'drawer-navigator' }, children),
      Screen: ({ children }) => React.createElement('div', { testID: 'drawer-screen' }, children),
    })),
  };
});

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => {
  const React = require('react');
  return {
    SafeAreaProvider: ({ children }) => children,
    SafeAreaView: ({ children }) => children,
    useSafeAreaInsets: () => ({ top: 0, right: 0, bottom: 0, left: 0 }),
    useSafeAreaFrame: () => ({ x: 0, y: 0, width: 375, height: 812 }),
  };
});

// Mock react-native-gesture-handler components
jest.mock('react-native-gesture-handler', () => {
  const View = require('react-native').View;
  const Text = require('react-native').Text;
  const ScrollView = require('react-native').ScrollView;
  const TouchableOpacity = require('react-native').TouchableOpacity;

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
    TextInput: require('react-native').TextInput,
    ToolbarAndroid: View,
    ViewPagerAndroid: View,
    DrawerLayoutAndroid: View,
    WebView: View,
    Directions: {},
    State: {},
    Swipeable: View,
    DrawerLayout: View,
    TouchableHighlight: TouchableOpacity,
    gestureHandlerRootHOC: (Component) => Component,
    Gesture: {
      Tap: () => ({}),
      Pan: () => ({}),
      Pinch: () => ({}),
      Rotation: () => ({}),
      Fling: () => ({}),
      LongPress: () => ({}),
      ForceTouch: () => ({}),
      Native: () => ({}),
      Race: () => ({}),
      Simultaneous: () => ({}),
      Exclusive: () => ({}),
    },
    GestureDetector: View,
  };
});

// Mock react-native-screens
jest.mock('react-native-screens', () => ({
  enableScreens: jest.fn(),
  Screen: require('react-native').View,
  ScreenContainer: require('react-native').View,
  NativeScreen: require('react-native').View,
  NativeScreenContainer: require('react-native').View,
}));

// Context providers not mocked - will use real implementation in functional tests

// API services not mocked - will use real implementation with MSW in functional tests

// Mock screens
jest.mock('@/screens/AuthScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return React.forwardRef((props, ref) => {
    return React.createElement(View, { ref, testID: 'auth-screen' },
      React.createElement(Text, {}, 'Auth Screen')
    );
  });
});

jest.mock('@/screens/ChatScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return React.forwardRef((props, ref) => {
    return React.createElement(View, { ref, testID: 'chat-screen' },
      React.createElement(Text, {}, 'Chat Screen')
    );
  });
});

jest.mock('@/screens/ConversationsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return React.forwardRef((props, ref) => {
    return React.createElement(View, { ref, testID: 'conversations-screen' },
      React.createElement(Text, {}, 'Conversations Screen')
    );
  });
});

jest.mock('@/screens/SettingsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return React.forwardRef((props, ref) => {
    return React.createElement(View, { ref, testID: 'settings-screen' },
      React.createElement(Text, {}, 'Settings Screen')
    );
  });
});

// Mock utils
jest.mock('@/utils/rtl', () => ({
  initializeRTL: jest.fn(),
  isRTL: jest.fn(() => true),
  getTextDirection: jest.fn(() => 'rtl'),
}));

// Silence the warning: Animated: `useNativeDriver` is not supported
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');
