import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { ChatInput } from '@/components/chat/ChatInput';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { chatAPI } from '@/services/api';
import type { Message, Conversation } from '@/types';

// Abort controller for cleanup
let messageAbortController: AbortController | null = null;

// Suggested questions for new conversations
const SUGGESTED_QUESTIONS = [
  'ما هي إجراءات تأسيس شركة تجارية؟',
  'حقوق الموظف عند إنهاء الخدمة',
  'ما هي عقوبات التهرب الضريبي؟',
  'ما هي حقوق المستهلك في السعودية؟',
];

function ChatScreen(): React.JSX.Element {
  const { colors } = useTheme();
  const { user, isAuthenticated } = useAuth();

  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading] = useState(false);  // Currently unused but reserved for future loading states
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const flatListRef = useRef<FlatList>(null);

  // Initialize session for guest users
  useEffect(() => {
    let isCancelled = false;

    const initializeSession = async () => {
      if (!isAuthenticated) {
        // Guest user - create/restore session ID
        try {
          if (isCancelled) {return;}

          let storedSessionId = await AsyncStorage.getItem('guestSessionId');
          if (!storedSessionId) {
            storedSessionId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            await AsyncStorage.setItem('guestSessionId', storedSessionId);
          }

          if (!isCancelled) {
            setSessionId(storedSessionId);
            console.log('Guest session initialized:', storedSessionId);
          }
        } catch (error) {
          if (!isCancelled) {
            console.error('Failed to initialize guest session:', error);
          }
        }
      } else {
        // Authenticated user - clear guest session
        if (!isCancelled) {
          setSessionId(null);
          await AsyncStorage.removeItem('guestSessionId');
        }
      }
    };

    initializeSession();

    // Cleanup function
    return () => {
      isCancelled = true;
    };
  }, [isAuthenticated]);

  // Load conversations for authenticated users
  useEffect(() => {
    let isCancelled = false;

    const loadConversationsAsync = async () => {
      if (isAuthenticated && user && !isCancelled) {
        await loadConversations();
      }
    };

    loadConversationsAsync();

    // Cleanup function
    return () => {
      isCancelled = true;
    };
  }, [isAuthenticated, user?.id]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cancel any ongoing message requests on unmount
      if (messageAbortController) {
        messageAbortController.abort();
        messageAbortController = null;
      }
    };
  }, []);

  // Load conversations
  const loadConversations = async () => {
    if (!isAuthenticated) {return;}

    try {
      setRefreshing(true);
      const response = await chatAPI.getConversations();
      if (response.success) {
        setConversations(response.data || []);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Load conversation messages
  // Currently not used but available for future functionality
  // const loadConversationMessages = async (convId: string) => {
  //   if (!isAuthenticated) return;

  //   try {
  //     setIsLoading(true);
  //     setError(null);
  //     const response = await chatAPI.getConversationMessages(convId);
  //     if (response.success) {
  //       setMessages(response.data || []);
  //       setConversationId(convId);
  //     } else {
  //       throw new Error(response.error || 'Failed to load messages');
  //     }
  //   } catch (error) {
  //     console.error('Failed to load conversation:', error);
  //     setError('فشل في تحميل المحادثة');
  //     Alert.alert('خطأ', 'فشل في تحميل المحادثة');
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  // Send message handler with proper abort handling
  const handleSendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim()) {return;}

    // Check if user can send messages (you might want to add rate limiting)
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

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    // Add user message to UI
    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);
    setError(null);

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      // Create placeholder for assistant message
      const assistantMessageId = (Date.now() + 1).toString();
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

      // Create new abort controller for this request
      messageAbortController = new AbortController();

      // Send message with streaming
      await chatAPI.sendMessageStreaming(
        messageText,
        conversationId || undefined,
        sessionId || undefined,
        // onChunk callback - update message in real-time
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
        (response: any) => {
          console.log('Message complete:', response);

          // Extract final content
          const finalContent = response.ai_message?.content ||
                             response.fullResponse ||
                             streamingContent ||
                             'عذراً، لم أتمكن من معالجة طلبك.';

          // Update with final content and metadata
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: finalContent,
                    processing_time_ms: response.processing_time_ms,
                  }
                : msg
            )
          );

          // Update conversation ID if new conversation was created
          if (response.conversation_id && !conversationId) {
            setConversationId(response.conversation_id);
          }

          // Reload conversations list for authenticated users
          if (isAuthenticated) {
            loadConversations();
          }

          setIsSending(false);
        },
        // onError callback
        (error: string) => {
          console.error('Streaming error:', error);
          setError(error);

          // Remove the empty assistant message on error
          setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));

          Alert.alert('خطأ', 'فشل في إرسال الرسالة. يرجى المحاولة مرة أخرى.');
          setIsSending(false);
        },
        // Pass the abort signal
        messageAbortController.signal
      );
    } catch (error) {
      console.error('Failed to send message:', error);

      // Remove both user and assistant messages on error
      setMessages(prev => prev.slice(0, -2));

      Alert.alert('خطأ', 'حدث خطأ في الإرسال. حاول مرة أخرى.');
      setIsSending(false);
    }
  }, [conversationId, sessionId, isAuthenticated, messages.length, loadConversations]);

  // Handle suggested question tap
  const handleSuggestedQuestion = useCallback((question: string) => {
    handleSendMessage(question);
  }, [handleSendMessage]);

  // Start new conversation
  const startNewConversation = useCallback(() => {
    // Cancel any ongoing message requests
    if (messageAbortController) {
      messageAbortController.abort();
      messageAbortController = null;
    }

    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  // Render message item - memoized to prevent unnecessary re-renders
  const renderMessage = useCallback(({ item, index }: { item: Message; index: number }) => (
    <MessageBubble
      message={item}
      isLastMessage={index === messages.length - 1}
    />
  ), [messages.length]);

  // Render empty state with suggested questions - memoized
  const renderEmptyState = useCallback(() => (
    <View style={[styles.emptyState, { backgroundColor: colors.background }]}>
      <Text style={[styles.welcomeTitle, { color: colors.text }]}>
        {isAuthenticated ? `أهلاً ${user?.full_name}` : 'مرحباً بك'}
      </Text>
      <Text style={[styles.welcomeSubtitle, { color: colors.textSecondary }]}>
        اسأل أي سؤال قانوني وسأساعدك في الإجابة عليه
      </Text>

      <View style={styles.suggestionsContainer}>
        <Text style={[styles.suggestionsTitle, { color: colors.textSecondary }]}>
          أسئلة مقترحة:
        </Text>
        {SUGGESTED_QUESTIONS.map((question, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.suggestionButton, { backgroundColor: colors.surface, borderColor: colors.border }]}
            onPress={() => handleSuggestedQuestion(question)}
            activeOpacity={0.7}
          >
            <Text style={[styles.suggestionText, { color: colors.text }]}>
              {question}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  ), [colors, isAuthenticated, user?.full_name, handleSuggestedQuestion]);

  // Render loading indicator - memoized
  const renderLoadingIndicator = useCallback(() => {
    if (!isSending) {return null;}

    return (
      <View style={[styles.loadingContainer, { backgroundColor: colors.surface }]}>
        <ActivityIndicator size="small" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
          جاري التحليل القانوني...
        </Text>
      </View>
    );
  }, [isSending, colors]);

  // Render header with conversation actions - memoized
  const renderHeader = useCallback(() => {
    if (!isAuthenticated || conversations.length === 0) {return null;}

    return (
      <View style={[styles.header, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <TouchableOpacity
          style={[styles.newChatButton, { backgroundColor: colors.primary }]}
          onPress={startNewConversation}
          activeOpacity={0.7}
        >
          <Text style={styles.newChatButtonText}>محادثة جديدة +</Text>
        </TouchableOpacity>

        {conversationId && (
          <Text style={[styles.conversationInfo, { color: colors.textSecondary }]}>
            المحادثة الحالية
          </Text>
        )}
      </View>
    );
  }, [isAuthenticated, conversations.length, colors, conversationId, startNewConversation]);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 16,
      paddingVertical: 12,
      borderBottomWidth: 1,
    },
    newChatButton: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 20,
    },
    newChatButtonText: {
      color: '#ffffff',
      fontSize: 14,
      fontWeight: '600',
    },
    conversationInfo: {
      fontSize: 14,
    },
    messagesList: {
      flex: 1,
      paddingVertical: 8,
    },
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: 32,
      paddingTop: 40,
    },
    welcomeTitle: {
      fontSize: 28,
      fontWeight: 'bold',
      marginBottom: 12,
      textAlign: 'center',
    },
    welcomeSubtitle: {
      fontSize: 16,
      marginBottom: 40,
      textAlign: 'center',
      lineHeight: 24,
    },
    suggestionsContainer: {
      width: '100%',
      maxWidth: 400,
    },
    suggestionsTitle: {
      fontSize: 14,
      marginBottom: 16,
      textAlign: 'center',
    },
    suggestionButton: {
      padding: 16,
      borderRadius: 12,
      marginBottom: 12,
      borderWidth: 1,
    },
    suggestionText: {
      fontSize: 15,
      textAlign: 'right',
      lineHeight: 22,
    },
    loadingContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 12,
      marginHorizontal: 16,
      marginVertical: 8,
      borderRadius: 12,
      gap: 12,
    },
    loadingText: {
      fontSize: 14,
    },
    errorContainer: {
      padding: 16,
      marginHorizontal: 16,
      marginVertical: 8,
      borderRadius: 12,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    errorText: {
      flex: 1,
      fontSize: 14,
    },
    retryButton: {
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
    },
    retryButtonText: {
      fontSize: 12,
      fontWeight: '600',
    },
  });

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {renderHeader()}

      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 100 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={[
            styles.messagesList,
            messages.length === 0 && { flex: 1 },
          ]}
          ListEmptyComponent={renderEmptyState}
          ListFooterComponent={renderLoadingIndicator}
          onContentSizeChange={() => {
            if (messages.length > 0) {
              flatListRef.current?.scrollToEnd({ animated: true });
            }
          }}
          refreshControl={
            isAuthenticated ? (
              <RefreshControl
                refreshing={refreshing}
                onRefresh={loadConversations}
                colors={[colors.primary]}
                tintColor={colors.primary}
              />
            ) : undefined
          }
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          removeClippedSubviews={Platform.OS === 'android'}
          maxToRenderPerBatch={10}
          initialNumToRender={10}
          windowSize={10}
        />

        {error && (
          <View style={[styles.errorContainer, { backgroundColor: colors.error + '20' }]}>
            <Text style={[styles.errorText, { color: colors.error }]}>
              {error}
            </Text>
            <TouchableOpacity
              style={[styles.retryButton, { backgroundColor: colors.error }]}
              onPress={() => setError(null)}
            >
              <Text style={[styles.retryButtonText, { color: '#ffffff' }]}>
                إغلاق
              </Text>
            </TouchableOpacity>
          </View>
        )}

        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isSending || isLoading}
          placeholder={
            isSending
              ? 'جاري الإرسال...'
              : 'اكتب سؤالك القانوني هنا...'
          }
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

export default ChatScreen;
