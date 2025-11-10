import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import type { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
  isLastMessage?: boolean;
}

// Parse message content for basic formatting
function parseMessageContent(content: string): React.ReactNode[] {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];

  lines.forEach((line, lineIndex) => {
    // Check for headers (lines starting with #)
    if (line.startsWith('### ')) {
      elements.push(
        <Text key={`h3-${lineIndex}`} style={styles.heading3}>
          {line.substring(4).trim()}
        </Text>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <Text key={`h2-${lineIndex}`} style={styles.heading2}>
          {line.substring(3).trim()}
        </Text>
      );
    } else if (line.startsWith('# ')) {
      elements.push(
        <Text key={`h1-${lineIndex}`} style={styles.heading1}>
          {line.substring(2).trim()}
        </Text>
      );
    }
    // Check for bullet points
    else if (line.trim().startsWith('• ') || line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      elements.push(
        <View key={`bullet-${lineIndex}`} style={styles.bulletContainer}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.bulletText}>
            {line.substring(line.indexOf(' ') + 1).trim()}
          </Text>
        </View>
      );
    }
    // Check for numbered lists
    else if (/^\d+\.\s/.test(line.trim())) {
      const match = line.trim().match(/^(\d+)\.\s(.*)$/);
      if (match) {
        elements.push(
          <View key={`numbered-${lineIndex}`} style={styles.bulletContainer}>
            <Text style={styles.bullet}>{match[1]}.</Text>
            <Text style={styles.bulletText}>{match[2]}</Text>
          </View>
        );
      }
    }
    // Regular paragraph
    else if (line.trim()) {
      elements.push(
        <Text key={`p-${lineIndex}`} style={styles.paragraph}>
          {formatInlineText(line)}
        </Text>
      );
    }
    // Empty line (spacing)
    else if (lineIndex > 0 && lineIndex < lines.length - 1) {
      elements.push(<View key={`space-${lineIndex}`} style={styles.spacer} />);
    }
  });

  return elements;
}

// Format inline text for bold and italic
function formatInlineText(text: string): React.ReactNode {
  // Simple regex for **bold** text
  const boldPattern = /\*\*(.*?)\*\*/g;
  const parts = text.split(boldPattern);

  return parts.map((part, index) => {
    // Odd indices are the bold parts
    if (index % 2 === 1) {
      return (
        <Text key={index} style={styles.bold}>
          {part}
        </Text>
      );
    }
    return part;
  });
}

export function MessageBubble({ message }: MessageBubbleProps): React.JSX.Element {
  const { colors } = useTheme();
  const isUser = message.role === 'user';

  const bubbleStyles = [
    styles.bubble,
    isUser ? styles.userBubble : styles.assistantBubble,
    {
      backgroundColor: isUser ? colors.primary : colors.surface,
      borderColor: isUser ? colors.primary : colors.border,
    },
  ];

  const textStyles = [
    styles.text,
    { color: isUser ? '#ffffff' : colors.text },
  ];

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'م' : 'ص';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes < 10 ? `0${minutes}` : minutes;
    return `${displayHours}:${displayMinutes} ${ampm}`;
  };

  // Render content based on role
  const renderContent = () => {
    if (isUser) {
      // User messages are rendered as plain text
      return (
        <Text style={textStyles}>
          {message.content}
        </Text>
      );
    } else {
      // Assistant messages get formatted
      return (
        <View style={styles.formattedContent}>
          {parseMessageContent(message.content)}
        </View>
      );
    }
  };

  return (
    <View style={[styles.container, isUser ? styles.userContainer : styles.assistantContainer]}>
      <View style={bubbleStyles}>
        {renderContent()}

        <View style={styles.metaContainer}>
          <Text style={[
            styles.timestamp,
            isUser ? styles.timestampUser : { color: colors.textSecondary },
          ]}>
            {formatTime(message.timestamp)}
          </Text>
          {message.processing_time_ms && (
            <Text style={[
              styles.processingTime,
              isUser ? styles.timestampUser : { color: colors.textSecondary },
            ]}>
              • {(message.processing_time_ms / 1000).toFixed(1)}ث
            </Text>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 4,
    paddingHorizontal: 16,
  },
  userContainer: {
    alignItems: 'flex-end',
  },
  assistantContainer: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '85%',
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
    minWidth: 80,
  },
  userBubble: {
    borderBottomRightRadius: 4,
    marginLeft: 40,
  },
  assistantBubble: {
    borderBottomLeftRadius: 4,
    marginRight: 40,
  },
  text: {
    fontSize: 16,
    lineHeight: 24,
    textAlign: 'right',
  },
  formattedContent: {
    flexDirection: 'column',
  },
  heading1: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 8,
    textAlign: 'right',
  },
  heading2: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 6,
    marginBottom: 6,
    textAlign: 'right',
  },
  heading3: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 4,
    marginBottom: 4,
    textAlign: 'right',
  },
  paragraph: {
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 8,
    textAlign: 'right',
  },
  bulletContainer: {
    flexDirection: 'row-reverse',
    marginBottom: 6,
    paddingRight: 0,
  },
  bullet: {
    fontSize: 16,
    marginLeft: 8,
    minWidth: 20,
    textAlign: 'right',
  },
  bulletText: {
    fontSize: 16,
    lineHeight: 24,
    flex: 1,
    textAlign: 'right',
  },
  bold: {
    fontWeight: 'bold',
  },
  spacer: {
    height: 8,
  },
  metaContainer: {
    flexDirection: 'row',
    marginTop: 4,
    alignItems: 'center',
  },
  timestamp: {
    fontSize: 12,
  },
  timestampUser: {
    color: 'rgba(255,255,255,0.7)',
  },
  processingTime: {
    fontSize: 12,
    marginLeft: 4,
  },
});
