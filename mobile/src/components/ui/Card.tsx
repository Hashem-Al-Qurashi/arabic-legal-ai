import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  padding?: number;
  margin?: number;
  elevation?: number;
}

export function Card({
  children,
  style,
  padding = 16,
  margin = 8,
  elevation = 2,
}: CardProps): React.JSX.Element {
  const { colors } = useTheme();

  const cardStyles = [
    styles.card,
    {
      backgroundColor: colors.surface,
      borderColor: colors.border,
      padding,
      margin,
      elevation,
      shadowOpacity: elevation * 0.1,
    },
    style,
  ];

  return <View style={cardStyles}>{children}</View>;
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowRadius: 4,
  },
});
