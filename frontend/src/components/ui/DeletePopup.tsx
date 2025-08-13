import React, { useEffect } from 'react';

interface DeletePopupProps {
  isOpen: boolean;
  conversationTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const DeletePopup: React.FC<DeletePopupProps> = ({ isOpen, conversationTitle, onConfirm, onCancel }) => {
  useEffect(() => {
    if (isOpen) {
      // Focus management for accessibility
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Premium Saudi backdrop */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 15, 15, 0.85)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backdropFilter: 'blur(20px)',
          animation: 'fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
        onClick={onCancel}
      >
        {/* Premium glass popup */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%)',
            borderRadius: '20px',
            padding: '32px',
            maxWidth: '400px',
            width: '90%',
            boxShadow: `
              0 32px 64px rgba(0, 0, 0, 0.12),
              0 0 0 1px rgba(255, 255, 255, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.2)
            `,
            animation: 'premiumSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
            direction: 'rtl',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(20px)'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{
            textAlign: 'center',
            marginBottom: '24px'
          }}>
            {/* Warning Icon with pulsing effect */}
            <div style={{
              width: '72px',
              height: '72px',
              background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
              borderRadius: '20px',
              margin: '0 auto 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 32px rgba(220, 38, 38, 0.3)',
              position: 'relative',
              animation: 'subtlePulse 2s infinite'
            }}>
              {/* Inner glow effect */}
              <div style={{
                position: 'absolute',
                inset: '2px',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%)',
                borderRadius: '18px'
              }} />
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" style={{ position: 'relative', zIndex: 1 }}>
                <polyline points="3,6 5,6 21,6"/>
                <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </div>
            
            <h3 style={{
              margin: '0 0 8px 0',
              color: '#212121',
              fontSize: '22px',
              fontWeight: '600',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif',
              letterSpacing: '-0.01em'
            }}>
              حذف المحادثة
            </h3>
            
            <p style={{
              margin: '0 0 16px 0',
              color: '#757575',
              fontSize: '15px',
              fontWeight: '400',
              lineHeight: '1.4',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
            }}>
              هل أنت متأكد من حذف هذه المحادثة؟
            </p>
            
            {/* Conversation title in a subtle card */}
            <div style={{
              background: 'rgba(220, 38, 38, 0.05)',
              border: '1px solid rgba(220, 38, 38, 0.1)',
              borderRadius: '12px',
              padding: '12px 16px',
              margin: '0 auto',
              maxWidth: '280px'
            }}>
              <p style={{
                margin: 0,
                color: '#DC2626',
                fontSize: '14px',
                fontWeight: '500',
                fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                "{conversationTitle}"
              </p>
            </div>
            
            <p style={{
              margin: '16px 0 0 0',
              color: '#9CA3AF',
              fontSize: '13px',
              fontWeight: '400',
              lineHeight: '1.3',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
            }}>
              لا يمكن التراجع عن هذا الإجراء
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            direction: 'rtl'
          }}>
            {/* Cancel button */}
            <button
                onClick={onCancel}
                style={{
                  padding: '12px 24px',
                  background: 'rgba(117, 117, 117, 0.08)',
                  color: '#757575',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '100px',
                  flex: '0 0 auto',
                  backdropFilter: 'blur(10px)'
                }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'rgba(117, 117, 117, 0.12)';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.color = '#424242';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'rgba(117, 117, 117, 0.08)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.color = '#757575';
              }}
            >
              إلغاء
            </button>
            
            {/* Delete button - Danger Red */}
            <button
                onClick={onConfirm}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '100px',
                  flex: '0 0 auto',
                  boxShadow: '0 8px 32px rgba(220, 38, 38, 0.25)'
                }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 12px 40px rgba(220, 38, 38, 0.35)';
                e.currentTarget.style.background = 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 8px 32px rgba(220, 38, 38, 0.25)';
                e.currentTarget.style.background = 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)';
              }}
            >
              حذف المحادثة
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default DeletePopup;