import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthScreen: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false);
  const handleNavigateToChat = () => {
    console.log('🏠 Navigating to chat page...');
    window.history.pushState({}, '', '/');
    window.dispatchEvent(new PopStateEvent('popstate'));
    // Force a re-render by dispatching a custom event
    window.dispatchEvent(new CustomEvent('auth-navigation'));
  };
  
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

export default AuthScreen;