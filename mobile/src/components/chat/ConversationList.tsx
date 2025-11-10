import React from 'react';
import {
  FlatList,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ViewStyle,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { Card } from '@/components/ui';
import type { Conversation } from '@/types';

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId?: string | null;
  onSelectConversation: (conversationId: string) => void;
  onRefresh?: () => Promise<void>;
  refreshing?: boolean;
  loading?: boolean;
  emptyMessage?: string;
}

export function ConversationList({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onRefresh,
  refreshing = false,
  loading = false,
  emptyMessage = 'No conversations yet. Start a new chat!',
}: ConversationListProps): React.JSX.Element {
  const { colors } = useTheme();

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const renderConversationItem = ({ item }: { item: Conversation }): React.JSX.Element => {
    const isSelected = item.id === selectedConversationId;

    const cardStyle: ViewStyle = isSelected ? {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    } : {
      backgroundColor: colors.surface,
      borderColor: colors.border,
    };

    return (
      <TouchableOpacity
        onPress={() => onSelectConversation(item.id)}
        activeOpacity={0.7}
      >
        <Card
          style={{
            ...styles.conversationItem,
            ...cardStyle,
          }}
          padding={16}
          margin={8}
        >
          <View style={styles.conversationHeader}>
            <Text
              style={[
                styles.conversationTitle,
                isSelected ? styles.conversationTitleSelected : { color: colors.text },
              ]}
              numberOfLines={1}
            >
              {item.title}
            </Text>
            <Text
              style={[
                styles.conversationDate,
                isSelected ? styles.conversationDateSelected : { color: colors.textSecondary },
              ]}
            >
              {formatDate(item.updated_at)}
            </Text>
          </View>

          {item.last_message_preview && (
            <Text
              style={[
                styles.conversationPreview,
                isSelected ? styles.conversationPreviewSelected : { color: colors.textSecondary },
              ]}
              numberOfLines={2}
            >
              {item.last_message_preview}
            </Text>
          )}

          <View style={styles.conversationMeta}>
            <Text
              style={[
                styles.messageCount,
                isSelected ? styles.messageCountSelected : { color: colors.textSecondary },
              ]}
            >
              {item.message_count} message{item.message_count !== 1 ? 's' : ''}
            </Text>
          </View>
        </Card>
      </TouchableOpacity>
    );
  };

  const renderEmptyState = (): React.JSX.Element => (
    <View style={styles.emptyContainer}>
      <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
        {emptyMessage}
      </Text>
    </View>
  );

  return (
    <FlatList
      data={conversations}
      renderItem={renderConversationItem}
      keyExtractor={(item) => item.id}
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={conversations.length === 0 ? styles.emptyContentContainer : undefined}
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        ) : undefined
      }
      ListEmptyComponent={!loading ? renderEmptyState : undefined}
      showsVerticalScrollIndicator={false}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  conversationItem: {
    marginHorizontal: 16,
    marginVertical: 4,
  },
  conversationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  conversationTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  conversationTitleSelected: {
    color: '#ffffff',
  },
  conversationDate: {
    fontSize: 12,
  },
  conversationDateSelected: {
    color: 'rgba(255,255,255,0.7)',
  },
  conversationPreview: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 8,
  },
  conversationPreviewSelected: {
    color: 'rgba(255,255,255,0.8)',
  },
  conversationMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  messageCount: {
    fontSize: 12,
  },
  messageCountSelected: {
    color: 'rgba(255,255,255,0.7)',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyContentContainer: {
    flexGrow: 1,
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
});
