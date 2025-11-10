/**
 * Date and time formatting utilities
 */

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
  const diffMinutes = Math.floor(diffTime / (1000 * 60));

  if (diffMinutes < 1) {
    return 'Just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return formatDate(dateString);
  }
};

/**
 * Text formatting utilities
 */

export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) {return text;}
  return text.slice(0, maxLength).trim() + '...';
};

export const capitalizeFirst = (text: string): string => {
  if (!text) {return text;}
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const formatName = (fullName: string): string => {
  return fullName
    .split(' ')
    .map(name => capitalizeFirst(name))
    .join(' ');
};

/**
 * Number formatting utilities
 */

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat().format(num);
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) {return '0 Bytes';}

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Arabic text utilities
 */

export const isArabicText = (text: string): boolean => {
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  return arabicRegex.test(text);
};

export const getTextDirection = (text: string): 'rtl' | 'ltr' => {
  return isArabicText(text) ? 'rtl' : 'ltr';
};

/**
 * URL and string utilities
 */

export const sanitizeFileName = (fileName: string): string => {
  return fileName.replace(/[^a-z0-9\-_.]/gi, '_').toLowerCase();
};

export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export const extractDomain = (url: string): string => {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
};
