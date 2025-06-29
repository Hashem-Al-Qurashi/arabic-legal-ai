import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import LegalForm from './components/legal/LegalForm';
import { legalAPI } from './services/api';
import type { Consultation } from './types/auth';
import './App.css';

// Toast notification system
const toast = {
  error: (msg: string) => {
    // Create a better toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      font-family: 'Noto Sans Arabic', sans-serif;
      font-weight: 500;
      max-width: 300px;
      animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => document.body.removeChild(toast), 300);
    }, 4000);
  },
  success: (msg: string) => {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      z-index: 1000;
      font-family: 'Noto Sans Arabic', sans-serif;
      font-weight: 500;
      max-width: 300px;
      animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => document.body.removeChild(toast), 300);
    }, 4000);
  }
};

// Add animation keyframes to document
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { opacity: 0; transform: translateX(100%); }
    to { opacity: 1; transform: translateX(0); }
  }
  @keyframes slideOut {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(100%); }
  }
`;
document.head.appendChild(style);

const AuthScreen: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🇸🇦 المساعد القانوني الذكي</h1>
          <p>استشارة قانونية ومالية وإدارية ذكية مبنية على القانون السعودي</p>
          <p style={{ fontSize: '0.9rem', color: '#6b7280', marginTop: '0.5rem' }}>
            نظام حديث ومتطور لتقديم الاستشارات القانونية المتخصصة
          </p>
        </div>
        
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
            <p>جاري التحميل...</p>
          </div>
        ) : showRegister ? (
          <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
        )}
      </div>
    </div>
  );
};

const MainApp: React.FC = () => {
  const { user, logout, loading } = useAuth();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [isExporting, setIsExporting] = useState<string | null>(null);

  const handleNewConsultation = (consultation: Consultation) => {
    setConsultations(prev => [consultation, ...prev]);
    toast.success('تم الحصول على الإجابة بنجاح! 🎉');
  };

  const handleExport = async (consultation: Consultation) => {
    setIsExporting(consultation.id);
    try {
      await legalAPI.exportDocx(consultation.question, consultation.answer);
      toast.success('تم تحميل الملف بنجاح! 📄');
    } catch (error) {
      toast.error('حدث خطأ في التحميل. حاول مرة أخرى.');
    } finally {
      setIsExporting(null);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <h2>جاري تحميل المساعد القانوني...</h2>
        <p>يرجى الانتظار بينما نجهز كل شيء لك</p>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <div>
              <h1 className="title">🇸🇦 المساعد القانوني الذكي</h1>
              <p className="subtitle">
                نظام متطور للاستشارات القانونية المبنية على الذكاء الاصطناعي والقانون السعودي
              </p>
            </div>
            <div className="user-section">
              <div className="user-info">
                <div style={{ fontWeight: '600' }}>أهلاً وسهلاً</div>
                <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>{user.full_name}</div>
              </div>
              <button onClick={logout} className="logout-btn">
                تسجيل الخروج
              </button>
            </div>
          </div>
        </header>

        <main className="main">
          <LegalForm onNewConsultation={handleNewConsultation} />
          
          {consultations.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ 
                color: '#1f2937', 
                marginBottom: '1.5rem', 
                fontSize: '1.5rem',
                fontWeight: '600'
              }}>
                📚 تاريخ الاستشارات القانونية
              </h2>
            </div>
          )}
          
          {consultations.map((consultation, index) => (
            <div key={consultation.id} className="response-card">
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '1rem',
                flexWrap: 'wrap',
                gap: '0.5rem'
              }}>
                <h3 style={{ margin: 0 }}>✅ الإجابة القانونية</h3>
                <div style={{ 
                  fontSize: '0.9rem', 
                  color: '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  🕐 {formatDate(consultation.timestamp)}
                </div>
              </div>

              <div style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '1.5rem',
                border: '1px solid #e2e8f0'
              }}>
                <h4 style={{ 
                  color: '#374151', 
                  marginBottom: '0.5rem',
                  fontWeight: '500',
                  fontSize: '1rem'
                }}>
                  📝 السؤال:
                </h4>
                <p style={{ 
                  margin: 0, 
                  color: '#4b5563',
                  lineHeight: '1.6'
                }}>
                  {consultation.question}
                </p>
              </div>

              <div 
                className="response-content" 
                dangerouslySetInnerHTML={{ __html: consultation.answer }}
              />
              
              <div className="response-actions">
                <button 
                  onClick={() => handleExport(consultation)}
                  disabled={isExporting === consultation.id}
                  className="export-btn"
                >
                  {isExporting === consultation.id ? (
                    <>
                      <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                      جاري التحميل...
                    </>
                  ) : (
                    <>
                      📄 تحميل ملف Word
                    </>
                  )}
                </button>
              </div>

              {index < consultations.length - 1 && (
                <div style={{
                  height: '1px',
                  background: 'linear-gradient(90deg, transparent, #e5e7eb, transparent)',
                  margin: '2rem 0 0'
                }} />
              )}
            </div>
          ))}

          {consultations.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '3rem 2rem',
              color: '#6b7280'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚖️</div>
              <h3 style={{ marginBottom: '0.5rem', color: '#374151' }}>
                ابدأ أول استشارة قانونية
              </h3>
              <p>اطرح سؤالك القانوني وسنقدم لك إجابة مفصلة مبنية على القانون السعودي</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};

export default App;