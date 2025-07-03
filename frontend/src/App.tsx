// Replace your entire frontend/src/App.tsx with this smooth implementation
import React, { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import { legalAPI, chatAPI } from './services/api';
// Simple navigation helper
const navigateTo = (path: string) => {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
};


interface RenamePopupProps {
  isOpen: boolean;
  currentTitle: string;
  onSave: (newTitle: string) => void;
  onCancel: () => void;
}

const RenamePopup: React.FC<RenamePopupProps> = ({ isOpen, currentTitle, onSave, onCancel }) => {
  const [newTitle, setNewTitle] = useState(currentTitle);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setNewTitle(currentTitle);
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 100);
    }
  }, [isOpen, currentTitle]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTitle.trim() && newTitle.trim() !== currentTitle) {
      onSave(newTitle.trim());
    } else {
      onCancel();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Premium Saudi backdrop */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 15, 15, 0.8)',
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
            borderRadius: '20px', // 🔧 Reduced to match rename dialog
            padding: '32px', // 🔧 Reduced to match rename dialog
            maxWidth: '400px', // 🔧 Reduced to match rename dialog
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
            marginBottom: '32px'
          }}>
            {/* Saudi Green Icon */}
            <div style={{
              width: '72px',
              height: '72px',
              background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
              borderRadius: '20px',
              margin: '0 auto 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 32px rgba(0, 108, 53, 0.25)',
              position: 'relative'
            }}>
              {/* Inner glow effect */}
              <div style={{
                position: 'absolute',
                inset: '2px',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%)',
                borderRadius: '18px'
              }} />
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ position: 'relative', zIndex: 1 }}>
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
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
              تعديل اسم المحادثة
            </h3>
            
            <p style={{
              margin: 0,
              color: '#757575',
              fontSize: '15px',
              fontWeight: '400',
              lineHeight: '1.4',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
            }}>
              اختر اسماً جديداً يصف محتوى هذه المحادثة
            </p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '24px' }}> {/* 🔧 Reduced spacing */}              <input
                ref={inputRef}
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="اسم المحادثة الجديد"
                 style={{
                    width: '100%',
                    padding: '14px 18px', // 🔧 Reduced padding
                    border: '2px solid #F5F5F5',
                    borderRadius: '12px', // 🔧 Reduced border radius
                    fontSize: '15px', // 🔧 Slightly smaller font
                    outline: 'none',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    direction: 'rtl',
                    textAlign: 'right',
                    background: 'rgba(255, 255, 255, 0.9)', // 🔧 More opaque
                    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                    boxSizing: 'border-box',
                    color: '#212121',
                    fontWeight: '400'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#006C35';
                  e.target.style.background = 'rgba(255, 255, 255, 1)';
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 25px rgba(0, 108, 53, 0.15)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#F5F5F5';
                  e.target.style.background = 'rgba(255, 255, 255, 0.8)';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
            
            <div style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'center', // 🔧 Changed to flex-start for RTL
              direction: 'rtl' // 🔧 Ensure RTL direction
            }}>
              {/* Cancel button */}
              <button
                type="button"
                onClick={onCancel}
                style={{
                  padding: '12px 24px', // 🔧 Reduced padding
                  background: 'rgba(117, 117, 117, 0.08)',
                  color: '#757575',
                  border: 'none',
                  borderRadius: '10px', // 🔧 Reduced border radius
                  cursor: 'pointer',
                  fontSize: '14px', // 🔧 Slightly smaller font
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '90px', // 🔧 Reduced from 100px
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
              
              {/* Save button - Saudi Green */}
              <button
                type="submit"
                disabled={!newTitle.trim() || newTitle.trim() === currentTitle}
                style={{
                  padding: '14px 28px',
                  background: (!newTitle.trim() || newTitle.trim() === currentTitle) 
                    ? 'rgba(189, 189, 189, 0.5)' 
                    : 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
                  color: (!newTitle.trim() || newTitle.trim() === currentTitle) ? '#BDBDBD' : 'white',
                  border: 'none',
                  borderRadius: '12px',
                  cursor: (!newTitle.trim() || newTitle.trim() === currentTitle) ? 'not-allowed' : 'pointer',
                  fontSize: '15px',
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '100px',
                  boxShadow: (!newTitle.trim() || newTitle.trim() === currentTitle) 
                    ? 'none' 
                    : '0 8px 32px rgba(0, 108, 53, 0.25)'
                }}
                onMouseOver={(e) => {
                  if (newTitle.trim() && newTitle.trim() !== currentTitle) {
                    e.currentTarget.style.transform = 'translateY(-1px)';
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.3)';
                    e.currentTarget.style.background = 'linear-gradient(135deg, #00A852 0%, #006C35 100%)';
                  }
                }}
                onMouseOut={(e) => {
                  if (newTitle.trim() && newTitle.trim() !== currentTitle) {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25)';
                    e.currentTarget.style.background = 'linear-gradient(135deg, #006C35 0%, #004A24 100%)';
                  }
                }}
              >
                حفظ
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

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
            borderRadius: '20px', // 🔧 Reduced border radius
            padding: '32px', // 🔧 Reduced padding from 40px to 32px
            maxWidth: '400px', // 🔧 Reduced from 440px to 400px
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
            justifyContent: 'center', // 🔧 Center the buttons
            direction: 'rtl'
          }}>
            {/* Cancel button */}
            <button
                onClick={onCancel}
                style={{
                  padding: '12px 24px', // 🔧 Reduced padding to match rename dialog
                  background: 'rgba(117, 117, 117, 0.08)',
                  color: '#757575',
                  border: 'none',
                  borderRadius: '10px', // 🔧 Reduced border radius to match
                  cursor: 'pointer',
                  fontSize: '14px', // 🔧 Smaller font to match
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '100px',
                  flex: '0 0 auto', // 🔧 Prevent flex growing
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
                  padding: '12px 24px', // 🔧 Reduced padding to match rename dialog
                  background: 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px', // 🔧 Reduced border radius to match
                  cursor: 'pointer',
                  fontSize: '14px', // 🔧 Smaller font to match
                  fontWeight: '500',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '100px',
                  flex: '0 0 auto', // 🔧 Prevent flex growing
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

// Premium Progress Indicator Component
interface PremiumProgressProps {
  current: number;
  max: number;
  label: string;
  type: 'messages' | 'exports' | 'exchanges' | 'citations';
}

const PremiumProgress: React.FC<PremiumProgressProps> = ({ current, max, label, type }) => {
  const percentage = (current / max) * 100;
  const isNearLimit = percentage > 70;
  const isAtLimit = current >= max;

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '12px',
      padding: '12px 16px',
      margin: '8px 0',
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      transform: isNearLimit ? 'scale(1.02)' : 'scale(1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <span style={{
          fontSize: '14px',
          fontWeight: '500',
          color: isAtLimit ? '#DC2626' : isNearLimit ? '#D97706' : '#6B7280',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
        }}>
          {label}
        </span>
        <span style={{
          fontSize: '13px',
          fontWeight: '600',
          color: isAtLimit ? '#DC2626' : isNearLimit ? '#D97706' : '#374151'
        }}>
          {current}/{max}
        </span>
      </div>
      
      {/* Elegant progress bar */}
      <div style={{
        width: '100%',
        height: '4px',
        background: 'rgba(0, 0, 0, 0.1)',
        borderRadius: '2px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${Math.min(percentage, 100)}%`,
          height: '100%',
          background: isAtLimit 
            ? 'linear-gradient(90deg, #DC2626 0%, #EF4444 100%)'
            : isNearLimit
            ? 'linear-gradient(90deg, #D97706 0%, #F59E0B 100%)'
            : 'linear-gradient(90deg, #006C35 0%, #10B981 100%)',
          borderRadius: '2px',
          transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isNearLimit ? '0 0 8px rgba(217, 119, 6, 0.4)' : 'none'
        }} />
      </div>
      
      {/* Clean upgrade hint */}
{isNearLimit && (
  <div style={{
    marginTop: '8px',
    fontSize: '11px',
    color: '#6B7280',
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '6px'
  }}>
    <div style={{
      width: '6px',
      height: '6px',
      borderRadius: '50%',
      background: isAtLimit ? '#DC2626' : '#D97706'
    }} />
    {isAtLimit ? 'حد مجاني مكتمل' : 'قريباً من الحد'}
  </div>
)}
    </div>
  );
};

// Premium Feature Tease Component
interface FeatureTeaseProps {
  title: string;
  description: string;
  icon: string;
  disabled: boolean;
  onUpgrade: () => void;
}

const FeatureTease: React.FC<FeatureTeaseProps> = ({ title, description, icon, disabled, onUpgrade }) => {
  if (!disabled) return null;

  return (
    <div 
      onClick={onUpgrade}
      style={{
        background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.05) 0%, rgba(0, 74, 36, 0.05) 100%)',
        border: '1px dashed rgba(0, 108, 53, 0.2)',
        borderRadius: '12px',
        padding: '16px',
        margin: '12px 0',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.1) 0%, rgba(0, 74, 36, 0.1) 100%)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 108, 53, 0.15)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.05) 0%, rgba(0, 74, 36, 0.05) 100%)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <span style={{ fontSize: '24px' }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <h4 style={{
            margin: '0 0 4px 0',
            fontSize: '16px',
            fontWeight: '600',
            color: '#006C35',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
          }}>
            {title}
          </h4>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#6B7280',
            lineHeight: '1.4'
          }}>
            {description}
          </p>
        </div>
        <div style={{
          background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
          color: 'white',
          borderRadius: '6px',
          padding: '4px 8px',
          fontSize: '11px',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          PRO
        </div>
      </div>
      
      {/* Subtle shimmer effect */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: '-100%',
        width: '100%',
        height: '100%',
        background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
        animation: 'shimmer 3s ease-in-out infinite'
      }} />
    </div>
  );
};

interface ActionsBarProps {
  content: string;
  isLastMessage: boolean;
}

interface ActionsBarProps {
  content: string;
  isLastMessage: boolean;
  messages: Message[];
  conversations: Conversation[];
  selectedConversation: string | null;
}

const ActionsBar: React.FC<ActionsBarProps> = ({ content, isLastMessage, messages, conversations, selectedConversation }) => {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleCopy = async () => {
    try {
      // Clean HTML tags from content
      const cleanContent = content.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
      await navigator.clipboard.writeText(cleanContent);
      setCopied(true);
      showToast('تم نسخ النص بنجاح', 'success');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      showToast('فشل في نسخ النص', 'error');
    }
  };

  const handleDownloadSingle = async () => {
    setDownloading(true);
    try {
      // Clean content for download
      const cleanContent = content.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
      const lastUserMessage = messages.length > 1 ? messages[messages.length - 2]?.content || 'سؤال المستخدم' : 'سؤال المستخدم';
      
      await legalAPI.exportDocx(lastUserMessage, cleanContent);
      showToast('تم تحميل الإجابة بنجاح', 'success');
    } catch (error) {
      showToast('فشل في تحميل الملف', 'error');
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadFull = async () => {
    setDownloading(true);
    try {
      // Generate full conversation content
      let fullContent = '';
      let conversationTitle = selectedConversation ? 
        conversations.find((c: any) => c.id === selectedConversation)?.title || 'محادثة قانونية' : 
        'محادثة قانونية';

      fullContent += `عنوان المحادثة: ${conversationTitle}\n\n`;
      fullContent += `تاريخ الإنشاء: ${new Date().toLocaleDateString('ar-SA')}\n\n`;
      fullContent += '='.repeat(50) + '\n\n';

      messages.forEach((message: any, index: any) => {
        const roleLabel = message.role === 'user' ? '👤 السؤال' : '🤖 الإجابة';
        const cleanContent = message.content.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
        
        fullContent += `${roleLabel} ${Math.floor(index / 2) + 1}:\n`;
        fullContent += `${cleanContent}\n\n`;
        
        if (message.role === 'assistant') {
          fullContent += '-'.repeat(30) + '\n\n';
        }
      });

      fullContent += '\n\nتم إنتاج هذا المستند بواسطة معين المساعد الذكي\n';
      fullContent += 'استشار ذكية مبنية على القانون السعودي';

      await legalAPI.exportDocx('المحادثة الكاملة', fullContent);
      showToast('تم تحميل المحادثة الكاملة بنجاح', 'success');
    } catch (error) {
      showToast('فشل في تحميل المحادثة الكاملة', 'error');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      gap: '8px',
      marginTop: '16px',
      padding: '12px 0',
      borderTop: '1px solid rgba(0, 0, 0, 0.05)',
      direction: 'rtl'
    }}>
      {/* Copy Button */}
      <button
        onClick={handleCopy}
        disabled={copied}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '8px 16px',
          background: copied 
            ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)'
            : 'linear-gradient(135deg, rgba(0, 108, 53, 0.1) 0%, rgba(0, 74, 36, 0.1) 100%)',
          color: copied ? '#10B981' : '#006C35',
          border: copied ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid rgba(0, 108, 53, 0.2)',
          borderRadius: '10px',
          cursor: copied ? 'default' : 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          backdropFilter: 'blur(10px)'
        }}
        title={copied ? 'تم النسخ!' : 'نسخ النص'}
        onMouseOver={(e) => {
          if (!copied) {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.15) 0%, rgba(0, 74, 36, 0.15) 100%)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }
        }}
        onMouseOut={(e) => {
          if (!copied) {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.1) 0%, rgba(0, 74, 36, 0.1) 100%)';
            e.currentTarget.style.transform = 'translateY(0)';
          }
        }}
      >
        {copied ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="20,6 9,17 4,12"/>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5,15H4a2,2 0 0,1 -2,-2V4a2,2 0 0,1 2,-2H13a2,2 0 0,1 2,2v1"/>
          </svg>
        )}
        <span>{copied ? 'تم النسخ' : 'نسخ'}</span>
      </button>

      {/* Download Single Button */}
      <button
        onClick={handleDownloadSingle}
        disabled={downloading}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '8px 16px',
          background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(184, 134, 11, 0.1) 100%)',
          color: '#D4AF37',
          border: '1px solid rgba(212, 175, 55, 0.2)',
          borderRadius: '10px',
          cursor: downloading ? 'default' : 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          backdropFilter: 'blur(10px)'
        }}
        title="تحميل هذه الإجابة"
        onMouseOver={(e) => {
          if (!downloading) {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(184, 134, 11, 0.15) 100%)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }
        }}
        onMouseOut={(e) => {
          if (!downloading) {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(184, 134, 11, 0.1) 100%)';
            e.currentTarget.style.transform = 'translateY(0)';
          }
        }}
      >
        {downloading ? (
          <div style={{
            width: '16px',
            height: '16px',
            border: '2px solid rgba(212, 175, 55, 0.3)',
            borderTop: '2px solid currentColor',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21,15v4a2,2 0 0,1 -2,2H5a2,2 0 0,1 -2,-2v-4"/>
            <polyline points="7,10 12,15 17,10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        )}
        <span>تحميل</span>
      </button>

      {/* Download Full Conversation Button (only show on last message) */}
      {isLastMessage && messages.length > 2 && (
        <button
          onClick={handleDownloadFull}
          disabled={downloading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%)',
            color: '#2563EB',
            border: '1px solid rgba(37, 99, 235, 0.2)',
            borderRadius: '10px',
            cursor: downloading ? 'default' : 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            backdropFilter: 'blur(10px)'
          }}
          title="تحميل المحادثة الكاملة"
          onMouseOver={(e) => {
            if (!downloading) {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(29, 78, 216, 0.15) 100%)';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }
          }}
          onMouseOut={(e) => {
            if (!downloading) {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%)';
              e.currentTarget.style.transform = 'translateY(0)';
            }
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14,2H6a2,2 0 0,0 -2,2v16a2,2 0 0,0 2,2h12a2,2 0 0,0 2,-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10,9 9,9 8,9"/>
          </svg>
          <span>تحميل الكل</span>
        </button>
      )}
    </div>
  );
};  

interface ParsedElement {
  type: 'heading' | 'paragraph' | 'text' | 'strong' | 'emphasis' | 'listItem';
  content: string;
  level?: number;
  children?: ParsedElement[];
}



class HTMLToReactParser {
  static parseHTML(htmlContent: string): ParsedElement[] {
    if (!htmlContent) return [];

    // Use browser's native DOMParser - most reliable
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<div>${htmlContent}</div>`, 'text/html');
    const container = doc.body.firstChild as HTMLElement;
    
    if (!container) return [];

    const elements: ParsedElement[] = [];
    
    // Process each child node
    for (const node of Array.from(container.childNodes)) {
      const parsed = this.parseNode(node);
      if (parsed) {
        elements.push(parsed);
      }
    }
    
    return elements;
  }

  private static parseNode(node: Node): ParsedElement | null {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent?.trim();
      if (text) {
        return { type: 'text', content: text };
      }
      return null;
    }
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node as HTMLElement;
      const tagName = element.tagName.toLowerCase();
      
      switch (tagName) {
        case 'h1':
        case 'h2':
        case 'h3':
        case 'h4':
        case 'h5':
        case 'h6':
          return {
            type: 'heading',
            level: parseInt(tagName.charAt(1)),
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'p':
          return {
            type: 'paragraph',
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'li':
          return {
            type: 'listItem',
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'strong':
        case 'b':
          return {
            type: 'strong',
            content: element.textContent || ''
          };
          
        case 'em':
        case 'i':
          return {
            type: 'emphasis',
            content: element.textContent || ''
          };
          
        case 'br':
          return { type: 'text', content: '\n' };
          
        default:
          // For other tags, treat as paragraph with children
          const children = this.parseChildNodes(element);
          if (children.length > 0) {
            return {
              type: 'paragraph',
              content: element.textContent || '',
              children
            };
          }
          return null;
      }
    }
    
    return null;
  }

  private static parseChildNodes(element: HTMLElement): ParsedElement[] {
    const children: ParsedElement[] = [];
    
    for (const node of Array.from(element.childNodes)) {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent?.trim();
        if (text) {
          children.push({ type: 'text', content: text });
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const childElement = node as HTMLElement;
        const tagName = childElement.tagName.toLowerCase();
        
        switch (tagName) {
          case 'strong':
          case 'b':
            children.push({
              type: 'strong',
              content: childElement.textContent || ''
            });
            break;
            
          case 'em':
          case 'i':
            children.push({
              type: 'emphasis',
              content: childElement.textContent || ''
            });
            break;
            
          case 'br':
            children.push({ type: 'text', content: ' ' });
            break;
            
          default:
            // For other inline elements, just get text content
            const text = childElement.textContent?.trim();
            if (text) {
              children.push({ type: 'text', content: text });
            }
        }
      }
    }
    
    return children;
  }
}
interface FormattedMessageProps {
  content: string;
  role: 'user' | 'assistant';
  sidebarOpen: boolean;
  isLastMessage?: boolean;
  messages?: Message[];
  conversations?: Conversation[];
  selectedConversation?: string | null;
}

const FormattedMessage: React.FC<FormattedMessageProps> = ({ 
  content, 
  role, 
  sidebarOpen, 
  isLastMessage = false,
  messages = [],
  conversations = [],
  selectedConversation = null
}) => {
  if (role === 'user') {
    return (
      <div style={{
        lineHeight: '1.6',
        textAlign: 'right',
        direction: 'rtl',
        fontSize: '25px'
      }}>
        {content}
      </div>
    );
  }

  // AI messages: use browser's native HTML rendering
  return (
    <div
      className="ai-response-container"
      style={{
        maxWidth: sidebarOpen ? '90%' : '90%',
        marginLeft: sidebarOpen ? '0' : 'auto',
        marginRight: sidebarOpen ? '0' : 'auto'
      }}
    >
      <div
        className="ai-response"
        dangerouslySetInnerHTML={{ __html: content }}
        style={{
          direction: 'rtl',
          textAlign: 'right',
          lineHeight: '1.7'
        }}
      />
      
      {/* Add ActionsBar for AI messages */}
      <ActionsBar
        content={content}
        isLastMessage={isLastMessage}
        messages={messages}
        conversations={conversations}
        selectedConversation={selectedConversation}
      />
    </div>
  );
};
interface MessageElement {
  type: 'heading' | 'paragraph' | 'list' | 'listItem' | 'strong' | 'emphasis' | 'text';
  level?: number; // for headings (1-6)
  content: string;
  children?: MessageElement[];
}

const parseMessageContent = (htmlContent: string): MessageElement[] => {
  // First, let's handle if it's plain text (no HTML)
  if (!htmlContent.includes('<') && !htmlContent.includes('>')) {
    // Split by double newlines for paragraphs
    return htmlContent.split('\n\n').map(paragraph => ({
  type: 'paragraph' as const,
  content: paragraph.trim(),
  children: parseInlineElements(paragraph.trim())
})).filter(p => p.content);
  }
  
  // For HTML content, we'll parse it properly
  const elements: MessageElement[] = [];
  const lines = htmlContent.split('\n');
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    
    // Parse headings
    if (trimmed.startsWith('<h') && trimmed.includes('>')) {
      const level = parseInt(trimmed.charAt(2));
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'heading', level, content });
    }
    // Parse paragraphs
    else if (trimmed.startsWith('<p>') || (!trimmed.startsWith('<'))) {
      const content = trimmed.replace(/<[^>]*>/g, '');
      if (content) {
        elements.push({ 
          type: 'paragraph', 
          content,
          children: parseInlineElements(content)
        });
      }
    }
    // Parse list items
    else if (trimmed.startsWith('<li>')) {
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'listItem', content });
    }
  }
  
  return elements;
};

const parseInlineElements = (text: string): MessageElement[] => {
  const elements: MessageElement[] = [];
  let currentIndex = 0;
  
  // Simple regex patterns for bold and italic
  const patterns = [
    { regex: /\*\*(.*?)\*\*/g, type: 'strong' as const },
    { regex: /\*(.*?)\*/g, type: 'emphasis' as const },
    { regex: /<strong>(.*?)<\/strong>/g, type: 'strong' as const },
    { regex: /<em>(.*?)<\/em>/g, type: 'emphasis' as const }
  ];
  
  let remaining = text;
  
  for (const pattern of patterns) {
    remaining = remaining.replace(pattern.regex, (match, content) => {
      elements.push({ type: pattern.type, content });
      return `__${pattern.type}_${elements.length - 1}__`;
    });
  }
  
  // Split by our placeholders and create text elements
  const parts = remaining.split(/(__\w+_\d+__)/);
  let elementIndex = 0;
  
  for (const part of parts) {
    if (part.startsWith('__') && part.endsWith('__')) {
      // This is a placeholder, skip it as we already have the element
      continue;
    } else if (part.trim()) {
      elements.splice(elementIndex, 0, { type: 'text', content: part });
      elementIndex++;
    }
    elementIndex++;
  }
  
  return elements.filter(el => el.content.trim());
};

const formatAIResponse = (content: string): string => {
  // If content has no HTML tags, apply enhanced markdown-like formatting
  if (!content.includes('<') && !content.includes('>')) {
    return content
      // Headers
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      // Bold text (keep **bold** as bold)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Bullet points with asterisks (make them italic and add bullet symbol)
      .replace(/^\* (.*$)/gm, '<li style="font-style: italic; list-style-type: disc; margin-right: 20px;">$1</li>')
      // Regular numbered lists
      .replace(/^(\d+)\. (.*$)/gm, '<li style="list-style-type: decimal; margin-right: 20px;">$1. $2</li>')
      // Regular dash lists
      .replace(/^- (.*$)/gm, '<li style="list-style-type: disc; margin-right: 20px;">$1</li>')
      // Single asterisk for emphasis (not at line start)
      .replace(/(?<!^)\*(.*?)\*/g, '<em>$1</em>')
      // Line breaks and paragraphs
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.*)$/gm, '<p>$1</p>')
      // Wrap consecutive list items in proper ul tags
      .replace(/(<li[^>]*>.*?<\/li>\s*)+/g, '<ul style="direction: rtl; text-align: right; padding-right: 20px; margin: 10px 0;">$&</ul>')
      // Clean up
      .replace(/<p><\/p>/g, '')
      .replace(/<p>(<[hul])/g, '$1')
      .replace(/(<\/[hul]>)<\/p>/g, '$1')
      .replace(/<p>(<li)/g, '$1')
      .replace(/(<\/li>)<\/p>/g, '$1');
  }
  return content;
};

const MessageRenderer: React.FC<{ elements: MessageElement[] }> = ({ elements }) => {
  const renderElement = (element: MessageElement, index: number): React.ReactNode => {
    const baseStyle = {
      margin: 0,
      padding: 0,
      textAlign: 'right' as const,
      direction: 'rtl' as const,
      fontFamily: "'Noto Sans Arabic', sans-serif"
    };
    
    switch (element.type) {
      case 'heading':
        const HeadingTag = `h${element.level || 2}` as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag
            key={index}
            style={{
              ...baseStyle,
              fontSize: element.level === 1 ? '2rem' : element.level === 2 ? '1.8rem' : '1.6rem',
              fontWeight: '700',
              color: element.level === 1 ? '#1e40af' : element.level === 2 ? '#059669' : '#dc2626',
              marginBottom: '0.5rem',
              marginTop: index === 0 ? '0' : '1rem'
            }}
          >
            {element.content}
          </HeadingTag>
        );
        
      case 'paragraph':
        return (
          <p
            key={index}
            style={{
              ...baseStyle,
              fontSize: '15px',
              lineHeight: '1.5',
              marginBottom: '0.8rem',
              marginTop: index === 0 ? '0' : '0.3rem'
            }}
          >
            {element.children ? renderInlineElements(element.children) : element.content}
          </p>
        );
        
      case 'listItem':
        return (
          <li
            key={index}
            style={{
              ...baseStyle,
              fontSize: '24px',
              lineHeight: '1.4',
              marginBottom: '0.3rem',
              listStylePosition: 'inside'
            }}
          >
            {element.content}
          </li>
        );
        
      default:
        return null;
    }
  };
  
  const renderInlineElements = (elements: MessageElement[]): React.ReactNode => {
    return elements.map((element, index) => {
      switch (element.type) {
        case 'strong':
          return (
            <strong key={index} style={{ color: '#1e40af', fontWeight: '700' }}>
              {element.content}
            </strong>
          );
        case 'emphasis':
          return (
            <em key={index} style={{ color: '#059669', fontStyle: 'italic' }}>
              {element.content}
            </em>
          );
        case 'text':
        default:
          return element.content;
      }
    });
  };
  
  // Group consecutive list items
  const groupedElements: React.ReactNode[] = [];
  let currentListItems: MessageElement[] = [];
  
  elements.forEach((element, index) => {
    if (element.type === 'listItem') {
      currentListItems.push(element);
    } else {
      if (currentListItems.length > 0) {
        groupedElements.push(
          <ul key={`list-${index}`} style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
            {currentListItems.map((item, i) => renderElement(item, i))}
          </ul>
        );
        currentListItems = [];
      }
      groupedElements.push(renderElement(element, index));
    }
  });
  
  // Handle remaining list items
  if (currentListItems.length > 0) {
    groupedElements.push(
      <ul key="list-final" style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
        {currentListItems.map((item, i) => renderElement(item, i))}
      </ul>
    );
  }
  
  return <div style={{ direction: 'rtl', textAlign: 'right' }}>{groupedElements}</div>;
};


interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  processing_time_ms?: number;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview: string | null;
  message_count: number;
}
const cleanHtmlContent = (htmlContent: string): string => {
  // Remove HTML tags and clean up the content
  return htmlContent
    .replace(/<[^>]*>/g, '') // Remove all HTML tags
    .replace(/&nbsp;/g, ' ') // Replace non-breaking spaces
    .replace(/&amp;/g, '&') // Replace HTML entities
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .trim(); // Remove leading/trailing whitespace
};
const showToast = (message: string, type: 'error' | 'success' = 'error') => {
  const toast = document.createElement('div');
  const bgColor = type === 'error' 
    ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
    : 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
  
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${bgColor};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    font-family: 'Noto Sans Arabic', sans-serif;
    font-weight: 500;
    max-width: 350px;
    animation: slideInToast 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOutToast 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    setTimeout(() => document.body.removeChild(toast), 400);
  }, 4000);
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'اليوم';
  if (diffDays === 2) return 'أمس';
  if (diffDays <= 7) return `منذ ${diffDays} أيام`;
  return date.toLocaleDateString('ar-SA');
};

const AuthScreen: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false);
  const handleNavigateToChat = () => {
    console.log('🏠 Navigating to chat page...');
    window.history.pushState({}, '', '/');
    window.dispatchEvent(new PopStateEvent('popstate'));
    // Force a re-render by dispatching a custom event
    window.dispatchEvent(new CustomEvent('auth-navigation'));};
  
  return (
    <>
      {/* Premium Background with animated gradient */}
      <div style={{
        minHeight: '100vh',
        background: `
          linear-gradient(135deg, 
            rgba(0, 108, 53, 0.9) 0%, 
            rgba(0, 74, 36, 0.8) 25%,
            rgba(16, 163, 127, 0.7) 50%,
            rgba(0, 108, 53, 0.9) 75%,
            rgba(0, 74, 36, 1) 100%
          ),
          radial-gradient(circle at 20% 80%, rgba(212, 175, 55, 0.3) 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 40% 40%, rgba(0, 168, 82, 0.2) 0%, transparent 50%)
        `,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        position: 'relative',
        overflow: 'hidden'
      }}>
        
        {/* Animated background elements */}
        <div style={{
          position: 'absolute',
          top: '10%',
          right: '10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 6s ease-in-out infinite'
        }} />
        
        <div style={{
          position: 'absolute',
          bottom: '10%',
          left: '10%',
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 8s ease-in-out infinite reverse'
        }} />

        {/* Ultra Premium Glass Container */}
        <div style={{
          background: `
            linear-gradient(135deg, 
              rgba(255, 255, 255, 0.25) 0%, 
              rgba(255, 255, 255, 0.18) 25%,
              rgba(255, 255, 255, 0.15) 50%,
              rgba(255, 255, 255, 0.12) 75%,
              rgba(255, 255, 255, 0.08) 100%
            )
          `,
          borderRadius: '32px',
          padding: '48px',
          maxWidth: '480px',
          width: '100%',
          boxShadow: `
            0 32px 64px rgba(0, 0, 0, 0.25),
            0 16px 32px rgba(0, 0, 0, 0.15),
            0 8px 16px rgba(0, 0, 0, 0.1),
            inset 0 2px 0 rgba(255, 255, 255, 0.3),
            inset 0 -2px 0 rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.15)
          `,
          backdropFilter: 'blur(40px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          animation: 'luxurySlideIn 1s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          
          {/* Inner glass reflection */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '50%',
            background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.15) 0%, transparent 100%)',
            borderRadius: '32px 32px 0 0',
            pointerEvents: 'none'
          }} />

          {/* Header Section */}
          <div style={{
            textAlign: 'center',
            marginBottom: '40px',
            position: 'relative',
            zIndex: 1
          }}>
            {/* Premium Logo */}
            <div style={{
              width: '80px',
              height: '80px',
              background: 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
              borderRadius: '24px',
              margin: '0 auto 24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `
                0 16px 32px rgba(0, 108, 53, 0.4),
                0 8px 16px rgba(0, 108, 53, 0.3),
                inset 0 2px 0 rgba(255, 255, 255, 0.2)
              `,
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Logo inner glow */}
              <div style={{
                position: 'absolute',
                inset: '2px',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%)',
                borderRadius: '22px'
              }} />
              
              {/* Saudi Emblem or Legal Icon */}
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ position: 'relative', zIndex: 1 }}>
                <path d="M14,2H6a2,2 0 0,0 -2,2v16a2,2 0 0,0 2,2h12a2,2 0 0,0 2,-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </div>

            <h1 style={{
              color: 'rgba(255, 255, 255, 0.95)',
              fontSize: '32px',
              fontWeight: '700',
              marginBottom: '8px',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif',
              letterSpacing: '-0.02em',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}>
              المساعد القانوني الذكي
            </h1>
            
            <p style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '16px',
              fontWeight: '400',
              lineHeight: '1.5',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
              margin: 0
            }}>
              استشارة قانونية متقدمة مبنية على الذكاء الاصطناعي
            </p>

            {/* Clean Premium Subtitle */}
<div style={{
  marginTop: '20px',
  padding: '16px 24px',
  background: `
    linear-gradient(135deg, 
      rgba(255, 255, 255, 0.1) 0%, 
      rgba(255, 255, 255, 0.05) 100%
    )
  `,
  borderRadius: '16px',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.1)'
}}>
  <p style={{
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '14px',
    fontWeight: '500',
    lineHeight: '1.4',
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
    margin: 0,
    textAlign: 'center',
    letterSpacing: '0.01em'
  }}>
    مدعوم بالقانون السعودي والأنظمة الحديثة
  </p>
</div>
          </div>

          {/* Form Content */}
          <div style={{ position: 'relative', zIndex: 1 }}>
        {showRegister ? (
          <RegisterForm 
            onSwitchToLogin={() => setShowRegister(false)}
            onSuccess={() => {
              console.log('📝 Register success, navigating to chat...');
              setTimeout(handleNavigateToChat, 300);
            }}
          />
        ) : (
          <LoginForm 
            onSwitchToRegister={() => setShowRegister(true)}
            onSuccess={() => {
              console.log('🔑 Login success, navigating to chat...');
              setTimeout(handleNavigateToChat, 300);
            }}
          />
        )}
      </div>

          {/* Bottom shine effect */}
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '2px',
            background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.5) 50%, transparent 100%)',
            animation: 'shimmerBottom 3s ease-in-out infinite'
          }} />
        </div>
      </div>

      {/* Premium CSS Animations */}
      <style>{`
        @keyframes luxurySlideIn {
          0% {
            opacity: 0;
            transform: translateY(40px) scale(0.96);
            filter: blur(10px);
          }
          100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0px);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px) scale(1);
            opacity: 0.7;
          }
          50% {
            transform: translateY(-20px) scale(1.05);
            opacity: 0.9;
          }
        }

        @keyframes shimmerBottom {
          0%, 100% {
            opacity: 0.3;
            transform: translateX(-100%);
          }
          50% {
            opacity: 0.8;
            transform: translateX(100%);
          }
        }
      `}</style>
    </>
  );
};

const ChatApp: React.FC = () => {
  const { user, logout, isGuest, guestLimits, incrementGuestMessage, incrementGuestExchange, incrementGuestExport, incrementGuestCitation, canSendMessage, canAskFollowup, canExport, canGetCitations, updateUserData, refreshUserData, questionsRemaining, isInCooldown, cooldownTimeRemaining, canAskNewQuestion } = useAuth();
  const [isMobile, setIsMobile] = useState(false); // 🔧 ADD THIS LINE
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  // ... rest of your state variables ...
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [exchangeCount, setExchangeCount] = useState(0);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
  const [upgradePromptType, setUpgradePromptType] = useState<'messages' | 'exchanges' | 'exports' | 'citations'>('messages');
  const [renamePopup, setRenamePopup] = useState<{
  isOpen: boolean;
  conversationId: string;
  currentTitle: string;
}>({
  isOpen: false,
  conversationId: '',
  currentTitle: ''
});
  const [deletePopup, setDeletePopup] = useState<{
  isOpen: boolean;
  conversationId: string;
  conversationTitle: string;
}>({
  isOpen: false,
  conversationId: '',
  conversationTitle: ''
});
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Detect mobile screen size
  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const scrollToBottom = () => {
  setTimeout(() => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: "smooth",
      block: "end",
      inline: "nearest"
    });
  }, 100);
};

useEffect(() => {
  if (messages.length > 0) {
    scrollToBottom();
  }
}, [messages.length]); // Only trigger when message count changes

  useEffect(() => {
  if (user) {  // Only load when user is authenticated
    console.log('🔄 User authenticated, loading conversations...');
    loadConversations();
  }
}, [user?.id]); // Only trigger when user ID changes, not on every user update

  const loadConversations = async () => {
    if (!user || loadingConversations) return; // Safety check + prevent multiple calls
    
    setLoadingConversations(true);
    try {
      console.log('🔄 Loading conversations for user:', user.email);
      const response = await chatAPI.getConversations();
      console.log('✅ Loaded conversations:', response.conversations?.length || 0);
      
      // Only update if conversations actually changed
      const newConversations = response.conversations || [];
      setConversations(prevConversations => {
        // Simple comparison to prevent unnecessary updates
        if (JSON.stringify(prevConversations) !== JSON.stringify(newConversations)) {
          return newConversations;
        }
        return prevConversations;
      });
      
      // 🔧 FIX: Update user data if provided in conversations response (but only once)
      if (response.current_user) {
        console.log('🔄 Updating user data from conversations response:', response.current_user);
        updateUserData({
          questions_used_this_month: response.current_user.questions_used_this_month,
          subscription_tier: response.current_user.subscription_tier
        });
      }
    } catch (error: any) {
      console.log('❌ Error loading conversations:', error);
      // Don't show auth-related errors
      if (error.response?.status !== 401) {
        showToast('فشل في تحميل المحادثات السابقة', 'error');
      }
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    try {
      const response = await chatAPI.getConversationMessages(conversationId);
      setMessages(response.messages || []);
      setSelectedConversation(conversationId);
      if (isMobile) setSidebarOpen(false);
    } catch (error) {
      showToast('فشل في تحميل المحادثة', 'error');
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
const containsCitations = (content: string): boolean => {
  const citationPatterns = [
    /المادة\s*\(\s*\d+\s*\)/g,
    /نظام\s+.+\s+رقم\s+م\/\d+/g,
    /المرسوم\s+الملكي\s+رقم/g,
    /اللائحة\s+التنفيذية/g
  ];
  
  return citationPatterns.some(pattern => pattern.test(content));
};

const stripCitations = (content: string): string => {
  let strippedContent = content
    .replace(/\(المادة\s*\(\s*\d+\s*\)[^)]*\)/g, '')
    .replace(/حسب\s+المادة\s*\(\s*\d+\s*\)[^.]*\./g, '')
    .replace(/وفقاً\s+لنظام\s+[^.]*\./g, '')
    .replace(/\(المرسوم\s+الملكي\s+رقم\s+[^)]*\)/g, '');
  
  // Add upgrade prompt
  strippedContent += '\n\n⚠️ للحصول على المراجع القانونية التفصيلية ومواد الأنظمة السعودية، يرجى الترقية للحساب المدفوع.';
  
  return strippedContent;
};

  const startNewConversation = () => {
    setMessages([]);
    setSelectedConversation(null);
    setInputMessage('');
    if (isMobile) setSidebarOpen(false);
  };
  

const handleRenameConversation = (conversationId: string, currentTitle: string) => {
  setRenamePopup({
    isOpen: true,
    conversationId,
    currentTitle
  });
};

const handleRenameSubmit = async (newTitle: string) => {
  try {
    await chatAPI.updateConversationTitle(renamePopup.conversationId, newTitle);
    
    // Update the conversation in the local state to maintain order
    setConversations(prev => prev.map(conv => 
      conv.id === renamePopup.conversationId 
        ? { ...conv, title: newTitle }
        : conv
    ));
    
    showToast('تم تغيير اسم المحادثة بنجاح', 'success');
    setRenamePopup({ isOpen: false, conversationId: '', currentTitle: '' });
  } catch (error) {
    showToast('فشل في تغيير اسم المحادثة', 'error');
  }
};

const handleRenameCancel = () => {
  setRenamePopup({ isOpen: false, conversationId: '', currentTitle: '' });
};

const handleDeleteConversation = (conversationId: string, title: string) => {
  setDeletePopup({
    isOpen: true,
    conversationId,
    conversationTitle: title
  });
};

const handleDeleteConfirm = async () => {
  try {
    await chatAPI.archiveConversation(deletePopup.conversationId);
    
    // Remove from local state immediately
    setConversations(prev => prev.filter(conv => conv.id !== deletePopup.conversationId));
    
    // Clear current conversation if it's the deleted one
    if (selectedConversation === deletePopup.conversationId) {
      setSelectedConversation(null);
      setMessages([]);
    }
    
    showToast('تم حذف المحادثة بنجاح', 'success');
    setDeletePopup({ isOpen: false, conversationId: '', conversationTitle: '' });
  } catch (error) {
    showToast('فشل في حذف المحادثة', 'error');
  }
};

const handleDeleteCancel = () => {
  setDeletePopup({ isOpen: false, conversationId: '', conversationTitle: '' });
};

  const handleSendMessage = async () => {
  if (!inputMessage.trim()) return;
  
  // 🔧 NEW: Check cooldown first
  if (!canAskNewQuestion()) {
    if (isInCooldown) {
      showToast(`يجب الانتظار ${cooldownTimeRemaining} دقيقة قبل طرح سؤال جديد`, 'error');
    } else {
      setUpgradePromptType('messages');
      setShowUpgradePrompt(true);
    }
    return;
  }
  
  // Check exchange limit for guests (after 3 back-and-forth exchanges)
  if (isGuest && messages.length > 0 && !canAskFollowup()) {
    setUpgradePromptType('exchanges');
    setShowUpgradePrompt(true);
    return;
  }
  
  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage,
    timestamp: new Date().toISOString()
  };
  
  setMessages(prev => [...prev, userMessage]);
  const currentMessage = inputMessage;
  setInputMessage('');
  setIsLoading(true);
  
  // Increment counters for guests
  if (isGuest) {
    incrementGuestMessage();
    if (messages.length > 0) {
      incrementGuestExchange();
      setExchangeCount(prev => prev + 1);
    }
  }
  
  try {
    // For guests, use the simple consultation API (no conversation persistence)
    if (isGuest) {
      const consultation = await legalAPI.askQuestion(currentMessage);
      
      // Process citation limitations for guests
      let aiContent = consultation.answer;
      if (isGuest && !canGetCitations()) {
        // Strip Saudi law citations after limit
        aiContent = stripCitations(aiContent);
      } else if (isGuest) {
        // Check if response contains citations and increment counter
        if (containsCitations(aiContent)) {
          incrementGuestCitation();
        }
      }
      
      const aiMessage: Message = {
        id: consultation.id,
        role: 'assistant',
        content: formatAIResponse(aiContent),
        timestamp: consultation.timestamp
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } else {
      // For authenticated users, use the full chat API with persistence
      try {
        const chatResponse = await chatAPI.sendMessage(currentMessage, selectedConversation || undefined);
        
        // 🔧 FIX: Update user data if provided in response
        if (chatResponse.updated_user) {
          console.log('🔄 Updating user data from chat response:', chatResponse.updated_user);
          updateUserData({
            questions_used_this_month: chatResponse.updated_user.questions_used_this_month,
            subscription_tier: chatResponse.updated_user.subscription_tier,
            is_active: chatResponse.updated_user.is_active,
            is_verified: chatResponse.updated_user.is_verified
          });
        } else {
          // 🔧 FIX: If no user data in response, refresh from backend
          console.log('🔄 No user data in response, refreshing from backend...');
          await refreshUserData();
        }
        
        const aiMessage: Message = {
          id: chatResponse.ai_message.id,
          role: 'assistant',
          content: formatAIResponse(chatResponse.ai_message.content),
          timestamp: chatResponse.ai_message.timestamp,
          processing_time_ms: chatResponse.ai_message.processing_time_ms
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setSelectedConversation(chatResponse.conversation_id);
        
        // Refresh conversations list
        // Only refresh conversations if this is a new conversation
        if (chatResponse.conversation_id && chatResponse.conversation_id !== selectedConversation) {
          setTimeout(() => loadConversations(), 1000);
        }
      } catch (chatError) {
        // Fallback to old API
        console.log('Chat API failed, using fallback:', chatError);
        
        // 🔧 FIX: Use the enhanced askQuestion method that returns user data
        try {
          const result = await legalAPI.askQuestionWithUserUpdate(currentMessage);
          
          // Update user data if provided
          if (result.updatedUser && !result.updatedUser.error) {
            console.log('🔄 Updating user data from fallback API:', result.updatedUser);
            updateUserData({
              questions_used_this_month: result.updatedUser.questions_used_this_month,
              subscription_tier: result.updatedUser.subscription_tier,
              is_active: result.updatedUser.is_active,
              is_verified: result.updatedUser.is_verified
            });
          }
          
          const aiMessage: Message = {
            id: result.consultation.id,
            role: 'assistant',
            content: result.consultation.answer,
            timestamp: result.consultation.timestamp
          };
          
          setMessages(prev => [...prev, aiMessage]);
        } catch (fallbackError) {
          // Ultimate fallback - just process the question without user updates
          const consultation = await legalAPI.askQuestion(currentMessage);
          
          const aiMessage: Message = {
            id: consultation.id,
            role: 'assistant',
            content: consultation.answer,
            timestamp: consultation.timestamp
          };
          
          setMessages(prev => [...prev, aiMessage]);
          
          // Try to refresh user data separately
          await refreshUserData();
        }
      }
    }
    
  } catch (error: any) {
    console.error('❌ Error sending message:', error);
    showToast(error.response?.data?.detail || 'حدث خطأ في معالجة السؤال', 'error');
  } finally {
    setIsLoading(false);
  }
};

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

 const suggestedQuestions = [
  'ما هي إجراءات تأسيس شركة تجارية؟',
  'حقوق الموظف عند إنهاء الخدمة',
  'إجراءات الطلاق في النظام السعودي',
  'حقوق المستأجر في عقد الإيجار'
];
  const LegalLoadingIndicator: React.FC = () => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  
  const loadingMessages = [
    { icon: "⚖️", title: "جاري تحليل القضية القانونية", subtitle: "فهم وتحليل السؤال المطروح..." },
    { icon: "📚", title: "البحث في الأنظمة السعودية", subtitle: "مراجعة القوانين واللوائح ذات الصلة..." },
    { icon: "🔍", title: "تحليل السوابق القضائية", subtitle: "البحث في الأحكام والقرارات السابقة..." },
    { icon: "📋", title: "مراجعة المواد القانونية", subtitle: "فحص النصوص النظامية المعمول بها..." },
    { icon: "⚡", title: "تجميع الاستشارة القانونية", subtitle: "إعداد الرد المفصل والشامل..." },
    { icon: "✨", title: "التحقق من دقة المعلومات", subtitle: "مراجعة نهائية للاستشارة المقدمة..." },
    { icon: "📄", title: "تنسيق الاستجابة النهائية", subtitle: "إعداد النص بالتنسيق المناسب..." }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 4000); // Change every 4 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  const currentMessage = loadingMessages[currentMessageIndex];
  
  return (
    <div 
      key={currentMessageIndex} // This forces re-render for animation
      style={{
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        borderRadius: '16px 16px 16px 4px',
        padding: '20px 24px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
        border: '1px solid #cbd5e0',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        minWidth: '350px',
        animation: 'fadeInScale 0.5s ease-out',
        transform: 'scale(1)',
        opacity: 1
      }}
    >
      <div style={{
        display: 'flex',
        gap: '4px'
      }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#10a37f',
          animation: 'pulse 1.8s infinite'
        }}></div>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#059669',
          animation: 'pulse 1.8s infinite 0.3s'
        }}></div>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#047857',
          animation: 'pulse 1.8s infinite 0.6s'
        }}></div>
      </div>
      <div style={{ direction: 'rtl', flex: 1 }}>
        <div style={{
          color: '#2d3748',
          fontSize: '20px',
          fontWeight: '600',
          marginBottom: '4px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '24px' }}>{currentMessage.icon}</span>
          {currentMessage.title}
        </div>
        <div style={{
          color: '#718096',
          fontSize: '16px'
        }}>{currentMessage.subtitle}</div>
      </div>
      
      {/* Progress indicator */}
      <div style={{
        width: '40px',
        height: '4px',
        background: '#e2e8f0',
        borderRadius: '2px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <div style={{
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, #10a37f, #059669)',
          borderRadius: '2px',
          animation: 'progressBar 4s linear infinite'
        }}></div>
      </div>
    </div>
  );
};
  return (
    <>
      <style>{`

      @keyframes subtlePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.02);
    opacity: 0.95;
  }
}

@keyframes luxuryPulse {
  0%, 100% {
    border-color: rgba(0, 108, 53, 0.1);
    box-shadow: 0 8px 32px rgba(0, 108, 53, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    border-color: rgba(0, 108, 53, 0.3);
    box-shadow: 0 12px 40px rgba(0, 108, 53, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
}
      @keyframes inputPulse {
  0%, 100% {
    border-color: #e5e7eb;
    box-shadow: none;
  }
  50% {
    border-color: #10a37f;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
  }
}
        @keyframes slideInToast {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slideOutToast {
          from {
            opacity: 1;
            transform: translateX(0);
          }
          to {
            opacity: 0;
            transform: translateX(100%);
          }
        }
        
        @keyframes fadeInScale {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .message-enter {
          animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .loading-dots {
          animation: pulse 1.5s infinite;
        }
        
        .suggested-card {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          transform: translateY(0);
        }
        
        .suggested-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }
      `}</style>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : sidebarOpen ? '320px 1fr' : '1fr',
        gridTemplateAreas: isMobile 
          ? '"main"'
          : sidebarOpen 
            ? '"sidebar main"'
            : '"main"',
        height: '100vh',
        fontFamily: "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        background: '#f7f7f8',
        direction: 'rtl',
        contain: 'layout style paint',
        overflow: 'hidden'
      }}>
        
        {/* Mobile Backdrop */}
        {isMobile && sidebarOpen && (
          <div 
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 40,
              opacity: 1,
              transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              backdropFilter: 'blur(4px)',
              willChange: 'opacity'
            }}
            onClick={toggleSidebar}
          />
        )}

        {/* Sidebar */}
        {/* Sidebar Toggle Button */}
{!sidebarOpen && (
  <button
    onClick={() => setSidebarOpen(true)}
    style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 100,
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '12px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.2s ease',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      backdropFilter: 'blur(10px)'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)';
      e.currentTarget.style.transform = 'scale(1.05)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'rgba(0, 0, 0, 0.8)';
      e.currentTarget.style.transform = 'scale(1)';
    }}
  >
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="3" y1="6" x2="21" y2="6"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
      <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  </button>
)}

{/* Sidebar */}
<div 
  style={{
    gridArea: 'sidebar',
    position: isMobile ? 'fixed' : 'relative',
    inset: isMobile ? '0 auto 0 0' : 'auto',
    width: isMobile ? '320px' : '100%',
    height: '100vh',
    background: '#171717',
    display: sidebarOpen ? 'flex' : 'none',
    flexDirection: 'column',
    borderLeft: '1px solid #363739',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: isMobile ? 50 : 'auto',
    boxShadow: isMobile ? '0 10px 25px rgba(0, 0, 0, 0.15)' : 'none'
  }}
>
          {/* Sidebar Header - Clean & Spaced */}
<div style={{
  padding: '20px',
  borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  minHeight: '80px'
}}>
  <h2 style={{
    color: 'rgba(255, 255, 255, 0.95)',
    fontSize: '20px',
    fontWeight: '600',
    margin: 0,
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
    letterSpacing: '-0.01em'
  }}>
    المحادثات
  </h2>
  
  {/* Only show close button, properly spaced */}
  <button
    onClick={() => setSidebarOpen(false)}
    style={{
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      color: 'rgba(142, 142, 160, 0.8)',
      cursor: 'pointer',
      padding: '8px',
      borderRadius: '8px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      width: '36px',
      height: '36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backdropFilter: 'blur(10px)'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)';
      e.currentTarget.style.color = '#EF4444';
      e.currentTarget.style.borderColor = 'rgba(220, 38, 38, 0.2)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
      e.currentTarget.style.color = 'rgba(142, 142, 160, 0.8)';
      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }}
  >
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  </button>
</div>

          {/* New Chat Button */}
          <div style={{ padding: '16px' }}>
            <button
              onClick={startNewConversation}
              style={{
                width: '100%',
                background: 'transparent',
                border: '1px solid #565869',
                color: 'white',
                borderRadius: '8px',
                padding: '12px 16px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: 'translateY(0)',
                minHeight: '44px'
              }}
              onMouseOver={(e) => {
                (e.target as HTMLElement).style.background = '#2d2d30';
                (e.target as HTMLElement).style.transform = 'translateY(-1px)';
                (e.target as HTMLElement).style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
              }}
              onMouseOut={(e) => {
                (e.target as HTMLElement).style.background = 'transparent';
                (e.target as HTMLElement).style.transform = 'translateY(0)';
                (e.target as HTMLElement).style.boxShadow = 'none';
              }}
            >
              <span style={{ fontSize: '16px' }}>+</span>
              محادثة جديدة
            </button>
          </div>

          {/* Conversations List */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0 16px'
          }}>
            {loadingConversations ? (
              <div style={{ 
                color: '#8e8ea0', 
                textAlign: 'center', 
                padding: '20px',
                fontSize: '16px'
              }}>
                جاري تحميل المحادثات...
              </div>
            ) : conversations.length === 0 ? (
              <div style={{ 
                color: '#8e8ea0', 
                textAlign: 'center', 
                padding: '20px',
                fontSize: '16px'
              }}>
                لا توجد محادثات سابقة
              </div>
            ) : (
              conversations.map((conv, index) => (
  <div
    key={conv.id}
    style={{
      padding: '12px 16px',
      margin: '4px 0',
      borderRadius: '8px',
      background: selectedConversation === conv.id ? '#2d2d30' : 'transparent',
      color: 'white',
      fontSize: '16px',
      lineHeight: '1.4',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      border: selectedConversation === conv.id ? '1px solid #4f4f4f' : '1px solid transparent',
      minHeight: '44px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      position: 'relative',
    }}
    onMouseEnter={(e) => {
      if (selectedConversation !== conv.id) {
        e.currentTarget.style.background = '#2d2d30';
      }
      // Show action buttons on hover
      const actionsDiv = e.currentTarget.querySelector('.conversation-actions') as HTMLElement;
      if (actionsDiv) actionsDiv.style.opacity = '1';
    }}
    onMouseLeave={(e) => {
      if (selectedConversation !== conv.id) {
        e.currentTarget.style.background = 'transparent';
      }
      // Hide action buttons
      const actionsDiv = e.currentTarget.querySelector('.conversation-actions') as HTMLElement;
      if (actionsDiv) actionsDiv.style.opacity = '0';
    }}
  >
    {/* Main content - clickable to load conversation */}
    <div
      onClick={() => loadConversationMessages(conv.id)}
      style={{ cursor: 'pointer', flex: 1 }}
    >
      <div style={{
        fontWeight: '500',
        marginBottom: '4px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }}>
        {conv.title}
      </div>
      <div style={{
        fontSize: '16px',
        color: '#8e8ea0',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }}>
        {conv.last_message_preview || `${conv.message_count} رسالة`}
      </div>
    </div>

    {/* Premium action buttons - show on hover */}
<div 
  className="conversation-actions"
  style={{
    position: 'absolute',
    top: '6px',
    left: '6px',
    display: 'flex',
    gap: '6px',
    opacity: '0',
    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
  }}
>
  {/* Premium Rename button */}
  <button
    onClick={(e) => {
      e.stopPropagation();
      handleRenameConversation(conv.id, conv.title);
    }}
    style={{
      background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.9) 0%, rgba(0, 74, 36, 0.9) 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '6px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '28px',
      height: '28px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 2px 8px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}
    title="تعديل الاسم"
    onMouseOver={(e) => {
      e.currentTarget.style.transform = 'translateY(-1px) scale(1.05)';
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 168, 82, 0.9) 0%, rgba(0, 108, 53, 0.9) 100%)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.9) 0%, rgba(0, 74, 36, 0.9) 100%)';
    }}
  >
    {/* Premium edit icon */}
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  </button>

  {/* Premium Delete button */}
  <button
    onClick={(e) => {
      e.stopPropagation();
      handleDeleteConversation(conv.id, conv.title);
    }}
    style={{
      background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '6px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '28px',
      height: '28px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 2px 8px rgba(220, 38, 38, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}
    title="حذف المحادثة"
    onMouseOver={(e) => {
      e.currentTarget.style.transform = 'translateY(-1px) scale(1.05)';
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(220, 38, 38, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.9) 100%)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(220, 38, 38, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%)';
    }}
  >
    {/* Premium delete icon */}
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
      <polyline points="3,6 5,6 21,6"/>
      <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
      <line x1="10" y1="11" x2="10" y2="17"/>
      <line x1="14" y1="11" x2="14" y2="17"/>
    </svg>
  </button>
</div>
  </div>
)))}
          </div>

          {/* User Info - Premium Clean Design */}
<div style={{
  padding: '24px 20px',
  borderTop: '1px solid rgba(255, 255, 255, 0.08)',
  background: 'linear-gradient(180deg, rgba(23, 23, 23, 0.8) 0%, rgba(23, 23, 23, 1) 100%)'
}}>
  {isGuest ? (
    // Ultra Premium Guest Section
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      gap: '20px'
    }}>
      {/* Premium User Avatar & Info */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: `
            linear-gradient(135deg, 
              rgba(107, 114, 128, 0.9) 0%, 
              rgba(75, 85, 99, 0.9) 100%
            )
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `,
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ opacity: 0.9 }}>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            color: 'rgba(255, 255, 255, 0.95)', 
            fontWeight: '600', 
            fontSize: '17px',
            marginBottom: '4px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
            letterSpacing: '-0.01em'
          }}>
            مستخدم ضيف
          </div>
          <div style={{ 
            color: 'rgba(142, 142, 160, 0.8)', 
            fontSize: '13px',
            fontWeight: '500',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
          }}>
            تجربة محدودة • ترقى للمزيد
          </div>
        </div>
      </div>
      
      {/* Premium Progress Indicators with Glass Effect */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        padding: '16px',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)'
      }}>
        <PremiumProgress
          current={guestLimits.messagesUsed}
          max={guestLimits.maxMessages}
          label="الرسائل المجانية"
          type="messages"
        />
        
        <PremiumProgress
          current={guestLimits.exportsUsed}
          max={guestLimits.maxExports}
          label="التحميلات المجانية"
          type="exports"
        />
      </div>
      
      {/* Ultra Premium Upgrade Button */}
      <button
        onClick={() => {
          console.log('🚀 Navigating to auth page...');
          window.history.pushState({}, '', '/auth');
          window.dispatchEvent(new PopStateEvent('popstate'));
        }}
        style={{
          width: '100%',
          background: `
            linear-gradient(135deg, 
              #006C35 0%, 
              #004A24 50%,
              #002D16 100%
            )
          `,
          color: 'white',
          border: 'none',
          borderRadius: '16px',
          padding: '16px 24px',
          cursor: 'pointer',
          fontSize: '15px',
          fontWeight: '600',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: `
            0 8px 32px rgba(0, 108, 53, 0.4),
            0 4px 16px rgba(0, 108, 53, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          letterSpacing: '-0.01em',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = `
            linear-gradient(135deg, 
              #00A852 0%, 
              #006C35 50%,
              #004A24 100%
            )
          `;
          e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
          e.currentTarget.style.boxShadow = `
            0 12px 48px rgba(0, 168, 82, 0.5),
            0 8px 24px rgba(0, 108, 53, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
          `;
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = `
            linear-gradient(135deg, 
              #006C35 0%, 
              #004A24 50%,
              #002D16 100%
            )
          `;
          e.currentTarget.style.transform = 'translateY(0) scale(1)';
          e.currentTarget.style.boxShadow = `
            0 8px 32px rgba(0, 108, 53, 0.4),
            0 4px 16px rgba(0, 108, 53, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `;
        }}
      >
        {/* Premium shine effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
          animation: 'shimmer 3s ease-in-out infinite'
        }} />
        
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ position: 'relative', zIndex: 1 }}>
          <path d="M12 2L15.09 8.26L22 9L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9L8.91 8.26L12 2Z"/>
        </svg>
        
        <span style={{ position: 'relative', zIndex: 1 }}>ترقية للحساب المميز</span>
      </button>
    </div>
  ) : (
    // Ultra Premium Authenticated User Section
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      gap: '20px'
    }}>
      {/* Premium User Avatar & Info */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: `
            linear-gradient(135deg, 
              #10a37f 0%, 
              #047857 100%
            )
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `
            0 8px 32px rgba(16, 163, 127, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
          `,
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ opacity: 0.9 }}>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            color: 'rgba(255, 255, 255, 0.95)', 
            fontWeight: '600', 
            fontSize: '17px',
            marginBottom: '4px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
            letterSpacing: '-0.01em'
          }}>
            {user?.full_name}
          </div>
          <div style={{ 
            color: '#10a37f', 
            fontSize: '13px', 
            fontWeight: '600',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
            letterSpacing: '0.5px',
            textTransform: 'uppercase'
          }}>
            حساب مميز
          </div>
        </div>
      </div>

      {/* Premium Usage Stats */}
      <div style={{ 
        padding: '16px 20px',
        background: `
          linear-gradient(135deg, 
            rgba(16, 163, 127, 0.1) 0%, 
            rgba(5, 150, 105, 0.05) 100%
          )
        `,
        borderRadius: '16px',
        border: '1px solid rgba(16, 163, 127, 0.2)',
        backdropFilter: 'blur(20px)'
      }}>
        <div style={{ 
          fontSize: '13px', 
          color: 'rgba(142, 142, 160, 0.8)', 
          marginBottom: '8px',
          fontWeight: '500',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          الاستخدام الشهري
        </div>
        <div style={{ 
              color: '#10a37f', 
              fontWeight: '700',
              fontSize: '20px',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
              letterSpacing: '-0.02em'
            }}>
              {questionsRemaining} / 20
            </div>
        <div style={{
          fontSize: '12px',
          color: 'rgba(16, 163, 127, 0.7)',
          marginTop: '4px',
          fontWeight: '500'
        }}>
          أسئلة متبقية
        </div>
      </div>

      {/* Premium Logout Button */}
      <button
        onClick={logout}
        style={{
          width: '100%',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'rgba(142, 142, 160, 0.9)',
          borderRadius: '12px',
          padding: '14px 20px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          backdropFilter: 'blur(10px)'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)';
          e.currentTarget.style.color = '#EF4444';
          e.currentTarget.style.borderColor = 'rgba(220, 38, 38, 0.2)';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
          e.currentTarget.style.color = 'rgba(142, 142, 160, 0.9)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16,17 21,12 16,7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        تسجيل الخروج
      </button>
    </div>
  )}
</div> 
        </div>

        {/* Main Chat Area */}
        <div style={{
          gridArea: 'main',
          display: 'flex',
          flexDirection: 'column',
          background: 'white',
          height: '100vh',
          position: 'relative'
        }}>
          <div style={{
  background: isGuest 
    ? guestLimits.messagesUsed >= guestLimits.maxMessages 
      ? 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)' 
      : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
    : selectedConversation 
      ? 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)' 
      : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
  color: isGuest 
    ? guestLimits.messagesUsed >= guestLimits.maxMessages 
      ? '#dc2626' 
      : '#059669'
    : selectedConversation ? '#2563eb' : '#059669',
  padding: '8px 16px',
  borderRadius: '12px',
  fontSize: '13px',
  fontWeight: '600',
  transition: 'all 0.2s ease',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  border: '1px solid',
  borderColor: isGuest 
    ? guestLimits.messagesUsed >= guestLimits.maxMessages 
      ? 'rgba(220, 38, 38, 0.2)' 
      : 'rgba(5, 150, 105, 0.2)'
    : selectedConversation ? 'rgba(37, 99, 235, 0.2)' : 'rgba(5, 150, 105, 0.2)'
}}>
  <div style={{
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'currentColor'
  }} />
  {isGuest ? (
    guestLimits.messagesUsed >= guestLimits.maxMessages ? (
      'تم استنفاد الرسائل المجانية'
    ) : (
      `${guestLimits.messagesUsed}/${guestLimits.maxMessages} رسائل مجانية`
    )
  ) : (
    selectedConversation ? 'محادثة نشطة' : 'محادثة جديدة'
  )}
</div>

          {/* Messages Area */}
          <div 
  className="chat-main-area"
  style={{
    flex: 1,
    overflowY: 'auto',
    padding: '24px 0',
    scrollBehavior: 'smooth'
  }}
>
            {messages.length === 0 ? (
              // Welcome Screen
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                padding: '0 24px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '64px',
                  marginBottom: '24px'
                }}></div>
                <h2 style={{
                  fontSize: 'clamp(50px, 4vw, 26px)',
                  fontWeight: '600',
                  color: '#2d333a',
                  marginBottom: '16px'
                }}>
                  مرحبا بك في معين
                </h2>
                <p style={{
                  fontSize: 'clamp(24px, 2vw, 16px)',
                  color: '#6b7280',
                  marginBottom: '32px',
                  maxWidth: '600px',
                  lineHeight: '1.6'
                }}>
                  احصل على استشارات قانونية دقيقة ومفصلة مبنية على القانون السعودي باستخدام تقنيات الذكاء الاصطناعي المتقدمة
                </p>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '16px',
                  width: '100%',
                  maxWidth: '800px'
                }}>
                  {suggestedQuestions.map((question, index) => (
                    <div
                      key={index}
                      className="suggested-card"
                      style={{
                        background: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '20px',
                        cursor: 'pointer',
                        textAlign: 'right',
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                        animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s both`
                      }}
                      onClick={() => handleSuggestedQuestion(question)}
                      onMouseOver={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#10a37f';
                        (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(16, 163, 127, 0.15)';
                      }}
                      onMouseOut={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#e5e7eb';
                        (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      <div style={{
                        fontSize: '22px',
                        color: '#374151',
                        fontWeight: '500',
                        lineHeight: '1.5'
                      }}>
                        {question}
                      </div>
                      <div style={{
  fontSize: '14px',
  color: '#9ca3af',
  marginTop: '8px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  gap: '6px',
  fontWeight: '500'
}}>
  اضغط للسؤال
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/>
  </svg>
</div><div style={{
                        fontSize: '22px',
                        color: '#374151',
                        fontWeight: '500',
                        lineHeight: '1.5'
                      }}>
                        
                      </div>
                    </div>
                    
                  ))}

                  
                </div>
              </div>
            ) : (
              // Messages
              <div 
  className="chat-messages-container"
  style={{
    maxWidth: sidebarOpen ? '1200%' : '1400%',
    padding: sidebarOpen ? '0 3rem 0 0' : '0 2rem 0 11rem'
  }}
>
                {messages.map((message, index) => (
                 <div
  key={message.id}
  className="message-enter"
  style={{
    display: 'flex',
    flexDirection: 'row',
    justifyContent: message.role === 'user' ? 'flex-start' : 'center',
    marginBottom: '24px',
    animationDelay: `${index * 0.1}s`
  }}
>

  <div
  className={message.role === 'user' ? 'user-message-enhanced' : ''}
  style={{
    maxWidth: message.role === 'user' 
      ? (sidebarOpen ? '75%' : '65%') 
      : (sidebarOpen ? '85%' : '75%'),
    background: message.role === 'user' 
      ? `linear-gradient(135deg, 
          rgba(0, 108, 53, 0.95) 0%, 
          rgba(0, 74, 36, 0.9) 50%,
          rgba(0, 108, 53, 0.85) 100%
        )` 
      : 'transparent',
    color: message.role === 'user' ? 'white' : '#2d333a',
    borderRadius: message.role === 'user' ? '20px 20px 4px 16px' : '0',
    padding: message.role === 'user' ? '18px 22px' : '0',
    boxShadow: message.role === 'user' 
      ? `0 8px 32px rgba(0, 108, 53, 0.25),
         0 4px 16px rgba(0, 108, 53, 0.15),
         inset 0 1px 0 rgba(255, 255, 255, 0.1),
         0 0 0 1px rgba(255, 255, 255, 0.05)` 
      : 'none',
    border: message.role === 'user' ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
    backdropFilter: message.role === 'user' ? 'blur(20px)' : 'none',
    fontSize: message.role === 'user' ? '25px' : '25px',
    lineHeight: '1.5',
    textAlign: 'right',
    marginRight: message.role === 'user' 
      ? (sidebarOpen ? '5%' : '20%') 
      : (sidebarOpen ? '0%' : '12%'),
    marginLeft: message.role === 'user' ? '0%' : '0%',
    wordBreak: 'break-word',
    overflowWrap: 'break-word',
    whiteSpace: 'normal',
    hyphens: 'auto',
    position: 'relative',
    overflow: 'hidden'
  }}
>
                      <FormattedMessage
  content={message.content}
  role={message.role}
  sidebarOpen={sidebarOpen}
  isLastMessage={index === messages.length - 1}
  messages={messages}
  conversations={conversations}
  selectedConversation={selectedConversation}
/>
                      <div style={{
                        fontSize: '18px',
                        opacity: 0.7,
                        marginTop: '8px',
                        textAlign: message.role === 'user' ? 'right' : 'left'
                      }}>
                        {new Date(message.timestamp).toLocaleTimeString('ar-SA', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Dynamic Legal Analysis Loading indicator */}
{isLoading && (
  <div style={{
    display: 'flex',
    justifyContent: 'flex-start',
    marginBottom: '16px',
    marginTop: '50px',  // ← Add this to push it down
  }}>
    <LegalLoadingIndicator />
  </div>
)}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
<div style={{
  padding: '32px 24px',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)',
  borderTop: '1px solid rgba(0, 108, 53, 0.1)',
  position: 'relative',
  display: 'flex',
  justifyContent: 'center',
  backdropFilter: 'blur(20px)',
  boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 -4px 32px rgba(0, 108, 53, 0.05)'
}}>
  <div style={{
    position: 'relative',
    maxWidth: sidebarOpen ? '800px' : '1000px',
    width: '100%'
  }}>
    
    <div 
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        gap: '16px',
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)',
        borderRadius: '24px',
        padding: '20px 24px',
        border: '2px solid rgba(0, 108, 53, 0.1)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: '80px',
        backdropFilter: 'blur(20px)',
        boxShadow: `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `,
        animation: inputMessage.length === 0 ? 'luxuryPulse 4s ease-in-out infinite' : 'none'
      }}
      onFocus={() => {
        // Stop animation on focus
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.borderColor = 'rgba(0, 108, 53, 0.2)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = `
          0 12px 40px rgba(0, 108, 53, 0.12),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.borderColor = 'rgba(0, 108, 53, 0.1)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `;
      }}
    >
                 <textarea
        ref={inputRef}
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="اكتب سؤالك القانوني هنا..."
        disabled={isLoading}
        style={{
          flex: 1,
          border: 'none',
          background: 'transparent',
          resize: 'none',
          outline: 'none',
          fontSize: '20px',
          lineHeight: '1.5',
          color: '#1f2937',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          minHeight: '48px',
          maxHeight: '150px',
          overflow: 'auto',
          padding: '0',
          fontWeight: '400',
          letterSpacing: '-0.01em'
        }}
        rows={1}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = 'auto';
          target.style.height = Math.min(target.scrollHeight, 120) + 'px';
        }}
        onFocus={(e) => {
          const container = e.target.closest('div[style*="borderRadius"]') as HTMLElement;
          if (container) {
            container.style.borderColor = '#006C35';
            container.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.8) 100%)';
          }
        }}
        onBlur={(e) => {
          const container = e.target.closest('div[style*="borderRadius"]') as HTMLElement;
          if (container) {
            container.style.borderColor = 'rgba(0, 108, 53, 0.1)';
            container.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)';
          }
        }}
      />
                
                <button
        onClick={handleSendMessage}
        disabled={!inputMessage.trim() || isLoading}
        style={{
          background: (!inputMessage.trim() || isLoading) 
            ? 'rgba(189, 189, 189, 0.3)' 
            : 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
          color: (!inputMessage.trim() || isLoading) ? '#9ca3af' : 'white',
          border: 'none',
          borderRadius: '16px',
          width: '56px',
          height: '56px',
          cursor: (!inputMessage.trim() || isLoading) ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          flexShrink: 0,
          boxShadow: (!inputMessage.trim() || isLoading) 
            ? 'none' 
            : '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          if (!(!inputMessage.trim() || isLoading)) {
            e.currentTarget.style.background = 'linear-gradient(135deg, #00A852 0%, #006C35 100%)';
            e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
          }
        }}
        onMouseOut={(e) => {
          if (!(!inputMessage.trim() || isLoading)) {
            e.currentTarget.style.background = 'linear-gradient(135deg, #006C35 0%, #004A24 100%)';
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
          }
        }}
      >
                  {isLoading ? (
          <div style={{
            width: '24px',
            height: '24px',
            border: '3px solid transparent',
            borderTop: '3px solid currentColor',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            opacity: 0.8
          }} />
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
            <path d="m22 2-7 20-4-9-9-4z"/>
            <path d="M22 2 11 13"/>
          </svg>
        )}
      </button>
    </div>
              
              {/* Character count and tips */}
              <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: '16px',
      fontSize: '16px',
      color: 'rgba(0, 108, 53, 0.7)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
      fontWeight: '400'
    }}>
                <div style={{ opacity: 0.8 }}>
        اضغط Enter للإرسال، Shift+Enter للسطر الجديد
      </div>
<div style={{ 
        background: 'rgba(0, 108, 53, 0.1)',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500'
      }}>
        الأسئلة المتبقية: {questionsRemaining}/20
      </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <RenamePopup
        isOpen={renamePopup.isOpen}
        currentTitle={renamePopup.currentTitle}
        onSave={handleRenameSubmit}
        onCancel={handleRenameCancel}
      />
      <DeletePopup
  isOpen={deletePopup.isOpen}
  conversationTitle={deletePopup.conversationTitle}
  onConfirm={handleDeleteConfirm}
  onCancel={handleDeleteCancel}
/>
      {/* Additional CSS for animations */}
     
    </>
  );
};

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
  console.log('🎯 AppContent render - Route:', currentRoute, 'User:', user?.email || 'guest', 'Loading:', loading);

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
