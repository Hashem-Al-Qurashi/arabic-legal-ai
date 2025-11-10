import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import type { Conversation } from '@/types';

interface ConversationsListProps {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (conversation: Conversation) => void;
  onDelete?: (conversationId: string) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function ConversationsList({
  conversations,
  selectedId,
  onSelect,
  onDelete,
  isLoading = false,
  onRefresh,
}: ConversationsListProps): React.JSX.Element {
  const { colors } = useTheme();

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'اليوم';
    } else if (days === 1) {
      return 'أمس';
    } else if (days < 7) {
      return `منذ ${days} أيام`;
    } else if (days < 30) {
      const weeks = Math.floor(days / 7);
      return `منذ ${weeks} ${weeks === 1 ? 'أسبوع' : 'أسابيع'}`;
    } else {
      const months = Math.floor(days / 30);
      return `منذ ${months} ${months === 1 ? 'شهر' : 'أشهر'}`;
    }
  };

  const renderConversation = ({ item }: { item: Conversation }) => {
    const isSelected = item.id === selectedId;

    return (
      <TouchableOpacity
        style={[
          styles.conversationItem,
          {
            backgroundColor: isSelected ? colors.primary + '20' : colors.surface,
            borderColor: isSelected ? colors.primary : colors.border,
          },
        ]}
        onPress={() => onSelect(item)}
        activeOpacity={0.7}
      >
        <View style={styles.conversationContent}>
          <Text
            style={[
              styles.conversationTitle,
              { color: isSelected ? colors.primary : colors.text },
            ]}
            numberOfLines={1}
          >
            {item.title || 'محادثة بدون عنوان'}
          </Text>
          {item.last_message_preview && (
            <Text
              style={[styles.conversationPreview, { color: colors.textSecondary }]}
              numberOfLines={2}
            >
              {item.last_message_preview}
            </Text>
          )}
          <View style={styles.conversationMeta}>
            <Text style={[styles.conversationDate, { color: colors.textSecondary }]}>
              {formatDate(item.updated_at)}
            </Text>
            {item.message_count > 0 && (
              <Text style={[styles.messageCount, { color: colors.textSecondary }]}>
                • {item.message_count} رسالة
              </Text>
            )}
          </View>
        </View>

        {onDelete && (
          <TouchableOpacity
            style={[styles.deleteButton, { backgroundColor: colors.error + '20' }]}
            onPress={() => onDelete(item.id)}
          >
            <Text style={[styles.deleteButtonText, { color: colors.error }]}>
              ×
            </Text>
          </TouchableOpacity>
        )}
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={[styles.emptyTitle, { color: colors.textSecondary }]}>
        لا توجد محادثات سابقة
      </Text>
      <Text style={[styles.emptySubtitle, { color: colors.textSecondary }]}>
        ابدأ محادثة جديدة للبدء
      </Text>
    </View>
  );

  const renderHeader = () => (
    <View style={[styles.header, { borderColor: colors.border }]}>
      <Text style={[styles.headerTitle, { color: colors.text }]}>
        المحادثات السابقة
      </Text>
      {isLoading && <ActivityIndicator size="small" color={colors.primary} />}
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {renderHeader()}
      <FlatList
        data={conversations}
        renderItem={renderConversation}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={[
          styles.listContent,
          conversations.length === 0 && styles.emptyListContent,
        ]}
        showsVerticalScrollIndicator={false}
        onRefresh={onRefresh}
        refreshing={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  listContent: {
    padding: 12,
  },
  emptyListContent: {
    flex: 1,
  },
  conversationItem: {
    flexDirection: 'row',
    padding: 12,
    marginBottom: 8,
    borderRadius: 12,
    borderWidth: 1,
  },
  conversationContent: {
    flex: 1,
  },
  conversationTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
    textAlign: 'right',
  },
  conversationPreview: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 6,
    textAlign: 'right',
  },
  conversationMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  conversationDate: {
    fontSize: 12,
  },
  messageCount: {
    fontSize: 12,
    marginLeft: 8,
  },
  deleteButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
    alignSelf: 'center',
  },
  deleteButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    textAlign: 'center',
  },
});
