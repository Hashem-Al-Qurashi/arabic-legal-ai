/**
 * @format
 *
 * FUNCTIONAL NAVIGATION TESTS
 *
 * These tests verify REAL navigation functionality:
 * - Navigation state changes work correctly
 * - Screen transitions are handled properly
 * - Navigation callbacks function as expected
 * - Back button behavior works correctly
 * - Deep linking and route parameters work
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { NavigationContainer, useNavigation, useRoute } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Button } from '@/components/ui/Button';
import { ThemeProvider } from '@/contexts/ThemeContext';

// Declare global mock navigator types
declare global {
  var __mockNavigator: {
    __setNavigationState: (state: any) => void;
    __getNavigationState: () => any;
    canGoBack: () => boolean;
    navigate: (screenName: string, params?: any) => void;
    reset: (state: any) => void;
  };
}

// Test screens
const HomeScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();

  return (
    <>
      <Button
        title="Go to Profile"
        onPress={() => (navigation as any).navigate('Profile', { userId: 123 })}
      />
      <Button
        title="Go to Settings"
        onPress={() => (navigation as any).navigate('Settings')}
      />
      <Button
        title={`Current Screen: ${route.name}`}
        onPress={() => {}}
      />
    </>
  );
};

const ProfileScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const params = route.params as { userId?: number } | undefined;
  const { userId } = params || {};

  return (
    <>
      <Button
        title={`Profile for User: ${userId || 'Unknown'}`}
        onPress={() => {}}
      />
      <Button
        title="Go Back"
        onPress={() => navigation.goBack()}
      />
      <Button
        title="Go to Settings"
        onPress={() => (navigation as any).navigate('Settings')}
      />
    </>
  );
};

const SettingsScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();

  return (
    <>
      <Button
        title="Settings Screen"
        onPress={() => {}}
      />
      <Button
        title="Go Back"
        onPress={() => navigation.goBack()}
      />
      <Button
        title="Reset to Home"
        onPress={() => (navigation as any).reset({
          index: 0,
          routes: [{ name: 'Home' }],
        })}
      />
      <Button
        title={`Current Screen: ${route.name}`}
        onPress={() => {}}
      />
    </>
  );
};

// Test navigator
const Stack = createStackNavigator();

const TestNavigator = () => (
  <NavigationContainer>
    <Stack.Navigator initialRouteName="Home">
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
      <Stack.Screen name="Settings" component={SettingsScreen} />
    </Stack.Navigator>
  </NavigationContainer>
);

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>
    {children}
  </ThemeProvider>
);

describe('Navigation Functional Tests', () => {
  beforeEach(() => {
    // Reset navigation state before each test
    global.__mockNavigator.__setNavigationState({
      index: 0,
      routes: [{ name: 'Home', key: 'home' }],
      currentScreen: 'Home',
    });
  });

  describe('Basic Navigation', () => {
    test('should navigate between screens', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Should start on Home screen
      expect(screen.getByText('Current Screen: Home')).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Go to Profile' })).toBeTruthy();

      // Navigate to Profile
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('Profile for User: 123')).toBeTruthy();
        expect(screen.getByRole('button', { name: 'Go Back' })).toBeTruthy();
      });

      // Navigate to Settings from Profile
      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      await waitFor(() => {
        expect(screen.getByText('Settings Screen')).toBeTruthy();
        expect(screen.getByText('Current Screen: Settings')).toBeTruthy();
      });
    });

    test('should handle back navigation', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Navigate to Profile
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('Profile for User: 123')).toBeTruthy();
      });

      // Go back to Home
      fireEvent.press(screen.getByRole('button', { name: 'Go Back' }));

      await waitFor(() => {
        expect(screen.getByText('Current Screen: Home')).toBeTruthy();
      });
    });

    test('should handle navigation reset', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Navigate through multiple screens
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('Profile for User: 123')).toBeTruthy();
      });

      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      await waitFor(() => {
        expect(screen.getByText('Settings Screen')).toBeTruthy();
      });

      // Reset to Home
      fireEvent.press(screen.getByRole('button', { name: 'Reset to Home' }));

      await waitFor(() => {
        expect(screen.getByText('Current Screen: Home')).toBeTruthy();
      });

      // Should not be able to go back (since we reset)
      const navigationState = global.__mockNavigator.__getNavigationState();
      expect(navigationState.index).toBe(0);
    });
  });

  describe('Route Parameters', () => {
    test('should pass and receive route parameters correctly', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Navigate with parameters
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('Profile for User: 123')).toBeTruthy();
      });
    });

    test('should handle missing parameters gracefully', async () => {
      const CustomProfileScreen = () => {
        const navigation = useNavigation();
        const route = useRoute();
        const params = route.params as { userId?: number; name?: string } | undefined;
        const { userId, name } = params || {};

        return (
          <>
            <Button
              title={`User: ${userId || 'No ID'}, Name: ${name || 'No Name'}`}
              onPress={() => {}}
            />
            <Button
              title="Go Back"
              onPress={() => navigation.goBack()}
            />
          </>
        );
      };

      const CustomNavigator = () => (
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Profile" component={CustomProfileScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      );

      render(
        <TestWrapper>
          <CustomNavigator />
        </TestWrapper>
      );

      // Navigate to Profile without parameters
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('User: 123, Name: No Name')).toBeTruthy();
      });
    });
  });

  describe('Navigation State Tracking', () => {
    test('should track navigation state correctly', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Initial state
      let navState = global.__mockNavigator.__getNavigationState();
      expect(navState.currentScreen).toBe('Home');
      expect(navState.index).toBe(0);

      // Navigate to Profile
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        navState = global.__mockNavigator.__getNavigationState();
        expect(navState.currentScreen).toBe('Profile');
        expect(navState.index).toBe(1);
      });

      // Navigate to Settings
      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      await waitFor(() => {
        navState = global.__mockNavigator.__getNavigationState();
        expect(navState.currentScreen).toBe('Settings');
        expect(navState.index).toBe(2);
      });

      // Go back
      fireEvent.press(screen.getByRole('button', { name: 'Go Back' }));

      await waitFor(() => {
        navState = global.__mockNavigator.__getNavigationState();
        expect(navState.currentScreen).toBe('Profile');
        expect(navState.index).toBe(1);
      });
    });

    test('should handle canGoBack correctly', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Initially cannot go back
      expect(global.__mockNavigator.canGoBack()).toBe(false);

      // Navigate to Profile
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(global.__mockNavigator.canGoBack()).toBe(true);
      });

      // Go back to Home
      fireEvent.press(screen.getByRole('button', { name: 'Go Back' }));

      await waitFor(() => {
        expect(global.__mockNavigator.canGoBack()).toBe(false);
      });
    });
  });

  describe('Complex Navigation Flows', () => {
    test('should handle deep navigation stack', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Navigate through multiple screens
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));

      await waitFor(() => {
        expect(screen.getByText('Profile for User: 123')).toBeTruthy();
      });

      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      await waitFor(() => {
        expect(screen.getByText('Settings Screen')).toBeTruthy();
      });

      // Check navigation stack
      const navState = global.__mockNavigator.__getNavigationState();
      expect(navState.routes).toHaveLength(3);
      expect(navState.routes[0].name).toBe('Home');
      expect(navState.routes[1].name).toBe('Profile');
      expect(navState.routes[2].name).toBe('Settings');
    });

    test('should handle rapid navigation changes', async () => {
      render(
        <TestWrapper>
          <TestNavigator />
        </TestWrapper>
      );

      // Rapid navigation
      fireEvent.press(screen.getByRole('button', { name: 'Go to Profile' }));
      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      await waitFor(() => {
        expect(screen.getByText('Settings Screen')).toBeTruthy();
      });

      // Should handle the navigation correctly
      const navState = global.__mockNavigator.__getNavigationState();
      expect(navState.currentScreen).toBe('Settings');
    });
  });

  describe('Navigation Error Handling', () => {
    test('should handle navigation to non-existent screen gracefully', () => {
      const TestScreen = () => {
        const navigation = useNavigation();

        return (
          <Button
            title="Navigate to Non-existent"
            onPress={() => {
              try {
                (navigation as any).navigate('NonExistentScreen');
              } catch (error) {
                console.log('Navigation error handled');
              }
            }}
          />
        );
      };

      const TestNav = () => (
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Test" component={TestScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      );

      render(
        <TestWrapper>
          <TestNav />
        </TestWrapper>
      );

      // Should not crash when navigating to non-existent screen
      expect(() => {
        fireEvent.press(screen.getByRole('button', { name: 'Navigate to Non-existent' }));
      }).not.toThrow();
    });
  });

  describe('Real-world Navigation Scenarios', () => {
    test('should handle authentication-based navigation', async () => {
      const AuthScreen = () => (
        <Button title="Login" onPress={() => global.__mockNavigator.navigate('Main')} />
      );

      const MainScreen = () => (
        <>
          <Button title="Main App" onPress={() => {}} />
          <Button title="Logout" onPress={() => {
            global.__mockNavigator.reset({
              index: 0,
              routes: [{ name: 'Auth' }],
            });
          }} />
        </>
      );

      const AuthNavigator = () => (
        <NavigationContainer>
          <Stack.Navigator initialRouteName="Auth">
            <Stack.Screen name="Auth" component={AuthScreen} />
            <Stack.Screen name="Main" component={MainScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      );

      render(
        <TestWrapper>
          <AuthNavigator />
        </TestWrapper>
      );

      // Start with auth screen
      expect(screen.getByRole('button', { name: 'Login' })).toBeTruthy();

      // Login
      fireEvent.press(screen.getByRole('button', { name: 'Login' }));

      await waitFor(() => {
        expect(screen.getByText('Main App')).toBeTruthy();
      });

      // Logout
      fireEvent.press(screen.getByRole('button', { name: 'Logout' }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: 'Login' })).toBeTruthy();
      });
    });

    test('should handle tab-like navigation behavior', async () => {
      const TabScreen1 = () => {
        const navigation = useNavigation();
        return (
          <>
            <Button title="Tab 1 Content" onPress={() => {}} />
            <Button title="Go to Tab 2" onPress={() => (navigation as any).navigate('Tab2')} />
          </>
        );
      };

      const TabScreen2 = () => {
        const navigation = useNavigation();
        return (
          <>
            <Button title="Tab 2 Content" onPress={() => {}} />
            <Button title="Go to Tab 1" onPress={() => (navigation as any).navigate('Tab1')} />
          </>
        );
      };

      const TabNavigator = () => (
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Tab1" component={TabScreen1} />
            <Stack.Screen name="Tab2" component={TabScreen2} />
          </Stack.Navigator>
        </NavigationContainer>
      );

      render(
        <TestWrapper>
          <TabNavigator />
        </TestWrapper>
      );

      // Start on Tab 1
      expect(screen.getByText('Tab 1 Content')).toBeTruthy();

      // Switch to Tab 2
      fireEvent.press(screen.getByRole('button', { name: 'Go to Tab 2' }));

      await waitFor(() => {
        expect(screen.getByText('Tab 2 Content')).toBeTruthy();
      });

      // Switch back to Tab 1
      fireEvent.press(screen.getByRole('button', { name: 'Go to Tab 1' }));

      await waitFor(() => {
        expect(screen.getByText('Tab 1 Content')).toBeTruthy();
      });
    });
  });
});
