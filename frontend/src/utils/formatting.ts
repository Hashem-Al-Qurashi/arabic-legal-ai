/**
 * Formatting utilities for Arabic legal AI chat
 */

// Types for message parsing
export interface MessageElement {
  type: 'heading' | 'paragraph' | 'list' | 'listItem' | 'strong' | 'emphasis' | 'text';
  level?: number; // for headings (1-6)
  content: string;
  children?: MessageElement[];
}

export interface TableData {
  headers: string[];
  rows: string[][];
}

/**
 * Format streaming content - IDENTICAL to final formatter for consistency
 */
export const formatPartialContent = (content: string): string => {
  // Use exact same logic as formatAIResponse for consistency
  return formatAIResponse(content);
};

/**
 * ULTIMATE FORMATTING FUNCTION - Handles Cramped Text Like a Boss!
 * Fixes the "everything on one line" problem by creating line breaks first
 */
export const formatAIResponse = (content: string): string => {
  let html = content;
  
  // STEP 1: EMERGENCY LINE BREAK INJECTION! 
  // The text comes as one giant line - we need to break it up first
  html = html
    .replace(/\r\n/g, '\n')           // Normalize line endings
    .replace(/\r/g, '\n')             // Handle old Mac line endings
    .replace(/\\\s*$/gm, '')          // Remove trailing \ characters
    .replace(/\\\s*\n/g, '\n')        // Remove weird \ with newlines
    .trim();

  // STEP 2: CREATE LINE BREAKS where headers should be (BEFORE processing)
  // Break before markdown headers - these are cramped into previous text
  html = html.replace(/([^#])#{1,5}\s+/g, '$1\n\n### '); // ####أولاً -> \n\n###أولاً
  
  // Break before Arabic ordinals - handle both start of string and middle of text
  html = html.replace(/(^|[^:\n])(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):/g, (match, before, ordinal) => {
    if (before === '') {
      // At start of string
      return ordinal + ':';
    } else {
      // In middle of text - add line breaks
      return before + '\n\n' + ordinal + ':';
    }
  });
  
  // Break before numbered points that are cramped
  html = html.replace(/([^.\n])(\d+)\.\s+([^0-9])/g, '$1\n\n$2. $3');
  
  // Break before bullet points
  html = html.replace(/([^-\n])-\s+/g, '$1\n- ');

  // STEP 3: Handle Headers (now they're on proper lines!)
  html = html.replace(/^#{1,5}\s*(.+?)$/gm, '<h3>$1</h3>');
  
  // Arabic ordinals as headers - separate the header from content after colon
  html = html.replace(/^(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):\s*(.+)$/gm, '<h3>$1:</h3>\n\n$2');
  
  // STEP 4: Handle Bold Text GLOBALLY (works everywhere!)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  // STEP 5: Handle Lists
  // Convert bullet points
  html = html.replace(/^-\s+(.+)$/gm, '<li>$1</li>');
  
  // Convert numbered points
  html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="legal-point"><strong>$1.</strong> $2</div>');
  
  // STEP 6: Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gs, (match) => {
    return `<ul>${match}</ul>`;
  });
  
  // STEP 7: Handle Paragraphs 
  const paragraphs = html.split(/\n\s*\n/);
  
  html = paragraphs.map(para => {
    const trimmed = para.trim();
    if (!trimmed) return '';
    
    // Skip if already HTML
    if (trimmed.match(/^<(h[1-6]|ul|li|div)/)) {
      return trimmed;
    }
    
    // Wrap in paragraph
    return `<p>${trimmed}</p>`;
  }).filter(para => para).join('\n\n');
  
  // STEP 8: Final spacing cleanup for perfect formatting
  html = html
    .replace(/\n{3,}/g, '\n\n')                    // Max 2 newlines
    .replace(/<\/h3>\s*([^<])/g, '</h3>\n\n<p>$1</p>')  // Space after headers
    .replace(/<\/h3>\s*<p>/g, '</h3>\n\n<p>')      // Proper header spacing
    .replace(/<\/ul>\s*<p>/g, '</ul>\n\n<p>')      // Space after lists
    .replace(/<\/p>\s*<p>/g, '</p>\n<p>')          // Paragraph spacing
    .trim();
  
  return html;
};

/**
 * Parse message content into structured elements
 */
export const parseMessageContent = (htmlContent: string): MessageElement[] => {
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

/**
 * Parse inline elements like bold and italic text
 */
export const parseInlineElements = (text: string): MessageElement[] => {
  const elements: MessageElement[] = [];
  let currentIndex = 0;
  
  // Simple regex patterns for bold and italic
  const boldRegex = /\*\*(.*?)\*\*/g;
  const italicRegex = /\*(.*?)\*/g;
  
  let match;
  const matches: Array<{start: number, end: number, type: string, content: string}> = [];
  
  // Find all bold matches
  while ((match = boldRegex.exec(text)) !== null) {
    matches.push({
      start: match.index,
      end: match.index + match[0].length,
      type: 'strong',
      content: match[1]
    });
  }
  
  // Find all italic matches
  while ((match = italicRegex.exec(text)) !== null) {
    matches.push({
      start: match.index,
      end: match.index + match[0].length,
      type: 'emphasis',
      content: match[1]
    });
  }
  
  // Sort matches by start position
  matches.sort((a, b) => a.start - b.start);
  
  // Build elements
  for (const match of matches) {
    // Add text before match
    if (match.start > currentIndex) {
      const textContent = text.slice(currentIndex, match.start);
      if (textContent) {
        elements.push({ type: 'text', content: textContent });
      }
    }
    
    // Add formatted element
    elements.push({ type: match.type as any, content: match.content });
    currentIndex = match.end;
  }
  
  // Add remaining text
  if (currentIndex < text.length) {
    const textContent = text.slice(currentIndex);
    if (textContent) {
      elements.push({ type: 'text', content: textContent });
    }
  }
  
  return elements;
};

/**
 * Detect if content contains multi-agent response patterns
 */
export const detectMultiAgentResponse = (content: string): boolean => {
  const indicators = [
    '📋', '🔍', '⚖️', '💡', '📚', '🎯',
    'التحقق من صحة المراجع',
    'الإجراءات المطلوبة', 
    'التحليل القانوني',
    'السوابق القضائية',
    'التوصيات',
    'الخلاصة',
    'نظرة عامة',
    'التفاصيل القانونية'
  ];
  
  return indicators.some(indicator => content.includes(indicator));
};

/**
 * Generate HTML table for legal comparisons
 */
export const generateComparisonTable = (data: TableData): string => {
  let html = '<table class="comparison-table legal-comparison">';
  
  // Add caption for legal comparison
  html += '<caption>مقارنة قانونية تفصيلية</caption>';
  
  // Table header
  html += '<thead><tr>';
  data.headers.forEach(header => {
    html += `<th>${header}</th>`;
  });
  html += '</tr></thead>';
  
  // Table body
  html += '<tbody>';
  data.rows.forEach(row => {
    html += '<tr>';
    row.forEach(cell => {
      html += `<td>${cell}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  
  return html;
};

/**
 * Check if content contains table structure
 */
export const containsTableStructure = (content: string): boolean => {
  const tableIndicators = [
    '|', // Markdown table separator
    '<table>', '<thead>', '<tbody>', '<tr>', '<td>', '<th>', // HTML table tags
    'مقارنة', 'جدول', 'الخصائص', 'المميزات', // Arabic table-related words
  ];
  
  return tableIndicators.some(indicator => content.includes(indicator));
};

/**
 * Clean HTML content by removing unwanted tags
 */
export const cleanHtmlContent = (htmlContent: string): string => {
  return htmlContent
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
    .replace(/onclick="[^"]*"/gi, '')
    .replace(/javascript:[^"']*/gi, '');
};

/**
 * Check if content contains citations
 */
export const containsCitations = (content: string): boolean => {
  const citationPattern = /\[\d+\]|\(\d+\)|مصدر:\s*|المرجع:\s*|انظر:\s*/;
  return citationPattern.test(content);
};

/**
 * Strip citations from content
 */
export const stripCitations = (content: string): string => {
  return content
    .replace(/\[\d+\]/g, '')
    .replace(/\(\d+\)/g, '')
    .replace(/مصدر:\s*[^\n]*/g, '')
    .replace(/المرجع:\s*[^\n]*/g, '')
    .replace(/انظر:\s*[^\n]*/g, '')
    .trim();
};