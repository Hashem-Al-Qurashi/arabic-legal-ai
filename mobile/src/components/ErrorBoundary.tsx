import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
}

const ERROR_COUNT_KEY = 'error_boundary_count';
const MAX_ERROR_COUNT = 3;
const ERROR_RESET_TIME = 60000; // 1 minute

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private errorResetTimeout: NodeJS.Timeout | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state to show fallback UI
    return {
      hasError: true,
      error,
    };
  }

  async componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Track error count to detect crash loops
    const errorCount = await this.getErrorCount();
    const newErrorCount = errorCount + 1;
    await this.setErrorCount(newErrorCount);

    // Update state with error details
    this.setState({
      errorInfo,
      errorCount: newErrorCount,
    });

    // Check if we're in a crash loop
    if (newErrorCount >= MAX_ERROR_COUNT) {
      Alert.alert(
        'التطبيق يواجه مشكلة',
        'حدثت أخطاء متكررة. يرجى إعادة تشغيل التطبيق.',
        [
          {
            text: 'إعادة تشغيل',
            onPress: () => this.clearErrorState(),
          },
        ],
        { cancelable: false }
      );
    }

    // Reset error count after timeout
    this.scheduleErrorCountReset();

    // Send error report to analytics/logging service in production
    if (!__DEV__) {
      this.reportError(error, errorInfo);
    }
  }

  private async getErrorCount(): Promise<number> {
    try {
      const count = await AsyncStorage.getItem(ERROR_COUNT_KEY);
      return count ? parseInt(count, 10) : 0;
    } catch {
      return 0;
    }
  }

  private async setErrorCount(count: number): Promise<void> {
    try {
      await AsyncStorage.setItem(ERROR_COUNT_KEY, count.toString());
    } catch {
      // Ignore storage errors
    }
  }

  private scheduleErrorCountReset() {
    if (this.errorResetTimeout) {
      clearTimeout(this.errorResetTimeout);
    }

    this.errorResetTimeout = setTimeout(async () => {
      await this.setErrorCount(0);
    }, ERROR_RESET_TIME);
  }

  private reportError(error: Error, errorInfo: ErrorInfo) {
    // In production, send error to logging service
    // This is a placeholder for actual error reporting
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
    };

    // TODO: Send to logging service (e.g., Sentry, Bugsnag, etc.)
    console.log('Error report:', errorReport);
  }

  private clearErrorState = async () => {
    // Reset error count
    await this.setErrorCount(0);

    // Clear error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    });
  };

  private handleRetry = () => {
    this.clearErrorState();
  };

  componentWillUnmount() {
    if (this.errorResetTimeout) {
      clearTimeout(this.errorResetTimeout);
    }
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <View style={styles.container}>
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <View style={styles.errorCard}>
              <Icon name="error-outline" size={64} color="#FF5252" />
              
              <Text style={styles.title}>عذراً، حدث خطأ غير متوقع</Text>
              
              <Text style={styles.message}>
                {this.state.error?.message || 'حدث خطأ في التطبيق'}
              </Text>

              {__DEV__ && this.state.error?.stack && (
                <View style={styles.debugInfo}>
                  <Text style={styles.debugTitle}>Debug Info:</Text>
                  <ScrollView style={styles.stackTrace} horizontal>
                    <Text style={styles.stackTraceText}>
                      {this.state.error.stack}
                    </Text>
                  </ScrollView>
                </View>
              )}

              <View style={styles.buttonContainer}>
                <TouchableOpacity
                  style={styles.retryButton}
                  onPress={this.handleRetry}
                  activeOpacity={0.8}
                >
                  <Icon name="refresh" size={20} color="#FFFFFF" />
                  <Text style={styles.retryButtonText}>إعادة المحاولة</Text>
                </TouchableOpacity>
              </View>

              {this.state.errorCount > 1 && (
                <Text style={styles.errorCountText}>
                  عدد الأخطاء: {this.state.errorCount}
                </Text>
              )}
            </View>
          </ScrollView>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    maxWidth: 400,
    width: '100%',
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333333',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007BFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  errorCountText: {
    fontSize: 12,
    color: '#999999',
    marginTop: 16,
  },
  debugInfo: {
    width: '100%',
    marginBottom: 20,
    padding: 12,
    backgroundColor: '#F8F8F8',
    borderRadius: 8,
  },
  debugTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666666',
    marginBottom: 8,
  },
  stackTrace: {
    maxHeight: 120,
  },
  stackTraceText: {
    fontSize: 10,
    color: '#999999',
    fontFamily: 'monospace',
  },
});

// HOC for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  return (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );
}

export default ErrorBoundary;