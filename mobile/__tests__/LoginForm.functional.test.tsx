/**
 * @format
 *
 * FUNCTIONAL LOGIN FORM TESTS
 *
 * These tests verify REAL functionality:
 * - Form input and validation work correctly
 * - User can actually type in fields and submit forms
 * - API integration works with real HTTP requests (mocked)
 * - Loading states and error handling function properly
 * - Navigation callbacks are triggered correctly
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from '@/components/auth/LoginForm';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { server, serverUtils } from './mocks/server';

// Mock Alert.alert for testing
jest.spyOn(Alert, 'alert');

// Create test wrapper with all necessary providers
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

describe('LoginForm Component - Functional Tests', () => {
  let TestWrapper: ReturnType<typeof createTestWrapper>;

  beforeEach(() => {
    TestWrapper = createTestWrapper();
    serverUtils.resetData();
    jest.clearAllMocks();
  });

  describe('Form Rendering and Layout', () => {
    test('should render all form elements correctly', () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Check for title and subtitle
      expect(screen.getByText('Sign In')).toBeTruthy();
      expect(screen.getByText('Welcome back to Arabic Legal AI')).toBeTruthy();

      // Check for input fields
      expect(screen.getByLabelText('Email')).toBeTruthy();
      expect(screen.getByLabelText('Password')).toBeTruthy();

      // Check for submit button
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeTruthy();
    });

    test('should show register button when onSwitchToRegister is provided', () => {
      const mockSwitchToRegister = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSwitchToRegister={mockSwitchToRegister} />
        </TestWrapper>
      );

      expect(screen.getByRole('button', { name: 'Sign Up' })).toBeTruthy();
      expect(screen.getByText("Don't have an account? ")).toBeTruthy();
    });

    test('should not show register button when onSwitchToRegister is not provided', () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      expect(screen.queryByRole('button', { name: 'Sign Up' })).toBeNull();
      expect(screen.queryByText("Don't have an account? ")).toBeNull();
    });
  });

  describe('Form Input and Validation', () => {
    test('should allow typing in email field', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');

      fireEvent.changeText(emailInput, 'test@example.com');

      expect(emailInput.props.value).toBe('test@example.com');
    });

    test('should allow typing in password field', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Password');

      fireEvent.changeText(passwordInput, 'password123');

      expect(passwordInput.props.value).toBe('password123');
    });

    test('should show validation errors for empty fields', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });
    });

    test('should show validation error for invalid email format', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'invalid-email');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      });
    });

    test('should show validation error for short password', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(passwordInput, '123');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeTruthy();
      });
    });

    test('should clear validation errors when user corrects input', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Trigger validation error
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
      });

      // Correct the input
      fireEvent.changeText(emailInput, 'test@example.com');

      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull();
      });
    });
  });

  describe('Form Submission and API Integration', () => {
    test('should successfully login with valid credentials', async () => {
      const mockOnSuccess = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSuccess={mockOnSuccess} />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Fill in valid credentials (matching our MSW mock)
      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');

      fireEvent.press(submitButton);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should call onSuccess after successful login
      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledTimes(1);
      }, { timeout: 3000 });
    });

    test('should show error alert for invalid credentials', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Fill in invalid credentials
      fireEvent.changeText(emailInput, 'wrong@example.com');
      fireEvent.changeText(passwordInput, 'wrongpassword');

      fireEvent.press(submitButton);

      // Should show loading state first
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should show error alert
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Login Failed',
          'Invalid credentials'
        );
      }, { timeout: 3000 });

      // Should return to normal state
      await waitFor(() => {
        expect(screen.queryByTestId('activity-indicator')).toBeNull();
        expect(screen.getByText('Sign In')).toBeTruthy();
      });
    });

    test('should handle network errors gracefully', async () => {
      // Simulate network error
      // Import MSW properly
      const { http, HttpResponse } = require('msw');
      server.use(
        // This will cause all requests to fail
        http.post('*/api/auth/login', () => {
          return HttpResponse.error();
        })
      );

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith(
          'Error',
          'Network error. Please try again.'
        );
      }, { timeout: 3000 });
    });

    test('should disable form during submission', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(submitButton);

      // Button should be disabled during loading
      await waitFor(() => {
        expect(submitButton.props.accessibilityState.disabled).toBe(true);
      });
    });
  });

  describe('Navigation and Callbacks', () => {
    test('should call onSwitchToRegister when register button is pressed', () => {
      const mockSwitchToRegister = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSwitchToRegister={mockSwitchToRegister} />
        </TestWrapper>
      );

      const registerButton = screen.getByRole('button', { name: 'Sign Up' });

      fireEvent.press(registerButton);

      expect(mockSwitchToRegister).toHaveBeenCalledTimes(1);
    });

    test('should call onSuccess after successful login', async () => {
      const mockOnSuccess = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSuccess={mockOnSuccess} />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      fireEvent.changeText(emailInput, 'test@example.com');
      fireEvent.changeText(passwordInput, 'password123');
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledTimes(1);
      }, { timeout: 3000 });
    });
  });

  describe('Real-world User Workflows', () => {
    test('should handle complete login workflow', async () => {
      const mockOnSuccess = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSuccess={mockOnSuccess} />
        </TestWrapper>
      );

      // User sees the form
      expect(screen.getByText('Sign In')).toBeTruthy();

      // User tries to submit empty form
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      // User sees validation errors
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });

      // User enters invalid email
      fireEvent.changeText(screen.getByLabelText('Email'), 'invalid');
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeTruthy();
      });

      // User corrects email
      fireEvent.changeText(screen.getByLabelText('Email'), 'test@example.com');

      // Error should clear
      await waitFor(() => {
        expect(screen.queryByText('Please enter a valid email address')).toBeNull();
      });

      // User enters valid password
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');

      // User submits form
      fireEvent.press(screen.getByRole('button', { name: 'Sign In' }));

      // Loading state appears
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Success callback is called
      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledTimes(1);
      }, { timeout: 3000 });
    });

    test('should handle switching between login and register', () => {
      const mockSwitchToRegister = jest.fn();

      render(
        <TestWrapper>
          <LoginForm onSwitchToRegister={mockSwitchToRegister} />
        </TestWrapper>
      );

      // User sees login form
      expect(screen.getByText('Sign In')).toBeTruthy();

      // User decides to register instead
      fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));

      expect(mockSwitchToRegister).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility and User Experience', () => {
    test('should have proper accessibility labels', () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      expect(screen.getByLabelText('Email')).toBeTruthy();
      expect(screen.getByLabelText('Password')).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeTruthy();
    });

    test('should maintain focus and user input during form interaction', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');

      // User types in email
      fireEvent.changeText(emailInput, 'user@example.com');
      expect(emailInput.props.value).toBe('user@example.com');

      // User switches to password field
      fireEvent.changeText(passwordInput, 'mypassword');
      expect(passwordInput.props.value).toBe('mypassword');

      // Email value should still be preserved
      expect(emailInput.props.value).toBe('user@example.com');
    });
  });
});
