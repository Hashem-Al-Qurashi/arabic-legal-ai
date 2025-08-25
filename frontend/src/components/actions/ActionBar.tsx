import React, { useState } from 'react';
import type { ActionsBarProps, Message, Conversation } from '../../types';
import { showToast } from '../../utils/helpers';
import { legalAPI } from '../../services/api';

export const ActionsBar: React.FC<ActionsBarProps> = ({ content, isLastMessage, messages, conversations, selectedConversation }) => {
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