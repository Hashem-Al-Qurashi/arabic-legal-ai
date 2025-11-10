/**
 * Debug form submission issues
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Alert } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LoginForm } from '@/components/auth/LoginForm';
import { server, serverUtils } from './mocks/server';

// Mock Alert
jest.spyOn(Alert, 'alert');

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

describe('Debug Form Tests', () => {
  let Wrapper: ReturnType<typeof createWrapper>;

  beforeEach(async () => {
    Wrapper = createWrapper();
    serverUtils.resetData();
    jest.clearAllMocks();

    const AsyncStorage = require('@react-native-async-storage/async-storage');
    await AsyncStorage.clear();

    server.resetHandlers();
  });

  test('should handle form input step by step', async () => {
    render(
      <Wrapper>
        <LoginForm />
      </Wrapper>
    );

    console.log('Form rendered, checking initial state...');

    // Check initial form state
    expect(screen.getByText('Sign In')).toBeTruthy();
    expect(screen.getByLabelText('Email')).toBeTruthy();
    expect(screen.getByLabelText('Password')).toBeTruthy();

    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });

    console.log('Initial email value:', emailInput.props.value);
    console.log('Initial password value:', passwordInput.props.value);

    // Step 1: Fill email
    console.log('Filling email...');
    await act(async () => {
      fireEvent.changeText(emailInput, 'test@example.com');
    });

    console.log('Email after change:', emailInput.props.value);

    // Step 2: Fill password
    console.log('Filling password...');
    await act(async () => {
      fireEvent.changeText(passwordInput, 'password123');
    });

    console.log('Password after change:', passwordInput.props.value);

    // Step 3: Check for validation errors before submit
    console.log('Checking for validation errors...');
    const emailError = screen.queryByText('Email is required');
    const passwordError = screen.queryByText('Password is required');

    console.log('Email error visible:', !!emailError);
    console.log('Password error visible:', !!passwordError);

    // Step 4: Submit form
    console.log('Submitting form...');
    await act(async () => {
      fireEvent.press(submitButton);
    });

    // Step 5: Check what happens after submit
    console.log('Checking post-submit state...');

    // Wait a bit and check for loading indicator or errors
    await waitFor(() => {
      const activityIndicator = screen.queryByTestId('activity-indicator');
      const newEmailError = screen.queryByText('Email is required');
      const newPasswordError = screen.queryByText('Password is required');

      console.log('Activity indicator visible:', !!activityIndicator);
      console.log('Email error after submit:', !!newEmailError);
      console.log('Password error after submit:', !!newPasswordError);
      console.log('Alert calls:', (Alert.alert as jest.Mock).mock.calls.length);

      // Just finish the test
      expect(true).toBe(true);
    }, { timeout: 2000 });
  });
});
