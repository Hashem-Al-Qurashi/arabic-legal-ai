import React, { useState } from 'react';
import { legalAPI } from '../../services/api';
import { showToast } from '../../utils/notifications';
import type { Message, Conversation } from '../../types/chat';

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
    // Step 1: Convert HTML to clean, professional Arabic text
    let cleanContent = content
      
      // Convert headings to clean structured text
      .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n━━━ $1 ━━━\n\n')
      .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n▎$1\n\n') 
      .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n▸ $1\n\n')
      
      // Convert legal-point divs to clean numbered format
      .replace(/<div class="legal-point"><strong>(.*?)<\/strong><p>(.*?)<\/p><\/div>/gi, '$1 $2\n\n')
      
      // 🔑 KEY FIX: Convert bold/strong to clean text (NO ASTERISKS!)
      .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '$1')
      .replace(/<b[^>]*>(.*?)<\/b>/gi, '$1')
      
      // Convert emphasis to clean text  
      .replace(/<em[^>]*>(.*?)<\/em>/gi, '$1')
      .replace(/<i[^>]*>(.*?)<\/i>/gi, '$1')
      
      // Convert lists to clean bullet points
      .replace(/<ul[^>]*>/gi, '\n')
      .replace(/<\/ul>/gi, '\n')
      .replace(/<ol[^>]*>/gi, '\n') 
      .replace(/<\/ol>/gi, '\n')
      .replace(/<li[^>]*>(.*?)<\/li>/gi, '• $1\n')
      
      // Convert paragraphs with proper spacing
      .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n')
      
      // Convert line breaks
      .replace(/<br\s*\/?>/gi, '\n')
      
      // Convert divs to clean text
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
      
      // Clean up whitespace while preserving structure
      .replace(/[ \t]+/g, ' ')                    // Normalize horizontal spaces
      .replace(/\n[ \t]+/g, '\n')                 // Remove leading spaces
      .replace(/[ \t]+\n/g, '\n')                 // Remove trailing spaces  
      .replace(/\n{4,}/g, '\n\n\n')               // Max 3 newlines for section breaks
      
      // Ensure proper Arabic text flow
      .replace(/([أ-ي])\n+(أولاً|ثانياً|ثالثاً|رابعاً|خامساً)/g, '$1\n\n$2')
      .replace(/([أ-ي])\n+(\d+\.)/g, '$1\n\n$2')
      .replace(/([أ-ي])\n+(▸|•)/g, '$1\n\n$2')
      
      .trim();

    // Step 2: Final cleanup for professional appearance
    cleanContent = cleanContent
      // Ensure sections have proper spacing
      .replace(/(━━━.*━━━)\n{1,2}([^▸•])/g, '$1\n\n$2')
      .replace(/(▸.*?)\n{1,2}([^▸•▎])/g, '$1\n\n$2')
      
      // Clean bullet formatting
      .replace(/•\s*/g, '• ')
      .replace(/▸\s*/g, '▸ ')
      
      // Remove excess whitespace at beginning/end
      .replace(/\n{2,}$/, '\n')
      .replace(/^\n{2,}/, '');

    console.log('📋 CLEAN PROFESSIONAL COPY:');
    console.log(cleanContent);

    // Copy to clipboard
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(cleanContent);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = cleanContent;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
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

export default ActionsBar;