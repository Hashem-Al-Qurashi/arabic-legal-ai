import React, { useState, useEffect, useRef } from 'react';

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
            <div style={{ marginBottom: '24px' }}>
              <input
                ref={inputRef}
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="اسم المحادثة الجديد"
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  border: '2px solid #F5F5F5',
                  borderRadius: '12px',
                  fontSize: '15px',
                  outline: 'none',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  direction: 'rtl',
                  textAlign: 'right',
                  background: 'rgba(255, 255, 255, 0.9)',
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
              justifyContent: 'center',
              direction: 'rtl'
            }}>
              {/* Cancel button */}
              <button
                type="button"
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
                  minWidth: '90px',
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
              
              {/* Save button */}
              <button
                type="submit"
                disabled={!newTitle.trim() || newTitle.trim() === currentTitle}
                style={{
                  padding: '12px 24px',
                  background: newTitle.trim() && newTitle.trim() !== currentTitle 
                    ? 'linear-gradient(135deg, #006C35 0%, #004A24 100%)' 
                    : 'rgba(117, 117, 117, 0.3)',
                  color: newTitle.trim() && newTitle.trim() !== currentTitle ? 'white' : '#9E9E9E',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: newTitle.trim() && newTitle.trim() !== currentTitle ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                  fontWeight: '600',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
                  minWidth: '90px',
                  boxShadow: newTitle.trim() && newTitle.trim() !== currentTitle 
                    ? '0 8px 32px rgba(0, 108, 53, 0.25)' 
                    : 'none'
                }}
                onMouseOver={(e) => {
                  if (newTitle.trim() && newTitle.trim() !== currentTitle) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.35)';
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

export default RenamePopup;