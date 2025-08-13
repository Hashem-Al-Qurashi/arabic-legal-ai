import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { legalAPI, chatAPI } from '../../services/api';
import { formatPartialChatGPTStyle, formatChatGPTStyle } from '../../utils/chatgptFormatter';
import { enhancedStreamingFormatter, applyTwoPassFormatting } from '../../services/twoPassFormatter';
import { parseMessageContent, detectMultiAgentResponse, generateComparisonTable, containsTableStructure, cleanHtmlContent, containsCitations, stripCitations, type MessageElement, type TableData } from '../../utils/formatting';
import { showToast, formatDate } from '../../utils/notifications';
import { navigateTo } from '../../utils/navigation';
import type { Message, Conversation, ParsedElement } from '../../types/chat';
import RenamePopup from '../ui/RenamePopup';
import DeletePopup from '../ui/DeletePopup';
import PremiumProgress from '../ui/PremiumProgress';
import FeatureTease from '../ui/FeatureTease';
import FormattedMessage from './FormattedMessage';

class HTMLToReactParser {
  static parseHTML(htmlContent: string): ParsedElement[] {
    if (!htmlContent) return [];

    // Use browser's native DOMParser - most reliable
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<div>${htmlContent}</div>`, 'text/html');
    const container = doc.body.firstChild as HTMLElement;
    
    if (!container) return [];

    const elements: ParsedElement[] = [];
    
    // Process each child node
    for (const node of Array.from(container.childNodes)) {
      const parsed = this.parseNode(node);
      if (parsed) {
        elements.push(parsed);
      }
    }
    
    return elements;
  }

  private static parseNode(node: Node): ParsedElement | null {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent?.trim();
      if (text) {
        return { type: 'text', content: text };
      }
      return null;
    }
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node as HTMLElement;
      const tagName = element.tagName.toLowerCase();
      
      switch (tagName) {
        case 'h1':
        case 'h2':
        case 'h3':
        case 'h4':
        case 'h5':
        case 'h6':
          return {
            type: 'heading',
            level: parseInt(tagName.charAt(1)),
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'p':
          return {
            type: 'paragraph',
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'li':
          return {
            type: 'listItem',
            content: element.textContent || '',
            children: this.parseChildNodes(element)
          };
          
        case 'strong':
        case 'b':
          return {
            type: 'strong',
            content: element.textContent || ''
          };
          
        case 'em':
        case 'i':
          return {
            type: 'emphasis',
            content: element.textContent || ''
          };
          
        case 'br':
          return { type: 'text', content: '\n' };
          
        default:
          // For other tags, treat as paragraph with children
          const children = this.parseChildNodes(element);
          if (children.length > 0) {
            return {
              type: 'paragraph',
              content: element.textContent || '',
              children
            };
          }
          return null;
      }
    }
    
    return null;
  }

  private static parseChildNodes(element: HTMLElement): ParsedElement[] {
    const children: ParsedElement[] = [];
    
    for (const node of Array.from(element.childNodes)) {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent?.trim();
        if (text) {
          children.push({ type: 'text', content: text });
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const childElement = node as HTMLElement;
        const tagName = childElement.tagName.toLowerCase();
        
        switch (tagName) {
          case 'strong':
          case 'b':
            children.push({
              type: 'strong',
              content: childElement.textContent || ''
            });
            break;
            
          case 'em':
          case 'i':
            children.push({
              type: 'emphasis',
              content: childElement.textContent || ''
            });
            break;
            
          case 'br':
            children.push({ type: 'text', content: ' ' });
            break;
            
          default:
            // For other inline elements, just get text content
            const text = childElement.textContent?.trim();
            if (text) {
              children.push({ type: 'text', content: text });
            }
        }
      }
    }
    
    return children;
  }
}

const ChatApp: React.FC = () => {
  const { 
  user, 
  isGuest, 
  cooldownInfo, 
  incrementQuestionUsage, 
  canSendMessage, 
  updateUserData,
  logout
} = useAuth();
  const [isMobile, setIsMobile] = useState(false); // 🔧 ADD THIS LINE
  const [sidebarOpen, setSidebarOpen] = useState(true);
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

  // Detect mobile screen size
  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
      const response = await chatAPI.getConversationMessages(conversationId);
      // Backend now stores perfectly formatted content, just use it directly
      setMessages(response.messages || []);
      setSelectedConversation(conversationId);
      if (isMobile) setSidebarOpen(false);
    } catch (error) {
      showToast('فشل في تحميل المحادثة', 'error');
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };


  const startNewConversation = () => {
    setMessages([]);
    setSelectedConversation(null);
    setInputMessage('');
    if (isMobile) setSidebarOpen(false);
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

  // Add this BEFORE your handleSendMessage function

// DEAD SIMPLE ARABIC FORMATTER - EXACTLY LIKE CLAUDE'S RESPONSES

/**
 * Simple streaming formatter - formats as content comes in
 */


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
      
       // 📡 Simple streaming callback - backend sends perfectly formatted chunks
(chunk: string) => {
  streamingContent += chunk;
  
  // Backend sends pre-formatted chunks, just display accumulated content
  setMessages(prev => prev.map(msg => 
    msg.id === assistantMessageId 
      ? { ...msg, content: streamingContent }
      : msg
  ));
},

      // ✅ Completion handler - content already perfectly formatted from backend
      async (response: any) => {
        console.log('📥 Received response:', { contentLength: response.fullResponse?.length || 0 });
        
        // Backend already applied perfect formatting, just use it
        const finalContent = response.ai_message?.content || streamingContent;
        
        console.log('✅ Using backend-formatted content (already perfect)');
        
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
          ? {
              ...msg,
              id: response.ai_message?.id || assistantMessageId,
              content: finalContent, // Already perfectly formatted by backend
              timestamp: response.ai_message?.timestamp || new Date().toISOString()
            }
          : msg
        ));

        // 🔄 Handle conversation and user data updates (your existing logic)
        if (response.conversation_id && !selectedConversation) {
          setSelectedConversation(response.conversation_id);
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
      `}</style>
      
<div style={{
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
  // 🔧 MOBILE FIX: Dynamic height
  height: isMobile ? 'auto' : '100vh',
  minHeight: isMobile ? '100vh' : 'auto',
  fontFamily: "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  background: '#f7f7f8',
  direction: 'rtl',
  contain: 'layout style paint',
  // 🔧 MOBILE FIX: Allow scrolling
  overflow: isMobile ? 'visible' : 'hidden'
}}>
        
        {/* Mobile Backdrop */}
       {/* Mobile Backdrop */}
{isMobile && sidebarOpen && (
  <div 
    style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      zIndex: 40,
      opacity: 1,
      transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      backdropFilter: 'blur(4px)',
      willChange: 'opacity'
    }}
    onClick={(e) => {
      // Only close if clicking the backdrop itself, not scrolling
      if (e.target === e.currentTarget) {
        toggleSidebar();
      }
    }}
  />
)}

        {/* Sidebar */}
        {/* Sidebar Toggle Button */}
{!sidebarOpen && (
  <button
    onClick={() => setSidebarOpen(true)}
    style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 100,
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '12px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.2s ease',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      backdropFilter: 'blur(10px)'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)';
      e.currentTarget.style.transform = 'scale(1.05)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.background = 'rgba(0, 0, 0, 0.8)';
      e.currentTarget.style.transform = 'scale(1)';
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
  style={{
    gridArea: 'sidebar',
    position: isMobile ? 'fixed' : 'relative',
    inset: isMobile ? '0 0 0 auto' : 'auto',  // ← This positions it on the RIGHT
    width: isMobile ? '320px' : '100%',
    // 🔧 MOBILE FIX: Dynamic height
    height: isMobile ? '100vh' : '100vh', // Keep 100vh for sidebar
    background: '#171717',
    display: sidebarOpen ? 'flex' : 'none',
    flexDirection: 'column',
    borderLeft: '1px solid #363739',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: isMobile ? 50 : 'auto',
    boxShadow: isMobile ? '0 10px 25px rgba(0, 0, 0, 0.15)' : 'none'
  }}
>
          {/* Sidebar Header - Clean & Spaced */}
<div style={{
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
  
  {/* Only show close button, properly spaced */}
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

          {/* New Chat Button */}
          <div style={{ padding: '16px' }}>
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

          {/* Conversations List */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0 16px'
          }}>
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
  <div
    key={conv.id}
    style={{
      padding: '12px 16px',
      margin: '4px 0',
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
      onClick={() => loadConversationMessages(conv.id)}
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
)))}
          </div>

          {/* User Info - Premium Clean Design */}
<div style={{
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
              {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)} / 20
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
        <div style={{
  gridArea: 'main',
  display: 'flex',
  flexDirection: 'column',
  background: 'white',
  // 🔧 MOBILE FIX: Dynamic height
  height: isMobile ? 'auto' : '100vh',
  minHeight: isMobile ? '100vh' : 'auto',
  position: 'relative',
  // 🔧 MOBILE FIX: Allow overflow on mobile
  overflow: isMobile ? 'visible' : 'hidden'
}}>
          <div style={{
  background: isGuest 
    ? cooldownInfo.questionsUsed >= cooldownInfo.maxQuestions
 
      ? 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)' 
      : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
    : selectedConversation 
      ? 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)' 
      : 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
  color: isGuest 
    ? cooldownInfo.questionsUsed >= cooldownInfo.maxQuestions
 
      ? '#dc2626' 
      : '#059669'
    : selectedConversation ? '#2563eb' : '#059669',
  padding: '8px 16px',
  borderRadius: '12px',
  fontSize: '13px',
  fontWeight: '600',
  transition: 'all 0.2s ease',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  border: '1px solid',
  borderColor: isGuest 
    ? cooldownInfo.questionsUsed >= cooldownInfo.maxQuestions
 
      ? 'rgba(220, 38, 38, 0.2)' 
      : 'rgba(5, 150, 105, 0.2)'
    : selectedConversation ? 'rgba(37, 99, 235, 0.2)' : 'rgba(5, 150, 105, 0.2)'
}}>
  <div style={{
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'currentColor'
  }} />
  {isGuest ? (
    cooldownInfo.questionsUsed >= cooldownInfo.maxQuestions
 ? (
      'تم استنفاد الرسائل المجانية'
    ) : (
      `${cooldownInfo.questionsUsed}/${cooldownInfo.maxQuestions
} رسائل مجانية`
    )
  ) : (
    selectedConversation ? 'محادثة نشطة' : 'محادثة جديدة'
  )}
</div>

          {/* Messages Area */}
          <div 
  className="chat-main-area"
  style={{
    flex: 1,
    overflowY: 'auto',
    padding: '24px 0',
    scrollBehavior: 'smooth',
    // 🔧 MOBILE FIX: Better touch scrolling
    WebkitOverflowScrolling: 'touch',
    // 🔧 MOBILE FIX: Ensure proper height on mobile
    minHeight: isMobile ? '60vh' : 'auto'
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
                  color: '#2d333a',
                  marginBottom: '16px'
                }}>
                  اهلا بك في حكم
                </h2>
                <p style={{
                  fontSize: 'clamp(24px, 2vw, 16px)',
                  color: '#6b7280',
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
                        background: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '20px',
                        cursor: 'pointer',
                        textAlign: 'right',
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                        animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s both`
                      }}
                      onClick={() => handleSuggestedQuestion(question)}
                      onMouseOver={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#10a37f';
                        (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(16, 163, 127, 0.15)';
                      }}
                      onMouseOut={(e) => {
                        (e.currentTarget as HTMLElement).style.borderColor = '#e5e7eb';
                        (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      <div style={{
                        fontSize: '22px',
                        color: '#374151',
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
    maxWidth: isMobile ? '100%' : (sidebarOpen ? '1200%' : '1400%'),
    padding: isMobile ? '0 1rem' : (sidebarOpen ? '0 3rem 0 0' : '0 2rem 0 11rem')
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
  : (message.role === 'user' ? 'flex-start' : 'center'),
    marginBottom: '24px',
    animationDelay: `${index * 0.1}s`
  }}
>

  <div
  className={message.role === 'user' ? 'user-message-enhanced' : ''}
  style={{
    maxWidth: message.role === 'user' 
      ? (sidebarOpen ? '75%' : '65%') 
      : (sidebarOpen ? '85%' : '75%'),
    background: message.role === 'user' 
      ? `linear-gradient(135deg, 
          rgba(0, 108, 53, 0.95) 0%, 
          rgba(0, 74, 36, 0.9) 50%,
          rgba(0, 108, 53, 0.85) 100%
        )` 
      : 'transparent',
    // Typography handled by CSS classes - no inline overrides for user messages!
    color: message.role === 'user' ? undefined : '#2d333a', 
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
    // Remove fontSize and lineHeight overrides - let CSS handle typography!
    fontSize: message.role === 'user' ? undefined : '25px',
    lineHeight: message.role === 'user' ? undefined : '1.5',
    textAlign: 'right',
    marginRight: isMobile 
  ? (message.role === 'user' ? '0.2rem' : 'auto')
  : (message.role === 'user' 
      ? (sidebarOpen ? '5%' : '20%') 
      : (sidebarOpen ? '0%' : '12%')),
marginLeft: isMobile 
  ? (message.role === 'user' ? 'auto' : 'auto')
  : (message.role === 'user' ? '0%' : '0%'),
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
<div style={{
  padding: '32px 24px',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)',
  borderTop: '1px solid rgba(0, 108, 53, 0.1)',
  position: 'relative',
  display: 'flex',
  justifyContent: 'center',
  backdropFilter: 'blur(20px)',
  boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 -4px 32px rgba(0, 108, 53, 0.05)'
}}>
  <div style={{
    position: 'relative',
    maxWidth: sidebarOpen ? '800px' : '1000px',
    width: '100%'
  }}>
    
    <div 
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        gap: '16px',
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.6) 100%)',
        borderRadius: '24px',
        padding: '20px 24px',
        border: '2px solid rgba(0, 108, 53, 0.1)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: '80px',
        backdropFilter: 'blur(20px)',
        boxShadow: `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `,
        animation: inputMessage.length === 0 ? 'luxuryPulse 4s ease-in-out infinite' : 'none'
      }}
      onFocus={() => {
        // Stop animation on focus
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.borderColor = 'rgba(0, 108, 53, 0.2)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = `
          0 12px 40px rgba(0, 108, 53, 0.12),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.borderColor = 'rgba(0, 108, 53, 0.1)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = `
          0 8px 32px rgba(0, 108, 53, 0.08),
          0 0 0 1px rgba(255, 255, 255, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `;
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
          color: '#1f2937',
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
            الأسئلة المتبقية: {(cooldownInfo.maxQuestions - cooldownInfo.questionsUsed)}/20
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

export default ChatApp;