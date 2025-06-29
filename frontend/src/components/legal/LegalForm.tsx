import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { legalAPI } from '../../services/api';
const toast = {
  error: (msg: string) => alert(msg),
  success: (msg: string) => alert(msg)
};import type { Consultation } from '../../types/auth';

interface LegalFormProps {
  onNewConsultation: (consultation: Consultation) => void;
}

const LegalForm: React.FC<LegalFormProps> = ({ onNewConsultation }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error('يرجى كتابة سؤالك');
      return;
    }

    setLoading(true);
    try {
      const consultation = await legalAPI.askQuestion(question.trim());
      onNewConsultation(consultation);
      setQuestion('');
      toast.success('تم الحصول على الإجابة بنجاح');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'حدث خطأ في معالجة السؤال');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="legal-form">
      <div className="user-info">
        <p>مرحباً، {user?.full_name}</p>
        <p>الأسئلة المتبقية هذا الشهر: <strong>{3 - (user?.questions_used_this_month || 0)}</strong></p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>📋 اكتب سؤالك القانوني:</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="مثال: ما هي حقوق الموظف عند إنهاء الخدمة؟"
            rows={6}
            disabled={loading}
            required
          />
        </div>
        
        <button type="submit" disabled={loading || !question.trim()} className="submit-btn">
          {loading ? (
            <>
              <span className="spinner"></span>
              جاري المعالجة...
            </>
          ) : (
            '🔍 أرسل السؤال'
          )}
        </button>
      </form>
    </div>
  );
};

export default LegalForm;
