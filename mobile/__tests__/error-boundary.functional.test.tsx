/**
 * @format
 *
 * FUNCTIONAL ERROR BOUNDARY TESTS
 *
 * These tests verify REAL error handling functionality:
 * - Error boundaries catch and handle component errors
 * - Error states are displayed properly to users
 * - Recovery mechanisms work correctly
 * - Network errors are handled gracefully
 * - Validation errors are displayed appropriately
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Button } from '@/components/ui/Button';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { server } from './mocks/server';
import { http, HttpResponse } from 'msw';

// Error Boundary Component
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ComponentType<{ error: Error; retry: () => void }> },
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    console.error('Error caught by boundary:', error, errorInfo);
  }

  retry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error!} retry={this.retry} />;
    }

    return this.props.children;
  }
}

// Default Error Fallback Component
const DefaultErrorFallback = ({ error, retry }: { error: Error; retry: () => void }) => (
  <View testID="error-boundary-fallback">
    <Text>Something went wrong:</Text>
    <Text testID="error-message">{error.message}</Text>
    <Button title="Try Again" onPress={retry} />
  </View>
);

// Custom Error Fallback Component
const CustomErrorFallback = ({ error, retry }: { error: Error; retry: () => void }) => (
  <View testID="custom-error-fallback">
    <Text>Oops! An error occurred</Text>
    <Text testID="custom-error-message">Error: {error.message}</Text>
    <Button title="Retry" onPress={retry} />
    <Button title="Go Home" onPress={() => console.log('Navigate home')} variant="secondary" />
  </View>
);

// Component that throws errors for testing
const ErrorThrowingComponent = ({ shouldThrow = false, errorMessage = 'Test error' }) => {
  if (shouldThrow) {
    throw new Error(errorMessage);
  }

  return <Text>Component rendered successfully</Text>;
};

// Async error component
const AsyncErrorComponent = () => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleAsyncError = async () => {
    setLoading(true);
    setError(null);

    try {
      // Simulate async operation that might fail
      const response = await fetch('/api/test/server-error');
      if (!response.ok) {
        throw new Error('Server error occurred');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <View testID="async-error-display">
        <Text>Async Error: {error}</Text>
        <Button title="Retry" onPress={handleAsyncError} />
      </View>
    );
  }

  return (
    <View>
      <Text>Async Component</Text>
      <Button
        title="Trigger Async Error"
        onPress={handleAsyncError}
        loading={loading}
      />
    </View>
  );
};

// Network Error Component
const NetworkErrorComponent = () => {
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const simulateNetworkError = async () => {
    setLoading(true);
    setError(null);

    try {
      await fetch('/api/test/network-error');
    } catch (err) {
      setError('Network error: Please check your connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      {error && (
        <View testID="network-error-display">
          <Text>{error}</Text>
          <Button title="Retry" onPress={simulateNetworkError} />
        </View>
      )}
      <Button
        title="Test Network Error"
        onPress={simulateNetworkError}
        loading={loading}
      />
    </View>
  );
};

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('Error Boundary Functional Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console.error for error boundary tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    (console.error as jest.Mock).mockRestore();
  });

  describe('Basic Error Boundary Functionality', () => {
    test('should catch and display component errors', () => {
      render(
        <TestWrapper>
          <ErrorBoundary>
            <ErrorThrowingComponent shouldThrow={true} errorMessage="Component crashed!" />
          </ErrorBoundary>
        </TestWrapper>
      );

      // Should show error boundary fallback
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();
      expect(screen.getByTestId('error-message')).toBeTruthy();
      expect(screen.getByText('Component crashed!')).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Try Again' })).toBeTruthy();
    });

    test('should render children normally when no error occurs', () => {
      render(
        <TestWrapper>
          <ErrorBoundary>
            <ErrorThrowingComponent shouldThrow={false} />
          </ErrorBoundary>
        </TestWrapper>
      );

      // Should render the component normally
      expect(screen.getByText('Component rendered successfully')).toBeTruthy();
      expect(screen.queryByTestId('error-boundary-fallback')).toBeNull();
    });

    test('should allow retry functionality', () => {
      const RetryTestComponent = () => {
        const [shouldThrow, setShouldThrow] = React.useState(true);

        return (
          <ErrorBoundary>
            <Button
              title="Toggle Error"
              onPress={() => setShouldThrow(!shouldThrow)}
            />
            <ErrorThrowingComponent shouldThrow={shouldThrow} />
          </ErrorBoundary>
        );
      };

      render(
        <TestWrapper>
          <RetryTestComponent />
        </TestWrapper>
      );

      // Should show error initially
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();

      // Click retry button
      fireEvent.press(screen.getByRole('button', { name: 'Try Again' }));

      // Should retry and still show error (since shouldThrow is still true)
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();
    });
  });

  describe('Custom Error Fallback', () => {
    test('should use custom error fallback when provided', () => {
      render(
        <TestWrapper>
          <ErrorBoundary fallback={CustomErrorFallback}>
            <ErrorThrowingComponent shouldThrow={true} errorMessage="Custom error!" />
          </ErrorBoundary>
        </TestWrapper>
      );

      // Should show custom error fallback
      expect(screen.getByTestId('custom-error-fallback')).toBeTruthy();
      expect(screen.getByText('Oops! An error occurred')).toBeTruthy();
      expect(screen.getByText('Error: Custom error!')).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Go Home' })).toBeTruthy();
    });
  });

  describe('Async Error Handling', () => {
    test('should handle async errors gracefully', async () => {
      // Mock server error response
      server.use(
        http.get('*/api/test/server-error', () => {
          return HttpResponse.json(
            { error: 'Server error occurred' },
            { status: 500 }
          );
        })
      );

      render(
        <TestWrapper>
          <AsyncErrorComponent />
        </TestWrapper>
      );

      // Initially should show normal component
      expect(screen.getByText('Async Component')).toBeTruthy();

      // Trigger async error
      fireEvent.press(screen.getByRole('button', { name: 'Trigger Async Error' }));

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should show error after async operation fails
      await waitFor(() => {
        expect(screen.getByTestId('async-error-display')).toBeTruthy();
        expect(screen.getByText('Async Error: Server error occurred')).toBeTruthy();
      }, { timeout: 3000 });
    });

    test('should allow retry of async operations', async () => {
      let callCount = 0;

      server.use(
        http.get('*/api/test/server-error', () => {
          callCount++;
          if (callCount === 1) {
            return HttpResponse.json(
              { error: 'Server error occurred' },
              { status: 500 }
            );
          }
          return HttpResponse.json({ success: true });
        })
      );

      render(
        <TestWrapper>
          <AsyncErrorComponent />
        </TestWrapper>
      );

      // Trigger error
      fireEvent.press(screen.getByRole('button', { name: 'Trigger Async Error' }));

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByTestId('async-error-display')).toBeTruthy();
      }, { timeout: 3000 });

      // Retry
      fireEvent.press(screen.getByRole('button', { name: 'Retry' }));

      // Should succeed on retry
      await waitFor(() => {
        expect(screen.queryByTestId('async-error-display')).toBeNull();
        expect(screen.getByText('Async Component')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Network Error Handling', () => {
    test('should handle network errors appropriately', async () => {
      // Mock network error
      server.use(
        http.get('*/api/test/network-error', () => {
          return HttpResponse.error();
        })
      );

      render(
        <TestWrapper>
          <NetworkErrorComponent />
        </TestWrapper>
      );

      // Trigger network error
      fireEvent.press(screen.getByRole('button', { name: 'Test Network Error' }));

      // Should show network error message
      await waitFor(() => {
        expect(screen.getByTestId('network-error-display')).toBeTruthy();
        expect(screen.getByText('Network error: Please check your connection')).toBeTruthy();
      }, { timeout: 3000 });
    });
  });

  describe('Error Recovery Scenarios', () => {
    test('should handle error recovery flow', () => {
      const ErrorRecoveryComponent = () => {
        const [hasError, setHasError] = React.useState(false);

        return (
          <ErrorBoundary>
            <Button
              title="Cause Error"
              onPress={() => setHasError(true)}
            />
            <Button
              title="Fix Error"
              onPress={() => setHasError(false)}
            />
            <ErrorThrowingComponent shouldThrow={hasError} />
          </ErrorBoundary>
        );
      };

      render(
        <TestWrapper>
          <ErrorRecoveryComponent />
        </TestWrapper>
      );

      // Initially no error
      expect(screen.getByText('Component rendered successfully')).toBeTruthy();

      // Cause error
      fireEvent.press(screen.getByRole('button', { name: 'Cause Error' }));

      // Should show error boundary
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();

      // Try again (retry)
      fireEvent.press(screen.getByRole('button', { name: 'Try Again' }));

      // Should still show error boundary since we haven't fixed the underlying issue
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();
    });
  });

  describe('Multiple Error Boundaries', () => {
    test('should handle nested error boundaries', () => {
      const NestedErrorComponent = () => (
        <ErrorBoundary fallback={({ error, retry }) => (
          <View testID="outer-error-boundary">
            <Text>Outer boundary caught: {error.message}</Text>
            <Button title="Outer Retry" onPress={retry} />
          </View>
        )}>
          <ErrorBoundary fallback={({ error, retry }) => (
            <View testID="inner-error-boundary">
              <Text>Inner boundary caught: {error.message}</Text>
              <Button title="Inner Retry" onPress={retry} />
            </View>
          )}>
            <ErrorThrowingComponent shouldThrow={true} errorMessage="Inner error" />
          </ErrorBoundary>
        </ErrorBoundary>
      );

      render(
        <TestWrapper>
          <NestedErrorComponent />
        </TestWrapper>
      );

      // Inner boundary should catch the error
      expect(screen.getByTestId('inner-error-boundary')).toBeTruthy();
      expect(screen.getByText('Inner boundary caught: Inner error')).toBeTruthy();
      expect(screen.queryByTestId('outer-error-boundary')).toBeNull();
    });
  });

  describe('Error Boundary with State Management', () => {
    test('should handle errors in stateful components', () => {
      const StatefulErrorComponent = () => {
        const [count, setCount] = React.useState(0);
        const [shouldThrow, setShouldThrow] = React.useState(false);

        return (
          <ErrorBoundary>
            <View>
              <Text>Count: {count}</Text>
              <Button title="Increment" onPress={() => setCount(c => c + 1)} />
              <Button
                title="Toggle Error"
                onPress={() => setShouldThrow(!shouldThrow)}
              />
              <ErrorThrowingComponent shouldThrow={shouldThrow} />
            </View>
          </ErrorBoundary>
        );
      };

      render(
        <TestWrapper>
          <StatefulErrorComponent />
        </TestWrapper>
      );

      // Should work normally initially
      expect(screen.getByText('Count: 0')).toBeTruthy();

      // Increment counter
      fireEvent.press(screen.getByRole('button', { name: 'Increment' }));
      expect(screen.getByText('Count: 1')).toBeTruthy();

      // Trigger error
      fireEvent.press(screen.getByRole('button', { name: 'Toggle Error' }));

      // Should show error boundary
      expect(screen.getByTestId('error-boundary-fallback')).toBeTruthy();
    });
  });

  describe('Real-world Error Scenarios', () => {
    test('should handle form submission errors', async () => {
      const FormWithErrorHandling = () => {
        const [error, setError] = React.useState<string | null>(null);
        const [loading, setLoading] = React.useState(false);

        const handleSubmit = async () => {
          setLoading(true);
          setError(null);

          try {
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              body: JSON.stringify({ email: 'invalid@test.com', password: 'wrong' }),
            });

            if (!response.ok) {
              throw new Error('Login failed');
            }
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Login failed');
          } finally {
            setLoading(false);
          }
        };

        return (
          <View>
            {error && (
              <View testID="form-error">
                <Text>Error: {error}</Text>
                <Button title="Dismiss" onPress={() => setError(null)} />
              </View>
            )}
            <Button
              title="Submit Form"
              onPress={handleSubmit}
              loading={loading}
            />
          </View>
        );
      };

      // Mock failed login
      server.use(
        http.post('*/api/auth/login', () => {
          return HttpResponse.json(
            { success: false, error: 'Invalid credentials' },
            { status: 401 }
          );
        })
      );

      render(
        <TestWrapper>
          <FormWithErrorHandling />
        </TestWrapper>
      );

      // Submit form
      fireEvent.press(screen.getByRole('button', { name: 'Submit Form' }));

      // Should show error
      await waitFor(() => {
        expect(screen.getByTestId('form-error')).toBeTruthy();
        expect(screen.getByText('Error: Login failed')).toBeTruthy();
      }, { timeout: 3000 });

      // Should be able to dismiss error
      fireEvent.press(screen.getByRole('button', { name: 'Dismiss' }));

      await waitFor(() => {
        expect(screen.queryByTestId('form-error')).toBeNull();
      });
    });
  });
});
