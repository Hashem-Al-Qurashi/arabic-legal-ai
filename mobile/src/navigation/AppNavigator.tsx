import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { useAuth } from '@/contexts/AuthContext';

// Import screens (we'll create these next)
import AuthScreen from '@/screens/AuthScreen';
import { EnhancedChatScreen } from '@/screens/EnhancedChatScreen';
import ConversationsScreen from '@/screens/ConversationsScreen';
import SettingsScreen from '@/screens/SettingsScreen';

// Navigation parameter types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Chat: { conversationId?: string };
  Conversations: undefined;
  Settings: undefined;
};

export type MainDrawerParamList = {
  Chat: { conversationId?: string };
  Conversations: undefined;
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const Drawer = createDrawerNavigator<MainDrawerParamList>();

// Main authenticated navigation with drawer
function MainNavigator(): React.JSX.Element {
  return (
    <Drawer.Navigator
      initialRouteName="Chat"
      screenOptions={{
        headerShown: true,
        drawerType: 'slide',
        drawerPosition: 'right', // RTL support for Arabic
        drawerStyle: {
          backgroundColor: '#f8f9fa',
          width: 280,
        },
        headerStyle: {
          backgroundColor: '#2563eb',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
          fontSize: 18,
        },
      }}
    >
      <Drawer.Screen
        name="Chat"
        component={EnhancedChatScreen}
        options={{
          title: 'المحادثة',
          drawerLabel: 'المحادثة الرئيسية',
        }}
      />
      <Drawer.Screen
        name="Conversations"
        component={ConversationsScreen}
        options={{
          title: 'المحادثات',
          drawerLabel: 'جميع المحادثات',
        }}
      />
      <Drawer.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          title: 'الإعدادات',
          drawerLabel: 'الإعدادات',
        }}
      />
    </Drawer.Navigator>
  );
}

// Root navigator handling authentication state
function AppNavigator(): React.JSX.Element {
  const { isAuthenticated, loading } = useAuth();

  // Show loading screen while checking auth state
  if (loading) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Auth" component={AuthScreen} />
      </Stack.Navigator>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isAuthenticated ? (
        <Stack.Screen name="Main" component={MainNavigator} />
      ) : (
        <Stack.Screen name="Auth" component={AuthScreen} />
      )}
    </Stack.Navigator>
  );
}

export default AppNavigator;
