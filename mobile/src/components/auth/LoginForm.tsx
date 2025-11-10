import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Button, Input } from '@/components/ui';
import type { LoginCredentials } from '@/types';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps): React.JSX.Element {
  const { login } = useAuth();
  const { colors } = useTheme();
  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Partial<LoginCredentials>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginCredentials> = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (): Promise<void> => {
    if (!validateForm()) {return;}

    setLoading(true);
    try {
      const result = await login(formData);

      if (result.success) {
        onSuccess?.();
      } else {
        Alert.alert('Login Failed', result.error || 'Please check your credentials and try again.');
      }
    } catch {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof LoginCredentials, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={[styles.title, { color: colors.text }]}>
        Sign In
      </Text>

      <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
        Welcome back to Arabic Legal AI
      </Text>

      <View style={styles.form}>
        <Input
          label="Email"
          placeholder="Enter your email"
          value={formData.email}
          onChangeText={(text) => updateField('email', text)}
          keyboardType="email-address"
          autoCapitalize="none"
          autoComplete="email"
          error={errors.email || undefined}
        />

        <Input
          label="Password"
          placeholder="Enter your password"
          value={formData.password}
          onChangeText={(text) => updateField('password', text)}
          secureTextEntry
          showPasswordToggle
          error={errors.password || undefined}
        />

        <Button
          title="Sign In"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading}
          style={styles.submitButton}
        />

        {onSwitchToRegister && (
          <View style={styles.switchContainer}>
            <Text style={[styles.switchText, { color: colors.textSecondary }]}>
              Don't have an account?{' '}
            </Text>
            <Button
              title="Sign Up"
              onPress={onSwitchToRegister}
              variant="ghost"
              size="small"
            />
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 32,
  },
  form: {
    gap: 16,
  },
  submitButton: {
    marginTop: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
  },
  switchText: {
    fontSize: 16,
  },
});
