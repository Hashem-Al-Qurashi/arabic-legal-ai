import React, { useState, useRef } from 'react';

// Simple SVG Icons
const PaperclipIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
  </svg>
);

const LoaderIcon = ({ size = 18 }: { size?: number }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2"
    style={{
      animation: 'spin 1s linear infinite'
    }}
  >
    <path d="M21 12a9 9 0 11-6.219-8.56"/>
    <style>{`
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    `}</style>
  </svg>
);

const AlertIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

const XIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

interface FileUploadButtonProps {
  onTextExtracted: (text: string) => void;
  isLoading?: boolean;
  user: any;
  sessionId?: string;
}

interface UploadResult {
  success: boolean;
  ocr_result?: {
    text: string;
    confidence: number;
    word_count: number;
  };
  error?: string;
}

export const FileUploadButton: React.FC<FileUploadButtonProps> = ({
  onTextExtracted,
  isLoading = false,
  user,
  sessionId
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>('');
  const [showError, setShowError] = useState(false);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // Validate file
    const maxSize = 50 * 1024 * 1024; // 50MB
    const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp', 'application/pdf'];
    
    if (!supportedTypes.includes(file.type)) {
      setError('نوع الملف غير مدعوم. يرجى رفع صورة أو ملف PDF');
      setShowError(true);
      return;
    }
    
    if (file.size > maxSize) {
      setError('حجم الملف كبير جداً. الحد الأقصى 50 ميجابايت');
      setShowError(true);
      return;
    }

    await processFile(file);
    
    // Clear the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const processFile = async (file: File) => {
    setUploading(true);
    setError('');
    setShowError(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('process_with_rag', 'false'); // Just extract text, don't analyze
      
      if (!user && sessionId) {
        formData.append('session_id', sessionId);
      }

      const response = await fetch('/api/ocr/extract', {
        method: 'POST',
        headers: {
          ...(user && { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` })
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'فشل في معالجة الملف');
      }

      const result: UploadResult = await response.json();
      
      if (result.success && result.ocr_result?.text) {
        const extractedText = result.ocr_result.text.trim();
        if (extractedText) {
          // Format the text nicely for chat
          const formattedText = `📄 نص مستخرج من الملف: ${file.name}\n\n${extractedText}`;
          onTextExtracted(formattedText);
        } else {
          setError('لم يتم العثور على نص في الملف');
          setShowError(true);
        }
      } else {
        setError('فشل في استخراج النص من الملف');
        setShowError(true);
      }

    } catch (error) {
      console.error('OCR error:', error);
      setError(error instanceof Error ? error.message : 'حدث خطأ في معالجة الملف');
      setShowError(true);
    } finally {
      setUploading(false);
    }
  };

  const handleButtonClick = () => {
    if (uploading || isLoading) return;
    fileInputRef.current?.click();
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.bmp,.tiff,.webp,.pdf"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      
      <button
        onClick={handleButtonClick}
        disabled={uploading || isLoading}
        title={uploading ? 'جاري المعالجة...' : 'رفع ملف للاستخراج النص'}
        style={{
          background: (uploading || isLoading) 
            ? 'rgba(189, 189, 189, 0.3)' 
            : 'transparent',
          color: (uploading || isLoading) ? '#9ca3af' : '#8e8ea0',
          border: 'none',
          borderRadius: '8px',
          width: '32px',
          height: '32px',
          cursor: (uploading || isLoading) ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s ease',
          marginRight: '8px',
          padding: '0'
        }}
        onMouseOver={(e) => {
          if (!(uploading || isLoading)) {
            e.currentTarget.style.background = 'rgba(142, 142, 160, 0.1)';
            e.currentTarget.style.color = '#525252';
          }
        }}
        onMouseOut={(e) => {
          if (!(uploading || isLoading)) {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = '#8e8ea0';
          }
        }}
      >
        {uploading ? (
          <LoaderIcon size={18} />
        ) : (
          <PaperclipIcon size={18} />
        )}
      </button>

      {/* Error Toast */}
      {showError && (
        <div
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 1000,
            maxWidth: '400px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)'
          }}
        >
          <AlertIcon size={16} />
          <span style={{ color: '#dc2626', fontSize: '14px', flex: 1 }}>
            {error}
          </span>
          <button
            onClick={() => setShowError(false)}
            style={{
              background: 'none',
              border: 'none',
              color: '#dc2626',
              cursor: 'pointer',
              padding: '0',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <XIcon size={16} />
          </button>
        </div>
      )}
    </>
  );
};