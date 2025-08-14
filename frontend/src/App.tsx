// Replace your entire frontend/src/App.tsx with this smooth implementation
import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import { legalAPI, chatAPI } from './services/api';
import DOMPurify from 'dompurify';

// Simple dark mode hook
const useTheme = () => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('dark-mode');
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark-mode', isDark);
    localStorage.setItem('dark-mode', JSON.stringify(isDark));
  }, [isDark]);

  return { isDark, toggleTheme: () => setIsDark(!isDark) };
};



// =====================================================================
// SENIOR-LEVEL TYPESCRIPT INTERFACES FOR URL ROUTING
// =====================================================================

/**
 * Route parameters for conversation URLs
 * @interface ConversationRouteParams
 */
interface ConversationRouteParams extends Record<string, string | undefined> {
  conversationId?: string;
}

/**
 * Props for conversation-aware components
 * @interface ConversationRouteProps  
 */
interface ConversationRouteProps {
  conversationId?: string;
  onConversationChange?: (conversationId: string | null) => void;
}

/**
 * Return type for the conversation routing hook
 * @interface UseConversationRoutingReturn
 */
interface UseConversationRoutingReturn {
  conversationId: string | null;
  navigateToConversation: (conversationId: string) => void;
  navigateToHome: () => void;
  isValidConversationId: (conversationId: string) => boolean;
}

// =====================================================================

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

  // FIXED: Copy function that produces clean professional text
const handleCopy = async () => {
  try {
    // Step 1: Clean markdown formatting (hashtags and asterisks)
    let cleanContent = content
      // Remove markdown headers (### Header -> Header)
      .replace(/^#{1,6}\s*(.+)$/gm, '$1')
      // Remove markdown bold (**text** -> text)
      .replace(/\*\*(.*?)\*\*/g, '$1')
      // Remove markdown italic (*text* -> text)  
      .replace(/\*(.*?)\*/g, '$1')
      // Remove markdown code blocks (```code``` -> code)
      .replace(/```[\s\S]*?```/g, '')
      .replace(/`([^`]+)`/g, '$1')
      
      // Step 2: Convert HTML to clean plain text (NO MARKDOWN SYMBOLS)
      // Main headers (h1, h2, h3) - convert to plain text with proper spacing
      .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n\n$1\n\n')
      .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n\n$1\n\n') 
      .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n\n$1\n\n')
      
      // Subsection headers (h4) - convert to plain text with colons
      .replace(/<h4[^>]*><strong>(.*?)<\/strong><\/h4>/gi, '\n\n$1\n\n')
      .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '\n\n$1\n\n')
      
      // Convert legal-point divs to plain text
      .replace(/<div class="legal-point"><strong>(.*?)<\/strong><p>(.*?)<\/p><\/div>/gi, '\n\n$1\n$2\n\n')
      
      // Convert strong/bold to plain text (NO ASTERISKS)
      .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '$1')
      .replace(/<b[^>]*>(.*?)<\/b>/gi, '$1')
      
      // Convert emphasis to clean text  
      .replace(/<em[^>]*>(.*?)<\/em>/gi, '$1')
      .replace(/<i[^>]*>(.*?)<\/i>/gi, '$1')
      
      // Convert lists to simple dashes
      .replace(/<ul[^>]*>/gi, '')
      .replace(/<\/ul>/gi, '')
      .replace(/<ol[^>]*>/gi, '') 
      .replace(/<\/ol>/gi, '')
      .replace(/<li[^>]*>(.*?)<\/li>/gi, '\n- $1')
      
      // Convert paragraphs with single line break
      .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n')
      
      // Convert line breaks
      .replace(/<br\s*\/?>/gi, '\n')
      
      // Convert divs to clean text with line break
      .replace(/<div[^>]*>(.*?)<\/div>/gi, '$1\n')
      
      // Remove any remaining HTML tags
      .replace(/<[^>]*>/g, '')
      
      // Convert HTML entities
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&hellip;/g, '...')
      
      .trim();

    // Step 2: Format for clean professional appearance (NO MARKDOWN)
    cleanContent = cleanContent
      
      // Ensure proper spacing between sections
      .replace(/([.!؟])\n([أ-ي]*اً:)/g, '$1\n\n$2')
      .replace(/([.!؟])\n([أ-ي])/g, '$1\n\n$2')
      
      // Add section separators (just line breaks, no symbols)
      .replace(/\n\n([أ-ي]*اً: تحليل|[أ-ي]*اً: المنطق|[أ-ي]*اً: الاستشهاد|[أ-ي]*اً: استراتيجية|[أ-ي]*اً: الخاتمة)/g, '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n$1')
      
      // Clean up multiple line breaks but keep structure
      .replace(/\n{4,}/g, '\n\n\n')
      
      // Ensure bullet points have proper spacing
      .replace(/\n- /g, '\n- ')
      
      // Add proper spacing after full stops before new sections
      .replace(/([.!؟])([أ-ي].*?:)/g, '$1\n\n$2')
      
      // Ensure headers end with colons where appropriate
      .replace(/^([أ-ي][^:\n]*?)([^:])$/gm, function(match, p1, p2) {
        if (p1.length < 50 && /[أ-ي]/.test(p1)) {
          return p1 + p2 + ':';
        }
        return match;
      })
      
      .trim();

    console.log('📋 CLEAN PROFESSIONAL COPY:');
    console.log(cleanContent);

    // Copy to clipboard with RTL formatting
    if (navigator.clipboard && window.isSecureContext) {
      // For modern browsers, we need to use clipboard API with HTML
      try {
        // Create a blob with RTL HTML formatting
        const htmlContent = `<div dir="rtl" style="text-align: right; direction: rtl;">${cleanContent.replace(/\n/g, '<br>')}</div>`;
        
        await navigator.clipboard.write([
          new ClipboardItem({
            'text/html': new Blob([htmlContent], { type: 'text/html' }),
            'text/plain': new Blob([cleanContent], { type: 'text/plain' })
          })
        ]);
      } catch (htmlError) {
        // Fallback to plain text if HTML clipboard fails
        await navigator.clipboard.writeText(cleanContent);
      }
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = cleanContent;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      textArea.style.direction = 'rtl';
      textArea.style.textAlign = 'right';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
    
    setCopied(true);
    showToast('تم نسخ النص بتنسيق نظيف ومهني', 'success');
    setTimeout(() => setCopied(false), 2000);
    
  } catch (error) {
    console.error('Copy failed:', error);
    showToast('فشل في نسخ النص', 'error');
  }
};

  const handleDownloadSingle = async () => {
    setDownloading(true);
    try {
      // Use the same clean formatting logic as copy function
      let cleanContent = content
        // Clean markdown formatting first
        .replace(/^#{1,6}\s*(.+)$/gm, '$1')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/```[\s\S]*?```/g, '')
        .replace(/`([^`]+)`/g, '$1')
        
        // Main headers (h1, h2, h3) - convert to plain text with proper spacing
        .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n\n$1\n\n')
        .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n\n$1\n\n') 
        .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n\n$1\n\n')
        
        // Subsection headers (h4) - convert to plain text with colons
        .replace(/<h4[^>]*><strong>(.*?)<\/strong><\/h4>/gi, '\n\n$1\n\n')
        .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '\n\n$1\n\n')
        
        // Convert legal-point divs to plain text
        .replace(/<div class="legal-point"><strong>(.*?)<\/strong><p>(.*?)<\/p><\/div>/gi, '\n\n$1\n$2\n\n')
        
        // Convert strong/bold to plain text (NO ASTERISKS)
        .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '$1')
        .replace(/<b[^>]*>(.*?)<\/b>/gi, '$1')
        
        // Convert emphasis to clean text  
        .replace(/<em[^>]*>(.*?)<\/em>/gi, '$1')
        .replace(/<i[^>]*>(.*?)<\/i>/gi, '$1')
        
        // Convert lists to simple dashes
        .replace(/<ul[^>]*>/gi, '')
        .replace(/<\/ul>/gi, '')
        .replace(/<ol[^>]*>/gi, '') 
        .replace(/<\/ol>/gi, '')
        .replace(/<li[^>]*>(.*?)<\/li>/gi, '\n- $1')
        
        // Convert paragraphs with single line break
        .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n')
        
        // Convert line breaks
        .replace(/<br\s*\/?>/gi, '\n')
        
        // Convert divs to clean text with line break
        .replace(/<div[^>]*>(.*?)<\/div>/gi, '$1\n')
        
        // Remove any remaining HTML tags
        .replace(/<[^>]*>/g, '')
        
        // Convert HTML entities
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&hellip;/g, '...')
        
        .trim();

      // Format for clean professional appearance (same as copy)
      cleanContent = cleanContent
        
        // Ensure proper spacing between sections
        .replace(/([.!؟])\n([أ-ي]*اً:)/g, '$1\n\n$2')
        .replace(/([.!؟])\n([أ-ي])/g, '$1\n\n$2')
        
        // Add section separators (just line breaks, no symbols)
        .replace(/\n\n([أ-ي]*اً: تحليل|[أ-ي]*اً: المنطق|[أ-ي]*اً: الاستشهاد|[أ-ي]*اً: استراتيجية|[أ-ي]*اً: الخاتمة)/g, '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n$1')
        
        // Clean up multiple line breaks but keep structure
        .replace(/\n{4,}/g, '\n\n\n')
        
        // Ensure bullet points have proper spacing
        .replace(/\n- /g, '\n- ')
        
        // Add proper spacing after full stops before new sections
        .replace(/([.!؟])([أ-ي].*?:)/g, '$1\n\n$2')
        
        // Ensure headers end with colons where appropriate
        .replace(/^([أ-ي][^:\n]*?)([^:])$/gm, function(match, p1, p2) {
          if (p1.length < 50 && /[أ-ي]/.test(p1)) {
            return p1 + p2 + ':';
          }
          return match;
        })
        
        .trim();
      
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
      // Generate full conversation content with clean formatting
      let fullContent = '';
      let conversationTitle = selectedConversation ? 
        conversations.find((c: any) => c.id === selectedConversation)?.title || 'محادثة قانونية' : 
        'محادثة قانونية';

      fullContent += `عنوان المحادثة: ${conversationTitle}\n\n`;
      fullContent += `تاريخ الإنشاء: ${new Date().toLocaleDateString('ar-SA')}\n\n`;
      fullContent += '='.repeat(50) + '\n\n';

      messages.forEach((message: any, index: any) => {
        const roleLabel = message.role === 'user' ? '👤 السؤال' : '🤖 الإجابة';
        
        // Use the same clean formatting logic as copy function
        let cleanContent = message.content
          // Clean markdown formatting first
          .replace(/^#{1,6}\s*(.+)$/gm, '$1')
          .replace(/\*\*(.*?)\*\*/g, '$1')
          .replace(/\*(.*?)\*/g, '$1')
          .replace(/```[\s\S]*?```/g, '')
          .replace(/`([^`]+)`/g, '$1')
          .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n\n$1\n\n')
          .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n\n$1\n\n')
          .replace(/<h4[^>]*><strong>(.*?)<\/strong><\/h4>/gi, '\n\n$1\n\n')
          .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '$1')
          .replace(/<li[^>]*>(.*?)<\/li>/gi, '\n- $1')
          .replace(/<ul[^>]*>/gi, '\n')
          .replace(/<\/ul>/gi, '\n')
          .replace(/<ol[^>]*>/gi, '\n')
          .replace(/<\/ol>/gi, '\n')
          .replace(/<br\s*\/?>/gi, '\n')
          .replace(/<p[^>]*>/gi, '\n')
          .replace(/<\/p>/gi, '\n')
          .replace(/<div[^>]*>/gi, '')
          .replace(/<\/div>/gi, '')
          .replace(/<span[^>]*>/gi, '')
          .replace(/<\/span>/gi, '')
          .replace(/&nbsp;/gi, ' ')
          .replace(/&amp;/gi, '&')
          .replace(/&lt;/gi, '<')
          .replace(/&gt;/gi, '>')
          .replace(/&quot;/gi, '"')
          .replace(/&#x27;/gi, "'")
          .replace(/\n\s*\n\s*\n/gi, '\n\n')
          .replace(/^\s+|\s+$/gm, '')
          .trim();
        
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
  isDark?: boolean;
}

// Replace your FormattedMessage component with this GREEN-THEMED version

const FormattedMessage: React.FC<FormattedMessageProps> = ({ 
  content, 
  role, 
  sidebarOpen, 
  isLastMessage = false,
  messages = [],
  conversations = [],
  selectedConversation = null,
  isDark = false
}) => {
  if (role === 'user') {
    return (
      <div style={{
        lineHeight: '1.6',
        textAlign: 'right',
        direction: 'rtl',
        fontSize: '25px',
        color: '#ffffff' // Always white for user messages (green background in both themes)
      }}>
        {content}
      </div>
    );
  }

  // AI messages: Premium Legal Document Container - GREEN THEME
  return (
    <div
      className="ai-response-container"
      style={{
        // Premium Legal Document Background - Theme Aware
        background: isDark
          ? 'linear-gradient(145deg, #1f2937 0%, #111827 50%, #0f1419 100%)'
          : 'linear-gradient(145deg, #ffffff 0%, #fefffe 50%, #f6fdf9 100%)',
        
        // Professional Border & Shadow - Theme Aware
        border: isDark 
          ? '1px solid rgba(75, 85, 99, 0.3)' 
          : '1px solid #d1f5d3',
        borderRadius: '24px',
        boxShadow: isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.4),
             0 4px 16px rgba(0, 0, 0, 0.3),
             0 1px 4px rgba(0, 0, 0, 0.3),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 4px 16px rgba(0, 108, 53, 0.04),
             0 1px 4px rgba(0, 108, 53, 0.04),
             inset 0 1px 0 rgba(255, 255, 255, 0.9)`,
        
        // Spacing & Layout
        padding: '3.5rem 4rem 3rem 4rem',
        margin: '2rem 0 2.5rem 0',
        position: 'relative' as const,
        overflow: 'hidden' as const,
        maxWidth: '90%',
        width: 'fit-content',
        minWidth: '400px',
        
        // Typography Base
        fontFamily: "'Noto Sans Arabic', 'SF Pro Display', -apple-system, sans-serif",
        direction: 'rtl' as const,
        textAlign: 'right' as const,
        
        // Smooth Transitions
        transition: 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        
        // Auto margins for centering
        marginLeft: 'auto',
        marginRight: 'auto',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-3px)';
        e.currentTarget.style.boxShadow = `
          0 12px 48px rgba(0, 108, 53, 0.12),
          0 8px 24px rgba(0, 108, 53, 0.08),
          0 2px 8px rgba(0, 108, 53, 0.06),
          inset 0 1px 0 rgba(255, 255, 255, 0.95)
        `;
        e.currentTarget.style.borderColor = '#b8f2bb';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 4px 16px rgba(0, 108, 53, 0.04),
          0 1px 4px rgba(0, 108, 53, 0.04),
          inset 0 1px 0 rgba(255, 255, 255, 0.9)
        `;
        e.currentTarget.style.borderColor = '#d1f5d3';
      }}
    >
      {/* Premium Legal Header Badge - GREEN THEME */}
      <div
        style={{
          content: '⚖️ الاستشارة القانونية',
          position: 'absolute',
          top: '0',
          right: '0',
          background: 'linear-gradient(135deg, #006C35 0%, #004A24 50%, #006C35 100%)',
          color: 'white',
          padding: '12px 32px 12px 28px',
          borderRadius: '0 24px 0 20px',
          fontSize: '16px',
          fontWeight: '600',
          letterSpacing: '0.02em',
          boxShadow: `
            0 4px 16px rgba(0, 108, 53, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
          `,
          zIndex: 10,
          fontFamily: "'Noto Sans Arabic', sans-serif"
        }}
      >
        ⚖️ الاستشارة القانونية
      </div>

      {/* Elegant Legal Accent Border - GREEN THEME */}
      <div
        style={{
          position: 'absolute',
          top: '0',
          right: '0',
          width: '5px',
          height: '100%',
          background: 'linear-gradient(180deg, #006C35 0%, #059669 25%, #004A24 50%, #059669 75%, #006C35 100%)',
          borderRadius: '0 24px 24px 0',
          boxShadow: 'inset 1px 0 2px rgba(255, 255, 255, 0.3)'
        }}
      />

      <div
  className="ai-response"
   dangerouslySetInnerHTML={{ __html: (() => {
     const formatted = formatAIResponse(content);
     console.log('🔍 FINAL HTML BEING RENDERED:');
     console.log(formatted);
     return formatted;
   })() }}
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

// Enhanced CSS for green theme typography (add this to your App.css)

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


// Enhanced formatAIResponse function - FIXED TYPESCRIPT VERSION

// Type definitions for table data
interface TableData {
  headers: string[];
  rows: string[][];
}

// Clean formatAIResponse function - No colors, just clean structure
// Enhanced version of your superior formatter
// This combines your clean approach with multi-agent section detection

const detectMultiAgentResponse = (content: string): boolean => {
  const indicators = [
    '📋', '🔍', '⚖️', '💡', '📚', '🎯',
    'التحقق من صحة المراجع',
    'الإجراءات المطلوبة', 
    'التحليل القانوني',
    'السوابق القضائية',
    'مستوى الثقة:',
    'التقييم:',
    'الاستشهاد:',
    'بناءً على التحليل القانوني',
    'الأسس القانونية لحقوقك'
  ];
  
  return indicators.some(indicator => content.includes(indicator));
};


const formatAIResponse = (content: string): string => {
  console.log('---- RAW INPUT ----');
  console.log(content);

  // Step 1: Clean the input
  let cleaned = content
    // Remove any existing HTML tags first
    .replace(/<\/?bold>/gi, '')
    .replace(/<\/?b>/gi, '')
    // Remove control characters
    .replace(/[\u200e\u200f\u202a-\u202e\uFEFF]/g, '')
    .trim();

  console.log('---- AFTER CLEANING ----');
  console.log(cleaned);

  // Step 2: CRITICAL FIX - Separate stuck markdown headers (GENERIC - NO HARDCODING)
  cleaned = cleaned
    // FIRST: Fix stuck markdown headers: ANY character followed immediately by ###
    .replace(/([^\s\n])(#{1,4}\s)/g, '$1\n$2')
    
    // SECOND: Fix Arabic ordinals stuck to previous text (but preserve the ordinal word intact)
    .replace(/([^\s\n:])(\s*)(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):/g, '$1\n$3:')
    
    // THIRD: Fix numbered points stuck to Arabic text
    .replace(/([أ-ي])(\d+\.)/g, '$1\n$2')
    
    // FOURTH: Fix common Arabic sentence starters stuck to previous text
    .replace(/([أ-ي])(بناءً|وفقاً|يجب|يمكن|نطلب|ختاماً|في\s+حال|على\s+أن|من\s+المهم)/g, '$1\n$2')
    
    // FIFTH: Add line breaks after Arabic ordinals if they're followed by more content on same line
    .replace(/(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):\s*([أ-ي][^:\n]{10,})/g, '$1: $2\n');

  console.log('---- AFTER HEADER SEPARATION ----');
  console.log(cleaned);

  // Step 3: Ensure proper spacing around headers
  cleaned = cleaned
    // Ensure headers have space after #
    .replace(/(#+)([^\s#])/g, '$1 $2')
    // Add line breaks before and after headers
    .replace(/\n(#+\s[^\n]+)\n/g, '\n\n$1\n\n')
    // Clean up multiple newlines
    .replace(/\n{3,}/g, '\n\n');

  // Step 4: Process line by line to convert markdown
  const lines = cleaned.split('\n');
  const processedLines = [];

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    
    if (!line) {
      processedLines.push('');
      continue;
    }

    // Convert headers - SIMPLE, NO INLINE STYLES (CSS will handle sizing)
    if (line.startsWith('####')) {
      line = line.replace(/^####\s*(.*)$/, '<h3>$1</h3>');
    } else if (line.startsWith('###')) {
      line = line.replace(/^###\s*(.*)$/, '<h3>$1</h3>');
    } else if (line.startsWith('##')) {
      line = line.replace(/^##\s*(.*)$/, '<h3>$1</h3>');
    } else if (line.startsWith('#')) {
      line = line.replace(/^#\s*(.*)$/, '<h3>$1</h3>');
    }
    // Convert Arabic ordinal headers - SIMPLE
    else if (/^(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):\s*.{0,100}$/.test(line)) {
      line = line.replace(/^(.*?)$/, '<h3>$1</h3>');
    }
    // Handle OTHER Arabic headers - SIMPLE
    else if (/^[أ-ي\s]{4,25}:\s*$/.test(line) && !line.includes('أولاً') && !line.includes('ثانياً') && !line.includes('ثالثاً')) {
      line = line.replace(/^(.*?):\s*$/, '<h3>$1</h3>');
    }

    processedLines.push(line);
  }

  // Step 5: Join and process other markdown
  let html = processedLines.join('\n');

  console.log('---- AFTER LINE PROCESSING ----');
  console.log(html);

  // Step 6: Process remaining markdown elements - CREATE PROPER SUBSECTIONS LIKE YOUR EXAMPLE
  html = html
    // First, handle numbered items that should become subsections
    .replace(/^(\d+)\.\s*\*\*(.*?)\*\*:\s*$/gm, '<h4><strong>$1. $2:</strong></h4>')
    
    // Handle standalone bold items that should be subsection headers (like **الحوالة البنكية:**)
    .replace(/^\*\*(.*?):\*\*\s*$/gm, '<h4><strong>$1:</strong></h4>')
    .replace(/^\*\*(.*?)\*\*:\s*$/gm, '<h4><strong>$1:</strong></h4>')
    
    // Convert remaining numbered items to clean bullet points
    .replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>')
    
    // Convert standalone bullet points 
    .replace(/^-\s+(.+)$/gm, '<li>$1</li>')
    .replace(/^\*\s+(.+)$/gm, '<li>$1</li>')
    .replace(/^•\s+(.+)$/gm, '<li>$1</li>')
    
    // Convert bold text (after headers are processed)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    // Clean up orphaned numbers
    .replace(/^(\d+)\.\s*$/gm, '')
    
    // Group consecutive list items into ul tags
    .replace(/(<li>.*?<\/li>(?:\n<li>.*?<\/li>)*)/gm, function(match) {
      return '<ul>' + match.replace(/\n/g, '') + '</ul>';
    })

  // Step 7: Wrap paragraphs and clean up
  const blocks = html.split(/\n\s*\n/);
  const finalBlocks = [];

  for (const block of blocks) {
    const trimmed = block.trim();
    if (!trimmed) continue;

    // Check if it's already an HTML element
    if (/^<(h[1-3]|div|ul|li)/.test(trimmed)) {
      finalBlocks.push(trimmed);
    } else {
      // Wrap in paragraph - SIMPLE (CSS will handle all styling)
      finalBlocks.push(`<p>${trimmed}</p>`);
    }
  }

  // Step 8: Final cleanup - SIMPLE
  let result = finalBlocks.join('\n\n')
    // Remove empty paragraphs
    .replace(/<p>\s*<\/p>/g, '')
    // Clean up strong tags inside headers
    .replace(/<h([1-3])><strong>(.*?)<\/strong><\/h[1-3]>/g, '<h$1>$2</h$1>')
    // Fix nested headers
    .replace(/<h([1-3])>\s*<h[1-3]>(.*?)<\/h[1-3]>\s*<\/h[1-3]>/g, '<h$1>$2</h$1>')
    // Fix empty headers
    .replace(/<h[1-3]>\s*<\/h[1-3]>/g, '')
    // Remove extra whitespace
    .replace(/\n{3,}/g, '\n\n');

  // 🛡️ SECURITY: Apply XSS protection before returning
  const sanitizedResult = sanitizeHTML(result);
  
  console.log('---- FINAL RESULT (SANITIZED) ----');
  console.log(sanitizedResult);
  
  return sanitizedResult;
};



// Parse Arabic comparison text into table structure
const parseArabicComparison = (lines: string[]): TableData => {
  const result: TableData = { headers: [], rows: [] };
  
  // Look for header indicators
  let processLines = lines;
  const firstLine = lines[0];
  if (firstLine && (firstLine.includes('مقارنة') || firstLine.includes('الفرق'))) {
    // Skip title line
    processLines = lines.slice(1);
  }
  
  // Try to identify comparison patterns
  const comparisonPatterns = [
    // Pattern: "الأول: ... | الثاني: ..."
    /^(.+?)[:：]\s*(.+?)(?:\s*\|\s*(.+?)[:：]\s*(.+?))?$/,
    // Pattern: "- النوع الأول: ... - النوع الثاني: ..."
    /^[-•]\s*(.+?)[:：]\s*(.+?)(?:\s*[-•]\s*(.+?)[:：]\s*(.+?))?$/,
    // Pattern: "1. ... 2. ..."
    /^(\d+)[.\-]\s*(.+?)(?:\s*(\d+)[.\-]\s*(.+?))?$/
  ];
  
  for (const line of processLines) {
    for (const pattern of comparisonPatterns) {
      const match = line.match(pattern);
      if (match) {
        if (result.headers.length === 0) {
          if (match[1] && match[3]) {
            result.headers = [match[1], match[3]];
          } else {
            result.headers = ['العنصر الأول', 'العنصر الثاني'];
          }
        }
        if (match[2] && match[4]) {
          result.rows.push([match[2], match[4]]);
        } else if (match[2]) {
          result.rows.push([match[2], '']);
        }
        break; // Found a match, move to next line
      }
    }
  }
  
  return result;
};

// Generate HTML table for comparisons
const generateComparisonTable = (data: TableData): string => {
  let html = '<table class="comparison-table legal-comparison">';
  
  // Add caption for legal comparison
  html += '<caption>مقارنة قانونية تفصيلية</caption>';
  
  // Table header
  html += '<thead><tr>';
  data.headers.forEach(header => {
    html += `<th>${header}</th>`;
  });
  html += '</tr></thead>';
  
  // Table body
  html += '<tbody>';
  data.rows.forEach(row => {
    html += '<tr>';
    row.forEach(cell => {
      html += `<td>${cell || '-'}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  
  return html;
};

// Simple function to detect if content contains table-like structure
const containsTableStructure = (content: string): boolean => {
  const tableIndicators = [
    /\|.*\|.*\|/,  // Pipe-separated values
    /مقارنة.*?:.*?مقابل/gi,  // Arabic comparison
    /الفرق.*?والــ/gi,  // Arabic difference
    /جدول/gi,  // Table in Arabic
    /vs\.?/gi,  // versus
    /^\s*[-\*]\s*.+?:\s*.+$/gm  // List with colons (potential table rows)
  ];
  
  return tableIndicators.some(pattern => pattern.test(content));
};

// Enhanced format function with table detection


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
              {showRegister ? 'إنشاء حساب جديد' : 'تسجيل الدخول'}
            </h1>
            
            <p style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '16px',
              fontWeight: '400',
              lineHeight: '1.5',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
              margin: 0
            }}>
              {showRegister ? 'انضم إلينا للحصول على استشارات قانونية متخصصة' : 'ادخل إلى حسابك للوصول إلى الاستشارات القانونية المتقدمة'}
            </p>

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

// =====================================================================
// 🛡️ SENIOR-LEVEL XSS PROTECTION & HTML SANITIZATION
// =====================================================================

/**
 * Secure HTML sanitizer to prevent XSS attacks
 * Uses DOMPurify with strict configuration for legal AI content
 * @param html - Raw HTML content to sanitize
 * @returns {string} Sanitized HTML safe for rendering
 */
const sanitizeHTML = (html: string): string => {
  // Configure DOMPurify for legal AI content
  const config = {
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'br', 'strong', 'b', 'em', 'i', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['class', 'style'], // Allow minimal styling
    ALLOW_DATA_ATTR: false, // No data attributes
    ALLOW_UNKNOWN_PROTOCOLS: false, // Block javascript: and other protocols
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button'],
    FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'],
    KEEP_CONTENT: true // Keep text content even if tags are removed
  };
  
  // Sanitize with strict rules
  const sanitized = DOMPurify.sanitize(html, config);
  
  // Additional validation for conversation IDs in content
  if (sanitized.includes('javascript:') || sanitized.includes('data:') || sanitized.includes('<script')) {
    console.warn('🚨 Potential XSS attempt blocked in content');
    return DOMPurify.sanitize(html.replace(/<[^>]*>/g, ''), { ALLOWED_TAGS: [] }); // Strip all HTML if suspicious
  }
  
  return sanitized;
};

// =====================================================================
// SENIOR-LEVEL CONVERSATION PARAMETER VALIDATION
// =====================================================================

/**
 * Validates conversation ID format and content
 * @param conversationId - The conversation ID to validate
 * @returns {boolean} True if valid, false otherwise
 */
const isValidConversationIdFormat = (conversationId: string): boolean => {
  if (!conversationId || typeof conversationId !== 'string') return false;
  
  // Conversation ID should be non-empty and not contain dangerous characters
  const trimmed = conversationId.trim();
  if (trimmed.length === 0) return false;
  
  // Basic security: no script injections, no path traversals
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /\.\.\/\.\.\//,
    /\0/,
    /%00/,
    /[<>'"]/
  ];
  
  return !dangerousPatterns.some(pattern => pattern.test(trimmed));
};

/**
 * Sanitizes conversation ID for safe usage
 * @param conversationId - Raw conversation ID
 * @returns {string} Sanitized conversation ID
 */
const sanitizeConversationId = (conversationId: string): string => {
  if (!conversationId || typeof conversationId !== 'string') return '';
  
  return conversationId
    .trim()
    .replace(/[<>'"]/g, '') // Remove potential HTML/script characters
    .replace(/\0|%00/g, ''); // Remove null bytes
};

// =====================================================================
// SENIOR-LEVEL CUSTOM HOOK FOR CONVERSATION ROUTING
// =====================================================================

/**
 * Senior-level custom hook for managing conversation URL routing
 * Handles bidirectional URL ↔ State synchronization with error boundaries
 * 
 * @returns {UseConversationRoutingReturn} Hook interface with navigation methods
 */
const useConversationRouting = (
  selectedConversation: string | null,
  conversations: any[],
  loadConversationMessages: (conversationId: string) => Promise<void>,
  user: any,
  loadingConversations: boolean,
  loadConversations: () => Promise<void>
): UseConversationRoutingReturn => {
  const { conversationId } = useParams<ConversationRouteParams>();
  const navigate = useNavigate();

  // Comprehensive conversation ID validation
  const isValidConversationId = (conversationId: string): boolean => {
    // First check format and security
    if (!isValidConversationIdFormat(conversationId)) return false;
    
    // Then check if it exists in user's conversations
    const sanitized = sanitizeConversationId(conversationId);
    return conversations.some(conv => conv.id === sanitized);
  };

  // Senior-level navigation methods with parameter validation and error handling
  const navigateToConversation = (conversationId: string) => {
    try {
      if (!conversationId) {
        console.warn('🚨 Empty conversation ID provided');
        navigate('/');
        return;
      }
      
      // Validate format first for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format:', conversationId);
        navigate('/', { replace: true });
        return;
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      if (isValidConversationId(sanitizedId)) {
        console.log('🎯 Navigating to conversation:', sanitizedId);
        navigate(`/c/${sanitizedId}`);
      } else {
        console.warn('🚨 Conversation not found:', sanitizedId);
        navigate('/', { replace: true });
      }
    } catch (error) {
      console.error('🚨 Navigation error:', error);
      navigate('/', { replace: true });
    }
  };

  const navigateToHome = () => {
    try {
      console.log('🏠 Navigating to home');
      navigate('/');
    } catch (error) {
      console.error('🚨 Home navigation error:', error);
      window.location.href = '/'; // Fallback
    }
  };

  // URL → State synchronization with race condition protection
  useEffect(() => {
    if (!conversationId) return;
    
    try {
      // Validate conversation ID format first for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format in URL:', conversationId);
        navigate('/', { replace: true });
        return;
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      if (sanitizedId !== selectedConversation) {
        // 🔧 FIX RACE CONDITION: Check if we have user AND if conversations are loading
        if (!user) {
          console.log('⏳ Waiting for user authentication...');
          return;
        }
        
        if (conversations.length === 0 && !loadingConversations) {
          // Conversations not loaded and not loading - trigger load
          console.log('🔄 Triggering conversation load for URL navigation');
          loadConversations();
          return;
        }
        
        if (conversations.length === 0 && loadingConversations) {
          // Still loading conversations - wait
          console.log('⏳ Waiting for conversations to load...');
          return;
        }
        
        // Conversations are loaded - validate and navigate
        if (isValidConversationId(sanitizedId)) {
          console.log('🔄 Loading conversation from URL:', sanitizedId);
          loadConversationMessages(sanitizedId).catch((error) => {
            console.error('🚨 Failed to load conversation:', error);
            navigate('/', { replace: true });
          });
        } else {
          console.warn('🚨 Conversation not found in URL, redirecting to home');
          navigate('/', { replace: true });
        }
      }
    } catch (error) {
      console.error('🚨 URL synchronization error:', error);
      navigate('/', { replace: true });
    }
  }, [conversationId, conversations, selectedConversation, user, loadingConversations, loadConversations, loadConversationMessages, navigate]);

  return {
    conversationId: conversationId || null,
    navigateToConversation,
    navigateToHome,
    isValidConversationId
  };
};

// =====================================================================

const ChatApp: React.FC = () => {
  const { 
  user, 
  isGuest, 
  cooldownInfo, 
  incrementQuestionUsage, 
  canSendMessage, 
  updateUserData,
  refreshUserData,
  logout
} = useAuth();
  
  // Dark mode for authenticated users
  const { isDark, toggleTheme } = useTheme();
  
  const [isMobile, setIsMobile] = useState(false); // 🔧 ADD THIS LINE
  // Initialize sidebar state from localStorage, default to true if not found
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const saved = localStorage.getItem('sidebarOpen');
    return saved !== null ? JSON.parse(saved) : true;
  });
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

  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('sidebarOpen', JSON.stringify(sidebarOpen));
  }, [sidebarOpen]);

  // Detect mobile screen size
  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      
      // Only force sidebar closed on mobile, but preserve user preference on desktop
      if (mobile) {
        setSidebarOpen(false);
      }
      // On desktop, keep the user's saved preference (don't force open)
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 🔄 Refresh user data on component mount to ensure accurate counters
  useEffect(() => {
    if (!isGuest && refreshUserData) {
      refreshUserData();
    }
  }, [isGuest, refreshUserData]);

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
  id: response.current_user.id,
  email: response.current_user.email,
  full_name: response.current_user.full_name,
  questions_used_current_cycle: response.current_user.questions_used_current_cycle,
  
  cycle_reset_time: response.current_user.cycle_reset_time,
  subscription_tier: response.current_user.subscription_tier,
  is_active: response.current_user.is_active,
  is_verified: response.current_user.is_verified
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
      // ✅ SENIOR-LEVEL PARAMETER VALIDATION
      if (!conversationId || typeof conversationId !== 'string') {
        console.warn('🚨 Invalid conversation ID provided to loadConversationMessages');
        throw new Error('Invalid conversation ID');
      }
      
      // Validate format for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format in loadConversationMessages:', conversationId);
        throw new Error('Invalid conversation ID format');
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      console.log('📥 Loading conversation messages for:', sanitizedId);
      const response = await chatAPI.getConversationMessages(sanitizedId);
      setMessages(response.messages || []);
      setSelectedConversation(sanitizedId);
      if (isMobile) setSidebarOpen(false);
    } catch (error) {
      console.error('❌ Failed to load conversation messages:', error);
      showToast('فشل في تحميل المحادثة', 'error');
      // Reset to clean state on error
      setMessages([]);
      setSelectedConversation(null);
      throw error; // Re-throw for upstream error handling
    }
  };

  // =====================================================================
  // SENIOR-LEVEL URL ROUTING INTEGRATION
  // =====================================================================
  
  // Integrate the custom hook for URL-state synchronization
  const { navigateToConversation, navigateToHome } = useConversationRouting(
    selectedConversation,
    conversations,
    loadConversationMessages,
    user,
    loadingConversations,
    loadConversations
  );

  // =====================================================================

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
    // Navigate to home when starting new conversation
    navigateToHome();
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

  // ✅ UNIFIED: Check cooldown for both user types
  if (!canSendMessage()) {
    if (cooldownInfo.isInCooldown) {
      showToast(`يجب الانتظار حتى الساعة ${cooldownInfo.resetTimeFormatted}`, 'error');
    } else {
      if (isGuest) {
        setUpgradePromptType('messages');
        setShowUpgradePrompt(true);
      } else {
        showToast('تم تجاوز الحد المسموح من الأسئلة', 'error');
      }
    }
    return;
  }

  // ✅ PREPARE: User message for immediate display
  const currentMessage = inputMessage;
  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage,
    timestamp: new Date().toISOString()
  };

  setMessages(prev => [...prev, userMessage]);
  setInputMessage('');
  setIsLoading(true);
  incrementQuestionUsage();

  // ✅ UNIFIED: Use chatAPI for both guests and auth users
  const guestSessionId = isGuest ?
    `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` :
    undefined;

  console.log('📤 Sending message:', {
    isGuest,
    conversationId: selectedConversation,
    sessionId: guestSessionId
  });

  try {
    // 🔥 Create assistant message for real-time streaming updates
    const assistantMessageId = (Date.now() + 1).toString();
    let streamingContent = '';

    // Add empty assistant message that will be updated in real-time
    setMessages(prev => [...prev, {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    }]);

    // 🚀 REAL STREAMING with conversation memory
    await chatAPI.sendMessageStreaming(
      currentMessage,
      selectedConversation || undefined,
      guestSessionId,
      
            // 📡 Real-time streaming callback
      (chunk: string) => {
        streamingContent += chunk;
        
        // Update the assistant message in real-time with RAW content
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: streamingContent }  // ← FIX: No formatting during streaming
            : msg
        ));
      },

      // ✅ Completion handler
      (response: any) => {
        console.log('📥 Received response:', { contentLength: response.fullResponse?.length || 0 });
        
        // Update final message with complete data and SINGLE formatting pass
        const finalContent = response.ai_message?.content || streamingContent;
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
          ? {
              ...msg,
              id: response.ai_message?.id || assistantMessageId,
              content: formatAIResponse(finalContent), // ← FIX: Format only once at the end
              timestamp: response.ai_message?.timestamp || new Date().toISOString()
            }
          : msg
        ));

        // 🔄 Handle conversation and user data updates with URL synchronization
        if (response.conversation_id && !selectedConversation) {
          setSelectedConversation(response.conversation_id);
          // 🎯 SENIOR-LEVEL URL SYNC: Navigate to new conversation URL
          navigateToConversation(response.conversation_id);
        }

        if (response.updated_user && !isGuest) {
          updateUserData({
            id: response.updated_user.id,
            email: response.updated_user.email,
            full_name: response.updated_user.full_name,
            questions_used_current_cycle: response.updated_user.questions_used_current_cycle,
            cycle_reset_time: response.updated_user.cycle_reset_time,
            subscription_tier: response.updated_user.subscription_tier,
            is_active: response.updated_user.is_active,
            is_verified: response.updated_user.is_verified
          });
        }

        if (!isGuest) {
          loadConversations();
          // 🔄 Refresh user data to ensure accurate question counters
          refreshUserData();
        }

        console.log('✅ Message processed successfully');
      },
      
      // ❌ Error handler
      (error: string) => {
        console.error('❌ Streaming failed:', error);
        
        // Remove the assistant message on streaming error
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
        showToast('حدث خطأ في الإرسال. حاول مرة أخرى.', 'error');
      }
    );

  } catch (error: any) {
    console.error('❌ Chat API failed:', error);
    
    // Remove user message on complete failure
    setMessages(prev => prev.slice(0, -2)); // Remove both user and assistant messages
    
    if (error.response?.status === 429) {
      showToast('تم تجاوز الحد المسموح من الأسئلة', 'error');
    } else {
      showToast('حدث خطأ في الإرسال. حاول مرة أخرى.', 'error');
    }
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
  'ما هي عقوبات التهرب الضريبي؟',
  'ما هي حقوق المستهلك في السعودية؟',
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
  gridTemplateColumns: isMobile 
    ? (sidebarOpen ? '320px 1fr' : '1fr')
    : sidebarOpen 
      ? '320px 1fr' 
      : '1fr',
  gridTemplateAreas: isMobile 
    ? (sidebarOpen ? '"sidebar main"' : '"main"')
    : sidebarOpen 
      ? '"sidebar main"'
      : '"main"',
  // 🔧 MOBILE FIX: Dynamic height
  height: isMobile ? 'auto' : '100vh',
  minHeight: isMobile ? '100vh' : 'auto',
  fontFamily: "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  background: 'var(--background-light)',
  direction: 'rtl',
  contain: 'layout style paint',
  // 🔧 MOBILE FIX: Allow scrolling
  overflow: isMobile ? 'visible' : 'hidden'
}}>
        
        {/* Mobile Backdrop */}
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
    onClick={(e) => {
      // Only close if clicking the backdrop itself, not scrolling
      if (e.target === e.currentTarget) {
        toggleSidebar();
      }
    }}
  />
)}

        {/* Sidebar */}
        {/* Sidebar Toggle Button */}
{!sidebarOpen && (
  <button
    onClick={() => setSidebarOpen(true)}
    style={{
      position: 'fixed',
      top: '24px',
      right: '24px',
      zIndex: 100,
      background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.95) 0%, rgba(0, 74, 36, 0.9) 50%, rgba(0, 108, 53, 0.85) 100%)',
      color: 'white',
      border: '1px solid rgba(255, 255, 255, 0.15)',
      borderRadius: '16px',
      padding: '14px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      boxShadow: '0 8px 32px rgba(0, 108, 53, 0.25), 0 4px 16px rgba(0, 108, 53, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)',
      width: '48px',
      height: '48px'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 1) 0%, rgba(0, 74, 36, 0.95) 50%, rgba(0, 108, 53, 0.9) 100%)';
      e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
      e.currentTarget.style.boxShadow = '0 12px 48px rgba(0, 108, 53, 0.35), 0 8px 24px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.95) 0%, rgba(0, 74, 36, 0.9) 50%, rgba(0, 108, 53, 0.85) 100%)';
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25), 0 4px 16px rgba(0, 108, 53, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
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
    inset: isMobile ? '0 0 0 auto' : 'auto',  // ← This positions it on the RIGHT
    width: isMobile ? '320px' : '100%',
    // 🔧 MOBILE FIX: Dynamic height
    height: isMobile ? '100vh' : '100vh', // Keep 100vh for sidebar
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
  
  {/* Theme and close buttons */}
  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
    {/* Theme toggle */}
    <button
      onClick={toggleTheme}
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
      title={isDark ? 'تبديل للوضع الفاتح' : 'تبديل للوضع المظلم'}
    >
      {isDark ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      )}
    </button>
    
    {/* Close button */}
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
      onClick={() => navigateToConversation(conv.id)}
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
          current={cooldownInfo.questionsUsed}
          max={cooldownInfo.maxQuestions
}
          label="الرسائل المجانية"
          type="messages"
        />
        
        <PremiumProgress
  current={cooldownInfo.questionsUsed}
  max={cooldownInfo.maxQuestions}
  label="الأسئلة المستخدمة"
  type="messages"
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
              {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)} / {cooldownInfo.maxQuestions}
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
  background: 'var(--background-white)',
  // 🔧 MOBILE FIX: Dynamic height
  height: isMobile ? 'auto' : '100vh',
  minHeight: isMobile ? '100vh' : 'auto',
  position: 'relative',
  // 🔧 MOBILE FIX: Allow overflow on mobile
  overflow: isMobile ? 'visible' : 'hidden'
}}>

          {/* Messages Area */}
          <div 
  className="chat-main-area"
  style={{
    flex: 1,
    overflowY: 'auto',
    padding: '24px 0',
    scrollBehavior: 'smooth',
    // 🔧 MOBILE FIX: Better touch scrolling
    WebkitOverflowScrolling: 'touch',
    // 🔧 MOBILE FIX: Ensure proper height on mobile
    minHeight: isMobile ? '60vh' : 'auto'
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
                  اهلا بك في حكم
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
                        background: 'var(--background-white)',
                        border: isDark 
                          ? '1px solid rgba(75, 85, 99, 0.3)' 
                          : '1px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '20px',
                        cursor: 'pointer',
                        textAlign: 'right',
                        boxShadow: isDark 
                          ? '0 2px 4px rgba(0, 0, 0, 0.2)' 
                          : '0 2px 4px rgba(0, 0, 0, 0.05)',
                        animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s both`
                      }}
                      onClick={() => handleSuggestedQuestion(question)}
                      onMouseOver={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#10a37f';
                        (e.currentTarget as HTMLElement).style.boxShadow = isDark 
                          ? '0 4px 12px rgba(16, 163, 127, 0.3)' 
                          : '0 4px 12px rgba(16, 163, 127, 0.15)';
                      }}
                      onMouseOut={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = isDark 
                          ? 'rgba(75, 85, 99, 0.3)' 
                          : '#e5e7eb';
                        (e.currentTarget as HTMLElement).style.boxShadow = isDark 
                          ? '0 2px 4px rgba(0, 0, 0, 0.2)' 
                          : '0 2px 4px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      <div style={{
                        fontSize: '22px',
                        color: isDark ? '#f9fafb' : '#374151',
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
    // 🔧 MOBILE FIX: Different calculations for mobile  
    maxWidth: isMobile ? '100%' : '100%',
    padding: isMobile ? '0 1rem' : '0 2rem'
  }}
>
                {messages.map((message, index) => (
                 <div
  key={message.id}
  className="message-enter"
  style={{
    display: 'flex',
    flexDirection: 'row',
    justifyContent: isMobile 
  ? (message.role === 'user' ? 'flex-end' : 'center') 
  : (message.role === 'user' ? 'flex-end' : 'center'),
    marginBottom: '24px',
    animationDelay: `${index * 0.1}s`
  }}
>

  <div
  className={message.role === 'user' ? 'user-message-enhanced' : ''}
  style={{
    maxWidth: message.role === 'user' 
      ? (isMobile ? '75%' : '60%')
      : '90%',
    minWidth: message.role === 'user' ? '200px' : 'auto',
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
    marginLeft: message.role === 'user' ? 'auto' : '0%',
    marginRight: message.role === 'user' ? '3cm' : '0',
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
  isDark={isDark}
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
  background: isDark 
    ? 'linear-gradient(135deg, rgba(31, 41, 55, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%)'
    : 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)',
  borderTop: isDark 
    ? '1px solid rgba(55, 65, 81, 0.3)'
    : '1px solid rgba(0, 108, 53, 0.1)',
  position: 'relative',
  display: 'flex',
  justifyContent: 'center',
  backdropFilter: 'blur(20px)',
  boxShadow: isDark
    ? 'inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 -4px 32px rgba(0, 0, 0, 0.2)'
    : 'inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 -4px 32px rgba(0, 108, 53, 0.05)'
}}>
  <div style={{
    position: 'relative',
    maxWidth: '1200px',
    width: '100%'
  }}>
    
    <div 
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        gap: '16px',
        background: isDark
          ? 'linear-gradient(135deg, rgba(55, 65, 81, 0.8) 0%, rgba(31, 41, 55, 0.6) 100%)'
          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)',
        borderRadius: '24px',
        padding: '20px 24px',
        border: isDark
          ? '2px solid rgba(75, 85, 99, 0.3)'
          : '2px solid rgba(0, 108, 53, 0.1)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: '80px',
        backdropFilter: 'blur(20px)',
        boxShadow: isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.3),
             0 0 0 1px rgba(255, 255, 255, 0.05),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`,
        animation: inputMessage.length === 0 ? 'luxuryPulse 4s ease-in-out infinite' : 'none'
      }}
      onFocus={() => {
        // Stop animation on focus
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.borderColor = isDark 
          ? 'rgba(75, 85, 99, 0.5)' 
          : 'rgba(0, 108, 53, 0.2)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = isDark
          ? `0 12px 40px rgba(0, 0, 0, 0.4),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.15)`
          : `0 12px 40px rgba(0, 108, 53, 0.12),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.borderColor = isDark 
          ? 'rgba(75, 85, 99, 0.3)' 
          : 'rgba(0, 108, 53, 0.1)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.3),
             0 0 0 1px rgba(255, 255, 255, 0.05),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`;
      }}
    >
                 <textarea
        ref={inputRef}
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="اكتب سؤالك هنا..."
        disabled={isLoading}
        style={{
          flex: 1,
          border: 'none',
          background: 'transparent',
          resize: 'none',
          outline: 'none',
          fontSize: '20px',
          lineHeight: '1.5',
          color: isDark ? '#f9fafb' : '#1f2937',
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
            الأسئلة المتبقية: {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)}/{cooldownInfo.maxQuestions}
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
</>);
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

const AppContent: React.FC = () => {
  const { loading, user, isGuest } = useAuth();

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

  // =====================================================================
  // SENIOR-LEVEL REACT ROUTER IMPLEMENTATION
  // =====================================================================
  return (
    <Routes>
      {/* Authentication Route */}
      <Route path="/auth" element={<AuthScreen />} />
      
      {/* Conversation Routes - Senior-level URL structure */}
      <Route path="/c/:conversationId" element={<ChatApp />} />
      
      {/* Home Route - Default chat interface */}
      <Route path="/" element={<ChatApp />} />
      
      {/* Fallback Route - Redirect invalid URLs to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;