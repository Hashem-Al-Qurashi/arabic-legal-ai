/**
 * @format
 */

// import React from 'react'; // Unused import
import ReactTestRenderer from 'react-test-renderer';
import { View, Text } from 'react-native';

// Simple test to validate Jest configuration is working
test('Jest configuration is working', () => {
  expect(true).toBe(true);
});

test('React Test Renderer is working', () => {
  const component = ReactTestRenderer.create(<div>Test</div>);
  expect(component).toBeDefined();
});

test('Mock functions are working', () => {
  const mockFn = jest.fn();
  mockFn('test');
  expect(mockFn).toHaveBeenCalledWith('test');
});

test('React Native components render correctly', () => {
  const TestComponent = () => (
    <View testID="test-view">
      <Text testID="test-text">Hello React Native</Text>
    </View>
  );

  const component = ReactTestRenderer.create(<TestComponent />);
  expect(component).toBeDefined();

  const testInstance = component.root;
  const viewElement = testInstance.findByProps({ testID: 'test-view' });
  const textElement = testInstance.findByProps({ testID: 'test-text' });

  expect(viewElement).toBeDefined();
  expect(textElement).toBeDefined();
});

test('React Native Reanimated mocks are working', () => {
  const reanimated = require('react-native-reanimated');

  expect(reanimated.useSharedValue).toBeDefined();
  expect(reanimated.useAnimatedStyle).toBeDefined();
  expect(reanimated.withSpring).toBeDefined();
  expect(reanimated.withTiming).toBeDefined();

  // Test that mocked functions return expected values
  const sharedValue = reanimated.useSharedValue(0);
  expect(sharedValue).toEqual({ value: 0 });

  const animatedStyle = reanimated.useAnimatedStyle(() => ({ opacity: 1 }));
  expect(animatedStyle).toEqual({ opacity: 1 });
});

test('TanStack React Query mocks are working', () => {
  const reactQuery = require('@tanstack/react-query');

  expect(reactQuery.QueryClient).toBeDefined();
  expect(reactQuery.QueryClientProvider).toBeDefined();
  expect(reactQuery.useQuery).toBeDefined();
  expect(reactQuery.useMutation).toBeDefined();

  // Test that mocked hooks return expected values
  const queryResult = reactQuery.useQuery();
  expect(queryResult).toEqual({
    data: undefined,
    error: null,
    isLoading: false,
    isError: false,
    isSuccess: true,
    refetch: expect.any(Function),
  });
});

test('Navigation mocks are working', () => {
  const navigation = require('@react-navigation/native');
  const stack = require('@react-navigation/stack');
  const drawer = require('@react-navigation/drawer');

  expect(navigation.NavigationContainer).toBeDefined();
  expect(navigation.useNavigation).toBeDefined();
  expect(stack.createStackNavigator).toBeDefined();
  expect(drawer.createDrawerNavigator).toBeDefined();

  // Test that navigation hooks return expected values
  const nav = navigation.useNavigation();
  expect(nav.navigate).toBeDefined();
  expect(nav.goBack).toBeDefined();
});

test('React Native third-party library mocks are working', () => {
  const gestureHandler = require('react-native-gesture-handler');
  const safeAreaContext = require('react-native-safe-area-context');
  const asyncStorage = require('@react-native-async-storage/async-storage');
  const vectorIcons = require('react-native-vector-icons/MaterialIcons');

  expect(gestureHandler.GestureHandlerRootView).toBeDefined();
  expect(safeAreaContext.SafeAreaProvider).toBeDefined();
  expect(asyncStorage.getItem).toBeDefined();
  expect(vectorIcons).toBeDefined();
});
