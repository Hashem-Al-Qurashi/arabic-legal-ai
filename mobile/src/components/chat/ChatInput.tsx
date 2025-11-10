import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, Alert, Text } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = 'اكتب سؤالك القانوني هنا...',
}: ChatInputProps): React.JSX.Element {
  const { colors } = useTheme();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [inputHeight, setInputHeight] = useState(48);

  const handleSend = async (): Promise<void> => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || sending || disabled) {return;}

    setSending(true);
    try {
      await onSendMessage(trimmedMessage);
      setMessage('');
      setInputHeight(48); // Reset height after sending
    } catch {
      Alert.alert('خطأ', 'فشل في إرسال الرسالة. يرجى المحاولة مرة أخرى.');
    } finally {
      setSending(false);
    }
  };

  const canSend = message.trim().length > 0 && !sending && !disabled;

  // Handle content size change for auto-growing textarea
  const handleContentSizeChange = (event: any) => {
    const height = Math.min(120, Math.max(48, event.nativeEvent.contentSize.height));
    setInputHeight(height);
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background, borderColor: colors.border }]}>
      <View style={[
        styles.inputContainer,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
          minHeight: inputHeight + 16,
        },
      ]}>
        <TextInput
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
          maxLength={2000}
          editable={!disabled && !sending}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          blurOnSubmit={false}
          onContentSizeChange={handleContentSizeChange}
          textAlignVertical="center"
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            canSend ? { backgroundColor: colors.primary } : { backgroundColor: colors.border },
          ]}
          onPress={handleSend}
          disabled={!canSend}
          activeOpacity={0.7}
        >
          <Text style={[
            styles.sendButtonText,
            canSend ? styles.sendButtonTextActive : { color: colors.textSecondary },
          ]}>
            {sending ? '⏳' : '←'}
          </Text>
        </TouchableOpacity>
      </View>
      {message.length > 1800 && (
        <Text style={[styles.characterCount, { color: colors.warning }]}>
          {message.length}/2000
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    borderWidth: 1,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
    minHeight: 48,
  },
  input: {
    flex: 1,
    fontSize: 16,
    lineHeight: 20,
    maxHeight: 120,
    paddingVertical: 8,
  },
  sendButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  sendButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  sendButtonTextActive: {
    color: '#ffffff',
  },
  characterCount: {
    fontSize: 12,
    textAlign: 'right',
    marginTop: 4,
  },
});
