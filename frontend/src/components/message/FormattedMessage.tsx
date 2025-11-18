import React from 'react';
import type { FormattedMessageProps } from '../../types';
import { formatAIResponse } from '../../utils/messageParser';
import { ActionsBar } from '../actions';
import { ThinkingBubble } from './ThinkingBubble';

export const FormattedMessage: React.FC<FormattedMessageProps> = ({ 
  content, 
  role, 
  sidebarOpen, 
  isLastMessage = false,
  messages = [],
  message,  // Full message object for thinking
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

  // ✅ COMPLETE SEPARATION: Mobile ChatGPT vs Desktop Legal
  const isMobile = window.innerWidth <= 768;
  
  // 🎯 MOBILE: Exact ChatGPT replica - NO containers, page background, same font as user
  if (isMobile) {
    return (
      <div
        style={{
          // ✅ NO CONTAINER: Use page background, no borders, no padding, no shadows
          background: 'transparent',
          border: 'none',
          borderRadius: '0',
          boxShadow: 'none',
          padding: '0',
          margin: '0',
          
          // ✅ EXACT CHATGPT: Same font size as user question (25px)
          fontSize: '25px',
          lineHeight: '1.6',
          
          // ✅ CHATGPT TYPOGRAPHY
          fontFamily: '"Söhne", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", sans-serif, "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
          
          // ✅ RTL Support
          direction: 'rtl' as const,
          textAlign: 'right' as const,
          
          // ✅ ChatGPT colors - responsive to theme
          color: isDark ? '#d1d5db' : '#374151',
          
          // ✅ Full width, no containers
          width: '100%',
          maxWidth: '100%',
        }}
      >
        {/* DeepSeek-style thinking bubble */}
        {message?.role === 'assistant' && (message.thinking || message.thinkingActive) && (
          <ThinkingBubble 
            thinking={message.thinking || []}
            isActive={message.thinkingActive || false}
            startTime={message.thinkingStartTime}
            onCancel={message.onCancel}
          />
        )}
        
        <div
          className="ai-response"
          dangerouslySetInnerHTML={{ __html: (() => {
            const formatted = formatAIResponse(content);
            return formatted;
          })() }}
        />
        
        {/* Add ActionsBar for mobile */}
        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #f3f4f6' }}>
          <ActionsBar
            content={content}
            isLastMessage={isLastMessage}
            messages={messages}
            conversations={conversations}
            selectedConversation={selectedConversation}
            isDark={isDark}
          />
        </div>
      </div>
    );
  }

  // 🏢 DESKTOP: Premium Legal Theme (unchanged)
  return (
    <div
      className="ai-response-container"
      style={{
        // Desktop: Premium legal theme
        background: isDark
          ? 'linear-gradient(145deg, #1f2937 0%, #111827 50%, #0f1419 100%)'
          : 'linear-gradient(145deg, #ffffff 0%, #fefffe 50%, #f6fdf9 100%)',
        
        // Desktop: Premium borders
        border: isDark 
          ? '1px solid rgba(75, 85, 99, 0.3)' 
          : '1px solid #d1f5d3',
        
        // Desktop: Rounded corners
        borderRadius: '24px',
        
        // Desktop: Premium shadows
        boxShadow: isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.4),
             0 4px 16px rgba(0, 0, 0, 0.3),
             0 1px 4px rgba(0, 0, 0, 0.3),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 4px 16px rgba(0, 108, 53, 0.04),
             0 1px 4px rgba(0, 108, 53, 0.04),
             inset 0 1px 0 rgba(255, 255, 255, 0.9)`,
        
        // Desktop: Spacious padding
        padding: '3.5rem 4rem 3rem 4rem',
        
        // Desktop: Generous margins
        margin: '2rem 0 2.5rem 0',
        
        // Desktop: Relative positioning for badges
        position: 'relative' as const,
        overflow: 'hidden' as const,
        
        // Desktop: Fitted width
        maxWidth: '90%',
        width: 'fit-content',
        minWidth: '400px',
        
        // Desktop: Typography
        fontFamily: "'Noto Sans Arabic', 'SF Pro Display', -apple-system, sans-serif",
        direction: 'rtl' as const,
        textAlign: 'right' as const,
        
        // Desktop: Smooth transitions
        transition: 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        
        // Desktop: Auto centering
        marginLeft: 'auto',
        marginRight: 'auto',
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

      {/* DeepSeek-style thinking bubble for desktop */}
      {!isMobile && message?.role === 'assistant' && (message.thinking || message.thinkingActive) && (
        <ThinkingBubble 
          thinking={message.thinking || []}
          isActive={message.thinkingActive || false}
          startTime={message.thinkingStartTime}
          onCancel={message.onCancel}
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