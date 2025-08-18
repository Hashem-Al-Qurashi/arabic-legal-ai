import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, Camera, AlertCircle, CheckCircle, Loader2, FileImage, FilePdf, X } from 'lucide-react';
import { useAuthContext } from '../../contexts/AuthContext';

interface OcrResult {
  success: boolean;
  request_id: string;
  file_info: {
    filename: string;
    content_type: string;
    size_bytes: number;
    pages_processed?: number;
  };
  ocr_result: {
    text: string;
    confidence: number;
    word_count: number;
    language: string;
    engine: string;
  };
  rag_analysis?: {
    enabled: boolean;
    question?: string;
    response?: string;
    success?: boolean;
  };
  processing: {
    ocr_time_ms: number;
    total_time_ms: number;
    timestamp: string;
  };
}

interface OcrUploadProps {
  onTextExtracted?: (text: string, analysis?: string) => void;
  maxFileSize?: number; // in MB
  allowRagProcessing?: boolean;
}

export const OcrUpload: React.FC<OcrUploadProps> = ({
  onTextExtracted,
  maxFileSize = 50,
  allowRagProcessing = true
}) => {
  const { user, sessionId } = useAuthContext();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [extractedText, setExtractedText] = useState<string>('');
  const [analysisText, setAnalysisText] = useState<string>('');
  const [result, setResult] = useState<OcrResult | null>(null);
  const [error, setError] = useState<string>('');
  const [processWithRag, setProcessWithRag] = useState(false);
  const [customQuestion, setCustomQuestion] = useState('');

  // Supported file types
  const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp', 'application/pdf'];
  const maxFileSizeBytes = maxFileSize * 1024 * 1024;

  const validateFile = (file: File): string | null => {
    if (!supportedTypes.includes(file.type)) {
      return 'نوع الملف غير مدعوم. يرجى رفع صورة (JPG, PNG, BMP, TIFF, WebP) أو ملف PDF';
    }
    
    if (file.size > maxFileSizeBytes) {
      return `حجم الملف كبير جداً. الحد الأقصى ${maxFileSize} ميجابايت`;
    }
    
    return null;
  };

  const handleFileSelect = useCallback((file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSelectedFile(file);
    setError('');
    setResult(null);
    setExtractedText('');
    setAnalysisText('');
  }, [maxFileSizeBytes]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const processFile = async () => {
    if (!selectedFile) return;
    
    setIsProcessing(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('process_with_rag', processWithRag.toString());
      
      if (processWithRag && customQuestion.trim()) {
        formData.append('question', customQuestion.trim());
      }
      
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

      const data: OcrResult = await response.json();
      setResult(data);
      setExtractedText(data.ocr_result.text);
      
      if (data.rag_analysis?.enabled && data.rag_analysis.response) {
        setAnalysisText(data.rag_analysis.response);
      }
      
      // Notify parent component
      if (onTextExtracted) {
        onTextExtracted(
          data.ocr_result.text, 
          data.rag_analysis?.response
        );
      }
      
    } catch (err) {
      console.error('OCR processing error:', err);
      setError(err instanceof Error ? err.message : 'حدث خطأ في معالجة الملف');
    } finally {
      setIsProcessing(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setResult(null);
    setExtractedText('');
    setAnalysisText('');
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type === 'application/pdf') {
      return <FilePdf className="h-8 w-8 text-red-500" />;
    }
    return <FileImage className="h-8 w-8 text-blue-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} بايت`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} كيلوبايت`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} ميجابايت`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          استخراج النص من المستندات
        </h2>
        <p className="text-gray-600">
          ارفع صورة أو ملف PDF لاستخراج النص العربي باستخدام تقنية OCR المتقدمة
        </p>
      </div>

      {/* File Upload Area */}
      {!selectedFile && (
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.bmp,.tiff,.webp,.pdf"
            onChange={handleFileInputChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            اسحب وأفلت الملف هنا أو اضغط للتصفح
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            يدعم: JPG, PNG, BMP, TIFF, WebP, PDF
          </p>
          <p className="text-xs text-gray-500">
            الحد الأقصى: {maxFileSize} ميجابايت
          </p>
        </div>
      )}

      {/* Selected File Display */}
      {selectedFile && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 space-x-reverse">
              {getFileIcon(selectedFile)}
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-600">
                  {formatFileSize(selectedFile.size)} • {selectedFile.type}
                </p>
              </div>
            </div>
            <button
              onClick={clearFile}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* RAG Processing Options */}
          {allowRagProcessing && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <label className="flex items-center space-x-2 space-x-reverse">
                <input
                  type="checkbox"
                  checked={processWithRag}
                  onChange={(e) => setProcessWithRag(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  معالجة النص المستخرج بالذكاء الاصطناعي
                </span>
              </label>
              
              {processWithRag && (
                <div className="mt-3">
                  <textarea
                    value={customQuestion}
                    onChange={(e) => setCustomQuestion(e.target.value)}
                    placeholder="اكتب سؤالاً محدداً حول المستند (اختياري)"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    rows={2}
                  />
                </div>
              )}
            </div>
          )}

          {/* Process Button */}
          <div className="mt-4 flex justify-center">
            <button
              onClick={processFile}
              disabled={isProcessing}
              className="flex items-center space-x-2 space-x-reverse px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Camera className="h-5 w-5" />
              )}
              <span>
                {isProcessing ? 'جاري المعالجة...' : 'استخراج النص'}
              </span>
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 space-x-reverse">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-4">
          {/* Success Status */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 space-x-reverse">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-green-700 font-medium">تم استخراج النص بنجاح</p>
                <p className="text-sm text-green-600">
                  معدل الثقة: {(result.ocr_result.confidence * 100).toFixed(1)}% • 
                  عدد الكلمات: {result.ocr_result.word_count} • 
                  وقت المعالجة: {result.processing.ocr_time_ms}ms
                </p>
              </div>
            </div>
          </div>

          {/* Extracted Text */}
          {extractedText && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-3">النص المستخرج</h3>
              <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-arabic">
                  {extractedText}
                </pre>
              </div>
              <div className="mt-3 flex justify-end">
                <button
                  onClick={() => navigator.clipboard.writeText(extractedText)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  نسخ النص
                </button>
              </div>
            </div>
          )}

          {/* RAG Analysis */}
          {analysisText && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-3">التحليل الذكي</h3>
              <div className="bg-blue-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                <div className="text-sm text-gray-700 font-arabic prose prose-sm">
                  {analysisText.split('\n').map((line, index) => (
                    <p key={index} className="mb-2">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
              <div className="mt-3 flex justify-end">
                <button
                  onClick={() => navigator.clipboard.writeText(analysisText)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  نسخ التحليل
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};