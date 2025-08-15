import React from 'react';
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
  if (role === 'user') {
    return (
      <div style={{
        lineHeight: '1.6',
        textAlign: 'right',
        direction: 'rtl',
        fontSize: '25px',
        color: '#ffffff' // Always white for user messages (green background in both themes)
      }}>
        {content}
      </div>
    );
  }

  // AI messages: Mobile ChatGPT-style vs Desktop Legal theme
  const isMobile = window.innerWidth <= 768;
  
  return (
    <div
      className="ai-response-container"
      style={{
        // Background - Mobile: clean white, Desktop: premium legal theme
        background: isMobile 
          ? '#ffffff'
          : isDark
            ? 'linear-gradient(145deg, #1f2937 0%, #111827 50%, #0f1419 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #fefffe 50%, #f6fdf9 100%)',
        
        // Border - Mobile: minimal, Desktop: premium legal
        border: isMobile
          ? '1px solid #e5e5e5'
          : isDark 
            ? '1px solid rgba(75, 85, 99, 0.3)' 
            : '1px solid #d1f5d3',
        
        // Border radius - Mobile: simple, Desktop: rounded
        borderRadius: isMobile ? '8px' : '24px',
        
        // Shadow - Mobile: subtle, Desktop: premium
        boxShadow: isMobile
          ? '0 1px 3px rgba(0, 0, 0, 0.1)'
          : isDark
            ? `0 8px 32px rgba(0, 0, 0, 0.4),
               0 4px 16px rgba(0, 0, 0, 0.3),
               0 1px 4px rgba(0, 0, 0, 0.3),
               inset 0 1px 0 rgba(255, 255, 255, 0.1)`
            : `0 8px 32px rgba(0, 108, 53, 0.08),
               0 4px 16px rgba(0, 108, 53, 0.04),
               0 1px 4px rgba(0, 108, 53, 0.04),
               inset 0 1px 0 rgba(255, 255, 255, 0.9)`,
        
        // Padding - Mobile: compact, Desktop: spacious
        padding: isMobile ? '24px' : '3.5rem 4rem 3rem 4rem',
        
        // Margin - Mobile: tight, Desktop: generous
        margin: isMobile ? '16px 0' : '2rem 0 2.5rem 0',
        
        // Position - Mobile: static, Desktop: relative for badges
        position: isMobile ? 'static' : 'relative' as const,
        overflow: isMobile ? 'visible' : 'hidden' as const,
        
        // Width - Mobile: full width, Desktop: fitted
        maxWidth: isMobile ? '100%' : '90%',
        width: isMobile ? '100%' : 'fit-content',
        minWidth: isMobile ? 'auto' : '400px',
        
        // Typography
        fontFamily: "'Noto Sans Arabic', 'SF Pro Display', -apple-system, sans-serif",
        direction: 'rtl' as const,
        textAlign: 'right' as const,
        
        // Transitions - Mobile: none, Desktop: smooth
        transition: isMobile ? 'none' : 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        
        // Centering - Mobile: normal, Desktop: auto margins
        marginLeft: isMobile ? '0' : 'auto',
        marginRight: isMobile ? '0' : 'auto',
      }}
      onMouseEnter={!isMobile ? (e) => {
        e.currentTarget.style.transform = 'translateY(-3px)';
        e.currentTarget.style.boxShadow = `
          0 12px 48px rgba(0, 108, 53, 0.12),
          0 8px 24px rgba(0, 108, 53, 0.08),
          0 2px 8px rgba(0, 108, 53, 0.06),
          inset 0 1px 0 rgba(255, 255, 255, 0.95)
        `;
        e.currentTarget.style.borderColor = '#b8f2bb';
      } : undefined}
      onMouseLeave={!isMobile ? (e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 4px 16px rgba(0, 108, 53, 0.04),
          0 1px 4px rgba(0, 108, 53, 0.04),
          inset 0 1px 0 rgba(255, 255, 255, 0.9)
        `;
        e.currentTarget.style.borderColor = '#d1f5d3';
      } : undefined}
    >
      {/* Premium Legal Header Badge - GREEN THEME - Desktop Only */}
      {!isMobile && (
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
      )}

      {/* Elegant Legal Accent Border - GREEN THEME - Desktop Only */}
      {!isMobile && (
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
      )}

      <div
        className="ai-response"
        style={{
          // Content styling - Mobile: clean, Desktop: default
          fontSize: isMobile ? '16px' : undefined,
          lineHeight: isMobile ? '1.7' : undefined,
          color: isMobile ? '#374151' : undefined,
        }}
        dangerouslySetInnerHTML={{ __html: (() => {
          const formatted = formatAIResponse(content);
          return formatted;
        })() }}
      />
      
      {/* Add ActionsBar for AI messages */}
      <div style={isMobile ? { marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #f3f4f6' } : undefined}>
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