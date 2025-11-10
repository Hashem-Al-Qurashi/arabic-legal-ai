import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';

function AuthScreen(): React.JSX.Element {
  const { colors } = useTheme();
  const { login, register, loading } = useAuth();
  const [isLogin, setIsLogin] = useState(true);

  const handleAuth = async (): Promise<void> => {
    // Demo credentials for development
    if (isLogin) {
      await login({ email: 'demo@example.com', password: 'password' });
    } else {
      await register({
        email: 'demo@example.com',
        password: 'password',
        full_name: 'Demo User',
      });
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
      justifyContent: 'center',
      alignItems: 'center',
      padding: 20,
    },
    title: {
      fontSize: 28,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 10,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 16,
      color: colors.textSecondary,
      marginBottom: 40,
      textAlign: 'center',
    },
    button: {
      backgroundColor: colors.primary,
      paddingHorizontal: 32,
      paddingVertical: 16,
      borderRadius: 8,
      marginBottom: 16,
      minWidth: 200,
    },
    buttonText: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: '600',
      textAlign: 'center',
    },
    switchButton: {
      paddingVertical: 12,
    },
    switchText: {
      color: colors.primary,
      fontSize: 14,
      textAlign: 'center',
    },
  });

  return (
    <SafeAreaView style={styles.container}>
      <View>
        <Text style={styles.title}>مساعد القانون العربي</Text>
        <Text style={styles.subtitle}>
          مساعدك الذكي للاستشارات القانونية
        </Text>

        <TouchableOpacity
          style={styles.button}
          onPress={handleAuth}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {loading ? 'جاري التحميل...' : isLogin ? 'تسجيل الدخول' : 'إنشاء حساب'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.switchButton}
          onPress={() => setIsLogin(!isLogin)}
        >
          <Text style={styles.switchText}>
            {isLogin ? 'ليس لديك حساب؟ إنشاء حساب جديد' : 'لديك حساب؟ تسجيل الدخول'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

export default AuthScreen;
