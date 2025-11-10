/**
 * @format
 *
 * INTEGRATION TESTS
 *
 * These tests verify that components work together as a system:
 * - Authentication flow with real API calls
 * - Navigation between screens
 * - Form validation and submission
 * - Error handling across components
 * - State management integration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LoginForm } from '@/components/auth/LoginForm';
import { Button } from '@/components/ui/Button';
import { server, serverUtils } from './mocks/server';
import { http, HttpResponse } from 'msw';

// Mock Alert
jest.spyOn(Alert, 'alert');

// Test app component that demonstrates integration
const TestApp = () => {
  const { isAuthenticated, user, logout, loading } = useAuth();

  // Show loading state during authentication check
  if (loading) {
    return (
      <Button
        title="Loading..."
        onPress={() => {}}
        disabled
      />
    );
  }

  // Use authentication state directly instead of local state
  if (!isAuthenticated) {
    return (
      <LoginForm
        onSuccess={() => {}}
        onSwitchToRegister={() => console.log('Switch to register')}
      />
    );
  }

  return (
    <>
      <Button
        title={`Welcome, ${user?.full_name || 'User'}!`}
        onPress={() => {}}
      />
      <Button
        title="Logout"
        onPress={logout}
        variant="secondary"
      />
    </>
  );
};

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('Integration Tests', () => {
  beforeEach(async () => {
    serverUtils.resetData();
    jest.clearAllMocks();
    // Clear AsyncStorage to ensure clean state
    const AsyncStorage = require('@react-native-async-storage/async-storage');
    await AsyncStorage.clear();
  });

  describe('Authentication Flow Integration', () => {
    test('should handle complete login and logout flow', async () => {
      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Should start with login form
      expect(screen.getByText('Sign In')).toBeTruthy();
      expect(screen.getByLabelText('Email')).toBeTruthy();
      expect(screen.getByLabelText('Password')).toBeTruthy();

      // User logs in
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const loginButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(loginButton);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should transition to logged-in state
      await waitFor(() => {
        expect(screen.getByText('Welcome, Test User!')).toBeTruthy();
        expect(screen.getByRole('button', { name: 'Logout' })).toBeTruthy();
      }, { timeout: 3000 });

      // User logs out
      const logoutButton = screen.getByRole('button', { name: 'Logout' });
      fireEvent.press(logoutButton);

      // Should return to login form
      await waitFor(() => {
        expect(screen.getByText('Sign In')).toBeTruthy();
      });
    });

    test('should handle login failure and retry', async () => {
      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Try to login with wrong credentials
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const loginButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'wrong@example.com');
      fireEvent.changeText(passwordInput, 'wrongpassword');
      fireEvent.press(loginButton);

      // Should show error
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          'Invalid credentials'
        );
      }, { timeout: 3000 });

      // Form should still be visible
      expect(screen.getByText('Sign In')).toBeTruthy();

      // User can try again with correct credentials
      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(loginButton);

      // Should succeed this time
      await waitFor(() => {
        expect(screen.getByText('Welcome, Test User!')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Form Validation Integration', () => {
    test('should validate form fields and show errors', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Submit empty form
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // Fill invalid email
      fireEvent.changeText(screen.getByLabelText('Email'), 'invalid');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      });

      // Fix email but add short password
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), '123');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeTruthy();
      });

      // Fix password - errors should clear
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');

      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull();
        expect(screen.queryByText('Password is required')).toBeNull();
        expect(screen.queryByText('Please enter a valid email address')).toBeNull();
        expect(screen.queryByText('Password must be at least 6 characters')).toBeNull();
      });
    });
  });

  describe('State Management Integration', () => {
    test('should maintain authentication state across components', async () => {
      const TestComponent = () => {
        const { isAuthenticated, user } = useAuth();

        if (isAuthenticated) {
          return <Button title={`Logged in as: ${user?.email}`} onPress={() => {}} />;
        }

        return (
          <>
            <Button title="Not logged in" onPress={() => {}} />
            <LoginForm onSuccess={() => {}} />
          </>
        );
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      // Initially not authenticated
      expect(screen.getByText('Not logged in')).toBeTruthy();

      // Login
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      // Should update state across components
      await waitFor(() => {
        expect(screen.getByText('Logged in as: test@example.com')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Error Handling Integration', () => {
    test('should handle network errors gracefully across components', async () => {
      // Simulate network failure
      server.use(
        http.post('*/api/auth/login', () => {
          return HttpResponse.error();
        })
      );

      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Try to login
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      // Should show network error
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          'Network error. Please try again.'
        );
      }, { timeout: 3000 });

      // App should remain functional
      expect(screen.getByText('Sign In')).toBeTruthy();
    });
  });

  describe('Component Interaction Integration', () => {
    test('should handle multiple component interactions', async () => {
      const MultiComponentTest = () => {
        const [counter, setCounter] = React.useState(0);
        const [showForm, setShowForm] = React.useState(true);

        return (
          <>
            <Button
              title={`Counter: ${counter}`}
              onPress={() => setCounter(c => c + 1)}
            />
            <Button
              title={showForm ? 'Hide Form' : 'Show Form'}
              onPress={() => setShowForm(!showForm)}
              variant="secondary"
            />
            {showForm && (
              <LoginForm onSuccess={() => setShowForm(false)} />
            )}
          </>
        );
      };

      render(
        <TestWrapper>
          <MultiComponentTest />
        </TestWrapper>
      );

      // Test counter button
      expect(screen.getByText('Counter: 0')).toBeTruthy();
      fireEvent.press(screen.getByRole('button', { name: 'Counter: 0' }));
      expect(screen.getByText('Counter: 1')).toBeTruthy();

      // Test form visibility toggle
      expect(screen.getByText('Sign In')).toBeTruthy();
      fireEvent.press(screen.getByRole('button', { name: 'Hide Form' }));

      await waitFor(() => {
        expect(screen.queryByText('Sign In')).toBeNull();
        expect(screen.getByText('Show Form')).toBeTruthy();
      });

      // Show form again and test login
      fireEvent.press(screen.getByRole('button', { name: 'Show Form' }));

      await waitFor(() => {
        expect(screen.getByText('Sign In')).toBeTruthy();
      });

      // Login should hide form
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.queryByText('Sign In')).toBeNull();
        expect(screen.getByText('Show Form')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Real User Workflow Integration', () => {
    test('should handle complete user journey', async () => {
      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // User sees login form
      expect(screen.getByText('Welcome back to Arabic Legal AI')).toBeTruthy();

      // User tries empty form
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
      });

      // User enters email but forgets password
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // User enters password and submits
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      // User sees loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // User is logged in successfully
      await waitFor(() => {
        expect(screen.getByText('Welcome, Test User!')).toBeTruthy();
      }, { timeout: 3000 });

      // User can interact with app
      expect(screen.getByRole('button', { name: 'Logout' })).toBeTruthy();

      // User logs out
      fireEvent.press(screen.getByRole('button', { name: 'Logout' }));

      // User is back to login form
      await waitFor(() => {
        expect(screen.getByText('Sign In')).toBeTruthy();
      });
    });
  });
});
