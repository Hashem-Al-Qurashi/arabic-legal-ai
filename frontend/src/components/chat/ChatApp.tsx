// =====================================================================
// 💬 MAIN CHAT APPLICATION COMPONENT
// Extracted from 4550-line App.tsx (lines 2589-4511)
// =====================================================================

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chatAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../hooks/useTheme';
import { useConversationRouting } from '../../hooks/useConversationRouting';
import { RenamePopup, DeletePopup } from '../ui';
import { PremiumProgress, FeatureTease } from '../premium';
import { FormattedMessage } from '../message';
import { showToast, formatDate, cleanHtmlContent, containsCitations, stripCitations } from '../../utils/helpers';
import { formatAIResponse } from '../../utils/messageParser';
import { sanitizeHTML, isValidConversationIdFormat, sanitizeConversationId } from '../../utils/security';
import type { Message, Conversation } from '../../types';

export const ChatApp: React.FC = () => {
  const { 
  user, 
  isGuest, 
  cooldownInfo, 
  incrementQuestionUsage, 
  canSendMessage, 
  updateUserData,
  refreshUserData,
  logout
} = useAuth();
  
  // Dark mode for authenticated users
  const { isDark, toggleTheme } = useTheme();
  
  const [isMobile, setIsMobile] = useState(false); // 🔧 ADD THIS LINE
  // Initialize sidebar state from localStorage, default to true if not found
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const saved = localStorage.getItem('sidebarOpen');
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [conversations, setConversations] = useState<Conversation[]>([]);
  // ... rest of your state variables ...
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [exchangeCount, setExchangeCount] = useState(0);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
  const [upgradePromptType, setUpgradePromptType] = useState<'messages' | 'exchanges' | 'exports' | 'citations'>('messages');
  const [renamePopup, setRenamePopup] = useState<{
  isOpen: boolean;
  conversationId: string;
  currentTitle: string;
}>({
  isOpen: false,
  conversationId: '',
  currentTitle: ''
});
  const [deletePopup, setDeletePopup] = useState<{
  isOpen: boolean;
  conversationId: string;
  conversationTitle: string;
}>({
  isOpen: false,
  conversationId: '',
  conversationTitle: ''
});
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('sidebarOpen', JSON.stringify(sidebarOpen));
  }, [sidebarOpen]);

  // Detect mobile screen size
  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      
      // Only force sidebar closed on mobile, but preserve user preference on desktop
      if (mobile) {
        setSidebarOpen(false);
      }
      // On desktop, keep the user's saved preference (don't force open)
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 🔄 Refresh user data on component mount to ensure accurate counters
  useEffect(() => {
    if (!isGuest && refreshUserData) {
      refreshUserData();
    }
  }, [isGuest, refreshUserData]);

  const scrollToBottom = () => {
  setTimeout(() => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: "smooth",
      block: "end",
      inline: "nearest"
    });
  }, 100);
};

useEffect(() => {
  if (messages.length > 0) {
    scrollToBottom();
  }
}, [messages.length]); // Only trigger when message count changes

  useEffect(() => {
  if (user) {  // Only load when user is authenticated
    console.log('🔄 User authenticated, loading conversations...');
    loadConversations();
  }
}, [user?.id]); // Only trigger when user ID changes, not on every user update

  const loadConversations = async () => {
    if (!user || loadingConversations) return; // Safety check + prevent multiple calls
    
    setLoadingConversations(true);
    try {
      console.log('🔄 Loading conversations for user:', user.email);
      const response = await chatAPI.getConversations();
      console.log('✅ Loaded conversations:', response.conversations?.length || 0);
      
      // Only update if conversations actually changed
      const newConversations = response.conversations || [];
      setConversations(prevConversations => {
        // Simple comparison to prevent unnecessary updates
        if (JSON.stringify(prevConversations) !== JSON.stringify(newConversations)) {
          return newConversations;
        }
        return prevConversations;
      });
      
      // 🔧 FIX: Update user data if provided in conversations response (but only once)
      if (response.current_user) {
 console.log('🔄 Updating user data from conversations response:', response.current_user);
updateUserData({
  id: response.current_user.id,
  email: response.current_user.email,
  full_name: response.current_user.full_name,
  questions_used_current_cycle: response.current_user.questions_used_current_cycle,
  
  cycle_reset_time: response.current_user.cycle_reset_time,
  subscription_tier: response.current_user.subscription_tier,
  is_active: response.current_user.is_active,
  is_verified: response.current_user.is_verified
});
 }
    } catch (error: any) {
      console.log('❌ Error loading conversations:', error);
      // Don't show auth-related errors
      if (error.response?.status !== 401) {
        showToast('فشل في تحميل المحادثات السابقة', 'error');
      }
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    try {
      // ✅ SENIOR-LEVEL PARAMETER VALIDATION
      if (!conversationId || typeof conversationId !== 'string') {
        console.warn('🚨 Invalid conversation ID provided to loadConversationMessages');
        throw new Error('Invalid conversation ID');
      }
      
      // Validate format for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format in loadConversationMessages:', conversationId);
        throw new Error('Invalid conversation ID format');
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      console.log('📥 Loading conversation messages for:', sanitizedId);
      const response = await chatAPI.getConversationMessages(sanitizedId);
      setMessages(response.messages || []);
      setSelectedConversation(sanitizedId);
      if (isMobile) setSidebarOpen(false);
    } catch (error) {
      console.error('❌ Failed to load conversation messages:', error);
      showToast('فشل في تحميل المحادثة', 'error');
      // Reset to clean state on error
      setMessages([]);
      setSelectedConversation(null);
      throw error; // Re-throw for upstream error handling
    }
  };

  // =====================================================================
  // SENIOR-LEVEL URL ROUTING INTEGRATION
  // =====================================================================
  
  // Integrate the custom hook for URL-state synchronization
  const { navigateToConversation, navigateToHome } = useConversationRouting(
    selectedConversation,
    conversations,
    loadConversationMessages,
    user,
    loadingConversations,
    loadConversations
  );

  // =====================================================================

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
const containsCitations = (content: string): boolean => {
  const citationPatterns = [
    /المادة\s*\(\s*\d+\s*\)/g,
    /نظام\s+.+\s+رقم\s+م\/\d+/g,
    /المرسوم\s+الملكي\s+رقم/g,
    /اللائحة\s+التنفيذية/g
  ];
  
  return citationPatterns.some(pattern => pattern.test(content));
};

const stripCitations = (content: string): string => {
  let strippedContent = content
    .replace(/\(المادة\s*\(\s*\d+\s*\)[^)]*\)/g, '')
    .replace(/حسب\s+المادة\s*\(\s*\d+\s*\)[^.]*\./g, '')
    .replace(/وفقاً\s+لنظام\s+[^.]*\./g, '')
    .replace(/\(المرسوم\s+الملكي\s+رقم\s+[^)]*\)/g, '');
  
  // Add upgrade prompt
  strippedContent += '\n\n⚠️ للحصول على المراجع القانونية التفصيلية ومواد الأنظمة السعودية، يرجى الترقية للحساب المدفوع.';
  
  return strippedContent;
};

  const startNewConversation = () => {
    setMessages([]);
    setSelectedConversation(null);
    setInputMessage('');
    if (isMobile) setSidebarOpen(false);
    // Navigate to home when starting new conversation
    navigateToHome();
  };
  

const handleRenameConversation = (conversationId: string, currentTitle: string) => {
  setRenamePopup({
    isOpen: true,
    conversationId,
    currentTitle
  });
};

const handleRenameSubmit = async (newTitle: string) => {
  try {
    await chatAPI.updateConversationTitle(renamePopup.conversationId, newTitle);
    
    // Update the conversation in the local state to maintain order
    setConversations(prev => prev.map(conv => 
      conv.id === renamePopup.conversationId 
        ? { ...conv, title: newTitle }
        : conv
    ));
    
    showToast('تم تغيير اسم المحادثة بنجاح', 'success');
    setRenamePopup({ isOpen: false, conversationId: '', currentTitle: '' });
  } catch (error) {
    showToast('فشل في تغيير اسم المحادثة', 'error');
  }
};

const handleRenameCancel = () => {
  setRenamePopup({ isOpen: false, conversationId: '', currentTitle: '' });
};

const handleDeleteConversation = (conversationId: string, title: string) => {
  setDeletePopup({
    isOpen: true,
    conversationId,
    conversationTitle: title
  });
};

const handleDeleteConfirm = async () => {
  try {
    await chatAPI.archiveConversation(deletePopup.conversationId);
    
    // Remove from local state immediately
    setConversations(prev => prev.filter(conv => conv.id !== deletePopup.conversationId));
    
    // Clear current conversation if it's the deleted one
    if (selectedConversation === deletePopup.conversationId) {
      setSelectedConversation(null);
      setMessages([]);
    }
    
    showToast('تم حذف المحادثة بنجاح', 'success');
    setDeletePopup({ isOpen: false, conversationId: '', conversationTitle: '' });
  } catch (error) {
    showToast('فشل في حذف المحادثة', 'error');
  }
};

const handleDeleteCancel = () => {
  setDeletePopup({ isOpen: false, conversationId: '', conversationTitle: '' });
};

  const handleSendMessage = async () => {
  if (!inputMessage.trim()) return;

  // ✅ UNIFIED: Check cooldown for both user types
  if (!canSendMessage()) {
    if (cooldownInfo.isInCooldown) {
      showToast(`يجب الانتظار حتى الساعة ${cooldownInfo.resetTimeFormatted}`, 'error');
    } else {
      if (isGuest) {
        setUpgradePromptType('messages');
        setShowUpgradePrompt(true);
      } else {
        showToast('تم تجاوز الحد المسموح من الأسئلة', 'error');
      }
    }
    return;
  }

  // ✅ PREPARE: User message for immediate display
  const currentMessage = inputMessage;
  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage,
    timestamp: new Date().toISOString()
  };

  setMessages(prev => [...prev, userMessage]);
  setInputMessage('');
  setIsLoading(true);
  incrementQuestionUsage();

  // ✅ UNIFIED: Use chatAPI for both guests and auth users
  const guestSessionId = isGuest ?
    `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` :
    undefined;

  console.log('📤 Sending message:', {
    isGuest,
    conversationId: selectedConversation,
    sessionId: guestSessionId
  });

  try {
    // 🔥 Create assistant message for real-time streaming updates
    const assistantMessageId = (Date.now() + 1).toString();
    let streamingContent = '';

    // Add empty assistant message that will be updated in real-time
    setMessages(prev => [...prev, {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    }]);

    // 🚀 REAL STREAMING with conversation memory
    await chatAPI.sendMessageStreaming(
      currentMessage,
      selectedConversation || undefined,
      guestSessionId,
      
            // 📡 Real-time streaming callback
      (chunk: string) => {
        streamingContent += chunk;
        
        // Update the assistant message in real-time with RAW content
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: streamingContent }  // ← FIX: No formatting during streaming
            : msg
        ));
      },

      // ✅ Completion handler
      (response: any) => {
        console.log('📥 Received response:', { contentLength: response.fullResponse?.length || 0 });
        
        // Update final message with complete data and SINGLE formatting pass
        const finalContent = response.ai_message?.content || streamingContent;
        console.log('🚨 DEBUGGING ChatApp: finalContent received:', finalContent);
        console.log('🚨 DEBUGGING ChatApp: finalContent type:', typeof finalContent);
        console.log('🚨 DEBUGGING ChatApp: finalContent length:', finalContent?.length);
        
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
          ? {
              ...msg,
              id: response.ai_message?.id || assistantMessageId,
              content: finalContent, // ← Raw content - FormattedMessage will handle formatting
              timestamp: response.ai_message?.timestamp || new Date().toISOString()
            }
          : msg
        ));

        // 🔄 Handle conversation and user data updates with URL synchronization
        if (response.conversation_id && !selectedConversation) {
          setSelectedConversation(response.conversation_id);
          // 🎯 SENIOR-LEVEL URL SYNC: Navigate to new conversation URL
          navigateToConversation(response.conversation_id);
        }

        if (response.updated_user && !isGuest) {
          updateUserData({
            id: response.updated_user.id,
            email: response.updated_user.email,
            full_name: response.updated_user.full_name,
            questions_used_current_cycle: response.updated_user.questions_used_current_cycle,
            cycle_reset_time: response.updated_user.cycle_reset_time,
            subscription_tier: response.updated_user.subscription_tier,
            is_active: response.updated_user.is_active,
            is_verified: response.updated_user.is_verified
          });
        }

        if (!isGuest) {
          loadConversations();
          // 🔄 Refresh user data to ensure accurate question counters
          refreshUserData();
        }

        console.log('✅ Message processed successfully');
      },
      
      // ❌ Error handler
      (error: string) => {
        console.error('❌ Streaming failed:', error);
        
        // Remove the assistant message on streaming error
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
        showToast('حدث خطأ في الإرسال. حاول مرة أخرى.', 'error');
      }
    );

  } catch (error: any) {
    console.error('❌ Chat API failed:', error);
    
    // Remove user message on complete failure
    setMessages(prev => prev.slice(0, -2)); // Remove both user and assistant messages
    
    if (error.response?.status === 429) {
      showToast('تم تجاوز الحد المسموح من الأسئلة', 'error');
    } else {
      showToast('حدث خطأ في الإرسال. حاول مرة أخرى.', 'error');
    }
  } finally {
    setIsLoading(false);
  }
};
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

 const suggestedQuestions = [
  'ما هي إجراءات تأسيس شركة تجارية؟',
  'حقوق الموظف عند إنهاء الخدمة',
  'ما هي عقوبات التهرب الضريبي؟',
  'ما هي حقوق المستهلك في السعودية؟',
];
  const LegalLoadingIndicator: React.FC = () => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  
  const loadingMessages = [
    { icon: "⚖️", title: "جاري تحليل القضية القانونية", subtitle: "فهم وتحليل السؤال المطروح..." },
    { icon: "📚", title: "البحث في الأنظمة السعودية", subtitle: "مراجعة القوانين واللوائح ذات الصلة..." },
    { icon: "🔍", title: "تحليل السوابق القضائية", subtitle: "البحث في الأحكام والقرارات السابقة..." },
    { icon: "📋", title: "مراجعة المواد القانونية", subtitle: "فحص النصوص النظامية المعمول بها..." },
    { icon: "⚡", title: "تجميع الاستشارة القانونية", subtitle: "إعداد الرد المفصل والشامل..." },
    { icon: "✨", title: "التحقق من دقة المعلومات", subtitle: "مراجعة نهائية للاستشارة المقدمة..." },
    { icon: "📄", title: "تنسيق الاستجابة النهائية", subtitle: "إعداد النص بالتنسيق المناسب..." }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 4000); // Change every 4 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  const currentMessage = loadingMessages[currentMessageIndex];
  
  return (
    <div 
      key={currentMessageIndex} // This forces re-render for animation
      style={{
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        borderRadius: '16px 16px 16px 4px',
        padding: '20px 24px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
        border: '1px solid #cbd5e0',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        minWidth: '350px',
        animation: 'fadeInScale 0.5s ease-out',
        transform: 'scale(1)',
        opacity: 1
      }}
    >
      <div style={{
        display: 'flex',
        gap: '4px'
      }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#10a37f',
          animation: 'pulse 1.8s infinite'
        }}></div>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#059669',
          animation: 'pulse 1.8s infinite 0.3s'
        }}></div>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#047857',
          animation: 'pulse 1.8s infinite 0.6s'
        }}></div>
      </div>
      <div style={{ direction: 'rtl', flex: 1 }}>
        <div style={{
          color: '#2d3748',
          fontSize: '20px',
          fontWeight: '600',
          marginBottom: '4px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ fontSize: '24px' }}>{currentMessage.icon}</span>
          {currentMessage.title}
        </div>
        <div style={{
          color: '#718096',
          fontSize: '16px'
        }}>{currentMessage.subtitle}</div>
      </div>
      
      {/* Progress indicator */}
      <div style={{
        width: '40px',
        height: '4px',
        background: '#e2e8f0',
        borderRadius: '2px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <div style={{
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, #10a37f, #059669)',
          borderRadius: '2px',
          animation: 'progressBar 4s linear infinite'
        }}></div>
      </div>
    </div>
  );
};
  return (
    <>
      <style>{`

      @keyframes subtlePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.02);
    opacity: 0.95;
  }
}

@keyframes luxuryPulse {
  0%, 100% {
    border-color: rgba(0, 108, 53, 0.1);
    box-shadow: 0 8px 32px rgba(0, 108, 53, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    border-color: rgba(0, 108, 53, 0.3);
    box-shadow: 0 12px 40px rgba(0, 108, 53, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
}
      @keyframes inputPulse {
  0%, 100% {
    border-color: #e5e7eb;
    box-shadow: none;
  }
  50% {
    border-color: #10a37f;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
  }
}
        @keyframes slideInToast {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slideOutToast {
          from {
            opacity: 1;
            transform: translateX(0);
          }
          to {
            opacity: 0;
            transform: translateX(100%);
          }
        }
        
        @keyframes fadeInScale {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .message-enter {
          animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .loading-dots {
          animation: pulse 1.5s infinite;
        }
        
        .suggested-card {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          transform: translateY(0);
        }
        
        .suggested-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }
        
        /* Sidebar specific scrollbar styling */
        .sidebar-scroll::-webkit-scrollbar {
          width: 8px;
        }
        
        .sidebar-scroll::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
        }
        
        .sidebar-scroll::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
          transition: background 0.2s ease;
        }
        
        .sidebar-scroll::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        
        /* Firefox scrollbar for sidebar */
        .sidebar-scroll {
          scrollbar-width: thin;
          scrollbar-color: rgba(255, 255, 255, 0.2) rgba(255, 255, 255, 0.05);
        }
        
        /* =====================================================================
         * SENIOR-LEVEL HEIGHT CONSTRAINT ARCHITECTURE
         * Advanced CSS Layout System for Proper Scroll Containment
         * ===================================================================== */
        
        /* 1. VIEWPORT HEIGHT LOCKING SYSTEM */
        :root {
          --viewport-height: 100vh;
          --safe-area-bottom: env(safe-area-inset-bottom, 0px);
          --dynamic-viewport-height: 100dvh; /* Modern browsers */
          --stable-viewport-height: calc(100vh - var(--safe-area-bottom));
        }
        
        /* Support for dynamic viewport units with fallback */
        @supports (height: 100dvh) {
          :root {
            --viewport-height: 100dvh;
          }
        }
        
        /* 2. GRID CONTAINER HEIGHT PROPAGATION */
        .chat-grid-container {
          /* CRITICAL: Always constrained height, NEVER auto */
          height: var(--viewport-height) !important;
          min-height: var(--viewport-height) !important;
          max-height: var(--viewport-height) !important;
          /* Prevent content overflow breaking constraints */
          overflow: hidden !important;
          /* Establish proper stacking context */
          contain: layout style !important;
          /* Ensure no flex/grid conflicts */
          box-sizing: border-box !important;
        }
        
        /* 3. MOBILE VIEWPORT COMPATIBILITY LAYER */
        @media (max-width: 768px) {
          .chat-grid-container {
            /* Advanced mobile viewport handling */
            height: calc(100vh - var(--safe-area-bottom)) !important;
            height: var(--dynamic-viewport-height) !important;
            min-height: calc(100vh - var(--safe-area-bottom)) !important;
            min-height: var(--dynamic-viewport-height) !important;
            /* Prevent mobile address bar issues */
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            /* Mobile optimization */
            -webkit-overflow-scrolling: touch !important;
            overscroll-behavior: contain !important;
          }
        }
        
        /* 4. SIDEBAR HEIGHT CASCADE SYSTEM */
        .sidebar-container {
          /* Must inherit constrained height from grid */
          height: 100% !important;
          min-height: 100% !important;
          max-height: 100% !important;
          /* Establish flex context with height constraints */
          display: flex !important;
          flex-direction: column !important;
          /* Prevent content overflow */
          overflow: hidden !important;
          /* Create isolation boundary */
          contain: layout style !important;
        }
        
        /* 5. FLEX HEIGHT PROPAGATION LAYER */
        .sidebar-header {
          /* Fixed height sections */
          flex: none !important;
          flex-shrink: 0 !important;
        }
        
        .sidebar-scroll-container {
          /* CRITICAL: This creates the scroll boundary */
          flex: 1 !important;
          min-height: 0 !important; /* Allow flex shrinking */
          height: 0 !important; /* Force constraint respect */
          /* Establish scroll context */
          overflow: hidden !important;
          contain: layout style !important;
          /* Create isolated scroll area */
          position: relative !important;
        }
        
        .sidebar-scroll {
          /* ISOLATED SCROLL IMPLEMENTATION */
          position: absolute !important;
          top: 0 !important;
          left: 0 !important;
          right: 0 !important;
          bottom: 0 !important;
          /* Enable scrolling in constrained space */
          overflow-y: auto !important;
          overflow-x: hidden !important;
          /* Performance optimizations */
          -webkit-overflow-scrolling: touch !important;
          overscroll-behavior: contain !important;
          /* Scroll behavior */
          scroll-behavior: smooth !important;
          /* Content padding */
          padding: 16px !important;
          box-sizing: border-box !important;
        }
        
        .sidebar-footer {
          /* Fixed height sections */
          flex: none !important;
          flex-shrink: 0 !important;
        }
        
        /* 6. MAIN CHAT AREA HEIGHT SYSTEM */
        .main-chat-container {
          height: 100% !important;
          min-height: 100% !important;
          max-height: 100% !important;
          display: flex !important;
          flex-direction: column !important;
          overflow: hidden !important;
          contain: layout style !important;
        }
        
        .messages-container {
          flex: 1 !important;
          min-height: 0 !important;
          overflow-y: auto !important;
          -webkit-overflow-scrolling: touch !important;
          overscroll-behavior: contain !important;
        }
        
        .input-container {
          flex: none !important;
          flex-shrink: 0 !important;
        }
        
        /* 7. MOBILE SIDEBAR OVERLAY SYSTEM */
        @media (max-width: 768px) {
          .sidebar-container.mobile {
            /* Full viewport overlay */
            position: fixed !important;
            top: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 320px !important;
            height: 100vh !important;
            height: var(--dynamic-viewport-height) !important;
            z-index: 50 !important;
            /* Prevent parent constraints affecting overlay */
            transform: none !important;
          }
        }
        
        /* 8. ADVANCED SCROLLBAR ARCHITECTURE */
        .sidebar-scroll::-webkit-scrollbar {
          width: 8px;
        }
        
        .sidebar-scroll::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
        }
        
        .sidebar-scroll::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
          transition: background 0.2s ease;
        }
        
        .sidebar-scroll::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        
        /* 9. CLEAN PERFORMANCE ARCHITECTURE */
        .messages-container {
          /* Only enable GPU acceleration where needed */
          will-change: scroll-position;
          -webkit-overflow-scrolling: touch;
        }
        
        /* 10. MODERN TOUCH EVENT ARCHITECTURE */
        .mobile-backdrop {
          /* Ensure backdrop captures all touches */
          touch-action: none !important;
          pointer-events: auto !important;
          /* Prevent touch interference */
          -webkit-touch-callout: none !important;
          user-select: none !important;
        }
        
        .sidebar-container {
          /* Allow only vertical scrolling touches */
          touch-action: pan-y !important;
          /* Ensure sidebar captures touches */
          pointer-events: auto !important;
          /* Remove GPU conflicts */
          will-change: auto !important;
          transform: none !important;
          backface-visibility: visible !important;
        }
        
        .sidebar-scroll {
          /* Precise touch control for scroll area */
          touch-action: pan-y !important;
          /* Remove containment conflicts */
          contain: none !important;
          /* Ensure proper touch targeting */
          pointer-events: auto !important;
          /* Remove transform conflicts */
          transform: none !important;
          will-change: scroll-position !important;
        }
        
        .sidebar-container.mobile {
          /* Mobile-specific touch fixes */
          position: fixed !important;
          top: 0 !important;
          right: 0 !important;
          bottom: 0 !important;
          width: 320px !important;
          /* Critical: Higher z-index than backdrop */
          z-index: 50 !important;
          /* Ensure touch capture */
          pointer-events: auto !important;
          /* Remove transform conflicts */
          transform: none !important;
        }
        
        /* 11. Z-INDEX STACKING ARCHITECTURE */
        .mobile-backdrop {
          z-index: 40 !important;
        }
        
        .sidebar-container.mobile {
          z-index: 50 !important;
        }
        
        .sidebar-scroll {
          z-index: 51 !important;
        }
        
        /* 12. REMOVE ALL GPU ACCELERATION CONFLICTS */
        .chat-grid-container,
        .sidebar-container,
        .main-chat-container {
          /* Remove problematic GPU acceleration */
          will-change: auto !important;
          backface-visibility: visible !important;
          transform: none !important;
        }
        
        /* 13. FALLBACK COMPATIBILITY */
        @supports not (height: 100dvh) {
          .chat-grid-container {
            height: 100vh !important;
          }
        }
      `}</style>
      
<div 
  className="chat-grid-container"
  style={{
  display: 'grid',
  gridTemplateColumns: isMobile 
    ? (sidebarOpen ? '320px 1fr' : '1fr')
    : sidebarOpen 
      ? '320px 1fr' 
      : '1fr',
  gridTemplateAreas: isMobile 
    ? (sidebarOpen ? '"sidebar main"' : '"main"')
    : sidebarOpen 
      ? '"sidebar main"'
      : '"main"',
  // 🏗️ SENIOR-LEVEL: ALWAYS CONSTRAINED HEIGHT (CSS classes override inline)
  fontFamily: "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  background: 'var(--background-light)',
  direction: 'rtl'
  // ⚠️ REMOVED: All height/overflow props - handled by CSS classes
}}>
        
        {/* Mobile Backdrop */}
       {/* Mobile Backdrop */}
{isMobile && sidebarOpen && (
  <div 
    className="mobile-backdrop"
    style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      zIndex: 40,
      backdropFilter: 'blur(4px)'
    }}
    data-touch-zone="backdrop"
    onClick={() => setSidebarOpen(false)}
  />
)}

        {/* Sidebar */}
        {/* Sidebar Toggle Button */}
{!sidebarOpen && (
  <button
    onClick={() => setSidebarOpen(true)}
    style={{
      position: 'fixed',
      top: '24px',
      right: '24px',
      zIndex: 100,
      background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.95) 0%, rgba(0, 74, 36, 0.9) 50%, rgba(0, 108, 53, 0.85) 100%)',
      color: 'white',
      border: '1px solid rgba(255, 255, 255, 0.15)',
      borderRadius: '16px',
      padding: '14px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      boxShadow: '0 8px 32px rgba(0, 108, 53, 0.25), 0 4px 16px rgba(0, 108, 53, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)',
      width: '48px',
      height: '48px'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 1) 0%, rgba(0, 74, 36, 0.95) 50%, rgba(0, 108, 53, 0.9) 100%)';
      e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
      e.currentTarget.style.boxShadow = '0 12px 48px rgba(0, 108, 53, 0.35), 0 8px 24px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.95) 0%, rgba(0, 74, 36, 0.9) 50%, rgba(0, 108, 53, 0.85) 100%)';
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25), 0 4px 16px rgba(0, 108, 53, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
    }}
  >
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="3" y1="6" x2="21" y2="6"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
      <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  </button>
)}

{/* Sidebar */}
<div 
  className={`sidebar-container ${isMobile ? 'mobile' : ''}`}
  style={{
    gridArea: 'sidebar',
    // 🏗️ SENIOR-LEVEL: Position handled by CSS classes
    background: '#171717',
    display: sidebarOpen ? 'flex' : 'none',
    borderLeft: '1px solid #363739',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: isMobile ? 50 : 'auto',
    boxShadow: isMobile ? '0 10px 25px rgba(0, 0, 0, 0.15)' : 'none'
    // ⚠️ REMOVED: All height/position props - handled by CSS classes
  }}
  data-touch-zone="sidebar"
>
          {/* Sidebar Header - Clean & Spaced */}
<div className="sidebar-header" style={{
  padding: '20px',
  borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  minHeight: '80px'
}}>
  <h2 style={{
    color: 'rgba(255, 255, 255, 0.95)',
    fontSize: '20px',
    fontWeight: '600',
    margin: 0,
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
    letterSpacing: '-0.01em'
  }}>
    المحادثات
  </h2>
  
  {/* Theme and close buttons */}
  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
    {/* Theme toggle */}
    <button
      onClick={toggleTheme}
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        color: 'rgba(142, 142, 160, 0.8)',
        cursor: 'pointer',
        padding: '8px',
        borderRadius: '8px',
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        width: '36px',
        height: '36px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backdropFilter: 'blur(10px)'
      }}
      title={isDark ? 'تبديل للوضع الفاتح' : 'تبديل للوضع المظلم'}
    >
      {isDark ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      )}
    </button>
    
    {/* Close button */}
    <button
    onClick={() => setSidebarOpen(false)}
    style={{
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      color: 'rgba(142, 142, 160, 0.8)',
      cursor: 'pointer',
      padding: '8px',
      borderRadius: '8px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      width: '36px',
      height: '36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backdropFilter: 'blur(10px)'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)';
      e.currentTarget.style.color = '#EF4444';
      e.currentTarget.style.borderColor = 'rgba(220, 38, 38, 0.2)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
      e.currentTarget.style.color = 'rgba(142, 142, 160, 0.8)';
      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }}
  >
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  </button>
  </div>
</div>

          {/* New Chat Button */}
          <div className="sidebar-header" style={{ padding: '16px' }}>
            <button
              onClick={startNewConversation}
              style={{
                width: '100%',
                background: 'transparent',
                border: '1px solid #565869',
                color: 'white',
                borderRadius: '8px',
                padding: '12px 16px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: 'translateY(0)',
                minHeight: '44px'
              }}
              onMouseOver={(e) => {
                (e.target as HTMLElement).style.background = '#2d2d30';
                (e.target as HTMLElement).style.transform = 'translateY(-1px)';
                (e.target as HTMLElement).style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
              }}
              onMouseOut={(e) => {
                (e.target as HTMLElement).style.background = 'transparent';
                (e.target as HTMLElement).style.transform = 'translateY(0)';
                (e.target as HTMLElement).style.boxShadow = 'none';
              }}
            >
              <span style={{ fontSize: '16px' }}>+</span>
              محادثة جديدة
            </button>
          </div>

          {/* Section Divider */}
          <div className="sidebar-header" style={{
            height: '1px',
            background: 'rgba(255, 255, 255, 0.1)',
            margin: '0 16px',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              background: '#171717',
              padding: '0 12px',
              color: 'rgba(255, 255, 255, 0.5)',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              ————
            </div>
          </div>

          {/* 🏗️ SENIOR-LEVEL: ISOLATED SCROLL CONTAINER ARCHITECTURE */}
          <div className="sidebar-scroll-container">
            <div className="sidebar-scroll">
            {loadingConversations ? (
              <div style={{ 
                color: '#8e8ea0', 
                textAlign: 'center', 
                padding: '20px',
                fontSize: '16px'
              }}>
                جاري تحميل المحادثات...
              </div>
            ) : conversations.length === 0 ? (
              <div style={{ 
                color: '#8e8ea0', 
                textAlign: 'center', 
                padding: '20px',
                fontSize: '16px'
              }}>
                لا توجد محادثات سابقة
              </div>
            ) : (
              conversations.map((conv, index) => (
  <div key={`conversation-${conv.id}`}>
  <div
    key={conv.id}
    style={{
      padding: '12px 16px',
      margin: '8px 0',
      borderRadius: '8px',
      background: selectedConversation === conv.id ? '#2d2d30' : 'transparent',
      color: 'white',
      fontSize: '16px',
      lineHeight: '1.4',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      border: selectedConversation === conv.id ? '1px solid #4f4f4f' : '1px solid transparent',
      minHeight: '44px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      position: 'relative',
    }}
    onMouseEnter={(e) => {
      if (selectedConversation !== conv.id) {
        e.currentTarget.style.background = '#2d2d30';
      }
      // Show action buttons on hover
      const actionsDiv = e.currentTarget.querySelector('.conversation-actions') as HTMLElement;
      if (actionsDiv) actionsDiv.style.opacity = '1';
    }}
    onMouseLeave={(e) => {
      if (selectedConversation !== conv.id) {
        e.currentTarget.style.background = 'transparent';
      }
      // Hide action buttons
      const actionsDiv = e.currentTarget.querySelector('.conversation-actions') as HTMLElement;
      if (actionsDiv) actionsDiv.style.opacity = '0';
    }}
  >
    {/* Main content - clickable to load conversation */}
    <div
      onClick={() => navigateToConversation(conv.id)}
      style={{ cursor: 'pointer', flex: 1 }}
    >
      <div style={{
        fontWeight: '500',
        marginBottom: '4px',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }}>
        {conv.title}
      </div>
      <div style={{
        fontSize: '16px',
        color: '#8e8ea0',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }}>
        {conv.last_message_preview || `${conv.message_count} رسالة`}
      </div>
    </div>

    {/* Premium action buttons - show on hover */}
<div 
  className="conversation-actions"
  style={{
    position: 'absolute',
    top: '6px',
    left: '6px',
    display: 'flex',
    gap: '6px',
    opacity: '0',
    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
  }}
>
  {/* Premium Rename button */}
  <button
    onClick={(e) => {
      e.stopPropagation();
      handleRenameConversation(conv.id, conv.title);
    }}
    style={{
      background: 'linear-gradient(135deg, rgba(0, 108, 53, 0.9) 0%, rgba(0, 74, 36, 0.9) 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '6px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '28px',
      height: '28px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 2px 8px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}
    title="تعديل الاسم"
    onMouseOver={(e) => {
      e.currentTarget.style.transform = 'translateY(-1px) scale(1.05)';
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 168, 82, 0.9) 0%, rgba(0, 108, 53, 0.9) 100%)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 108, 53, 0.9) 0%, rgba(0, 74, 36, 0.9) 100%)';
    }}
  >
    {/* Premium edit icon */}
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  </button>

  {/* Premium Delete button */}
  <button
    onClick={(e) => {
      e.stopPropagation();
      handleDeleteConversation(conv.id, conv.title);
    }}
    style={{
      background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '6px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '28px',
      height: '28px',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 2px 8px rgba(220, 38, 38, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}
    title="حذف المحادثة"
    onMouseOver={(e) => {
      e.currentTarget.style.transform = 'translateY(-1px) scale(1.05)';
      e.currentTarget.style.boxShadow = '0 4px 16px rgba(220, 38, 38, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.9) 100%)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.transform = 'translateY(0) scale(1)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(220, 38, 38, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%)';
    }}
  >
    {/* Premium delete icon */}
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
      <polyline points="3,6 5,6 21,6"/>
      <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
      <line x1="10" y1="11" x2="10" y2="17"/>
      <line x1="14" y1="11" x2="14" y2="17"/>
    </svg>
  </button>
</div>
  </div>
  </div>
)))}
            </div>
          </div>

          {/* Section Divider before User Info */}
          <div className="sidebar-footer" style={{
            height: '1px',
            background: 'rgba(255, 255, 255, 0.1)',
            margin: '16px 16px 0 16px',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              background: '#171717',
              padding: '0 12px',
              color: 'rgba(255, 255, 255, 0.5)',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              ————
            </div>
          </div>

          {/* User Info - Premium Clean Design */}
<div className="sidebar-footer" style={{
  padding: '24px 20px',
  borderTop: '1px solid rgba(255, 255, 255, 0.08)',
  background: 'linear-gradient(180deg, rgba(23, 23, 23, 0.8) 0%, rgba(23, 23, 23, 1) 100%)'
}}>
  {isGuest ? (
    // Ultra Premium Guest Section
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      gap: '20px'
    }}>
      {/* Premium User Avatar & Info */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: `
            linear-gradient(135deg, 
              rgba(107, 114, 128, 0.9) 0%, 
              rgba(75, 85, 99, 0.9) 100%
            )
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `,
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ opacity: 0.9 }}>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            color: 'rgba(255, 255, 255, 0.95)', 
            fontWeight: '600', 
            fontSize: '17px',
            marginBottom: '4px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
            letterSpacing: '-0.01em'
          }}>
            مستخدم ضيف
          </div>
          <div style={{ 
            color: 'rgba(142, 142, 160, 0.8)', 
            fontSize: '13px',
            fontWeight: '500',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif'
          }}>
            تجربة محدودة • ترقى للمزيد
          </div>
        </div>
      </div>
      
      {/* Premium Progress Indicators with Glass Effect */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        padding: '16px',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)'
      }}>
        <PremiumProgress
          current={cooldownInfo.questionsUsed}
          max={cooldownInfo.maxQuestions
}
          label="الرسائل المجانية"
          type="messages"
        />
        
        <PremiumProgress
  current={cooldownInfo.questionsUsed}
  max={cooldownInfo.maxQuestions}
  label="الأسئلة المستخدمة"
  type="messages"
/>
      </div>
      
      {/* Ultra Premium Upgrade Button */}
      <button
        onClick={() => {
          console.log('🚀 Navigating to auth page...');
          window.history.pushState({}, '', '/auth');
          window.dispatchEvent(new PopStateEvent('popstate'));
        }}
        style={{
          width: '100%',
          background: `
            linear-gradient(135deg, 
              #006C35 0%, 
              #004A24 50%,
              #002D16 100%
            )
          `,
          color: 'white',
          border: 'none',
          borderRadius: '16px',
          padding: '16px 24px',
          cursor: 'pointer',
          fontSize: '15px',
          fontWeight: '600',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: `
            0 8px 32px rgba(0, 108, 53, 0.4),
            0 4px 16px rgba(0, 108, 53, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          letterSpacing: '-0.01em',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = `
            linear-gradient(135deg, 
              #00A852 0%, 
              #006C35 50%,
              #004A24 100%
            )
          `;
          e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
          e.currentTarget.style.boxShadow = `
            0 12px 48px rgba(0, 168, 82, 0.5),
            0 8px 24px rgba(0, 108, 53, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
          `;
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = `
            linear-gradient(135deg, 
              #006C35 0%, 
              #004A24 50%,
              #002D16 100%
            )
          `;
          e.currentTarget.style.transform = 'translateY(0) scale(1)';
          e.currentTarget.style.boxShadow = `
            0 8px 32px rgba(0, 108, 53, 0.4),
            0 4px 16px rgba(0, 108, 53, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1)
          `;
        }}
      >
        {/* Premium shine effect */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
          animation: 'shimmer 3s ease-in-out infinite'
        }} />
        
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ position: 'relative', zIndex: 1 }}>
          <path d="M12 2L15.09 8.26L22 9L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9L8.91 8.26L12 2Z"/>
        </svg>
        
        <span style={{ position: 'relative', zIndex: 1 }}>ترقية للحساب المميز</span>
      </button>
    </div>
  ) : (
    // Ultra Premium Authenticated User Section
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      gap: '20px'
    }}>
      {/* Premium User Avatar & Info */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: `
            linear-gradient(135deg, 
              #10a37f 0%, 
              #047857 100%
            )
          `,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `
            0 8px 32px rgba(16, 163, 127, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
          `,
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" style={{ opacity: 0.9 }}>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            color: 'rgba(255, 255, 255, 0.95)', 
            fontWeight: '600', 
            fontSize: '17px',
            marginBottom: '4px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
            letterSpacing: '-0.01em'
          }}>
            {user?.full_name}
          </div>
          <div style={{ 
            color: '#10a37f', 
            fontSize: '13px', 
            fontWeight: '600',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
            letterSpacing: '0.5px',
            textTransform: 'uppercase'
          }}>
            حساب مميز
          </div>
        </div>
      </div>

      {/* Premium Usage Stats */}
      <div style={{ 
        padding: '16px 20px',
        background: `
          linear-gradient(135deg, 
            rgba(16, 163, 127, 0.1) 0%, 
            rgba(5, 150, 105, 0.05) 100%
          )
        `,
        borderRadius: '16px',
        border: '1px solid rgba(16, 163, 127, 0.2)',
        backdropFilter: 'blur(20px)'
      }}>
        <div style={{ 
          fontSize: '13px', 
          color: 'rgba(142, 142, 160, 0.8)', 
          marginBottom: '8px',
          fontWeight: '500',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          الاستخدام الشهري
        </div>
        <div style={{ 
              color: '#10a37f', 
              fontWeight: '700',
              fontSize: '20px',
              fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
              letterSpacing: '-0.02em'
            }}>
              {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)} / {cooldownInfo.maxQuestions}
            </div>
        <div style={{
          fontSize: '12px',
          color: 'rgba(16, 163, 127, 0.7)',
          marginTop: '4px',
          fontWeight: '500'
        }}>
          أسئلة متبقية
        </div>
      </div>

      {/* Premium Logout Button */}
      <button
        onClick={logout}
        style={{
          width: '100%',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'rgba(142, 142, 160, 0.9)',
          borderRadius: '12px',
          padding: '14px 20px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          backdropFilter: 'blur(10px)'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)';
          e.currentTarget.style.color = '#EF4444';
          e.currentTarget.style.borderColor = 'rgba(220, 38, 38, 0.2)';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
          e.currentTarget.style.color = 'rgba(142, 142, 160, 0.9)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16,17 21,12 16,7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        تسجيل الخروج
      </button>
    </div>
  )}
</div> 
        </div>

        {/* Main Chat Area */}
        <div className="main-chat-container" style={{
  gridArea: 'main',
  background: 'var(--background-white)',
  position: 'relative'
  // 🏗️ SENIOR-LEVEL: All height/overflow handled by CSS classes
}}>

          {/* Messages Area */}
          <div 
  className="messages-container"
  style={{
    padding: '24px 0'
    // 🏗️ SENIOR-LEVEL: All scroll properties handled by CSS classes
  }}
>
            {messages.length === 0 ? (
              // Welcome Screen
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                padding: '0 24px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '64px',
                  marginBottom: '24px'
                }}></div>
                <h2 style={{
                  fontSize: 'clamp(50px, 4vw, 26px)',
                  fontWeight: '600',
                  color: isDark ? '#f9fafb' : '#1f2937',
                  marginBottom: '16px'
                }}>
                  اهلا بك في حكم
                </h2>
                <p style={{
                  fontSize: 'clamp(24px, 2vw, 16px)',
                  color: isDark ? '#d1d5db' : '#4b5563',
                  marginBottom: '32px',
                  maxWidth: '600px',
                  lineHeight: '1.6'
                }}>
                  احصل على استشارات قانونية دقيقة ومفصلة مبنية على القانون السعودي باستخدام تقنيات الذكاء الاصطناعي المتقدمة
                </p>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '16px',
                  width: '100%',
                  maxWidth: '800px'
                }}>
                  {suggestedQuestions.map((question, index) => (
                    <div
                      key={index}
                      className="suggested-card"
                      style={{
                        background: 'var(--background-white)',
                        border: isDark 
                          ? '1px solid rgba(75, 85, 99, 0.3)' 
                          : '1px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '20px',
                        cursor: 'pointer',
                        textAlign: 'right',
                        boxShadow: isDark 
                          ? '0 2px 4px rgba(0, 0, 0, 0.2)' 
                          : '0 2px 4px rgba(0, 0, 0, 0.05)',
                        animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s both`
                      }}
                      onClick={() => handleSuggestedQuestion(question)}
                      onMouseOver={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#10a37f';
                        (e.currentTarget as HTMLElement).style.boxShadow = isDark 
                          ? '0 4px 12px rgba(16, 163, 127, 0.3)' 
                          : '0 4px 12px rgba(16, 163, 127, 0.15)';
                      }}
                      onMouseOut={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = isDark 
                          ? 'rgba(75, 85, 99, 0.3)' 
                          : '#e5e7eb';
                        (e.currentTarget as HTMLElement).style.boxShadow = isDark 
                          ? '0 2px 4px rgba(0, 0, 0, 0.2)' 
                          : '0 2px 4px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      <div style={{
                        fontSize: '22px',
                        color: isDark ? '#f9fafb' : '#374151',
                        fontWeight: '500',
                        lineHeight: '1.5'
                      }}>
                        {question}
                      </div>
                      <div style={{
  fontSize: '14px',
  color: '#9ca3af',
  marginTop: '8px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  gap: '6px',
  fontWeight: '500'
}}>
  اضغط للسؤال
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/>
  </svg>
</div><div style={{
                        fontSize: '22px',
                        color: '#374151',
                        fontWeight: '500',
                        lineHeight: '1.5'
                      }}>
                        
                      </div>
                    </div>
                    
                  ))}

                  
                </div>
              </div>
            ) : (
              // Messages
              <div 
  className="chat-messages-container"
  style={{
    // 🔧 MOBILE FIX: Different calculations for mobile  
    maxWidth: isMobile ? '100%' : '100%',
    padding: isMobile ? '0 1rem' : '0 2rem'
  }}
>
                {messages.map((message, index) => (
                 <div
  key={message.id}
  className="message-enter"
  style={{
    display: 'flex',
    flexDirection: 'row',
    justifyContent: isMobile 
  ? (message.role === 'user' ? 'flex-end' : 'center') 
  : (message.role === 'user' ? 'flex-end' : 'center'),
    marginBottom: '24px',
    animationDelay: `${index * 0.1}s`
  }}
>

  <div
  className={message.role === 'user' ? 'user-message-enhanced' : ''}
  style={{
    maxWidth: message.role === 'user' 
      ? (isMobile ? '75%' : '60%')
      : '90%',
    minWidth: message.role === 'user' ? '200px' : 'auto',
    background: message.role === 'user' 
      ? `linear-gradient(135deg, 
          rgba(0, 108, 53, 0.95) 0%, 
          rgba(0, 74, 36, 0.9) 50%,
          rgba(0, 108, 53, 0.85) 100%
        )` 
      : 'transparent',
    color: message.role === 'user' ? 'white' : '#2d333a',
    borderRadius: message.role === 'user' ? '20px 20px 4px 16px' : '0',
    padding: message.role === 'user' ? '18px 22px' : '0',
    boxShadow: message.role === 'user' 
      ? `0 8px 32px rgba(0, 108, 53, 0.25),
         0 4px 16px rgba(0, 108, 53, 0.15),
         inset 0 1px 0 rgba(255, 255, 255, 0.1),
         0 0 0 1px rgba(255, 255, 255, 0.05)` 
      : 'none',
    border: message.role === 'user' ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
    backdropFilter: message.role === 'user' ? 'blur(20px)' : 'none',
    fontSize: message.role === 'user' ? '25px' : '25px',
    lineHeight: '1.5',
    textAlign: 'right',
    marginLeft: message.role === 'user' ? 'auto' : '0%',
    marginRight: message.role === 'user' ? '3cm' : '0',
    wordBreak: 'break-word',
    overflowWrap: 'break-word',
    whiteSpace: 'normal',
    hyphens: 'auto',
    position: 'relative',
    overflow: 'hidden'
  }}
>
                      <FormattedMessage
  content={message.content}
  role={message.role}
  sidebarOpen={sidebarOpen}
  isLastMessage={index === messages.length - 1}
  messages={messages}
  conversations={conversations}
  selectedConversation={selectedConversation}
  isDark={isDark}
/>
                      <div style={{
                        fontSize: '18px',
                        opacity: 0.7,
                        marginTop: '8px',
                        textAlign: message.role === 'user' ? 'right' : 'left'
                      }}>
                        {new Date(message.timestamp).toLocaleTimeString('ar-SA', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Dynamic Legal Analysis Loading indicator */}
{isLoading && (
  <div style={{
    display: 'flex',
    justifyContent: 'flex-start',
    marginBottom: '16px',
    marginTop: '50px',  // ← Add this to push it down
  }}>
    <LegalLoadingIndicator />
  </div>
)}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
<div className="input-container" style={{
  padding: '32px 24px',
  background: isDark 
    ? 'linear-gradient(135deg, rgba(31, 41, 55, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%)'
    : 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)',
  borderTop: isDark 
    ? '1px solid rgba(55, 65, 81, 0.3)'
    : '1px solid rgba(0, 108, 53, 0.1)',
  position: 'relative',
  display: 'flex',
  justifyContent: 'center',
  backdropFilter: 'blur(20px)',
  boxShadow: isDark
    ? 'inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 -4px 32px rgba(0, 0, 0, 0.2)'
    : 'inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 -4px 32px rgba(0, 108, 53, 0.05)'
}}>
  <div style={{
    position: 'relative',
    maxWidth: '1200px',
    width: '100%'
  }}>
    
    <div 
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        gap: '16px',
        background: isDark
          ? 'linear-gradient(135deg, rgba(55, 65, 81, 0.8) 0%, rgba(31, 41, 55, 0.6) 100%)'
          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)',
        borderRadius: '24px',
        padding: '20px 24px',
        border: isDark
          ? '2px solid rgba(75, 85, 99, 0.3)'
          : '2px solid rgba(0, 108, 53, 0.1)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: '80px',
        backdropFilter: 'blur(20px)',
        boxShadow: isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.3),
             0 0 0 1px rgba(255, 255, 255, 0.05),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`,
        animation: inputMessage.length === 0 ? 'luxuryPulse 4s ease-in-out infinite' : 'none'
      }}
      onFocus={() => {
        // Stop animation on focus
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.borderColor = isDark 
          ? 'rgba(75, 85, 99, 0.5)' 
          : 'rgba(0, 108, 53, 0.2)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = isDark
          ? `0 12px 40px rgba(0, 0, 0, 0.4),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.15)`
          : `0 12px 40px rgba(0, 108, 53, 0.12),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.borderColor = isDark 
          ? 'rgba(75, 85, 99, 0.3)' 
          : 'rgba(0, 108, 53, 0.1)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = isDark
          ? `0 8px 32px rgba(0, 0, 0, 0.3),
             0 0 0 1px rgba(255, 255, 255, 0.05),
             inset 0 1px 0 rgba(255, 255, 255, 0.1)`
          : `0 8px 32px rgba(0, 108, 53, 0.08),
             0 0 0 1px rgba(255, 255, 255, 0.1),
             inset 0 1px 0 rgba(255, 255, 255, 0.2)`;
      }}
    >
                 <textarea
        ref={inputRef}
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="اكتب سؤالك هنا..."
        disabled={isLoading}
        style={{
          flex: 1,
          border: 'none',
          background: 'transparent',
          resize: 'none',
          outline: 'none',
          fontSize: '20px',
          lineHeight: '1.5',
          color: isDark ? '#f9fafb' : '#1f2937',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          minHeight: '48px',
          maxHeight: '150px',
          overflow: 'auto',
          padding: '0',
          fontWeight: '400',
          letterSpacing: '-0.01em'
        }}
        rows={1}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = 'auto';
          target.style.height = Math.min(target.scrollHeight, 120) + 'px';
        }}
        onFocus={(e) => {
          const container = e.target.closest('div[style*="borderRadius"]') as HTMLElement;
          if (container) {
            container.style.borderColor = '#006C35';
            container.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.8) 100%)';
          }
        }}
        onBlur={(e) => {
          const container = e.target.closest('div[style*="borderRadius"]') as HTMLElement;
          if (container) {
            container.style.borderColor = 'rgba(0, 108, 53, 0.1)';
            container.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)';
          }
        }}
      />
                
                <button
        onClick={handleSendMessage}
        disabled={!inputMessage.trim() || isLoading}
        style={{
          background: (!inputMessage.trim() || isLoading) 
            ? 'rgba(189, 189, 189, 0.3)' 
            : 'linear-gradient(135deg, #006C35 0%, #004A24 100%)',
          color: (!inputMessage.trim() || isLoading) ? '#9ca3af' : 'white',
          border: 'none',
          borderRadius: '16px',
          width: '56px',
          height: '56px',
          cursor: (!inputMessage.trim() || isLoading) ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          flexShrink: 0,
          boxShadow: (!inputMessage.trim() || isLoading) 
            ? 'none' 
            : '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          if (!(!inputMessage.trim() || isLoading)) {
            e.currentTarget.style.background = 'linear-gradient(135deg, #00A852 0%, #006C35 100%)';
            e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
          }
        }}
        onMouseOut={(e) => {
          if (!(!inputMessage.trim() || isLoading)) {
            e.currentTarget.style.background = 'linear-gradient(135deg, #006C35 0%, #004A24 100%)';
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 108, 53, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1)';
          }
        }}
      >
                  {isLoading ? (
          <div style={{
            width: '24px',
            height: '24px',
            border: '3px solid transparent',
            borderTop: '3px solid currentColor',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            opacity: 0.8
          }} />
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ opacity: 0.9 }}>
            <path d="m22 2-7 20-4-9-9-4z"/>
            <path d="M22 2 11 13"/>
          </svg>
        )}
      </button>
    </div>
              
 {/* Character count and tips */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '16px',
          fontSize: '16px',
          color: 'rgba(0, 108, 53, 0.7)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
          fontWeight: '400'
        }}>
          <div style={{ opacity: 0.8 }}>
            اضغط Enter للإرسال، Shift+Enter للسطر الجديد
          </div>
          <div style={{
            background: 'rgba(0, 108, 53, 0.1)',
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            الأسئلة المتبقية: {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)}/{cooldownInfo.maxQuestions}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<RenamePopup
  isOpen={renamePopup.isOpen}
  currentTitle={renamePopup.currentTitle}
  onSave={handleRenameSubmit}
  onCancel={handleRenameCancel}
/>

<DeletePopup
  isOpen={deletePopup.isOpen}
  conversationTitle={deletePopup.conversationTitle}
  onConfirm={handleDeleteConfirm}
  onCancel={handleDeleteCancel}
/>

{/* Additional CSS for animations */}
</>);
};
