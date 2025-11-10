import React from 'react';
import { View, StyleSheet } from 'react-native';
import SkeletonPlaceholder from 'react-native-skeleton-placeholder';
import { useTheme } from '@/contexts/ThemeContext';

interface ConversationSkeletonProps {
  count?: number;
}

export function ConversationSkeleton({
  count = 5,
}: ConversationSkeletonProps): React.JSX.Element {
  const { colors, isDark } = useTheme();

  const renderSkeletonItem = () => (
    <View style={[styles.itemContainer, { backgroundColor: colors.card }]}>
      <SkeletonPlaceholder
        backgroundColor={isDark ? '#2a2a2a' : '#e1e9ee'}
        highlightColor={isDark ? '#3a3a3a' : '#f2f8fc'}
        speed={1500}
      >
        <SkeletonPlaceholder.Item flexDirection="column" padding={16}>
          {/* Title */}
          <SkeletonPlaceholder.Item
            width="60%"
            height={18}
            borderRadius={4}
            marginBottom={8}
          />

          {/* Preview text */}
          <SkeletonPlaceholder.Item
            width="90%"
            height={14}
            borderRadius={4}
            marginBottom={4}
          />
          <SkeletonPlaceholder.Item
            width="75%"
            height={14}
            borderRadius={4}
            marginBottom={8}
          />

          {/* Bottom row: date and message count */}
          <SkeletonPlaceholder.Item
            flexDirection="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <SkeletonPlaceholder.Item
              width={80}
              height={12}
              borderRadius={4}
            />
            <SkeletonPlaceholder.Item
              width={30}
              height={20}
              borderRadius={10}
            />
          </SkeletonPlaceholder.Item>
        </SkeletonPlaceholder.Item>
      </SkeletonPlaceholder>
    </View>
  );

  return (
    <View style={styles.container}>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index}>
          {renderSkeletonItem()}
          {index < count - 1 && (
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
          )}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  itemContainer: {
    marginVertical: 2,
  },
  divider: {
    height: StyleSheet.hairlineWidth,
    marginHorizontal: 16,
  },
});
