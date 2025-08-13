// Replace your entire frontend/src/App.tsx with this smooth implementation
import React, { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthScreen from './components/auth/AuthScreen';
import ChatApp from './components/chat/ChatApp';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

const AppContent: React.FC = () => {
  const { loading, user, isGuest } = useAuth();
  const [currentRoute, setCurrentRoute] = useState(window.location.pathname);

  useEffect(() => {
    const handleRouteChange = () => {
      console.log('🛣️ Route changed to:', window.location.pathname);
      setCurrentRoute(window.location.pathname);
    };

    const handleAuthNavigation = () => {
      console.log('🔄 Auth navigation event received');
      setCurrentRoute(window.location.pathname);
    };

    window.addEventListener('popstate', handleRouteChange);
    window.addEventListener('auth-navigation', handleAuthNavigation);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
      window.removeEventListener('auth-navigation', handleAuthNavigation);
    };
  }, []);

  // Log current state for debugging
// Removed infinite console log - use React DevTools instead
  // Rest of your AppContent code stays the same..

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
          padding: '2rem',
          backdropFilter: 'blur(20px)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(255, 255, 255, 0.3)',
            borderTop: '3px solid white',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: 'white', margin: 0 }}>جاري التحميل...</p>
        </div>
      </div>
    );
  }

  // Route to auth page
  if (currentRoute === '/auth') {
    return <AuthScreen />;
  }

  // Default route - Chat (for both guests and authenticated users)
  return <ChatApp />;
};

export default App;