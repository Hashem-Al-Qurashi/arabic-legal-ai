import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';

function SettingsScreen(): React.JSX.Element {
  const { colors, theme, toggleTheme } = useTheme();
  const { logout, user } = useAuth();

  const handleLogout = async (): Promise<void> => {
    await logout();
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
      padding: 20,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 30,
      textAlign: 'center',
    },
    section: {
      marginBottom: 20,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 15,
    },
    button: {
      backgroundColor: colors.surface,
      padding: 15,
      borderRadius: 8,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: colors.border,
    },
    buttonText: {
      color: colors.text,
      fontSize: 16,
      textAlign: 'center',
    },
    logoutButton: {
      backgroundColor: colors.error,
      padding: 15,
      borderRadius: 8,
      marginTop: 20,
    },
    logoutText: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: '600',
      textAlign: 'center',
    },
    userInfo: {
      backgroundColor: colors.surface,
      padding: 15,
      borderRadius: 8,
      marginBottom: 20,
    },
    userText: {
      color: colors.text,
      fontSize: 14,
      textAlign: 'center',
    },
  });

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>الإعدادات</Text>

      {user && (
        <View style={styles.userInfo}>
          <Text style={styles.userText}>{user.full_name}</Text>
          <Text style={styles.userText}>{user.email}</Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>المظهر</Text>
        <TouchableOpacity style={styles.button} onPress={toggleTheme}>
          <Text style={styles.buttonText}>
            {theme === 'light' ? 'التبديل للوضع الليلي' : 'التبديل للوضع النهاري'}
          </Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>تسجيل الخروج</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

export default SettingsScreen;
