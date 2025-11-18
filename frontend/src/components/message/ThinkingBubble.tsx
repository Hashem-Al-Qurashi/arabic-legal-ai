import React, { useState, useEffect } from 'react';

interface ThinkingBubbleProps {
  thinking: string[];
  isActive: boolean;
  startTime?: number;
  onCancel?: () => void;  // Cancel callback
}

export const ThinkingBubble: React.FC<ThinkingBubbleProps> = ({ 
  thinking, 
  isActive, 
  startTime,
  onCancel
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update timer every second when thinking is active
  useEffect(() => {
    if (!isActive || !startTime) return;
    
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isActive, startTime]);

  if (thinking.length === 0) return null;

  return (
    <div className="thinking-container" style={{
      marginBottom: '12px',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: '#f9fafb',
      direction: 'rtl'
    }}>
      {/* Header with spinner and timer */}
      <div 
        className="thinking-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          cursor: 'pointer',
          borderBottom: isExpanded ? '1px solid #e5e7eb' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isActive && (
            <div 
              className="spinner"
              style={{
                width: '16px',
                height: '16px',
                border: '2px solid #e5e7eb',
                borderTop: '2px solid #3b82f6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}
            />
          )}
          <span style={{ 
            fontSize: '14px', 
            color: '#6b7280',
            fontWeight: '500'
          }}>
            💭 عملية التفكير
          </span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isActive && onCancel && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onCancel();
              }}
              style={{
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.target.style.background = '#dc2626'}
              onMouseOut={(e) => e.target.style.background = '#ef4444'}
            >
              🛑 إيقاف
            </button>
          )}
          {isActive && (
            <span style={{ 
              fontSize: '12px', 
              color: '#9ca3af',
              fontFamily: 'monospace'
            }}>
              {elapsedTime}s
            </span>
          )}
          <span style={{ 
            fontSize: '12px', 
            color: '#9ca3af',
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s'
          }}>
            ▼
          </span>
        </div>
      </div>

      {/* Collapsible thinking content */}
      {isExpanded && (
        <div 
          className="thinking-content"
          style={{
            padding: '12px',
            maxHeight: '300px',
            overflowY: 'auto',
            backgroundColor: '#fafbfc'
          }}
        >
          {thinking.map((step, index) => (
            <div 
              key={index}
              style={{
                marginBottom: '8px',
                padding: '6px 8px',
                backgroundColor: 'white',
                borderRadius: '4px',
                fontSize: '13px',
                color: '#374151',
                border: '1px solid #f3f4f6',
                animation: `fadeIn 0.3s ease-in-out ${index * 0.1}s both`
              }}
            >
              {step}
            </div>
          ))}
          
          {isActive && (
            <div style={{
              marginTop: '8px',
              padding: '6px 8px',
              backgroundColor: '#eff6ff',
              borderRadius: '4px',
              fontSize: '13px',
              color: '#1e40af',
              border: '1px solid #dbeafe',
              fontStyle: 'italic'
            }}>
              🔄 جاري التفكير...
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .thinking-header:hover {
          background-color: #f3f4f6;
        }
        
        .thinking-content::-webkit-scrollbar {
          width: 4px;
        }
        
        .thinking-content::-webkit-scrollbar-track {
          background: #f1f5f9;
        }
        
        .thinking-content::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
};