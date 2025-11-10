import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Text,
  Animated,
  KeyboardAvoidingView,
  Platform,
  Keyboard,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import HapticFeedback from 'react-native-haptic-feedback';
import { useTheme } from '@/contexts/ThemeContext';
import { useOffline } from '@/hooks/useOffline';
import { FileUpload } from './FileUpload';
import type { FileAttachment } from '@/types';

interface EnhancedChatInputProps {
  onSendMessage: (message: string, attachments?: FileAttachment[]) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  showOfflineIndicator?: boolean;
  maxMessageLength?: number;
}

export function EnhancedChatInput({
  onSendMessage,
  disabled = false,
  placeholder = 'اكتب سؤالك القانوني هنا...',
  showOfflineIndicator = true,
  maxMessageLength = 2000,
}: EnhancedChatInputProps): React.JSX.Element {
  const { colors } = useTheme();
  const { isOnline, queuedMessages } = useOffline();

  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [inputHeight, setInputHeight] = useState(48);
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const [showActions, setShowActions] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    // Animate offline indicator
    if (showOfflineIndicator && !isOnline) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(fadeAnim, {
            toValue: 0.3,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [isOnline, showOfflineIndicator, fadeAnim]);

  const handleSend = async (): Promise<void> => {
    const trimmedMessage = message.trim();
    if ((!trimmedMessage && attachments.length === 0) || sending || disabled) {
      return;
    }

    // Haptic feedback
    HapticFeedback.trigger('impactMedium');

    // Animate send button
    Animated.sequence([
      Animated.spring(scaleAnim, {
        toValue: 0.8,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
      }),
    ]).start();

    setSending(true);
    try {
      await onSendMessage(trimmedMessage, attachments.length > 0 ? attachments : undefined);
      setMessage('');
      setAttachments([]);
      setInputHeight(48);
      HapticFeedback.trigger('notificationSuccess');

      // Dismiss keyboard
      Keyboard.dismiss();
    } catch (error) {
      HapticFeedback.trigger('notificationError');
      Alert.alert(
        'خطأ في الإرسال',
        !isOnline
          ? 'أنت غير متصل بالإنترنت. تم حفظ رسالتك وسيتم إرسالها عند الاتصال.'
          : 'فشل في إرسال الرسالة. يرجى المحاولة مرة أخرى.'
      );
    } finally {
      setSending(false);
    }
  };

  const handleContentSizeChange = (event: any) => {
    const height = Math.min(120, Math.max(48, event.nativeEvent.contentSize.height));
    setInputHeight(height);
  };

  const handleFilesSelected = (files: FileAttachment[]) => {
    setAttachments(files);
    HapticFeedback.trigger('selection');
  };

  const toggleActions = () => {
    HapticFeedback.trigger('impactLight');
    setShowActions(!showActions);
  };

  const handleVoiceRecord = () => {
    HapticFeedback.trigger('impactMedium');
    setIsRecording(!isRecording);
    // TODO: Implement voice recording functionality
    Alert.alert('التسجيل الصوتي', 'سيتم إضافة هذه الميزة قريباً');
  };

  const canSend = (message.trim().length > 0 || attachments.length > 0) && !sending && !disabled;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
    >
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        {/* Offline indicator */}
        {showOfflineIndicator && !isOnline && (
          <Animated.View
            style={[
              styles.offlineIndicator,
              { backgroundColor: colors.warning, opacity: fadeAnim },
            ]}
          >
            <Icon name="wifi-off" size={16} color="#fff" />
            <Text style={styles.offlineText}>
              غير متصل - سيتم الإرسال عند الاتصال
            </Text>
            {queuedMessages.length > 0 && (
              <View style={styles.queueBadge}>
                <Text style={styles.queueBadgeText}>{queuedMessages.length}</Text>
              </View>
            )}
          </Animated.View>
        )}

        {/* Attachments preview */}
        {attachments.length > 0 && (
          <View style={[styles.attachmentsContainer, { backgroundColor: colors.card }]}>
            <Text style={[styles.attachmentsText, { color: colors.text }]}>
              {attachments.length} ملف مرفق
            </Text>
            <TouchableOpacity onPress={() => setAttachments([])}>
              <Icon name="close" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>
        )}

        {/* Main input container */}
        <View style={[styles.inputWrapper, { borderColor: colors.border }]}>
          {/* Action buttons */}
          <View style={styles.actionsContainer}>
            {showActions ? (
              <>
                <FileUpload
                  onFilesSelected={handleFilesSelected}
                  disabled={disabled || sending}
                />
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={handleVoiceRecord}
                  disabled={disabled || sending}
                >
                  <Icon
                    name={isRecording ? 'mic-off' : 'mic'}
                    size={24}
                    color={isRecording ? colors.error : colors.primary}
                  />
                </TouchableOpacity>
              </>
            ) : (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={toggleActions}
                disabled={disabled}
              >
                <Icon name="add" size={24} color={colors.primary} />
              </TouchableOpacity>
            )}
          </View>

          {/* Text input */}
          <View style={[
            styles.inputContainer,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
              minHeight: inputHeight + 16,
            },
          ]}>
            <TextInput
              ref={inputRef}
              style={[
                styles.input,
                {
                  color: colors.text,
                  height: inputHeight,
                  textAlign: 'right',
                },
              ]}
              placeholder={placeholder}
              placeholderTextColor={colors.textSecondary}
              value={message}
              onChangeText={setMessage}
              multiline
              maxLength={maxMessageLength}
              editable={!disabled && !sending}
              onSubmitEditing={handleSend}
              returnKeyType="send"
              blurOnSubmit={false}
              onContentSizeChange={handleContentSizeChange}
              textAlignVertical="center"
            />
          </View>

          {/* Send button */}
          <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
            <TouchableOpacity
              style={[
                styles.sendButton,
                canSend
                  ? { backgroundColor: colors.primary }
                  : { backgroundColor: colors.border },
              ]}
              onPress={handleSend}
              disabled={!canSend}
              activeOpacity={0.7}
            >
              {sending ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Icon
                  name="send"
                  size={20}
                  color={canSend ? '#fff' : colors.textSecondary}
                />
              )}
            </TouchableOpacity>
          </Animated.View>
        </View>

        {/* Character count */}
        {message.length > maxMessageLength * 0.9 && (
          <Text style={[
            styles.characterCount,
            { color: message.length >= maxMessageLength ? colors.error : colors.warning },
          ]}>
            {message.length}/{maxMessageLength}
          </Text>
        )}
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  offlineIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  offlineText: {
    color: '#fff',
    fontSize: 12,
    marginLeft: 8,
    fontWeight: '500',
  },
  queueBadge: {
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginLeft: 8,
  },
  queueBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  attachmentsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 8,
  },
  attachmentsText: {
    fontSize: 14,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    borderTopWidth: 1,
  },
  actionsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingBottom: 8,
  },
  actionButton: {
    padding: 8,
    marginHorizontal: 4,
  },
  inputContainer: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 8,
  },
  input: {
    fontSize: 16,
    lineHeight: 20,
    maxHeight: 120,
    paddingVertical: 4,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  characterCount: {
    fontSize: 11,
    textAlign: 'right',
    marginTop: 4,
    paddingHorizontal: 8,
  },
});
