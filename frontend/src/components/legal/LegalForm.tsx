import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { legalAPI, chatAPI } from '../../services/api';  // ← FIXED
import type { Consultation } from '../../types/auth';

// Toast notification
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
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    font-family: 'Noto Sans Arabic', sans-serif;
    font-weight: 500;
    max-width: 350px;
    animation: slideIn 0.3s ease-out;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => document.body.removeChild(toast), 300);
  }, 4000);
};

interface LegalFormProps {
  onNewConsultation: (consultation: Consultation) => void;
}

const LegalForm: React.FC<LegalFormProps> = ({ onNewConsultation }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const { user } = useAuth();
  // ADD THESE LINES after your existing useState in LegalForm:
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);

  const maxChars = 1000;
  const questionsRemaining = 3 - (user?.questions_used_this_month || 0);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxChars) {
      setQuestion(value);
      setCharCount(value.length);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!question.trim()) {
    showToast('يرجى كتابة سؤالك القانوني قبل الإرسال', 'error');
    return;
  }

  if (question.trim().length < 10) {
    showToast('يرجى كتابة سؤال أكثر تفصيلاً (على الأقل 10 أحرف)', 'error');
    return;
  }

  if (questionsRemaining <= 0) {
    showToast('لقد استنفدت عدد الأسئلة المسموحة لهذا الشهر', 'error');
    return;
  }

  setLoading(true);
  try {
    // 🔥 NEW: Try chat API first (with memory), fallback to old API
    let consultation;
    try {
const chatResponse = await chatAPI.sendMessage(question.trim(), currentConversationId || undefined);      
      // Convert chat response to consultation format
      consultation = {
        id: chatResponse.ai_message.id,
        question: question.trim(),
        answer: chatResponse.ai_message.content,
        processing_time_ms: chatResponse.ai_message.processing_time_ms || 1500,
        timestamp: chatResponse.ai_message.timestamp,
        user_questions_remaining: chatResponse.user_questions_remaining
      };
      
      // Update conversation state
      setCurrentConversationId(chatResponse.conversation_id);
      setConversationHistory(prev => [...prev, {
        user: question.trim(),
        assistant: chatResponse.ai_message.content
      }]);
      
    } catch (chatError) {
      // Fallback to old API if chat fails
      console.log('Chat API failed, using fallback:', chatError);
      consultation = await legalAPI.askQuestion(question.trim());
    }
    
    onNewConsultation(consultation);
    setQuestion('');
    setCharCount(0);
    showToast('تم الحصول على الإجابة بنجاح! 🎉', 'success');
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'حدث خطأ في معالجة السؤال. حاول مرة أخرى.';
    showToast(errorMessage, 'error');
  } finally {
    setLoading(false);
  }
};

  const suggestionQuestions = [
    "ما هي حقوق الموظف عند إنهاء الخدمة؟",
    "كيف يتم تسجيل شركة جديدة في السعودية؟",
    "ما هي إجراءات الطلاق في النظام السعودي؟",
    "ما هي حقوق المستأجر في عقد الإيجار؟"
  ];

  const handleSuggestionClick = (suggestion: string) => {
    setQuestion(suggestion);
    setCharCount(suggestion.length);
  };

  return (
    <div className="legal-form">
      {/* User Info Header */}
      <div className="user-info">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <p style={{ margin: '0 0 0.25rem 0', fontWeight: '600', fontSize: '1.1rem' }}>
              👋 مرحباً، {user?.full_name}
            </p>
            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>
              نحن هنا لمساعدتك في جميع استفساراتك القانونية
            </p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              background: questionsRemaining > 0 ? '#dcfce7' : '#fee2e2',
              color: questionsRemaining > 0 ? '#166534' : '#991b1b',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '0.9rem'
            }}>
              الأسئلة المتبقية: {questionsRemaining} من 3
            </div>
          </div>
        </div>
      </div>

      {/* Quick Suggestions */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ 
          color: '#374151', 
          marginBottom: '1rem', 
          fontSize: '1.1rem',
          fontWeight: '600' 
        }}>
          💡 أسئلة شائعة للمساعدة:
        </h3>
        <div style={{ 
          display: 'grid', 
          gap: '0.75rem',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))'
        }}>
          {suggestionQuestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                padding: '0.75rem 1rem',
                textAlign: 'right',
                fontSize: '0.9rem',
                color: '#475569',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out',
                fontFamily: 'inherit',
                lineHeight: '1.4'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '0.75rem'
          }}>
            <span style={{ fontWeight: '600', fontSize: '1.1rem', color: '#374151' }}>
              📋 اكتب سؤالك القانوني بالتفصيل:
            </span>
            <span style={{ 
              fontSize: '0.85rem', 
              color: charCount > maxChars * 0.8 ? '#ef4444' : '#6b7280' 
            }}>
              {charCount}/{maxChars}
            </span>
          </label>
          
          <textarea
            value={question}
            onChange={handleInputChange}
            placeholder="مثال: أحتاج إلى معرفة الإجراءات المطلوبة لتأسيس شركة ذات مسؤولية محدودة في المملكة العربية السعودية، وما هي المتطلبات القانونية والمالية اللازمة؟"
            rows={6}
            disabled={loading || questionsRemaining <= 0}
            required
            className="textarea"
            style={{
              borderColor: charCount > maxChars * 0.8 ? '#f59e0b' : undefined,
              background: questionsRemaining <= 0 ? '#f3f4f6' : undefined
            }}
          />
          
          {charCount > maxChars * 0.8 && (
            <div style={{ 
              fontSize: '0.85rem', 
              color: '#f59e0b', 
              marginTop: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem'
            }}>
              ⚠️ أنت تقترب من الحد الأقصى للأحرف
            </div>
          )}
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !question.trim() || questionsRemaining <= 0} 
          className="submit-btn"
          style={{
            opacity: questionsRemaining <= 0 ? 0.5 : undefined,
            cursor: questionsRemaining <= 0 ? 'not-allowed' : undefined
          }}
        >
          {loading ? (
            <>
              <div className="spinner"></div>
              جاري معالجة السؤال...
            </>
          ) : questionsRemaining <= 0 ? (
            <>
              🚫 تم استنفاد الأسئلة لهذا الشهر
            </>
          ) : (
            <>
              🔍 احصل على الاستشارة القانونية
            </>
          )}
        </button>

        {questionsRemaining <= 0 && (
          <div style={{
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
            border: '1px solid #f59e0b',
            color: '#92400e',
            padding: '1rem',
            borderRadius: '8px',
            textAlign: 'center',
            marginTop: '1rem'
          }}>
            <strong>💎 ترقية للباقة المدفوعة</strong>
            <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
              احصل على المزيد من الاستشارات القانونية المتخصصة مع الباقة المميزة
            </p>
          </div>
        )}
      </form>

      {/* Tips Section */}
      <div style={{
        background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
        border: '1px solid #bfdbfe',
        borderRadius: '8px',
        padding: '1.5rem',
        marginTop: '2rem'
      }}>
        <h4 style={{ 
          color: '#1e40af', 
          marginBottom: '1rem',
          fontSize: '1rem',
          fontWeight: '600'
        }}>
          💡 نصائح للحصول على أفضل استشارة:
        </h4>
        <ul style={{ 
          margin: 0, 
          paddingRight: '1.5rem',
          color: '#1e40af',
          fontSize: '0.9rem',
          lineHeight: '1.6'
        }}>
          <li>اكتب سؤالك بوضوح وتفصيل</li>
          <li>اذكر السياق والظروف المحيطة بالقضية</li>
          <li>حدد نوع القانون (تجاري، عمل، عقاري، إلخ)</li>
          <li>اذكر أي تواريخ أو مبالغ مالية مهمة</li>
        </ul>
      </div>
    </div>
  );
};

export default LegalForm;