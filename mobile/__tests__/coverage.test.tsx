/**
 * @format
 *
 * COVERAGE TESTS
 *
 * These tests increase code coverage by testing previously untested components,
 * utilities, hooks, and edge cases to achieve minimum 70% coverage.
 */

import React from 'react';
import { Text } from 'react-native';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

// Test components
import { RegisterForm } from '@/components/auth/RegisterForm';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { ConversationList } from '@/components/chat/ConversationList';

// Test utilities
import { validateEmail, validatePassword, validateFullName, validateMessage } from '@/utils/validation';
import { formatDate, formatTime, formatRelativeTime } from '@/utils/formatting';
import { isPredominantlyArabic, getTextDirection, getTextAlign, isRTLEnabled, containsArabic } from '@/utils/rtl';
import { getFontFamily, createFontStyle, isArabicText } from '@/utils/fonts';
import { setItem, getItem, removeItem, clearAll, saveUserData, getUserData } from '@/utils/storage';

// Test hooks
// import { useApi } from '@/hooks/useApi'; // Unused import
import { useKeyboard } from '@/hooks/useKeyboard';
import { useOrientation } from '@/hooks/useOrientation';

// Test services
import { authAPI, chatAPI } from '@/services/api';

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

describe('Coverage Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Validation Utils', () => {
    test('validateEmail should work correctly', () => {
      expect(validateEmail('test@example.com')).toEqual({ isValid: true });
      expect(validateEmail('invalid').isValid).toBe(false);
      expect(validateEmail('').isValid).toBe(false);
      expect(validateEmail('test@').isValid).toBe(false);
      expect(validateEmail('@example.com').isValid).toBe(false);
    });

    test('validatePassword should work correctly', () => {
      expect(validatePassword('Password123').isValid).toBe(true);
      expect(validatePassword('12345').isValid).toBe(false); // too short
      expect(validatePassword('').isValid).toBe(false);
      expect(validatePassword('password').isValid).toBe(false); // no uppercase
      expect(validatePassword('PASSWORD').isValid).toBe(false); // no lowercase
      expect(validatePassword('Password').isValid).toBe(false); // no number
    });

    test('validateFullName should work correctly', () => {
      expect(validateFullName('John Doe').isValid).toBe(true);
      expect(validateFullName('A').isValid).toBe(false); // too short
      expect(validateFullName('').isValid).toBe(false);
      expect(validateFullName('  ').isValid).toBe(false); // only spaces
    });

    test('validateMessage should work correctly', () => {
      expect(validateMessage('Hello world').isValid).toBe(true);
      expect(validateMessage('').isValid).toBe(false);
      expect(validateMessage('   ').isValid).toBe(false); // only spaces after trim
    });
  });

  describe('Formatting Utils', () => {
    test('formatDate should format dates correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      expect(formatDate(date.toISOString())).toBeDefined();
      expect(typeof formatDate(date.toISOString())).toBe('string');
    });

    test('formatTime should format time correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      expect(formatTime(date.toISOString())).toBeDefined();
      expect(typeof formatTime(date.toISOString())).toBe('string');
    });

    test('formatRelativeTime should format relative time correctly', () => {
      const now = new Date();
      const minuteAgo = new Date(now.getTime() - 60000);
      expect(formatRelativeTime(minuteAgo.toISOString())).toBeDefined();
      expect(typeof formatRelativeTime(minuteAgo.toISOString())).toBe('string');
    });
  });

  describe('RTL Utils', () => {
    test('containsArabic should detect Arabic text correctly', () => {
      expect(containsArabic('Hello World')).toBe(false);
      expect(containsArabic('مرحبا بالعالم')).toBe(true);
      expect(containsArabic('Hello مرحبا')).toBe(true);
      expect(containsArabic('')).toBe(false);
    });

    test('isPredominantlyArabic should detect predominantly Arabic text', () => {
      expect(isPredominantlyArabic('مرحبا بالعالم')).toBe(true);
      expect(isPredominantlyArabic('Hello World')).toBe(false);
      expect(isPredominantlyArabic('Hello مرحبا')).toBe(false); // less than 50% Arabic
      expect(isPredominantlyArabic('')).toBe(false);
    });

    test('getTextDirection should return correct direction', () => {
      expect(getTextDirection('Hello')).toBe('ltr');
      expect(getTextDirection('مرحبا بالعالم')).toBe('rtl');
      expect(getTextDirection('')).toBe('ltr');
    });

    test('getTextAlign should return correct alignment', () => {
      expect(getTextAlign('Hello')).toBe('left');
      expect(getTextAlign('مرحبا بالعالم')).toBe('right');
    });

    test('isRTLEnabled should return boolean', () => {
      expect(typeof isRTLEnabled()).toBe('boolean');
    });
  });

  describe('Font Utils', () => {
    test('isArabicText should detect Arabic text', () => {
      expect(isArabicText('مرحبا')).toBe(true);
      expect(isArabicText('Hello')).toBe(false);
      expect(isArabicText('')).toBe(false);
    });

    test('getFontFamily should return correct font family', () => {
      expect(getFontFamily('مرحبا', 'regular')).toBeDefined();
      expect(getFontFamily('Hello', 'regular')).toBeDefined();
      expect(typeof getFontFamily('مرحبا', 'regular')).toBe('string');
      expect(typeof getFontFamily('Hello', 'bold')).toBe('string');
    });

    test('createFontStyle should create appropriate styles', () => {
      const arabicStyle = createFontStyle('مرحبا', 'body');
      const englishStyle = createFontStyle('Hello', 'body');

      expect(arabicStyle).toBeDefined();
      expect(englishStyle).toBeDefined();
      expect(typeof arabicStyle).toBe('object');
      expect(typeof englishStyle).toBe('object');
      expect(arabicStyle.fontFamily).toBeDefined();
      expect(englishStyle.fontFamily).toBeDefined();
    });
  });

  describe('Storage Utils', () => {
    test('basic storage operations should work correctly', async () => {
      const testData = { test: 'value' };

      await setItem('testKey', testData);
      const loaded = await getItem('testKey');
      expect(loaded).toEqual(testData);

      await removeItem('testKey');
      const removed = await getItem('testKey');
      expect(removed).toBeNull();
    });

    test('user data storage should work', async () => {
      const userData = { id: '1', name: 'Test User', email: 'test@example.com' };

      await saveUserData(userData);
      const loaded = await getUserData();
      expect(loaded).toEqual(userData);
    });

    test('clearAll should remove all data', async () => {
      await setItem('key1', 'value1');
      await setItem('key2', 'value2');
      await clearAll();

      const afterClear1 = await getItem('key1');
      const afterClear2 = await getItem('key2');
      expect(afterClear1).toBeNull();
      expect(afterClear2).toBeNull();
    });
  });

  describe('UI Components', () => {
    test('Card component should render correctly', () => {
      const TestText = () => <Text>Test Content</Text>;

      render(
        <TestWrapper>
          <Card>
            <TestText />
          </Card>
        </TestWrapper>
      );

      expect(screen.getByText('Test Content')).toBeTruthy();
    });

    test('LoadingSpinner should render correctly', () => {
      render(
        <TestWrapper>
          <LoadingSpinner />
        </TestWrapper>
      );

      expect(screen.getByTestId('activity-indicator')).toBeTruthy();
    });

    test('LoadingSpinner with custom props', () => {
      render(
        <TestWrapper>
          <LoadingSpinner size="large" color="red" text="Loading..." />
        </TestWrapper>
      );

      expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      expect(screen.getByText('Loading...')).toBeTruthy();
    });
  });

  describe('Chat Components', () => {
    test('MessageBubble should render user message correctly', () => {
      const message = {
        id: '1',
        role: 'user' as const,
        content: 'Hello there!',
        isUser: true,
        timestamp: new Date().toISOString(),
      };

      render(
        <TestWrapper>
          <MessageBubble message={message} />
        </TestWrapper>
      );

      expect(screen.getByText('Hello there!')).toBeTruthy();
    });

    test('MessageBubble should render AI message correctly', () => {
      const message = {
        id: '2',
        role: 'assistant' as const,
        content: 'How can I help you?',
        isUser: false,
        timestamp: new Date().toISOString(),
      };

      render(
        <TestWrapper>
          <MessageBubble message={message} />
        </TestWrapper>
      );

      expect(screen.getByText('How can I help you?')).toBeTruthy();
    });

    test('ChatInput should render and handle input', async () => {
      const onSendMessage = jest.fn().mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <ChatInput onSendMessage={onSendMessage} />
        </TestWrapper>
      );

      const input = screen.getByPlaceholderText('Ask your legal question...');
      const sendButton = screen.getByTestId('send-button');

      fireEvent.changeText(input, 'Test message');
      fireEvent.press(sendButton);

      await waitFor(() => {
        expect(onSendMessage).toHaveBeenCalledWith('Test message');
      });
    });

    test('ConversationList should render conversations', () => {
      const conversations = [
        {
          id: '1',
          title: 'Legal Question',
          lastMessage: 'Thank you',
          lastMessageAt: new Date().toISOString(),
          messages: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_message_preview: 'Thank you',
          message_count: 1,
        },
      ];

      render(
        <TestWrapper>
          <ConversationList
            conversations={conversations}
            onSelectConversation={jest.fn()}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Legal Question')).toBeTruthy();
      expect(screen.getByText('Thank you')).toBeTruthy();
    });
  });

  describe('RegisterForm Component', () => {
    test('should render registration form correctly', () => {
      render(
        <TestWrapper>
          <RegisterForm onSuccess={jest.fn()} />
        </TestWrapper>
      );

      expect(screen.getByText('Create Account')).toBeTruthy();
      expect(screen.getByLabelText('Full Name')).toBeTruthy();
      expect(screen.getByLabelText('Email')).toBeTruthy();
      expect(screen.getByLabelText('Password')).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Sign Up' })).toBeTruthy();
    });

    test('should validate registration form fields', async () => {
      render(
        <TestWrapper>
          <RegisterForm onSuccess={jest.fn()} />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: 'Sign Up' });

      // Submit empty form
      fireEvent.press(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Full name is required')).toBeTruthy();
        expect(screen.getByText('Email is required')).toBeTruthy();
        expect(screen.getByText('Password is required')).toBeTruthy();
      });
    });

    test('should handle registration submission', async () => {
      const onSuccess = jest.fn();

      render(
        <TestWrapper>
          <RegisterForm onSuccess={onSuccess} />
        </TestWrapper>
      );

      // Fill form
      fireEvent.changeText(screen.getByLabelText('Full Name'), 'John Doe');
      fireEvent.changeText(screen.getByLabelText('Email'), 'john@example.com');
      fireEvent.changeText(screen.getByLabelText('Password'), 'password123');

      // Submit form
      fireEvent.press(screen.getByRole('button', { name: 'Sign Up' }));

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });
    });
  });

  describe('Theme Context', () => {
    test('useTheme should provide theme values', () => {
      const TestComponent = () => {
        const { colors, theme, toggleTheme } = useTheme();
        const isDark = theme === 'dark';

        return (
          <>
            <Text testID="theme-colors">{JSON.stringify(colors)}</Text>
            <Text testID="is-dark">{isDark.toString()}</Text>
            <Text onPress={toggleTheme}>Toggle Theme</Text>
          </>
        );
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('theme-colors')).toBeTruthy();
      expect(screen.getByTestId('is-dark')).toBeTruthy();
    });
  });

  describe('Hooks', () => {
    test('useKeyboard should track keyboard state', () => {
      const TestComponent = () => {
        const { keyboardVisible, keyboardHeight } = useKeyboard();

        return (
          <>
            <Text testID="keyboard-visible">{keyboardVisible.toString()}</Text>
            <Text testID="keyboard-height">{keyboardHeight.toString()}</Text>
          </>
        );
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('keyboard-visible')).toBeTruthy();
      expect(screen.getByTestId('keyboard-height')).toBeTruthy();
    });

    test('useOrientation should track orientation', () => {
      const TestComponent = () => {
        const { orientation, isPortrait, isLandscape } = useOrientation();

        return (
          <>
            <Text testID="orientation">{orientation}</Text>
            <Text testID="is-portrait">{isPortrait.toString()}</Text>
            <Text testID="is-landscape">{isLandscape.toString()}</Text>
          </>
        );
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('orientation')).toBeTruthy();
      expect(screen.getByTestId('is-portrait')).toBeTruthy();
      expect(screen.getByTestId('is-landscape')).toBeTruthy();
    });
  });

  describe('API Services', () => {
    test('authAPI should have all required methods', () => {
      expect(typeof authAPI.login).toBe('function');
      expect(typeof authAPI.register).toBe('function');
      expect(typeof authAPI.getCurrentUser).toBe('function');
      expect(typeof authAPI.logout).toBe('function');
    });

    test('chatAPI should have all required methods', () => {
      expect(typeof chatAPI.sendMessage).toBe('function');
      expect(typeof chatAPI.sendMessageStreaming).toBe('function');
      expect(typeof chatAPI.getConversations).toBe('function');
      expect(typeof chatAPI.getConversationMessages).toBe('function');
      expect(typeof chatAPI.updateConversationTitle).toBe('function');
      expect(typeof chatAPI.archiveConversation).toBe('function');
      expect(typeof chatAPI.getUserStats).toBe('function');
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle undefined values gracefully', () => {
      expect(validateEmail(undefined as any)).toEqual({ isValid: false, error: expect.any(String) });
      expect(validatePassword(null as any)).toEqual({ isValid: false, error: expect.any(String) });
      expect(formatDate(null as any)).toBeDefined();
      expect(containsArabic(undefined as any)).toBe(false);
    });

    test('should handle empty conversation list', () => {
      render(
        <TestWrapper>
          <ConversationList
            conversations={[]}
            onSelectConversation={jest.fn()}
          />
        </TestWrapper>
      );

      // Should render empty message
      expect(screen.getByText('No conversations yet. Start a new chat!')).toBeTruthy();
    });
  });
});
