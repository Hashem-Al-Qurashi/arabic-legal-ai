import { useState, useEffect } from 'react';

interface OnlineStatus {
  isOnline: boolean;
  isSlowConnection: boolean;
  connectionType: string;
}

export const useOnlineStatus = (): OnlineStatus => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [connectionType, setConnectionType] = useState('unknown');

  useEffect(() => {
    const handleOnline = () => {
      console.log('🌐 Connection restored');
      setIsOnline(true);
      
      // Dispatch event for message queue processing
      window.dispatchEvent(new CustomEvent('connection-restored'));
    };

    const handleOffline = () => {
      console.log('📡 Connection lost');
      setIsOnline(false);
    };

    // Check connection speed and type
    const checkConnectionQuality = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        setConnectionType(connection.effectiveType || 'unknown');
        
        // Consider 2G as slow connection
        setIsSlowConnection(
          connection.effectiveType === '2g' || 
          connection.effectiveType === 'slow-2g'
        );
      }
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check connection quality on load and changes
    checkConnectionQuality();
    if ('connection' in navigator) {
      (navigator as any).connection.addEventListener('change', checkConnectionQuality);
    }

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if ('connection' in navigator) {
        (navigator as any).connection.removeEventListener('change', checkConnectionQuality);
      }
    };
  }, []);

  return {
    isOnline,
    isSlowConnection,
    connectionType
  };
};