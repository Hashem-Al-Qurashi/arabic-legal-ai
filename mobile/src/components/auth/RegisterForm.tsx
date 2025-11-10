import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Button, Input } from '@/components/ui';
import type { RegisterCredentials } from '@/types';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export function RegisterForm({ onSuccess, onSwitchToLogin }: RegisterFormProps): React.JSX.Element {
  const { register } = useAuth();
  const { colors } = useTheme();
  const [formData, setFormData] = useState<RegisterCredentials>({
    full_name: '',
    email: '',
    password: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Partial<RegisterCredentials & { confirmPassword: string }>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterCredentials & { confirmPassword: string }> = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (confirmPassword !== formData.password) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (): Promise<void> => {
    if (!validateForm()) {return;}

    setLoading(true);
    try {
      const result = await register(formData);

      if (result.success) {
        Alert.alert(
          'Registration Successful',
          'You can now sign in with your new account.',
          [{ text: 'OK', onPress: onSuccess }]
        );
      } else {
        Alert.alert('Registration Failed', result.error || 'Please try again.');
      }
    } catch {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof RegisterCredentials, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const updateConfirmPassword = (value: string): void => {
    setConfirmPassword(value);
    if (errors.confirmPassword) {
      setErrors(prev => ({ ...prev, confirmPassword: '' }));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={[styles.title, { color: colors.text }]}>
        Create Account
      </Text>

      <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
        Join Arabic Legal AI today
      </Text>

      <View style={styles.form}>
        <Input
          label="Full Name"
          placeholder="Enter your full name"
          value={formData.full_name}
          onChangeText={(text) => updateField('full_name', text)}
          autoCapitalize="words"
          error={errors.full_name || undefined}
        />

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
          placeholder="Create a password"
          value={formData.password}
          onChangeText={(text) => updateField('password', text)}
          secureTextEntry
          showPasswordToggle
          error={errors.password || undefined}
        />

        <Input
          label="Confirm Password"
          placeholder="Confirm your password"
          value={confirmPassword}
          onChangeText={updateConfirmPassword}
          secureTextEntry
          showPasswordToggle
          error={errors.confirmPassword || undefined}
        />

        <Button
          title="Sign Up"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading}
          style={styles.submitButton}
        />

        {onSwitchToLogin && (
          <View style={styles.switchContainer}>
            <Text style={[styles.switchText, { color: colors.textSecondary }]}>
              Already have an account?{' '}
            </Text>
            <Button
              title="Sign In"
              onPress={onSwitchToLogin}
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
