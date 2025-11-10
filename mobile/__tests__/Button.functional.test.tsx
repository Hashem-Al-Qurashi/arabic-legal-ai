/**
 * @format
 *
 * FUNCTIONAL BUTTON COMPONENT TESTS
 *
 * These tests verify REAL functionality:
 * - User interactions work correctly
 * - Press events are handled properly
 * - Loading and disabled states behave correctly
 * - Styling and theming work as expected
 * - Accessibility features function properly
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Button } from '@/components/ui/Button';
import { ThemeProvider } from '@/contexts/ThemeContext';

// Create a test wrapper with theme context
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>
    {children}
  </ThemeProvider>
);

describe('Button Component - Functional Tests', () => {
  describe('User Interactions', () => {
    test('should call onPress when button is tapped', async () => {
      const mockOnPress = jest.fn();

      render(
        <TestWrapper>
          <Button title="Test Button" onPress={mockOnPress} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Test Button' });

      fireEvent.press(button);

      expect(mockOnPress).toHaveBeenCalledTimes(1);
    });

    test('should handle multiple rapid taps correctly', async () => {
      const mockOnPress = jest.fn();

      render(
        <TestWrapper>
          <Button title="Rapid Tap Test" onPress={mockOnPress} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Rapid Tap Test' });

      // Simulate rapid tapping
      fireEvent.press(button);
      fireEvent.press(button);
      fireEvent.press(button);

      expect(mockOnPress).toHaveBeenCalledTimes(3);
    });

    test('should not call onPress when button is disabled', () => {
      const mockOnPress = jest.fn();

      render(
        <TestWrapper>
          <Button title="Disabled Button" onPress={mockOnPress} disabled />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Disabled Button' });

      fireEvent.press(button);

      expect(mockOnPress).not.toHaveBeenCalled();
    });

    test('should not call onPress when button is loading', () => {
      const mockOnPress = jest.fn();

      render(
        <TestWrapper>
          <Button title="Loading Button" onPress={mockOnPress} loading />
        </TestWrapper>
      );

      const button = screen.getByRole('button');

      fireEvent.press(button);

      expect(mockOnPress).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    test('should show activity indicator when loading', () => {
      render(
        <TestWrapper>
          <Button title="Loading Test" onPress={jest.fn()} loading />
        </TestWrapper>
      );

      // Should show loading indicator instead of text
      expect(screen.queryByText('Loading Test')).toBeNull();
      expect(screen.getByTestId('activity-indicator')).toBeTruthy();
    });

    test('should show title text when not loading', () => {
      render(
        <TestWrapper>
          <Button title="Normal Button" onPress={jest.fn()} />
        </TestWrapper>
      );

      expect(screen.getByText('Normal Button')).toBeTruthy();
      expect(screen.queryByTestId('activity-indicator')).toBeNull();
    });

    test('should transition correctly between loading and normal states', async () => {
      const TestComponent = () => {
        const [loading, setLoading] = React.useState(false);

        return (
          <>
            <Button
              title="Toggle Button"
              onPress={() => setLoading(!loading)}
              loading={loading}
            />
            <Button
              title="Control Button"
              onPress={() => setLoading(!loading)}
            />
          </>
        );
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      // Initially not loading
      expect(screen.getByText('Toggle Button')).toBeTruthy();

      // Trigger loading state
      fireEvent.press(screen.getByText('Control Button'));

      await waitFor(() => {
        expect(screen.queryByText('Toggle Button')).toBeNull();
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });
    });
  });

  describe('Button Variants', () => {
    test('should render primary variant correctly', () => {
      render(
        <TestWrapper>
          <Button title="Primary" onPress={jest.fn()} variant="primary" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Primary' });
      expect(button).toBeTruthy();

      // Should have primary styling (background color)
      expect(button.props.style).toEqual(
        expect.objectContaining({
          backgroundColor: '#007bff', // Primary color from theme mock
        })
      );
    });

    test('should render secondary variant correctly', () => {
      render(
        <TestWrapper>
          <Button title="Secondary" onPress={jest.fn()} variant="secondary" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Secondary' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          backgroundColor: '#6c757d', // Secondary color from theme mock
        })
      );
    });

    test('should render outline variant correctly', () => {
      render(
        <TestWrapper>
          <Button title="Outline" onPress={jest.fn()} variant="outline" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Outline' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderColor: '#007bff',
        })
      );
    });

    test('should render ghost variant correctly', () => {
      render(
        <TestWrapper>
          <Button title="Ghost" onPress={jest.fn()} variant="ghost" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Ghost' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          backgroundColor: 'transparent',
          borderWidth: 0,
        })
      );
    });
  });

  describe('Button Sizes', () => {
    test('should render small size correctly', () => {
      render(
        <TestWrapper>
          <Button title="Small" onPress={jest.fn()} size="small" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Small' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          minHeight: 36,
          paddingHorizontal: 12,
          paddingVertical: 8,
        })
      );
    });

    test('should render medium size correctly (default)', () => {
      render(
        <TestWrapper>
          <Button title="Medium" onPress={jest.fn()} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Medium' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          minHeight: 44,
          paddingHorizontal: 16,
          paddingVertical: 12,
        })
      );
    });

    test('should render large size correctly', () => {
      render(
        <TestWrapper>
          <Button title="Large" onPress={jest.fn()} size="large" />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Large' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          minHeight: 52,
          paddingHorizontal: 20,
          paddingVertical: 16,
        })
      );
    });
  });

  describe('Disabled State', () => {
    test('should apply disabled opacity', () => {
      render(
        <TestWrapper>
          <Button title="Disabled" onPress={jest.fn()} disabled />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Disabled' });
      expect(button.props.style).toEqual(
        expect.objectContaining({
          opacity: 0.6,
        })
      );
    });

    test('should have correct accessibility state when disabled', () => {
      render(
        <TestWrapper>
          <Button title="Disabled" onPress={jest.fn()} disabled />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Disabled' });
      expect(button.props.accessibilityState).toEqual(
        expect.objectContaining({
          disabled: true,
        })
      );
    });
  });

  describe('Custom Styling', () => {
    test('should apply custom button styles', () => {
      const customStyle = { marginTop: 20, borderRadius: 12 };

      render(
        <TestWrapper>
          <Button title="Custom" onPress={jest.fn()} style={customStyle} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Custom' });
      expect(button.props.style).toEqual(
        expect.objectContaining(customStyle)
      );
    });

    test('should apply custom text styles', () => {
      const customTextStyle = { fontSize: 20, fontWeight: 'bold' as const };

      render(
        <TestWrapper>
          <Button title="Custom Text" onPress={jest.fn()} textStyle={customTextStyle} />
        </TestWrapper>
      );

      const text = screen.getByText('Custom Text');
      expect(text.props.style).toEqual(
        expect.arrayContaining([
          expect.objectContaining(customTextStyle),
        ])
      );
    });
  });

  describe('Accessibility', () => {
    test('should have correct accessibility role', () => {
      render(
        <TestWrapper>
          <Button title="Accessible Button" onPress={jest.fn()} />
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeTruthy();
    });

    test('should have correct accessibility label', () => {
      render(
        <TestWrapper>
          <Button title="Test Label" onPress={jest.fn()} />
        </TestWrapper>
      );

      expect(screen.getByLabelText('Test Label')).toBeTruthy();
    });

    test('should be focusable when enabled', () => {
      render(
        <TestWrapper>
          <Button title="Focusable" onPress={jest.fn()} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Focusable' });
      expect(button.props.accessible).toBe(true);
    });
  });

  describe('Error Scenarios', () => {
    test('should handle onPress throwing an error gracefully', () => {
      const mockOnPress = jest.fn(() => {
        throw new Error('Button press error');
      });

      const consoleError = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <Button title="Error Button" onPress={mockOnPress} />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Error Button' });

      // Should allow errors to bubble up (this is the correct behavior)
      expect(() => fireEvent.press(button)).toThrow('Button press error');

      consoleError.mockRestore();
    });
  });

  describe('Real-world Usage Scenarios', () => {
    test('should work in a form submission scenario', async () => {
      const mockSubmit = jest.fn().mockResolvedValue({ success: true });

      const FormComponent = () => {
        const [loading, setLoading] = React.useState(false);

        const handleSubmit = async () => {
          setLoading(true);
          try {
            await mockSubmit();
          } finally {
            setLoading(false);
          }
        };

        return (
          <Button
            title="Submit Form"
            onPress={handleSubmit}
            loading={loading}
          />
        );
      };

      render(
        <TestWrapper>
          <FormComponent />
        </TestWrapper>
      );

      const button = screen.getByRole('button', { name: 'Submit Form' });

      fireEvent.press(button);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByTestId('activity-indicator')).toBeTruthy();
      });

      // Should return to normal state after completion
      await waitFor(() => {
        expect(screen.getByText('Submit Form')).toBeTruthy();
      });

      expect(mockSubmit).toHaveBeenCalledTimes(1);
    });

    test('should work in a navigation scenario', () => {
      const mockNavigate = jest.fn();

      render(
        <TestWrapper>
          <Button title="Go to Settings" onPress={() => mockNavigate('Settings')} />
        </TestWrapper>
      );

      fireEvent.press(screen.getByRole('button', { name: 'Go to Settings' }));

      expect(mockNavigate).toHaveBeenCalledWith('Settings');
    });
  });
});
