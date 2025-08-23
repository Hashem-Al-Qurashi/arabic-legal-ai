// =====================================================================
// 🛡️ SENIOR-LEVEL SECURITY UTILITIES - EXTRACTED FROM 4550-LINE APP.TSX
// =====================================================================

import DOMPurify from 'dompurify';

/**
 * Secure HTML sanitizer to prevent XSS attacks
 * Uses DOMPurify with strict configuration for legal AI content
 * @param html - Raw HTML content to sanitize
 * @returns {string} Sanitized HTML safe for rendering
 */
export const sanitizeHTML = (html: string): string => {
  // Configure DOMPurify for legal AI content
  const config = {
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'br', 'strong', 'b', 'em', 'i', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['class', 'style'], // Allow minimal styling
    ALLOW_DATA_ATTR: false, // No data attributes
    ALLOW_UNKNOWN_PROTOCOLS: false, // Block javascript: and other protocols
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button'],
    FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'],
    KEEP_CONTENT: true // Keep text content even if tags are removed
  };
  
  // Sanitize with strict rules
  const sanitized = DOMPurify.sanitize(html, config);
  
  // Additional validation for conversation IDs in content
  if (sanitized.includes('javascript:') || sanitized.includes('data:') || sanitized.includes('<script')) {
    console.warn('🚨 Potential XSS attempt blocked in content');
    return DOMPurify.sanitize(html.replace(/<[^>]*>/g, ''), { ALLOWED_TAGS: [] }); // Strip all HTML if suspicious
  }
  
  return sanitized;
};

/**
 * Validates conversation ID format and content
 * @param conversationId - The conversation ID to validate
 * @returns {boolean} True if valid, false otherwise
 */
export const isValidConversationIdFormat = (conversationId: string): boolean => {
  if (!conversationId || typeof conversationId !== 'string') return false;
  
  // Conversation ID should be non-empty and not contain dangerous characters
  const trimmed = conversationId.trim();
  if (trimmed.length === 0) return false;
  
  // Basic security: no script injections, no path traversals
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /\.\.\/\.\.\//,
    /\0/,
    /%00/,
    /[<>'"]/
  ];
  
  return !dangerousPatterns.some(pattern => pattern.test(trimmed));
};

/**
 * Sanitizes conversation ID by removing dangerous characters
 * @param conversationId - The conversation ID to sanitize
 * @returns {string} Sanitized conversation ID
 */
export const sanitizeConversationId = (conversationId: string): string => {
  if (!conversationId || typeof conversationId !== 'string') return '';
  
  return conversationId
    .trim()
    .replace(/[<>'"]/g, '') // Remove potential HTML/script characters
    .replace(/\0|%00/g, ''); // Remove null bytes
};