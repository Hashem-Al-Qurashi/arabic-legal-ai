/**
 * @format
 *
 * COMPREHENSIVE AUTHENTICATION FLOW TESTS
 *
 * This file contains end-to-end authentication flow tests that verify:
 * - Complete login/logout cycles
 * - API integration with MSW
 * - Authentication state management
 * - Error handling and recovery
 * - Real user workflows
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Alert } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { Button } from '@/components/ui/Button';
import { server, serverUtils } from './mocks/server';
import { http, HttpResponse } from 'msw';

// Mock Alert
jest.spyOn(Alert, 'alert');

// Create wrapper with all necessary providers
const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Test component that shows authentication state
const AuthStateDisplay = () => {
  const { isAuthenticated, user, loading, logout } = useAuth();

  if (loading) {
    return <Button title="Loading auth..." onPress={() => {}} disabled />;
  }

  if (isAuthenticated && user) {
    return (
      <>
        <Button title={`Authenticated: ${user.email}`} onPress={() => {}} />
        <Button title="Logout" onPress={logout} variant="secondary" />
      </>
    );
  }

  return <Button title="Not authenticated" onPress={() => {}} />;
};

// Full app component for integration testing
const TestApp = () => {
  const { isAuthenticated, user, loading } = useAuth();
  const [showRegister, setShowRegister] = React.useState(false);

  if (loading) {
    return <Button title="App loading..." onPress={() => {}} disabled />;
  }

  if (!isAuthenticated) {
    return (
      <>
        {showRegister ? (
          <RegisterForm
            onSuccess={() => setShowRegister(false)}
            onSwitchToLogin={() => setShowRegister(false)}
          />
        ) : (
          <LoginForm
            onSuccess={() => {}}
            onSwitchToRegister={() => setShowRegister(true)}
          />
        )}
      </>
    );
  }

  return (
    <>
      <Button title={`Welcome ${user?.full_name || 'User'}!`} onPress={() => {}} />
      <AuthStateDisplay />
    </>
  );
};

describe('Comprehensive Authentication Flow Tests', () => {
  let TestWrapper: ReturnType<typeof createTestWrapper>;

  beforeEach(async () => {
    TestWrapper = createTestWrapper();
    serverUtils.resetData();
    jest.clearAllMocks();

    // Clear AsyncStorage to ensure clean state
    const AsyncStorage = require('@react-native-async-storage/async-storage');
    await AsyncStorage.clear();

    // Reset MSW handlers
    server.resetHandlers();
  });

  describe('Authentication State Management', () => {
    test('should start unauthenticated and handle initial auth check', async () => {
      render(
        <TestWrapper>
          <AuthStateDisplay />
        </TestWrapper>
      );

      // Should start with loading state
      expect(screen.getByText('Loading auth...')).toBeTruthy();

      // Should transition to unauthenticated state
      await waitFor(() => {
        expect(screen.getByText('Not authenticated')).toBeTruthy();
      }, { timeout: 3000 });
    });

    test('should maintain authentication state when token exists', async () => {
      // Pre-populate AsyncStorage with valid token
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      await AsyncStorage.setItem('access_token', 'valid_token');

      // Set up MSW to recognize this token
      serverUtils.setAuthenticatedUser({
        id: '1',
        name: 'Test User',
        full_name: 'Test User',
        email: 'test@example.com',
        subscription_tier: 'free',
        is_active: true,
        is_verified: true,
        questions_used_current_cycle: 0,
        cycle_reset_time: null,
      }, 'valid_token');

      render(
        <TestWrapper>
          <AuthStateDisplay />
        </TestWrapper>
      );

      // Should start loading
      expect(screen.getByText('Loading auth...')).toBeTruthy();

      // Should recognize existing authentication
      await waitFor(() => {
        expect(screen.getByText('Authenticated: test@example.com')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Login Flow', () => {
    test('should complete full login flow successfully', async () => {
      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Wait for initial auth check
      await waitFor(() => {
        expect(screen.queryByText('App loading...')).toBeNull();
      });

      // Should show login form
      expect(screen.getByText('Sign In')).toBeTruthy();

      // Perform login
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      // Should show loading indicator
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should complete login and show welcome message
      await waitFor(() => {
        expect(screen.getByText('Welcome Test User!')).toBeTruthy();
        expect(screen.getByText('Authenticated: test@example.com')).toBeTruthy();
      }, { timeout: 5000 });
    });

    test('should handle login errors correctly', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Try invalid credentials
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'wrong@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'wrongpassword');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      // Should show error alert
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          'Invalid credentials'
        );
      }, { timeout: 3000 });

      // Form should still be visible for retry
      expect(screen.getByText('Sign In')).toBeTruthy();
    });

    test('should handle network errors during login', async () => {
      // Simulate network error
      server.use(
        http.post('*/api/auth/login', () => {
          return HttpResponse.error();
        })
      );

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          'Network error. Please try again.'
        );
      }, { timeout: 3000 });
    });
  });

  describe('Registration Flow', () => {
    test('should complete registration flow successfully', async () => {
      render(
        <TestWrapper>
          <RegisterForm />
        </TestWrapper>
      );

      // Fill registration form
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Full Name'), 'New User');
        fireEvent.changeText(screen.getByLabelText('Email'), 'newuser@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));
      });

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should complete registration
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Registration Successful',
          'You can now sign in with your new account.'
        );
      }, { timeout: 3000 });
    });

    test('should handle registration with existing email', async () => {
      render(
        <TestWrapper>
          <RegisterForm />
        </TestWrapper>
      );

      // Try to register with existing email
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Full Name'), 'Test User');
        fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Registration Failed',
          'Email already exists'
        );
      }, { timeout: 3000 });
    });
  });

  describe('Logout Flow', () => {
    test('should logout successfully and clear authentication state', async () => {
      // Start with authenticated state
      const AsyncStorage = require('@react-native-async-storage/async-storage');
      await AsyncStorage.setItem('access_token', 'valid_token');

      serverUtils.setAuthenticatedUser({
        id: '1',
        name: 'Test User',
        full_name: 'Test User',
        email: 'test@example.com',
        subscription_tier: 'free',
        is_active: true,
        is_verified: true,
        questions_used_current_cycle: 0,
        cycle_reset_time: null,
      }, 'valid_token');

      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Wait for authentication to complete
      await waitFor(() => {
        expect(screen.getByText('Welcome Test User!')).toBeTruthy();
      }, { timeout: 3000 });

      // Logout
      await act(async () => {
        fireEvent.press(screen.getByRole('button', { name: 'Logout' }));
      });

      // Should return to login form
      await waitFor(() => {
        expect(screen.getByText('Sign In')).toBeTruthy();
      }, { timeout: 2000 });

      // Token should be cleared from storage
      const token = await AsyncStorage.getItem('access_token');
      expect(token).toBeNull();
    });
  });

  describe('Full User Journey', () => {
    test('should handle complete user journey: register → login → logout', async () => {
      render(
        <TestWrapper>
          <TestApp />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.queryByText('App loading...')).toBeNull();
      });

      // Switch to registration
      await act(async () => {
        fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));
      });

      expect(screen.getByText('Create Account')).toBeTruthy();

      // Register new user
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Full Name'), 'Journey User');
        fireEvent.changeText(screen.getByLabelText('Email'), 'journey@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));
      });

      // Should show registration success
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Registration Successful',
          'You can now sign in with your new account.'
        );
      }, { timeout: 3000 });

      // Should return to login form
      expect(screen.getByText('Sign In')).toBeTruthy();

      // Login with new credentials
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'journey@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      // Should login successfully
      await waitFor(() => {
        expect(screen.getByText('Welcome Journey User!')).toBeTruthy();
      }, { timeout: 5000 });

      // Logout
      await act(async () => {
        fireEvent.press(screen.getByRole('button', { name: 'Logout' }));
      });

      // Should return to login
      await waitFor(() => {
        expect(screen.getByText('Sign In')).toBeTruthy();
      }, { timeout: 2000 });
    });
  });

  describe('Form Validation Integration', () => {
    test('should validate all form fields and show appropriate errors', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Submit empty form
      await act(async () => {
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // Fix email, keep password empty
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      });

      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // Add short password
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Password'), '123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeTruthy();
      });

      // Fix password - all errors should clear
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      });

      await waitFor(() => {
        expect(screen.queryByText('Password must be at least 6 characters')).toBeNull();
      });
    });
  });

  describe('Error Recovery', () => {
    test('should recover from network errors and allow retry', async () => {
      // First, simulate network error
      server.use(
        http.post('*/api/auth/login', () => {
          return HttpResponse.error();
        })
      );

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Try to login (should fail)
      await act(async () => {
        fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
        fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          'Network error. Please try again.'
        );
      }, { timeout: 3000 });

      // Reset to normal handlers
      server.resetHandlers();

      // Try again (should succeed)
      await act(async () => {
        fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
      });

      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should complete successfully
      await waitFor(() => {
        expect(screen.queryByTestId('activity-indicator')).toBeNull();
      }, { timeout: 3000 });
    });
  });
});
