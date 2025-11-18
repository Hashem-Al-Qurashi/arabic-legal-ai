import React, { useRef, useState, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { showToast } from '../../utils/helpers';

// Get API base URL - same logic as api.ts
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8891';
  }
  return `https://api.${hostname}`;
};
const API_BASE_URL = getApiBaseUrl();

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

interface FileUploadButtonProps {
  onFileAttached: (fileInfo: AttachmentInfo) => void;
  onUploadStart?: (filename: string) => void;
  isLoading?: boolean;
  sessionId?: string;
  maxFiles?: number;
  currentFileCount?: number;
  disabled?: boolean;
}

// Google OCR Only - as specified in OCR_BIBLE.md
const SUPPORTED_TYPES = [
  'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 
  'image/tiff', 'image/webp', 'application/pdf'
];
const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50MB
const MAX_FILES_DEFAULT = 5;

export const FileUploadButton: React.FC<FileUploadButtonProps> = ({
  onFileAttached,
  onUploadStart,
  isLoading = false,
  sessionId,
  maxFiles = MAX_FILES_DEFAULT,
  currentFileCount = 0,
  disabled = false
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { user } = useAuth();

  const validateFile = (file: File): string | null => {
    if (currentFileCount >= maxFiles) {
      return `الحد الأقصى ${maxFiles} ملفات. قم بإزالة ملف أولاً.`;
    }

    if (!SUPPORTED_TYPES.includes(file.type)) {
      return 'نوع الملف غير مدعوم. الأنواع المدعومة: JPG, PNG, BMP, TIFF, WebP, PDF';
    }
    
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const sizeMB = Math.round(file.size / (1024 * 1024));
      return `حجم الملف كبير جداً: ${sizeMB} ميجابايت. الحد الأقصى 50 ميجابايت`;
    }

    if (file.size === 0) {
      return 'الملف فارغ. يرجى اختيار ملف صالح.';
    }
    
    return null;
  };

  const processFile = async (file: File): Promise<void> => {
    const attachmentId = `attachment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create immediate attachment preview with "uploading" status
    const initialAttachment: AttachmentInfo = {
      id: attachmentId,
      fileType: file.type,
      extractedText: '',
      filename: file.name,
      confidence: 0,
      engine: '',
      fileSize: file.size,
      processingStatus: 'uploading'
    };

    onFileAttached(initialAttachment);
    onUploadStart?.(file.name);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('message', 'ما محتوى هذا الملف؟'); // Required by chat endpoint
      
      if (!user && sessionId) {
        formData.append('session_id', sessionId);
      }

      // Update to processing status
      onFileAttached({
        ...initialAttachment,
        processingStatus: 'processing'
      });

      const response = await fetch(`${API_BASE_URL}/api/ocr/extract`, {
        method: 'POST',
        headers: {
          ...(user && { 'Authorization': `Bearer ${localStorage.getItem('token')}` })
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'فشل في معالجة الملف';
        try {
          const errorData = await response.json();
          if (response.status === 429) {
            errorMessage = 'تم الوصول للحد الأقصى من الطلبات. يرجى المحاولة بعد قليل.';
          } else {
            errorMessage = errorData.detail || errorData.error || errorMessage;
          }
        } catch {
          if (response.status === 429) {
            errorMessage = 'تم الوصول للحد الأقصى من الطلبات. يرجى المحاولة بعد قليل.';
          }
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('🔍 OCR: Full backend response:', result);
      
      // OCR endpoint returns: { success: true, ocr_result: { text: "...", confidence: 0.95, engine: "..." } }
      const extractedText = result.success && result.ocr_result ? result.ocr_result.text : '';
      const confidence = result.ocr_result?.confidence || 0;
      const engine = result.ocr_result?.engine || 'Unknown';
      
      console.log('🔍 OCR: Extracted text:', extractedText);
      console.log('🔍 OCR: Confidence:', confidence);
      console.log('🔍 OCR: Engine:', engine);
      
      if (extractedText && !extractedText.includes('تعذر معالجة الملف')) {
        // Update attachment with completed OCR results
        const completedAttachment: AttachmentInfo = {
          ...initialAttachment,
          extractedText: extractedText,
          confidence: confidence,
          engine: engine,
          processingStatus: 'completed'
        };

        onFileAttached(completedAttachment);
        
        // Show success toast
        showToast(
          `✅ تم استخراج النص من ${file.name} بنجاح`, 
          'success'
        );
      } else {
        throw new Error('تعذر استخراج النص من الملف');
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'حدث خطأ غير متوقع';
      
      // Update attachment with error status
      onFileAttached({
        ...initialAttachment,
        processingStatus: 'error',
        error: errorMessage
      });
      
      showToast(`❌ فشل في معالجة ${file.name}: ${errorMessage}`, 'error');
      console.error('Google OCR processing error:', err);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      showToast(validationError, 'error');
      return;
    }

    setUploading(true);
    
    try {
      await processFile(file);
    } finally {
      setUploading(false);
      // Reset input to allow same file upload again
      if (e.target) e.target.value = '';
    }
  };

  // Drag and drop handlers
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (isCurrentlyDisabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    const file = files[0]; // Only process first file for now
    
    const validationError = validateFile(file);
    if (validationError) {
      showToast(validationError, 'error');
      return;
    }

    setUploading(true);
    
    try {
      await processFile(file);
    } finally {
      setUploading(false);
    }
  }, []);

  const openFileDialog = () => {
    if (!isCurrentlyDisabled) {
      fileInputRef.current?.click();
    }
  };

  const isCurrentlyDisabled = uploading || isLoading || disabled || (currentFileCount >= maxFiles);

  return (
    <div className="file-upload-button-container">
      <input
        ref={fileInputRef}
        type="file"
        accept={SUPPORTED_TYPES.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        multiple={false}
      />
      
      <button
        onClick={openFileDialog}
        disabled={isCurrentlyDisabled}
        title={isCurrentlyDisabled 
          ? currentFileCount >= maxFiles 
            ? `الحد الأقصى ${maxFiles} ملفات` 
            : 'غير متاح حالياً' 
          : 'رفع ملف (PNG, JPG, PDF)'
        }
        style={{
          background: isCurrentlyDisabled
            ? 'rgba(189, 189, 189, 0.3)' 
            : 'rgba(189, 189, 189, 0.3)',
          color: isCurrentlyDisabled ? '#9ca3af' : '#6b7280',
          border: 'none',
          borderRadius: '16px',
          width: '56px',
          height: '56px',
          cursor: isCurrentlyDisabled ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          flexShrink: 0,
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          if (!isCurrentlyDisabled) {
            e.currentTarget.style.background = 'linear-gradient(135deg, #00A852 0%, #006C35 100%)';
            e.currentTarget.style.color = 'white';
            e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 108, 53, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
          }
        }}
        onMouseOut={(e) => {
          if (!isCurrentlyDisabled) {
            e.currentTarget.style.background = 'rgba(189, 189, 189, 0.3)';
            e.currentTarget.style.color = '#6b7280';
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = 'none';
          }
        }}
      >
        {uploading ? (
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid rgba(0, 108, 53, 0.2)',
            borderTop: '2px solid #006C35',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        ) : (
          <span style={{ fontSize: '20px' }}>📎</span>
        )}
      </button>

      <style>{`
        .file-upload-button-container {
          display: inline-block;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};