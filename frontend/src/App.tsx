// Replace your entire frontend/src/App.tsx with this smooth implementation
import React, { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import { legalAPI, chatAPI } from './services/api';

interface ParsedElement {
  type: 'heading' | 'paragraph' | 'text' | 'strong' | 'emphasis' | 'listItem';
  content: string;
  level?: number;
  children?: ParsedElement[];
}



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
interface FormattedMessageProps {
  content: string;
  role: 'user' | 'assistant';
  sidebarOpen: boolean;
}



const FormattedMessage: React.FC<FormattedMessageProps> = ({ content, role, sidebarOpen }) => {
  if (role === 'user') {
    return (
      <div style={{
        lineHeight: '1.6',
        textAlign: 'right',
        direction: 'rtl',
        fontSize: '25px'
      }}>
        {content}
      </div>
    );
  }

  // AI messages: use browser's native HTML rendering
  return (
  <div 
    className="ai-response-container"
    style={{
      maxWidth: sidebarOpen ? '90%' : '90%',
      marginLeft: sidebarOpen ? '0' : 'auto',
      marginRight: sidebarOpen ? '0' : 'auto'
    }}
  >
    <div 
      className="ai-response"
      dangerouslySetInnerHTML={{ __html: content }}
      style={{
        direction: 'rtl',
        textAlign: 'right',
        lineHeight: '1.7'
      }}
    />
  </div>
);
};

interface MessageElement {
  type: 'heading' | 'paragraph' | 'list' | 'listItem' | 'strong' | 'emphasis' | 'text';
  level?: number; // for headings (1-6)
  content: string;
  children?: MessageElement[];
}

const parseMessageContent = (htmlContent: string): MessageElement[] => {
  // First, let's handle if it's plain text (no HTML)
  if (!htmlContent.includes('<') && !htmlContent.includes('>')) {
    // Split by double newlines for paragraphs
    return htmlContent.split('\n\n').map(paragraph => ({
  type: 'paragraph' as const,
  content: paragraph.trim(),
  children: parseInlineElements(paragraph.trim())
})).filter(p => p.content);
  }
  
  // For HTML content, we'll parse it properly
  const elements: MessageElement[] = [];
  const lines = htmlContent.split('\n');
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    
    // Parse headings
    if (trimmed.startsWith('<h') && trimmed.includes('>')) {
      const level = parseInt(trimmed.charAt(2));
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'heading', level, content });
    }
    // Parse paragraphs
    else if (trimmed.startsWith('<p>') || (!trimmed.startsWith('<'))) {
      const content = trimmed.replace(/<[^>]*>/g, '');
      if (content) {
        elements.push({ 
          type: 'paragraph', 
          content,
          children: parseInlineElements(content)
        });
      }
    }
    // Parse list items
    else if (trimmed.startsWith('<li>')) {
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'listItem', content });
    }
  }
  
  return elements;
};

const parseInlineElements = (text: string): MessageElement[] => {
  const elements: MessageElement[] = [];
  let currentIndex = 0;
  
  // Simple regex patterns for bold and italic
  const patterns = [
    { regex: /\*\*(.*?)\*\*/g, type: 'strong' as const },
    { regex: /\*(.*?)\*/g, type: 'emphasis' as const },
    { regex: /<strong>(.*?)<\/strong>/g, type: 'strong' as const },
    { regex: /<em>(.*?)<\/em>/g, type: 'emphasis' as const }
  ];
  
  let remaining = text;
  
  for (const pattern of patterns) {
    remaining = remaining.replace(pattern.regex, (match, content) => {
      elements.push({ type: pattern.type, content });
      return `__${pattern.type}_${elements.length - 1}__`;
    });
  }
  
  // Split by our placeholders and create text elements
  const parts = remaining.split(/(__\w+_\d+__)/);
  let elementIndex = 0;
  
  for (const part of parts) {
    if (part.startsWith('__') && part.endsWith('__')) {
      // This is a placeholder, skip it as we already have the element
      continue;
    } else if (part.trim()) {
      elements.splice(elementIndex, 0, { type: 'text', content: part });
      elementIndex++;
    }
    elementIndex++;
  }
  
  return elements.filter(el => el.content.trim());
};

const formatAIResponse = (content: string): string => {
  // If content has no HTML tags, apply basic markdown-like formatting
  if (!content.includes('<') && !content.includes('>')) {
    return content
      // Headers
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Lists
      .replace(/^- (.*$)/gm, '<li>$1</li>')
      .replace(/^(\d+)\. (.*$)/gm, '<li>$1. $2</li>')
      // Line breaks
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.*)$/gm, '<p>$1</p>')
      // Clean up
      .replace(/<p><\/p>/g, '')
      .replace(/<p>(<[hul])/g, '$1')
      .replace(/(<\/[hul]>)<\/p>/g, '$1');
  }
  return content;
};

const MessageRenderer: React.FC<{ elements: MessageElement[] }> = ({ elements }) => {
  const renderElement = (element: MessageElement, index: number): React.ReactNode => {
    const baseStyle = {
      margin: 0,
      padding: 0,
      textAlign: 'right' as const,
      direction: 'rtl' as const,
      fontFamily: "'Noto Sans Arabic', sans-serif"
    };
    
    switch (element.type) {
      case 'heading':
        const HeadingTag = `h${element.level || 2}` as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag
            key={index}
            style={{
              ...baseStyle,
              fontSize: element.level === 1 ? '2rem' : element.level === 2 ? '1.8rem' : '1.6rem',
              fontWeight: '700',
              color: element.level === 1 ? '#1e40af' : element.level === 2 ? '#059669' : '#dc2626',
              marginBottom: '0.5rem',
              marginTop: index === 0 ? '0' : '1rem'
            }}
          >
            {element.content}
          </HeadingTag>
        );
        
      case 'paragraph':
        return (
          <p
            key={index}
            style={{
              ...baseStyle,
              fontSize: '15px',
              lineHeight: '1.5',
              marginBottom: '0.8rem',
              marginTop: index === 0 ? '0' : '0.3rem'
            }}
          >
            {element.children ? renderInlineElements(element.children) : element.content}
          </p>
        );
        
      case 'listItem':
        return (
          <li
            key={index}
            style={{
              ...baseStyle,
              fontSize: '24px',
              lineHeight: '1.4',
              marginBottom: '0.3rem',
              listStylePosition: 'inside'
            }}
          >
            {element.content}
          </li>
        );
        
      default:
        return null;
    }
  };
  
  const renderInlineElements = (elements: MessageElement[]): React.ReactNode => {
    return elements.map((element, index) => {
      switch (element.type) {
        case 'strong':
          return (
            <strong key={index} style={{ color: '#1e40af', fontWeight: '700' }}>
              {element.content}
            </strong>
          );
        case 'emphasis':
          return (
            <em key={index} style={{ color: '#059669', fontStyle: 'italic' }}>
              {element.content}
            </em>
          );
        case 'text':
        default:
          return element.content;
      }
    });
  };
  
  // Group consecutive list items
  const groupedElements: React.ReactNode[] = [];
  let currentListItems: MessageElement[] = [];
  
  elements.forEach((element, index) => {
    if (element.type === 'listItem') {
      currentListItems.push(element);
    } else {
      if (currentListItems.length > 0) {
        groupedElements.push(
          <ul key={`list-${index}`} style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
            {currentListItems.map((item, i) => renderElement(item, i))}
          </ul>
        );
        currentListItems = [];
      }
      groupedElements.push(renderElement(element, index));
    }
  });
  
  // Handle remaining list items
  if (currentListItems.length > 0) {
    groupedElements.push(
      <ul key="list-final" style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
        {currentListItems.map((item, i) => renderElement(item, i))}
      </ul>
    );
  }
  
  return <div style={{ direction: 'rtl', textAlign: 'right' }}>{groupedElements}</div>;
};


interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  processing_time_ms?: number;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview: string | null;
  message_count: number;
}
const cleanHtmlContent = (htmlContent: string): string => {
  // Remove HTML tags and clean up the content
  return htmlContent
    .replace(/<[^>]*>/g, '') // Remove all HTML tags
    .replace(/&nbsp;/g, ' ') // Replace non-breaking spaces
    .replace(/&amp;/g, '&') // Replace HTML entities
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .trim(); // Remove leading/trailing whitespace
};
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
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    font-family: 'Noto Sans Arabic', sans-serif;
    font-weight: 500;
    max-width: 350px;
    animation: slideInToast 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOutToast 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    setTimeout(() => document.body.removeChild(toast), 400);
  }, 4000);
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'اليوم';
  if (diffDays === 2) return 'أمس';
  if (diffDays <= 7) return `منذ ${diffDays} أيام`;
  return date.toLocaleDateString('ar-SA');
};

const AuthScreen: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '1rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '2rem',
        maxWidth: '400px',
        width: '100%',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
        animation: 'fadeInScale 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ color: '#4CAF50', marginBottom: '0.5rem' }}>🇸🇦 المساعد القانوني الذكي</h1>
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

const ChatApp: React.FC = () => {
  const { user, logout } = useAuth();
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

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
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoadingConversations(true);
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.conversations || []);
    } catch (error) {
      console.log('Error loading conversations:', error);
      // Don't show error toast for conversations loading
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    try {
      const response = await chatAPI.getConversationMessages(conversationId);
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

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);
    
    try {
      // Try chat API first
      try {
        const chatResponse = await chatAPI.sendMessage(currentMessage, selectedConversation || undefined);
        
       const aiMessage: Message = {
  id: chatResponse.ai_message.id,
  role: 'assistant',
  content: formatAIResponse(chatResponse.ai_message.content),
  timestamp: chatResponse.ai_message.timestamp,
  processing_time_ms: chatResponse.ai_message.processing_time_ms
};
        
        setMessages(prev => [...prev, aiMessage]);
        setSelectedConversation(chatResponse.conversation_id);
        
        // Refresh conversations list
        loadConversations();
        
      } catch (chatError) {
        // Fallback to old API
        const consultation = await legalAPI.askQuestion(currentMessage);
        
        const aiMessage: Message = {
  id: consultation.id,
  role: 'assistant',
  content: consultation.answer, // Remove cleanHtmlContent to keep HTML
  timestamp: consultation.timestamp
};
        
        setMessages(prev => [...prev, aiMessage]);
      }
      
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'حدث خطأ في معالجة السؤال', 'error');
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
    'إجراءات الطلاق في النظام السعودي',
    'حقوق المستأجر في عقد الإيجار'
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
        gridTemplateColumns: isMobile ? '1fr' : sidebarOpen ? '320px 1fr' : '1fr',
        gridTemplateAreas: isMobile 
          ? '"main"'
          : sidebarOpen 
            ? '"sidebar main"'
            : '"main"',
        height: '100vh',
        fontFamily: "'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        background: '#f7f7f8',
        direction: 'rtl',
        contain: 'layout style paint',
        overflow: 'hidden'
      }}>
        
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
            onClick={toggleSidebar}
          />
        )}

        {/* Sidebar */}
        {/* Sidebar Toggle Button */}
<button
  onClick={() => setSidebarOpen(!sidebarOpen)}
  className={`sidebar-toggle-btn ${sidebarOpen ? 'open' : ''}`}
  style={{
  display: !sidebarOpen ? 'flex' : 'none'
}}
>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="3" y1="6" x2="21" y2="6"/>
    <line x1="3" y1="12" x2="21" y2="12"/>
    <line x1="3" y1="18" x2="21" y2="18"/>
  </svg>
</button>

{/* Sidebar */}
<div 
  style={{
    gridArea: 'sidebar',
    position: isMobile ? 'fixed' : 'relative',
    inset: isMobile ? '0 auto 0 0' : 'auto',
    width: isMobile ? '320px' : '100%',
    height: '100vh',
    background: '#171717',
    display: sidebarOpen ? 'flex' : 'none',
    flexDirection: 'column',
    borderLeft: '1px solid #363739',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    zIndex: isMobile ? 50 : 'auto',
    boxShadow: isMobile ? '0 10px 25px rgba(0, 0, 0, 0.15)' : 'none'
  }}
>
          {/* Sidebar Header */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #363739',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            minHeight: '70px'
          }}>
            <h2 style={{
              color: 'white',
              fontSize: '18px',
              fontWeight: '600',
              margin: 0
            }}>
              المحادثات
            </h2>
            {isMobile && (
  <button
    onClick={toggleSidebar}
    style={{
      background: 'transparent',
      border: 'none',
      color: '#8e8ea0',
      cursor: 'pointer',
      padding: '8px',
      borderRadius: '4px',
      transition: 'color 0.2s ease',
      minWidth: '32px',
      minHeight: '32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}
    onMouseOver={(e) => (e.target as HTMLElement).style.color = 'white'}
    onMouseOut={(e) => (e.target as HTMLElement).style.color = '#8e8ea0'}
  >
    ✕
  </button>
)}
{!isMobile && (
  <button
    onClick={() => setSidebarOpen(false)}
    style={{
      background: 'transparent',
      border: 'none',
      color: '#8e8ea0',
      cursor: 'pointer',
      padding: '8px',
      borderRadius: '4px',
      transition: 'color 0.2s ease',
    }}
    onMouseOver={(e) => (e.target as HTMLElement).style.color = 'white'}
    onMouseOut={(e) => (e.target as HTMLElement).style.color = '#8e8ea0'}
  >
    ✕
  </button>
)}
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
                  onClick={() => loadConversationMessages(conv.id)}
                  style={{
                    padding: '12px 16px',
                    margin: '4px 0',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: selectedConversation === conv.id ? '#2d2d30' : 'transparent',
                    color: 'white',
                    fontSize: '16px',
                    lineHeight: '1.4',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    border: selectedConversation === conv.id ? '1px solid #4f4f4f' : '1px solid transparent',
                    minHeight: '44px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center'
                  }}
                  onMouseOver={(e) => {
                    if (selectedConversation !== conv.id) {
                      (e.currentTarget as HTMLElement).style.background = '#2d2d30';
                      (e.currentTarget as HTMLElement).style.transform = 'translateX(-4px)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (selectedConversation !== conv.id) {
                      (e.currentTarget as HTMLElement).style.background = 'transparent';
                      (e.currentTarget as HTMLElement).style.transform = 'translateX(0)';
                    }
                  }}
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
              ))
            )}
          </div>

          {/* User Info */}
          <div style={{
            padding: '16px',
            borderTop: '1px solid #363739',
            color: '#8e8ea0',
            fontSize: '16px'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '8px' 
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: '#10a37f',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px'
              }}>
                👤
              </div>
              <strong style={{ color: 'white' }}>{user?.full_name}</strong>
            </div>
            <div style={{ marginBottom: '8px' }}>
              الأسئلة المتبقية: <strong style={{ color: '#10a37f' }}>{20 - (user?.questions_used_this_month || 0)}/20</strong>
            </div>
            <button
              onClick={logout}
              style={{
                width: '100%',
                background: 'transparent',
                border: '1px solid #565869',
                color: '#8e8ea0',
                borderRadius: '6px',
                padding: '8px 12px',
                cursor: 'pointer',
                fontSize: '16px',
                transition: 'all 0.2s ease',
                minHeight: '36px'
              }}
              onMouseOver={(e) => {
                (e.target as HTMLElement).style.background = '#2d2d30';
                (e.target as HTMLElement).style.color = 'white';
              }}
              onMouseOut={(e) => {
                (e.target as HTMLElement).style.background = 'transparent';
                (e.target as HTMLElement).style.color = '#8e8ea0';
              }}
            >
              تسجيل الخروج
            </button>
          </div>
        </div>

        {/* Main Chat Area */}
        <div style={{
          gridArea: 'main',
          display: 'flex',
          flexDirection: 'column',
          background: 'white',
          height: '100vh',
          position: 'relative'
        }}>
          {/* Header */}
          <div style={{
            padding: '16px 24px',
            borderBottom: '1px solid #e5e5e5',
            background: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            minHeight: '70px',
            zIndex: 10
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {(!sidebarOpen || isMobile) && (
                <button
                  onClick={toggleSidebar}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '8px',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'background-color 0.2s ease',
                    minWidth: '40px',
                    minHeight: '40px'
                  }}
                  onMouseOver={(e) => (e.target as HTMLElement).style.background = '#f3f4f6'}
                  onMouseOut={(e) => (e.target as HTMLElement).style.background = 'transparent'}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="3" y1="6" x2="21" y2="6"/>
                    <line x1="3" y1="12" x2="21" y2="12"/>
                    <line x1="3" y1="18" x2="21" y2="18"/>
                  </svg>
                </button>
              )}
              <h1 style={{
                margin: 0,
                fontSize: '20px',
                fontWeight: '600',
                color: '#2d333a'
              }}>
                🇸🇦 المساعد القانوني الذكي
              </h1>
            </div>
            
            <div style={{
              background: selectedConversation ? '#f0f9ff' : '#f0fdf4',
              color: selectedConversation ? '#0369a1' : '#166534',
              padding: '6px 12px',
              borderRadius: '16px',
              fontSize: '16px',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}>
              {selectedConversation ? 'محادثة نشطة' : 'محادثة جديدة'}
            </div>
          </div>

          {/* Messages Area */}
          <div 
  className="chat-main-area"
  style={{
    flex: 1,
    overflowY: 'auto',
    padding: '24px 0',
    scrollBehavior: 'smooth'
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
                }}>⚖️</div>
                <h2 style={{
                  fontSize: 'clamp(50px, 4vw, 26px)',
                  fontWeight: '600',
                  color: '#2d333a',
                  marginBottom: '16px'
                }}>
                  أهلاً بك في المساعد القانوني الذكي
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
                        fontSize: '16px',
                        color: '#9ca3af',
                        marginTop: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        gap: '4px'
                      }}>
                        اضغط للسؤال
                        <span style={{ fontSize: '20px' }}>💬</span>
                      </div>
                    </div>
                    
                  ))}

                  <div className="floating-actions">
  <button className="floating-btn" title="نسخ النص">
    📋
  </button>
  <button className="floating-btn" title="مشاركة">
    🔗
  </button>
  <button className="floating-btn" title="حفظ PDF">
    📄
  </button>
</div>
                </div>
              </div>
            ) : (
              // Messages
              <div 
  className="chat-messages-container"
  style={{
    maxWidth: sidebarOpen ? '1200%' : '1400%',
    padding: sidebarOpen ? '0 3rem 0 0' : '0 2rem 0 11rem'
  }}
>
                {messages.map((message, index) => (
                 <div
  key={message.id}
  className="message-enter"
  style={{
    display: 'flex',
    flexDirection: 'row',
    justifyContent: message.role === 'user' ? 'flex-start' : 'center',
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
    background: message.role === 'user' ? '#006C35' : 'transparent',
    color: message.role === 'user' ? 'white' : '#2d333a',
    borderRadius: message.role === 'user' ? '20px 20px 4px 16px' : '0',
    padding: message.role === 'user' ? '16px 20px' : '0',
    boxShadow: message.role === 'user' ? '0 2px 8px rgba(0, 108, 53, 0.3)' : 'none',
    border: 'none',
    fontSize: message.role === 'user' ? '25px' : '25px',
    lineHeight: '1.5',
    textAlign: 'right',
    marginRight: message.role === 'user' 
      ? (sidebarOpen ? '5%' : '20%') 
      : (sidebarOpen ? '0%' : '12%'),
    marginLeft: message.role === 'user' ? '0%' : '0%',
    wordBreak: 'break-word',
    overflowWrap: 'break-word',
    whiteSpace: 'normal',
    hyphens: 'auto'
  }}
>
                      <FormattedMessage 
  content={message.content} 
  role={message.role}
  sidebarOpen={sidebarOpen}
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
  padding: '24px',
  background: 'white',
  borderTop: '1px solid #e5e7eb',
  position: 'relative',
  display: 'flex',
  justifyContent: 'center'
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
    gap: '12px',
    background: '#f9fafb',
    borderRadius: '16px',
    padding: '16px 20px',
    border: '1px solid #e5e7eb',
    transition: 'all 0.2s ease',
    minHeight: '80px',
    animation: inputMessage.length === 0 ? 'inputPulse 3s ease-in-out infinite' : 'none'
  }}
  onFocus={() => {
    // Stop animation on focus
  }}
>
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="اكتب سؤالك القانوني هنا..."
                  disabled={isLoading}
                  style={{
  flex: 1,
  border: 'none',
  background: 'transparent',
  resize: 'none',
  outline: 'none',
  fontSize: '20px',
  lineHeight: '1.5',
  color: '#374151',
  fontFamily: 'inherit',
  minHeight: '48px',
  maxHeight: '150px',
  overflow: 'auto',
  padding: '0'
}}
                  rows={1}
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                  }}
                />
                
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  style={{
                    background: (!inputMessage.trim() || isLoading) ? '#e5e7eb' : '#10a37f',
                    color: (!inputMessage.trim() || isLoading) ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '12px',
                    width: '48px',
                    height: '48px',
                    cursor: (!inputMessage.trim() || isLoading) ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    transform: 'scale(1)',
                    flexShrink: 0
                  }}
                  onMouseOver={(e) => {
                    if (!(!inputMessage.trim() || isLoading)) {
                      (e.target as HTMLElement).style.background = '#0d9488';
                      (e.target as HTMLElement).style.transform = 'scale(1.05)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!(!inputMessage.trim() || isLoading)) {
                      (e.target as HTMLElement).style.background = '#10a37f';
                      (e.target as HTMLElement).style.transform = 'scale(1)';
                    }
                  }}
                >
                  {isLoading ? (
                    <div style={{
                      width: '20px',
                      height: '20px',
                      border: '2px solid transparent',
                      borderTop: '2px solid currentColor',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
                marginTop: '8px',
                fontSize: '18px',
                color: '#6b7280'
              }}>
                <div>
                  اضغط Enter للإرسال، Shift+Enter للسطر الجديد
                </div>
                <div>
                  الأسئلة المتبقية: {20 - (user?.questions_used_this_month || 0)}/20
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Additional CSS for animations */}
     
    </>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

const AppContent: React.FC = () => {
  const { user } = useAuth();
  
  return user ? <ChatApp /> : <AuthScreen />;
};

export default App;
