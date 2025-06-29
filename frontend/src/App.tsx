import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import LegalForm from './components/legal/LegalForm';
import { legalAPI } from './services/api';
import type { Consultation } from './types/auth';
import './App.css';

const toast = {
  error: (msg: string) => alert(msg),
  success: (msg: string) => alert(msg)
};

const AuthScreen: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🇸🇦 المساعد القانوني الذكي</h1>
          <p>استشارة قانونية ذكية مبنية على القانون السعودي</p>
        </div>
        
        {showRegister ? (
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

  const handleNewConsultation = (consultation: Consultation) => {
    setConsultations(prev => [consultation, ...prev]);
  };

  const handleExport = async (consultation: Consultation) => {
    try {
      await legalAPI.exportDocx(consultation.question, consultation.answer);
      alert('تم تحميل الملف بنجاح!');
    } catch (error) {
      alert('حدث خطأ في التحميل');
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>جاري التحميل...</p>
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
            <h1>🇸🇦 المساعد القانوني الذكي</h1>
            <div className="user-section">
              <span>مرحباً، {user.full_name}</span>
              <button onClick={logout} className="logout-btn">تسجيل الخروج</button>
            </div>
          </div>
        </header>

        <main className="main">
          <LegalForm onNewConsultation={handleNewConsultation} />
          
          {consultations.map((consultation) => (
            <div key={consultation.id} className="response-card">
              <h3>✅ الرد:</h3>
              <div className="response-content" dangerouslySetInnerHTML={{ __html: consultation.answer }} />
              <div className="response-actions">
                <button 
                  onClick={() => handleExport(consultation)}
                  className="export-btn"
                >
                  📝 تحميل Word
                </button>
              </div>
            </div>
          ))}
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