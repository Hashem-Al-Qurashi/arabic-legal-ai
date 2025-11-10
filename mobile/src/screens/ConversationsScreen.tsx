import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';

function ConversationsScreen(): React.JSX.Element {
  const { colors } = useTheme();

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 10,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
    },
  });

  return (
    <SafeAreaView style={styles.container}>
      <View>
        <Text style={styles.title}>المحادثات</Text>
        <Text style={styles.subtitle}>
          جميع محادثاتك السابقة
        </Text>
      </View>
    </SafeAreaView>
  );
}

export default ConversationsScreen;
