import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToRegister, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('يرجى ملء جميع الحقول');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      // Success - call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('خطأ في تسجيل الدخول. تحقق من البيانات وحاول مرة أخرى.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '440px',
      margin: '0 auto',
      padding: '48px 32px',
      textAlign: 'center'
    }}>

      {error && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.08) 100%)',
          color: '#dc2626',
          padding: '16px 20px',
          borderRadius: '12px',
          marginBottom: '24px',
          border: '1px solid rgba(220, 38, 38, 0.2)',
          fontSize: '15px',
          fontWeight: '500',
          textAlign: 'center',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          position: 'relative'
        }}>
          <div style={{
            position: 'absolute',
            left: '16px',
            top: '50%',
            transform: 'translateY(-50%)'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          <div style={{ paddingLeft: '32px' }}>
            {error}
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '24px' }}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{
            display: 'block',
            fontSize: '15px',
            fontWeight: '600',
            color: 'rgba(255, 255, 255, 0.9)',
            marginBottom: '8px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
          }}>
            البريد الإلكتروني
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            style={{
              width: '100%',
              padding: '16px 20px',
              fontSize: '16px',
              border: '1px solid rgba(209, 213, 219, 0.8)',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.8)',
              color: '#1f2937',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
              transition: 'all 0.2s ease',
              outline: 'none',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#006C35';
              e.target.style.background = 'rgba(255, 255, 255, 1)';
              e.target.style.boxShadow = '0 0 0 3px rgba(0, 108, 53, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(209, 213, 219, 0.8)';
              e.target.style.background = 'rgba(255, 255, 255, 0.8)';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
        
        <div style={{ marginBottom: '28px' }}>
          <label style={{
            display: 'block',
            fontSize: '15px',
            fontWeight: '600',
            color: 'rgba(255, 255, 255, 0.9)',
            marginBottom: '8px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
          }}>
            كلمة المرور
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            style={{
              width: '100%',
              padding: '16px 20px',
              fontSize: '16px',
              border: '1px solid rgba(209, 213, 219, 0.8)',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.8)',
              color: '#1f2937',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
              transition: 'all 0.2s ease',
              outline: 'none',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#006C35';
              e.target.style.background = 'rgba(255, 255, 255, 1)';
              e.target.style.boxShadow = '0 0 0 3px rgba(0, 108, 53, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(209, 213, 219, 0.8)';
              e.target.style.background = 'rgba(255, 255, 255, 0.8)';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !email || !password}
          style={{
            width: '100%',
            padding: '16px 24px',
            fontSize: '16px',
            fontWeight: '600',
            color: 'white',
            background: (!loading && email && password) 
              ? 'linear-gradient(135deg, #006C35 0%, #004A24 100%)'
              : 'rgba(156, 163, 175, 0.5)',
            border: 'none',
            borderRadius: '12px',
            cursor: (!loading && email && password) ? 'pointer' : 'not-allowed',
            transition: 'all 0.3s ease',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
            position: 'relative',
            overflow: 'hidden',
            boxShadow: (!loading && email && password) 
              ? '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
              : 'none'
          }}
          onMouseOver={(e) => {
            if (!loading && email && password) {
              e.currentTarget.style.background = 'linear-gradient(135deg, #00A852 0%, #006C35 100%)';
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
            }
          }}
          onMouseOut={(e) => {
            if (!loading && email && password) {
              e.currentTarget.style.background = 'linear-gradient(135deg, #006C35 0%, #004A24 100%)';
              e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
            }
          }}
        >
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
              <div style={{
                width: '20px',
                height: '20px',
                border: '2px solid transparent',
                borderTop: '2px solid currentColor',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              جاري تسجيل الدخول...
            </div>
          ) : (
            'تسجيل الدخول'
          )}
        </button>
      </form>
      
      {/* Forgot Password Link */}
      <div style={{
        textAlign: 'center',
        marginBottom: '24px'
      }}>
        <button 
          type="button"
          onClick={() => {
            // TODO: Implement forgot password functionality
            alert('سيتم تطبيق وظيفة استعادة كلمة المرور قريباً');
          }}
          style={{
            background: 'none',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            textDecoration: 'underline',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
            transition: 'color 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.color = '#006C35';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.color = 'rgba(255, 255, 255, 0.7)';
          }}
        >
          نسيت كلمة المرور؟
        </button>
      </div>
      
      <div style={{
        textAlign: 'center',
        fontSize: '15px',
        color: 'rgba(255, 255, 255, 0.7)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif'
      }}>
        ليس لديك حساب؟{' '}
        <button 
          type="button" 
          onClick={onSwitchToRegister}
          style={{
            background: 'none',
            border: 'none',
            color: '#006C35',
            fontSize: '15px',
            fontWeight: '600',
            cursor: 'pointer',
            textDecoration: 'underline',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
            transition: 'color 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.color = '#004A24';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.color = '#006C35';
          }}
        >
          إنشاء حساب جديد
        </button>
      </div>
    </div>
  );
};

export default LoginForm;