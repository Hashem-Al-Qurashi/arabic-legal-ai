import React from 'react';
import { useOnlineStatus } from '../../hooks/useOnlineStatus';

export const ConnectionStatus: React.FC = () => {
  const { isOnline, isSlowConnection, connectionType } = useOnlineStatus();

  if (isOnline && !isSlowConnection) {
    return null; // Don't show anything when connection is good
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        padding: '12px 16px',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: '600',
        color: 'white',
        background: isOnline 
          ? 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)' // Slow connection - orange
          : 'linear-gradient(90deg, #dc2626 0%, #b91c1c 100%)', // Offline - red
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        animation: 'slideDown 0.3s ease-out',
        direction: 'rtl'
      }}
    >
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        gap: '8px'
      }}>
        {!isOnline ? (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 12h18m-9-9v18"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            <span>لا يوجد اتصال بالإنترنت</span>
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7v10c0 5.55 3.84 10 9 9s9-4.45 9-9V7l-10-5z"/>
            </svg>
            <span>اتصال بطيء ({connectionType})</span>
          </>
        )}
      </div>

      <style>{`
        @keyframes slideDown {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};