import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css'; // Add syntax highlighting theme
import ActionsBar from './ActionsBar';
import type { Message, Conversation } from '../../types/chat';

interface FormattedMessageProps {
  content: string;
  role: 'user' | 'assistant';
  sidebarOpen: boolean;
  isLastMessage?: boolean;
  messages?: Message[];
  conversations?: Conversation[];
  selectedConversation?: string | null;
}

// ChatGPT-Level FormattedMessage Component with React Markdown
const FormattedMessage: React.FC<FormattedMessageProps> = ({ 
  content, 
  role, 
  sidebarOpen, 
  isLastMessage = false,
  messages = [],
  conversations = [],
  selectedConversation = null
}) => {
  if (role === 'user') {
    return (
      <div className="user-message">
        {content}
      </div>
    );
  }

  // AI messages: ChatGPT-style container with React Markdown
  return (
    <div
      className="ai-response-container"
      style={{
        // Container styling
        background: '#ffffff',
        border: '1px solid #e8eaed',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)',
        padding: '32px 36px',
        margin: '20px 0',
        
        // Layout positioning
        position: 'relative' as const,
        overflow: 'hidden' as const,
        maxWidth: sidebarOpen ? '85%' : '85%',
        width: 'fit-content',
        minWidth: '320px',
        marginLeft: sidebarOpen ? '0' : 'auto',
        marginRight: sidebarOpen ? '2rem' : 'auto',
        
        // Smooth interaction
        transition: 'all 0.2s ease'
      }}
    >
      <div className="ai-response markdown-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight as any]}
          components={{
            // Custom components for perfect Arabic legal formatting
            h1: ({node, ...props}) => (
              <h1 className="text-xl font-bold mt-6 mb-4 text-right" {...props} />
            ),
            h2: ({node, ...props}) => (
              <h2 className="text-lg font-semibold mt-5 mb-3 text-right" {...props} />
            ),
            h3: ({node, ...props}) => (
              <h3 className="text-base font-semibold mt-4 mb-2 text-right" {...props} />
            ),
            h4: ({node, ...props}) => (
              <h4 className="text-sm font-semibold mt-3 mb-2 text-right" {...props} />
            ),
            p: ({node, ...props}) => (
              <p className="mb-4 text-right leading-relaxed" {...props} />
            ),
            ul: ({node, ...props}) => (
              <ul className="mb-4 mr-6 text-right" {...props} />
            ),
            ol: ({node, ...props}) => (
              <ol className="mb-4 mr-6 text-right" {...props} />
            ),
            li: ({node, ...props}) => (
              <li className="mb-2 text-right" {...props} />
            ),
            strong: ({node, ...props}) => (
              <strong className="font-semibold" {...props} />
            ),
            code: ({inline, className, children, ...props}) => {
              if (inline) {
                return (
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                    {children}
                  </code>
                );
              }
              return (
                <div className="relative my-4">
                  <button
                    className="absolute top-2 left-2 text-xs px-2 py-1 rounded border border-gray-300 bg-white hover:bg-gray-50"
                    onClick={() => navigator.clipboard.writeText(String(children))}
                    title="نسخ الكود"
                  >
                    نسخ
                  </button>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              );
            },
            blockquote: ({node, ...props}) => (
              <blockquote className="border-r-4 border-blue-500 pr-4 py-2 my-4 bg-blue-50 text-right" {...props} />
            ),
            table: ({node, ...props}) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border border-gray-300" {...props} />
              </div>
            ),
            th: ({node, ...props}) => (
              <th className="border border-gray-300 px-4 py-2 bg-gray-50 text-right font-semibold" {...props} />
            ),
            td: ({node, ...props}) => (
              <td className="border border-gray-300 px-4 py-2 text-right" {...props} />
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
      
      <ActionsBar
        content={content}
        isLastMessage={isLastMessage}
        messages={messages}
        conversations={conversations}
        selectedConversation={selectedConversation}
      />
    </div>
  );
};

export default FormattedMessage;