/**
 * Simplified Authentication Tests
 *
 * Focus on getting basic authentication working step by step
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Alert, Text, View } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LoginForm } from '@/components/auth/LoginForm';
import { server, serverUtils } from './mocks/server';

// Mock Alert
jest.spyOn(Alert, 'alert');

// Create wrapper
const createWrapper = () => {
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

// Simple component to test auth state
const AuthStatusDisplay = () => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <View testID="auth-loading"><Text>Loading auth...</Text></View>;
  }

  if (isAuthenticated && user) {
    return <View testID="auth-success"><Text>Authenticated: {user.email}</Text></View>;
  }

  return <View testID="auth-unauthenticated"><Text>Not authenticated</Text></View>;
};

describe('Simplified Authentication Tests', () => {
  let Wrapper: ReturnType<typeof createWrapper>;

  beforeEach(async () => {
    Wrapper = createWrapper();
    serverUtils.resetData();
    jest.clearAllMocks();

    // Clear AsyncStorage
    const AsyncStorage = require('@react-native-async-storage/async-storage');
    await AsyncStorage.clear();

    server.resetHandlers();
  });

  test('should show unauthenticated state initially', async () => {
    render(
      <Wrapper>
        <AuthStatusDisplay />
      </Wrapper>
    );

    // Wait for auth check to complete
    await waitFor(() => {
      expect(screen.getByTestId('auth-unauthenticated')).toBeTruthy();
    }, { timeout: 3000 });
  });

  test('should handle successful login', async () => {
    render(
      <Wrapper>
        <LoginForm />
      </Wrapper>
    );

    // Fill and submit login form
    await act(async () => {
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
    });

    // Should show loading
    await waitFor(() => {
      expect(screen.getByTestId('activity-indicator')).toBeTruthy();
    });

    // Should complete without calling Alert.alert (success doesn't show alert)
    await waitFor(() => {
      expect(screen.queryByTestId('activity-indicator')).toBeNull();
    }, { timeout: 3000 });

    // Alert should not be called for success
    expect(Alert.alert).not.toHaveBeenCalled();
  });

  test('should handle login failure', async () => {
    render(
      <Wrapper>
        <LoginForm />
      </Wrapper>
    );

    // Fill and submit login form with wrong credentials
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
  });

  test('should show auth status after login', async () => {
    const TestComponent = () => {
      const [showStatus, setShowStatus] = React.useState(false);

      return (
        <>
          <LoginForm onSuccess={() => setShowStatus(true)} />
          {showStatus && <AuthStatusDisplay />}
        </>
      );
    };

    render(
      <Wrapper>
        <TestComponent />
      </Wrapper>
    );

    // Login successfully
    await act(async () => {
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));
    });

    // Wait for login to complete and status to show
    await waitFor(() => {
      expect(screen.getByTestId('auth-success')).toBeTruthy();
      expect(screen.getByText('Authenticated: test@example.com')).toBeTruthy();
    }, { timeout: 5000 });
  });
});
