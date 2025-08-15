// =====================================================================
// 🛠️ GENERAL UTILITY HELPERS - EXTRACTED FROM 4550-LINE APP.TSX
// =====================================================================

/**
 * Remove HTML tags and clean up content
 * @param htmlContent - Raw HTML content
 * @returns Clean text content
 */
export const cleanHtmlContent = (htmlContent: string): string => {
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

/**
 * Shows a toast notification with premium styling
 * @param message - The message to display
 * @param type - The type of toast (error or success)
 */
export const showToast = (message: string, type: 'error' | 'success' = 'error'): void => {
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

/**
 * Formats a date string into a human-readable Arabic format
 * @param dateString - ISO date string
 * @returns Formatted date string in Arabic
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'اليوم';
  if (diffDays === 2) return 'أمس';
  if (diffDays <= 7) return `منذ ${diffDays} أيام`;
  return date.toLocaleDateString('ar-SA');
};

/**
 * Checks if content contains legal citations
 * @param content - Text content to check
 * @returns True if citations are found
 */
export const containsCitations = (content: string): boolean => {
  const citationPatterns = [
    /المادة\s*\(\s*\d+\s*\)/g,
    /نظام\s+.+\s+رقم\s+م\/\d+/g,
    /المرسوم\s+الملكي\s+رقم/g,
    /اللائحة\s+التنفيذية/g
  ];
  
  return citationPatterns.some(pattern => pattern.test(content));
};

/**
 * Strips citations from content and adds upgrade prompt
 * @param content - Content with citations
 * @returns Content without citations plus upgrade prompt
 */
export const stripCitations = (content: string): string => {
  let strippedContent = content
    .replace(/\(المادة\s*\(\s*\d+\s*\)[^)]*\)/g, '')
    .replace(/حسب\s+المادة\s*\(\s*\d+\s*\)[^.]*\./g, '')
    .replace(/وفقاً\s+لنظام\s+[^.]*\./g, '')
    .replace(/\(المرسوم\s+الملكي\s+رقم\s+[^)]*\)/g, '');
  
  // Add upgrade prompt
  strippedContent += '\n\n⚠️ للحصول على المراجع القانونية التفصيلية ومواد الأنظمة السعودية، يرجى الترقية للحساب المدفوع.';
  
  return strippedContent;
};

/**
 * Copy text to clipboard with fallback
 * @param text - Text to copy
 */
export const copyToClipboard = async (text: string): Promise<void> => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'absolute';
      textArea.style.left = '-999999px';
      document.body.prepend(textArea);
      textArea.select();
      document.execCommand('copy');
      textArea.remove();
    }
  } catch (error) {
    console.error('Failed to copy text:', error);
    throw new Error('Failed to copy text');
  }
};