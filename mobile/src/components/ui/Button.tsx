import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  testID?: string;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'tab' | 'link' | 'menuitem';
  accessibilityState?: any;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  style,
  textStyle,
  testID,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  accessibilityState,
}: ButtonProps): React.JSX.Element {
  const { colors } = useTheme();

  const buttonStyles = [
    styles.button,
    styles[size],
    {
      backgroundColor: getBackgroundColor(variant, colors),
      borderColor: getBorderColor(variant, colors),
      borderWidth: variant === 'outline' ? 1 : 0,
      opacity: disabled ? 0.6 : 1,
    },
    style,
  ];

  const textStyles = [
    styles.text,
    styles[`${size}Text`],
    {
      color: getTextColor(variant, colors),
    },
    textStyle,
  ];

  return (
    <TouchableOpacity
      style={buttonStyles}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      testID={testID}
      accessibilityRole={accessibilityRole}
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityState={{
        disabled: disabled || loading,
        busy: loading,
        ...accessibilityState,
      }}
      accessible={true}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={getTextColor(variant, colors)}
          testID="activity-indicator"
          accessibilityLabel="Loading"
        />
      ) : (
        <Text style={textStyles}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

function getBackgroundColor(variant: string, colors: any): string {
  switch (variant) {
    case 'primary':
      return colors.primary;
    case 'secondary':
      return colors.secondary;
    case 'outline':
      return 'transparent';
    case 'ghost':
      return 'transparent';
    default:
      return colors.primary;
  }
}

function getBorderColor(variant: string, colors: any): string {
  switch (variant) {
    case 'outline':
      return colors.primary;
    default:
      return 'transparent';
  }
}

function getTextColor(variant: string, colors: any): string {
  switch (variant) {
    case 'primary':
      return '#ffffff';
    case 'secondary':
      return '#ffffff';
    case 'outline':
      return colors.primary;
    case 'ghost':
      return colors.text;
    default:
      return '#ffffff';
  }
}

const styles = StyleSheet.create({
  button: {
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  small: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    minHeight: 36,
  },
  medium: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    minHeight: 44,
  },
  large: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    minHeight: 52,
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  smallText: {
    fontSize: 14,
  },
  mediumText: {
    fontSize: 16,
  },
  largeText: {
    fontSize: 18,
  },
});
