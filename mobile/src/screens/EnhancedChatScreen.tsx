import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Animated,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';
import HapticFeedback from 'react-native-haptic-feedback';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useOffline } from '@/hooks/useOffline';
import { EnhancedChatInput } from '@/components/chat/EnhancedChatInput';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { MessageSkeleton } from '@/components/chat/MessageSkeleton';
// import { ConversationSkeleton } from '@/components/chat/ConversationSkeleton'; // Reserved for loading state
import { chatAPI } from '@/services/api';
import { offlineService, createOfflineService } from '@/services/offlineService';
import { appLifecycle, createAppLifecycleService } from '@/services/appLifecycle';
import { generateUUID } from '@/utils/uuid';
import type { Message, Conversation, FileAttachment } from '@/types';

// Abort controller for cleanup
let messageAbortController: AbortController | null = null;

// Suggested questions for new conversations
const SUGGESTED_QUESTIONS = [
  'ما هي إجراءات تأسيس شركة تجارية؟',
  'حقوق الموظف عند إنهاء الخدمة',
  'ما هي عقوبات التهرب الضريبي؟',
  'ما هي حقوق المستهلك في السعودية؟',
];

export function EnhancedChatScreen(): React.JSX.Element {
  const { colors } = useTheme();
  const { isAuthenticated } = useAuth();
  const { isOnline, queuedMessages } = useOffline();

  // Create service instances to avoid singleton memory issues
  const servicesRef = useRef<{
    offlineService?: ReturnType<typeof createOfflineService>;
    appLifecycle?: ReturnType<typeof createAppLifecycleService>;
  }>({});

  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [_isLoading, _setIsLoading] = useState(false); // Reserved for loading states
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [_conversations, setConversations] = useState<Conversation[]>([]); // Reserved for conversation list
  const [refreshing, setRefreshing] = useState(false);
  const [_error, setError] = useState<string | null>(null); // Reserved for error display
  const [showScrollToBottom, setShowScrollToBottom] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState(false);

  // Refs
  const flatListRef = useRef<FlatList>(null);
  // const scrollY = useRef(new Animated.Value(0)).current; // Reserved for scroll animations
  const fadeAnim = useRef(new Animated.Value(1)).current;

  // Initialize session and app lifecycle
  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    const initializeApp = async () => {
      // Initialize session for guest users with proper UUID
      if (!isAuthenticated) {
        let storedSessionId = await AsyncStorage.getItem('guestSessionId');
        if (!storedSessionId) {
          storedSessionId = `guest_${generateUUID()}`;
          await AsyncStorage.setItem('guestSessionId', storedSessionId);
        }
        setSessionId(storedSessionId);
      } else {
        setSessionId(null);
        await AsyncStorage.removeItem('guestSessionId');
      }

      // Subscribe to app lifecycle
      unsubscribe = appLifecycle.subscribe((state) => {
        console.log('App state:', state);
        if (state === 'active') {
          // Refresh data when app comes to foreground
          loadConversations();
        }
      });
    };

    initializeApp();

    return () => {
      // Cleanup subscriptions
      unsubscribe?.();

      // Abort any pending requests
      if (messageAbortController) {
        messageAbortController.abort();
        messageAbortController = null;
      }

      // Cleanup services
      if (servicesRef.current.offlineService) {
        servicesRef.current.offlineService.cleanup();
      }
      if (servicesRef.current.appLifecycle) {
        servicesRef.current.appLifecycle.cleanup();
      }
    };
  }, [isAuthenticated]);

  // Load conversations
  const loadConversations = async () => {
    if (!isAuthenticated) {
      // Load cached conversations for offline access
      const cached = await offlineService.getAllCachedConversations();
      setConversations(cached);
      return;
    }

    try {
      setRefreshing(true);

      if (isOnline) {
        const response = await chatAPI.getConversations();
        if (response.success && response.data) {
          setConversations(response.data);

          // Cache for offline access
          for (const conv of response.data) {
            await offlineService.cacheConversation(conv);
          }
        }
      } else {
        // Load from cache if offline
        const cached = await offlineService.getAllCachedConversations();
        setConversations(cached);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      // Try to load from cache on error
      const cached = await offlineService.getAllCachedConversations();
      setConversations(cached);
    } finally {
      setRefreshing(false);
    }
  };

  // Load conversation messages - reserved for future conversation feature
  // const loadConversationMessages = async (convId: string) => {
  //   try {
  //     setIsLoading(true);
  //     setError(null);
  //
  //     // Try to load from cache first for instant display
  //     const cachedMessages = await offlineService.getCachedMessages(convId);
  //     if (cachedMessages.length > 0) {
  //       setMessages(cachedMessages);
  //     }
  //
  //     if (isOnline && isAuthenticated) {
  //       const response = await chatAPI.getConversationMessages(convId);
  //       if (response.success && response.data) {
  //         setMessages(response.data);
  //         setConversationId(convId);
  //
  //         // Cache messages for offline access
  //         await offlineService.cacheMessages(convId, response.data);
  //       }
  //     }
  //   } catch (error) {
  //     console.error('Failed to load conversation:', error);
  //     setError('فشل في تحميل المحادثة');
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  // Enhanced send message with file attachments
  const handleSendMessage = useCallback(async (
    messageText: string,
    attachments?: FileAttachment[]
  ) => {
    if (!messageText.trim() && (!attachments || attachments.length === 0)) {return;}

    // Haptic feedback
    HapticFeedback.trigger('impactMedium');

    // Check guest limits
    if (!isAuthenticated && messages.length >= 3) {
      Alert.alert(
        'الحد الأقصى للأسئلة',
        'يمكن للمستخدمين الضيوف إرسال 3 أسئلة فقط. يرجى تسجيل الدخول للمتابعة.',
        [
          { text: 'إلغاء', style: 'cancel' },
          { text: 'تسجيل الدخول', onPress: () => console.log('Navigate to login') },
        ]
      );
      return;
    }

    // Create user message with proper UUID
    const userMessage: Message = {
      id: generateUUID(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    // Add user message to UI
    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);
    setError(null);
    setTypingIndicator(true);

    // Auto-scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      if (!isOnline) {
        // Queue message for offline sending
        await offlineService.queueMessage(messageText, conversationId || undefined, attachments);

        // Show offline notification
        Alert.alert(
          'غير متصل',
          'تم حفظ رسالتك وسيتم إرسالها عند الاتصال بالإنترنت',
          [{ text: 'حسناً' }]
        );

        setTypingIndicator(false);
        return;
      }

      // Create placeholder for assistant message with proper UUID
      const assistantMessageId = generateUUID();
      let streamingContent = '';

      // Add empty assistant message for streaming
      setMessages(prev => [...prev, {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      }]);

      // Cancel any previous message request
      if (messageAbortController) {
        messageAbortController.abort();
      }

      // Create new abort controller
      messageAbortController = new AbortController();

      // Send message with streaming
      await chatAPI.sendMessageStreaming(
        messageText,
        conversationId || undefined,
        sessionId || undefined,
        // onChunk callback
        (chunk: string) => {
          streamingContent += chunk;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: streamingContent }
                : msg
            )
          );

          // Auto-scroll during streaming
          flatListRef.current?.scrollToEnd({ animated: false });
        },
        // onComplete callback
        async (response: any) => {
          const finalContent = response.ai_message?.content ||
                             response.fullResponse ||
                             streamingContent ||
                             'عذراً، لم أتمكن من معالجة طلبك.';

          // Update with final content
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: finalContent,
                    processing_time_ms: response.ai_message?.processing_time_ms,
                  }
                : msg
            )
          );

          // Update conversation ID if new
          if (response.conversation_id && !conversationId) {
            setConversationId(response.conversation_id);
          }

          // Cache messages for offline access
          const updatedMessages = messages.concat([userMessage, {
            id: assistantMessageId,
            role: 'assistant' as const,
            content: finalContent,
            timestamp: new Date().toISOString(),
          }]);

          if (conversationId || response.conversation_id) {
            await offlineService.cacheMessages(
              conversationId || response.conversation_id,
              updatedMessages
            );
          }

          // Haptic feedback on success
          HapticFeedback.trigger('notificationSuccess');
        },
        // onError callback
        (error: string) => {
          console.error('Streaming error:', error);
          setError(error);
        },
        messageAbortController.signal
      );
    } catch (error: any) {
      console.error('Send message error:', error);

      if (error.name !== 'AbortError') {
        setError('فشل في إرسال الرسالة');
        HapticFeedback.trigger('notificationError');

        // Remove the empty assistant message on error
        setMessages(prev => prev.filter(msg => msg.content !== ''));
      }
    } finally {
      setIsSending(false);
      setTypingIndicator(false);
      messageAbortController = null;
    }
  }, [messages, isAuthenticated, conversationId, sessionId, isOnline]);

  // Handle scroll events
  const handleScroll = useCallback((event: any) => {
    const { contentOffset, contentSize, layoutMeasurement } = event.nativeEvent;
    const isNearBottom = contentOffset.y >= contentSize.height - layoutMeasurement.height - 100;

    setShowScrollToBottom(!isNearBottom);
  }, []);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    HapticFeedback.trigger('impactLight');
    flatListRef.current?.scrollToEnd({ animated: true });
  }, []);

  // Handle suggested question tap
  const handleSuggestedQuestion = useCallback((question: string) => {
    HapticFeedback.trigger('selection');
    handleSendMessage(question);
  }, [handleSendMessage]);

  // Pull to refresh
  const onRefresh = useCallback(async () => {
    HapticFeedback.trigger('impactLight');
    await loadConversations();
  }, [isAuthenticated]);

  // Render message item with proper memoization
  const renderMessage = useCallback(({ item, index }: { item: Message; index: number }) => {
    // Show skeleton for streaming empty messages
    if (item.role === 'assistant' && item.content === '' && typingIndicator) {
      return <MessageSkeleton isUser={false} />;
    }

    return (
      <MessageBubble
        message={item}
        isLastMessage={index === messages.length - 1}
      />
    );
  }, [messages.length, typingIndicator]);

  // Memoize keyExtractor to prevent re-renders
  const keyExtractor = useCallback((item: Message) => item.id, []);

  // Render empty state with memoization
  const renderEmptyState = useMemo(() => () => (
    <View style={styles.emptyState}>
      <Icon name="chat-bubble-outline" size={64} color={colors.textSecondary} />
      <Text style={[styles.emptyTitle, { color: colors.text }]}>
        ابدأ محادثة جديدة
      </Text>
      <Text style={[styles.emptySubtitle, { color: colors.textSecondary }]}>
        اسأل أي سؤال قانوني وسأساعدك في الإجابة عليه
      </Text>

      {/* Suggested questions */}
      <View style={styles.suggestedContainer}>
        <Text style={[styles.suggestedTitle, { color: colors.text }]}>
          أسئلة مقترحة:
        </Text>
        {SUGGESTED_QUESTIONS.map((question, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.suggestedButton, { backgroundColor: colors.card }]}
            onPress={() => handleSuggestedQuestion(question)}
          >
            <Text style={[styles.suggestedText, { color: colors.primary }]}>
              {question}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  ), [colors, handleSuggestedQuestion]);

  // Render header with memoization
  const renderHeader = useMemo(() => () => (
    <View style={[styles.header, { backgroundColor: colors.card }]}>
      <Text style={[styles.headerTitle, { color: colors.text }]}>
        المساعد القانوني
      </Text>
      {!isOnline && (
        <View style={[styles.offlineBadge, { backgroundColor: colors.warning }]}>
          <Icon name="wifi-off" size={12} color="#fff" />
          <Text style={styles.offlineBadgeText}>غير متصل</Text>
        </View>
      )}
      {queuedMessages.length > 0 && (
        <View style={[styles.queueBadge, { backgroundColor: colors.primary }]}>
          <Text style={styles.queueBadgeText}>{queuedMessages.length}</Text>
        </View>
      )}
    </View>
  ), [colors, isOnline, queuedMessages.length]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {renderHeader()}

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={keyExtractor}
          renderItem={renderMessage}
          removeClippedSubviews={true}
          maxToRenderPerBatch={10}
          windowSize={10}
          initialNumToRender={10}
          updateCellsBatchingPeriod={50}
          contentContainerStyle={[
            styles.messagesContent,
            messages.length === 0 && styles.emptyContent,
          ]}
          ListEmptyComponent={renderEmptyState}
          onScroll={handleScroll}
          scrollEventThrottle={16}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={[colors.primary]}
              tintColor={colors.primary}
            />
          }
          showsVerticalScrollIndicator={false}
          maintainVisibleContentPosition={{
            minIndexForVisible: 0,
            autoscrollToTopThreshold: 100,
          }}
        />

        {/* Scroll to bottom button */}
        {showScrollToBottom && (
          <Animated.View style={[styles.scrollToBottom, { opacity: fadeAnim }]}>
            <TouchableOpacity
              style={[styles.scrollToBottomButton, { backgroundColor: colors.primary }]}
              onPress={scrollToBottom}
            >
              <Icon name="keyboard-arrow-down" size={24} color="#fff" />
            </TouchableOpacity>
          </Animated.View>
        )}

        {/* Enhanced chat input */}
        <EnhancedChatInput
          onSendMessage={handleSendMessage}
          disabled={isSending}
          showOfflineIndicator={true}
          maxMessageLength={2000}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  offlineBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  offlineBadgeText: {
    color: '#fff',
    fontSize: 10,
    marginLeft: 4,
    fontWeight: '500',
  },
  queueBadge: {
    minWidth: 20,
    height: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 4,
  },
  queueBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  messagesContent: {
    paddingVertical: 16,
  },
  emptyContent: {
    flex: 1,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  suggestedContainer: {
    marginTop: 32,
    width: '100%',
  },
  suggestedTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 12,
  },
  suggestedButton: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  suggestedText: {
    fontSize: 14,
    textAlign: 'right',
  },
  scrollToBottom: {
    position: 'absolute',
    bottom: 80,
    right: 16,
  },
  scrollToBottomButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
});
