import React, { useEffect } from 'react';
import type { FormattedMessageProps } from '../../types';
import { formatAIResponse } from '../../utils/messageParser';
import { ActionsBar } from '../actions';

export const FormattedMessage: React.FC<FormattedMessageProps> = ({ 
  content, 
  role, 
  sidebarOpen, 
  isLastMessage = false,
  messages = [],
  conversations = [],
  selectedConversation = null,
  isDark = false
}) => {
  // Detect mobile - ChatGPT exact replica on mobile
  const isMobile = window.innerWidth <= 768;

  if (role === 'user') {
    return (
      <div style={{
        lineHeight: '1.6',
        textAlign: 'right',
        direction: 'rtl',
        fontSize: '25px',
        color: '#ffffff' // Always white for user messages (green background)
      }}>
        {content}
      </div>
    );
  }

  // Mobile: ChatGPT exact replica - NO container, just plain text with same font size as user
  if (isMobile) {
    return (
      <div style={{
        fontSize: '25px', // Match user question font size
        lineHeight: '1.6',
        color: isDark ? '#ffffff' : '#374151',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        direction: 'rtl',
        textAlign: 'right',
        margin: '0',
        padding: '0'
      }}>
        <div
          dangerouslySetInnerHTML={{ __html: formatAIResponse(content) }}
        />
        
        {/* Actions for mobile - simple, no container */}
        <div style={{ marginTop: '12px' }}>
          <ActionsBar
            content={content}
            isLastMessage={isLastMessage}
            messages={messages}
            conversations={conversations}
            selectedConversation={selectedConversation}
          />
        </div>
      </div>
    );
  }

  // Desktop: Keep the premium legal styling
  return (
    <div
      className="ai-response-container"
      style={{
        background: isDark
          ? 'linear-gradient(145deg, #1f2937 0%, #111827 50%, #0f1419 100%)'
          : 'linear-gradient(145deg, #ffffff 0%, #fefffe 50%, #f6fdf9 100%)',
        
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
        
        padding: '3.5rem 4rem 3rem 4rem',
        margin: '2rem 0 2.5rem 0',
        position: 'relative' as const,
        overflow: 'hidden' as const,
        maxWidth: '90%',
        width: 'fit-content',
        minWidth: '400px',
        fontFamily: "'Noto Sans Arabic', 'SF Pro Display', -apple-system, sans-serif",
        direction: 'rtl' as const,
        textAlign: 'right' as const,
        transition: 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
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
      {/* Premium Legal Header Badge - Desktop Only */}
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

      {/* Elegant Legal Accent Border - Desktop Only */}
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
        style={{
          color: isDark ? '#ffffff' : '#000000',
        }}
        dangerouslySetInnerHTML={{ __html: formatAIResponse(content) }}
      />
      
      {/* ActionsBar for desktop */}
      <div>
        <ActionsBar
          content={content}
          isLastMessage={isLastMessage}
          messages={messages}
          conversations={conversations}
          selectedConversation={selectedConversation}
        />
      </div>
    </div>
  );
};