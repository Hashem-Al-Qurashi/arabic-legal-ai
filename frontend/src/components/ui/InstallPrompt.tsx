import React from 'react';
import { usePWAInstall } from '../../hooks/usePWAInstall';

export const InstallPrompt: React.FC = () => {
  const { showInstallPrompt, promptInstall, dismissPrompt } = usePWAInstall();

  if (!showInstallPrompt) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '20px',
        left: '20px',
        right: '20px',
        zIndex: 9998,
        background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 8px 32px rgba(0, 108, 53, 0.3), 0 4px 16px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        animation: 'slideUpInstall 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        direction: 'rtl'
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '16px'
      }}>
        {/* App Icon */}
        <div style={{
          width: '56px',
          height: '56px',
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          flexShrink: 0
        }}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M14,2H6a2,2 0 0,0 -2,2v16a2,2 0 0,0 2,2h12a2,2 0 0,0 2,-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10,9 9,9 8,9"/>
          </svg>
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{
            color: 'white',
            fontSize: '18px',
            fontWeight: '600',
            margin: '0 0 8px 0',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
          }}>
            تثبيت تطبيق حكم
          </h3>
          
          <p style={{
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: '14px',
            lineHeight: '1.4',
            margin: '0 0 16px 0',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
          }}>
            احصل على تجربة أفضل مع الوصول السريع والتشغيل بدون انترنت
          </p>

          {/* Buttons */}
          <div style={{
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={promptInstall}
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                color: '#006C35',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 20px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'white';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              تثبيت التطبيق
            </button>

            <button
              onClick={dismissPrompt}
              style={{
                background: 'transparent',
                color: 'rgba(255, 255, 255, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '8px',
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
              }}
            >
              ليس الآن
            </button>
          </div>
        </div>

        {/* Close button */}
        <button
          onClick={dismissPrompt}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.6)',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '4px',
            transition: 'color 0.2s ease',
            flexShrink: 0
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.color = 'white';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.color = 'rgba(255, 255, 255, 0.6)';
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <style>{`
        @keyframes slideUpInstall {
          from {
            transform: translateY(100%);
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