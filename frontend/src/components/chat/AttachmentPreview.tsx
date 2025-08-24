import React, { useState } from 'react';

interface AttachmentInfo {
  id: string;
  fileType: string;
  extractedText: string;
  filename: string;
  confidence: number;
  engine: string;
  fileSize: number;
  processingStatus: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

interface AttachmentPreviewProps {
  attachment: AttachmentInfo;
  onRemove: (id: string) => void;
  onRetry?: (id: string) => void;
  compact?: boolean;
  showPreview?: boolean;
  isDark?: boolean;
}

export const AttachmentPreview: React.FC<AttachmentPreviewProps> = ({
  attachment,
  onRemove,
  onRetry,
  compact = true,
  showPreview = false,
  isDark = false
}) => {
  const [showFullText, setShowFullText] = useState(false);

  const getFileIcon = (contentType: string): string => {
    if (contentType === 'application/pdf') return '📄';
    if (contentType.startsWith('image/')) return '🖼️';
    return '📎';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusIcon = (): string => {
    switch (attachment.processingStatus) {
      case 'uploading': return '📤';
      case 'processing': return '⚙️';
      case 'completed': return '✅';
      case 'error': return '❌';
      default: return '📎';
    }
  };

  const getStatusText = (): string => {
    switch (attachment.processingStatus) {
      case 'uploading': return 'جاري الرفع...';
      case 'processing': return 'جاري استخراج النص...';
      case 'completed': return `تم الاستخراج (100.0%)`;
      case 'error': return 'فشل في المعالجة';
      default: return '';
    }
  };

  const getPreviewText = (): string => {
    if (!attachment.extractedText) return '';
    if (showFullText) return attachment.extractedText;
    return attachment.extractedText.length > 150 
      ? `${attachment.extractedText.substring(0, 150)}...` 
      : attachment.extractedText;
  };

  const canShowPreview = attachment.processingStatus === 'completed' && attachment.extractedText.trim();
  const canRetry = attachment.processingStatus === 'error' && onRetry;

  return (
    <div className="attachment-compact">
      <div className="attachment-header">
        <div className="file-info">
          <span className="file-icon">{getFileIcon(attachment.fileType)}</span>
          <div className="file-details">
            <span className="filename" style={{ color: isDark ? 'white' : '#1f2937' }}>{attachment.filename}</span>
            <div className="file-meta">
              <span className="file-size">{formatFileSize(attachment.fileSize)}</span>
              <span className="status-indicator">{getStatusIcon()}</span>
              <span className="status-text">{getStatusText()}</span>
            </div>
          </div>
        </div>
        
        <div className="actions">
          {canRetry && (
            <button 
              onClick={() => onRetry!(attachment.id)}
              className="action-btn retry-btn"
              title="إعادة المحاولة"
            >
              🔄
            </button>
          )}
          
          {canShowPreview && showPreview && (
            <button 
              onClick={() => setShowFullText(!showFullText)}
              className="action-btn preview-btn"
              title={showFullText ? "إخفاء النص" : "عرض النص"}
            >
              👁️
            </button>
          )}
          
          <button 
            onClick={() => onRemove(attachment.id)}
            className="action-btn remove-btn"
            title="إزالة الملف"
          >
            ✕
          </button>
        </div>
      </div>
      
      {/* Loading bar for processing states */}
      {(attachment.processingStatus === 'uploading' || attachment.processingStatus === 'processing') && (
        <div className="progress-bar">
          <div className="progress-fill"></div>
        </div>
      )}
      
      {/* Error message */}
      {attachment.processingStatus === 'error' && attachment.error && (
        <div className="error-message">
          <span className="error-text">{attachment.error}</span>
        </div>
      )}
      
      {/* Text preview */}
      {canShowPreview && showPreview && (
        <div className="text-preview">
          <div className="preview-content">
            {getPreviewText()}
          </div>
          {attachment.extractedText.length > 150 && (
            <button 
              className="toggle-text-btn"
              onClick={() => setShowFullText(!showFullText)}
            >
              {showFullText ? 'عرض أقل' : 'عرض المزيد'}
            </button>
          )}
        </div>
      )}

      <style>{`
        .attachment-compact {
          background: linear-gradient(135deg, 
            rgba(59, 130, 246, 0.05) 0%, 
            rgba(16, 185, 129, 0.03) 100%
          );
          border: 1px solid rgba(59, 130, 246, 0.2);
          border-radius: 16px;
          padding: 12px;
          margin: 4px 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          backdrop-filter: blur(10px);
          direction: rtl;
          position: relative;
          overflow: hidden;
        }

        .attachment-compact:hover {
          border-color: rgba(59, 130, 246, 0.4);
          transform: translateY(-1px);
          box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        }

        .attachment-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 12px;
        }

        .file-info {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          flex: 1;
          min-width: 0;
        }

        .file-icon {
          font-size: 24px;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .file-details {
          flex: 1;
          min-width: 0;
        }

        .filename {
          display: block;
          font-weight: 600;
          color: #1f2937;
          font-size: 14px;
          margin-bottom: 4px;
          word-break: break-word;
        }

        .file-meta {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #6b7280;
          flex-wrap: wrap;
        }

        .file-size {
          font-weight: 500;
        }

        .status-indicator {
          font-size: 14px;
          animation: ${attachment.processingStatus === 'processing' ? 'spin' : 'none'} 2s linear infinite;
        }

        .status-text {
          font-weight: 500;
          color: ${attachment.processingStatus === 'error' 
            ? '#ef4444' 
            : attachment.processingStatus === 'completed' 
              ? '#10b981' 
              : '#6b7280'
          };
        }

        .actions {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-shrink: 0;
        }

        .action-btn {
          background: rgba(255, 255, 255, 0.8);
          border: 1px solid rgba(0, 0, 0, 0.1);
          border-radius: 8px;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s ease;
          backdrop-filter: blur(4px);
        }

        .action-btn:hover {
          transform: scale(1.1);
        }

        .retry-btn:hover {
          background: rgba(59, 130, 246, 0.1);
          border-color: rgba(59, 130, 246, 0.3);
        }

        .preview-btn:hover {
          background: rgba(16, 185, 129, 0.1);
          border-color: rgba(16, 185, 129, 0.3);
        }

        .remove-btn:hover {
          background: rgba(239, 68, 68, 0.1);
          border-color: rgba(239, 68, 68, 0.3);
          color: #ef4444;
        }

        .progress-bar {
          margin-top: 8px;
          height: 3px;
          background: rgba(0, 0, 0, 0.1);
          border-radius: 2px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #10b981);
          border-radius: 2px;
          animation: progress 2s ease-in-out infinite;
        }

        .error-message {
          margin-top: 8px;
          padding: 6px 8px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 8px;
        }

        .error-text {
          font-size: 12px;
          color: #dc2626;
          font-weight: 500;
        }

        .text-preview {
          margin-top: 12px;
          border-top: 1px solid rgba(0, 0, 0, 0.1);
          padding-top: 12px;
        }

        .preview-content {
          background: rgba(255, 255, 255, 0.6);
          border: 1px solid rgba(0, 0, 0, 0.1);
          border-radius: 8px;
          padding: 10px;
          font-size: 13px;
          line-height: 1.5;
          color: #374151;
          white-space: pre-wrap;
          word-break: break-word;
          max-height: 120px;
          overflow-y: auto;
        }

        .toggle-text-btn {
          margin-top: 6px;
          background: none;
          border: none;
          color: #3b82f6;
          cursor: pointer;
          font-size: 12px;
          font-weight: 500;
          padding: 4px 0;
        }

        .toggle-text-btn:hover {
          text-decoration: underline;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes progress {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        /* Dark mode */
        [data-theme="dark"] .attachment-compact,
        .dark .attachment-compact {
          background: linear-gradient(135deg, 
            rgba(59, 130, 246, 0.1) 0%, 
            rgba(16, 185, 129, 0.05) 100%
          );
          border-color: rgba(59, 130, 246, 0.3);
        }

        [data-theme="dark"] .filename,
        .dark .filename {
          color: white !important;
        }

        [data-theme="dark"] .file-meta,
        .dark .file-meta {
          color: #9ca3af;
        }

        [data-theme="dark"] .preview-content,
        .dark .preview-content {
          background: rgba(31, 41, 55, 0.8);
          border-color: rgba(75, 85, 99, 0.3);
          color: #e5e7eb;
        }

        [data-theme="dark"] .action-btn,
        .dark .action-btn {
          background: rgba(31, 41, 55, 0.8);
          border-color: rgba(75, 85, 99, 0.3);
          color: #e5e7eb;
        }
      `}</style>
    </div>
  );
};