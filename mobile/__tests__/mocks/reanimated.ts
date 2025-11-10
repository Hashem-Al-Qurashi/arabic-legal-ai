/**
 * Functional React Native Reanimated Mock
 *
 * This mock provides TESTABLE animation functionality:
 * - Animations can be triggered and completed
 * - Shared values can be updated and observed
 * - Animation timing can be controlled in tests
 * - Gesture handling can be simulated
 */

import React from 'react';
import { View, Text, ScrollView, Image } from 'react-native';

// Animation state tracking
const animationState = {
  runningAnimations: new Map<string, any>(),
  sharedValues: new Map<string, any>(),
  animationCallbacks: new Map<string, Function[]>(),
};

// Mock shared value implementation
const createSharedValue = (initialValue: any) => {
  const id = Math.random().toString(36);
  const sharedValue = {
    value: initialValue,
    _id: id,
    addListener: (callback: Function) => {
      const callbacks = animationState.animationCallbacks.get(id) || [];
      callbacks.push(callback);
      animationState.animationCallbacks.set(id, callbacks);
    },
    removeListener: (callback: Function) => {
      const callbacks = animationState.animationCallbacks.get(id) || [];
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    },
  };

  animationState.sharedValues.set(id, sharedValue);

  // Proxy to track value changes
  return new Proxy(sharedValue, {
    set(target, prop, value) {
      if (prop === 'value') {
        const oldValue = target.value;
        target.value = value;

        // Notify listeners
        const callbacks = animationState.animationCallbacks.get(id) || [];
        callbacks.forEach(callback => callback(value, oldValue));

        return true;
      }
      return Reflect.set(target, prop, value);
    },
  });
};

// Mock animation functions
const withTiming = jest.fn((toValue: any, config?: any, callback?: Function) => {
  // Simulate animation completion after a short delay
  setTimeout(() => {
    callback && callback(true);
  }, config?.duration || 300);

  return toValue;
});

const withSpring = jest.fn((toValue: any, config?: any, callback?: Function) => {
  setTimeout(() => {
    callback && callback(true);
  }, config?.duration || 500);

  return toValue;
});

const withDelay = jest.fn((_delay: number, animation: any) => {
  return animation;
});

const withSequence = jest.fn((...animations: any[]) => {
  return animations[animations.length - 1];
});

const withRepeat = jest.fn((animation: any, _numberOfReps?: number) => {
  return animation;
});

// Mock animated components
const createMockComponent = (BaseComponent: any) => {
  const MockComponent = React.forwardRef((props: any, ref: any) => {
    return React.createElement(BaseComponent, { ...props, ref });
  });

  MockComponent.displayName = `Animated.${BaseComponent.displayName || BaseComponent.name || 'Component'}`;
  return MockComponent;
};

// Mock gesture detection
const createGesture = (type: string): any => ({
  enabled: jest.fn((): any => createGesture(type)),
  numberOfTaps: jest.fn((): any => createGesture(type)),
  minDistance: jest.fn((): any => createGesture(type)),
  direction: jest.fn((): any => createGesture(type)),
  minDuration: jest.fn((): any => createGesture(type)),
  onStart: jest.fn((): any => createGesture(type)),
  onUpdate: jest.fn((): any => createGesture(type)),
  onEnd: jest.fn((): any => createGesture(type)),
  runOnJS: jest.fn((): any => createGesture(type)),
});

// Test utilities for controlling animations
export const animationTestUtils = {
  // Advance all animations to completion
  completeAllAnimations: () => {
    animationState.runningAnimations.forEach((animation, _id) => {
      if (animation.callback) {
        animation.callback(true);
      }
    });
    animationState.runningAnimations.clear();
  },

  // Get current shared value
  getSharedValue: (sharedValue: any) => sharedValue.value,

  // Update shared value and trigger listeners
  setSharedValue: (sharedValue: any, newValue: any) => {
    sharedValue.value = newValue;
  },

  // Check if animations are running
  hasRunningAnimations: () => animationState.runningAnimations.size > 0,

  // Reset animation state
  resetAnimationState: () => {
    animationState.runningAnimations.clear();
    animationState.sharedValues.clear();
    animationState.animationCallbacks.clear();
  },
};

// Export the mock
export const ReanimatedMock = {
  default: {
    View: createMockComponent(View),
    Text: createMockComponent(Text),
    ScrollView: createMockComponent(ScrollView),
    Image: createMockComponent(Image),
    createAnimatedComponent: createMockComponent,
    call: jest.fn(),
  },
  View: createMockComponent(View),
  Text: createMockComponent(Text),
  ScrollView: createMockComponent(ScrollView),
  Image: createMockComponent(Image),
  createAnimatedComponent: createMockComponent,

  // Animation functions
  useSharedValue: jest.fn(createSharedValue),
  useDerivedValue: jest.fn((fn: Function) => {
    const derivedValue = createSharedValue(fn());
    return derivedValue;
  }),
  useAnimatedStyle: jest.fn((styleFunction: Function) => {
    try {
      return styleFunction();
    } catch {
      return {};
    }
  }),
  useAnimatedProps: jest.fn((propsFunction: Function) => {
    try {
      return propsFunction();
    } catch {
      return {};
    }
  }),
  useAnimatedGestureHandler: jest.fn((handlers: any) => handlers),
  useWorkletCallback: jest.fn((fn: Function) => fn),

  // Animation timing
  withTiming,
  withSpring,
  withDelay,
  withSequence,
  withRepeat,

  // Easing functions
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

  // Utilities
  runOnJS: jest.fn((fn: Function) => (...args: any[]) => {
    // Simulate running on JS thread
    setTimeout(() => fn(...args), 0);
  }),
  runOnUI: jest.fn((fn: Function) => fn),
  interpolate: jest.fn((_value: number, _inputRange: number[], outputRange: number[]) => {
    if (!outputRange || outputRange.length === 0) {return 0;}
    return outputRange[0];
  }),
  interpolateColor: jest.fn(() => '#000000'),
  makeMutable: jest.fn(createSharedValue),
  makeRemote: jest.fn((value: any) => value),

  // Layout animations
  enableLayoutAnimations: jest.fn(),
  disableLayoutAnimations: jest.fn(),

  // Gesture handling
  getRelativeCoords: jest.fn(() => ({ x: 0, y: 0 })),
  measure: jest.fn(() => ({ x: 0, y: 0, width: 100, height: 100 })),
  dispatchCommand: jest.fn(),
  setGestureState: jest.fn(),

  // Lists
  FlatList: createMockComponent(require('react-native').FlatList),
  SectionList: createMockComponent(require('react-native').SectionList),

  // Test utilities
  __testUtils: animationTestUtils,
};

// Gesture mock
export const GestureMock = {
  Tap: () => createGesture('tap'),
  Pan: () => createGesture('pan'),
  Pinch: () => createGesture('pinch'),
  Rotation: () => createGesture('rotation'),
  Fling: () => createGesture('fling'),
  LongPress: () => createGesture('longPress'),
  ForceTouch: () => createGesture('forceTouch'),
  Native: () => createGesture('native'),
  Race: (..._gestures: any[]) => createGesture('race'),
  Simultaneous: (..._gestures: any[]) => createGesture('simultaneous'),
  Exclusive: (..._gestures: any[]) => createGesture('exclusive'),
};
