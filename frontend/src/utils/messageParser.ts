// =====================================================================
// 📝 MESSAGE PARSING AND FORMATTING - EXTRACTED FROM 4550-LINE APP.TSX
// =====================================================================

import type { MessageElement, TableData, ParsedElement } from '../types';
import { sanitizeHTML } from './security';

/**
 * Detects if content is a multi-agent response
 * @param content - Content to analyze
 * @returns True if multi-agent response is detected
 */
export const detectMultiAgentResponse = (content: string): boolean => {
  const indicators = [
    '📋', '🔍', '⚖️', '💡', '📚', '🎯',
    'التحقق من صحة المراجع',
    'الإجراءات المطلوبة', 
    'التحليل القانوني',
    'السوابق القضائية',
    'مستوى الثقة:',
    'التقييم:',
    'الاستشهاد:',
    'بناءً على التحليل القانوني',
    'الأسس القانونية لحقوقك'
  ];
  
  return indicators.some(indicator => content.includes(indicator));
};

/**
 * Formats AI response content with proper structure and converts markdown to HTML
 * @param content - Raw AI response content
 * @returns HTML formatted content
 */
export const formatAIResponse = (content: string): string => {
  console.log('---- RAW INPUT ----');
  console.log(content);

  // Step 1: Clean the input
  let cleaned = content
    // Remove any existing HTML tags first
    .replace(/<\/?bold>/gi, '')
    .replace(/<\/?b>/gi, '')
    // Remove control characters
    .replace(/[\u200e\u200f\u202a-\u202e\uFEFF]/g, '')
    .trim();

  console.log('---- AFTER CLEANING ----');
  console.log(cleaned);

  // Step 2: CRITICAL FIX - Separate stuck markdown headers (GENERIC - NO HARDCODING)
  cleaned = cleaned
    // FIRST: Fix stuck markdown headers: ANY character followed immediately by ####
    .replace(/([^\s\n])(#{1,6})/g, '$1\n\n$2')
    
    // SECOND: Fix stuck sentences: Sentence-end followed immediately by capital/Arabic
    .replace(/([.!?؟])([A-Z\u0600-\u06FF])/g, '$1\n\n$2')
    
    // THIRD: Fix bullet points stuck to text
    .replace(/([^\s\n])(\s*[-•]\s)/g, '$1\n$2')
    
    // FOURTH: Fix numbered lists stuck to text  
    .replace(/([^\s\n])(\s*\d+\.\s)/g, '$1\n$2')
    
    // Clean up multiple newlines (max 2)
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  // Step 3: Convert markdown to HTML
  let html = cleaned
    // Headers - handle with or without spaces after #
    .replace(/^#{6}\s*(.*$)/gim, '<h6>$1</h6>')
    .replace(/^#{5}\s*(.*$)/gim, '<h5>$1</h5>')
    .replace(/^#{4}\s*(.*$)/gim, '<h4>$1</h4>')
    .replace(/^#{3}\s*(.*$)/gim, '<h3>$1</h3>')
    .replace(/^#{2}\s*(.*$)/gim, '<h2>$1</h2>')
    .replace(/^#{1}\s*(.*$)/gim, '<h1>$1</h1>')
    
    // Bold text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    // Italic text
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    
    // Bullet lists
    .replace(/^[-•]\s+(.*)$/gm, '<li>$1</li>')
    
    // Numbered lists
    .replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>');

  // Wrap consecutive list items in ul tags only (no numbered lists)
  html = html
    .replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gs, (match) => {
      // Always use ul (bullet lists) - no numbered lists for mobile
      return '<ul>' + match + '</ul>';
    });

  // Convert line breaks to paragraphs
  const paragraphs = html.split(/\n\s*\n/).filter(p => p.trim());
  html = paragraphs.map(p => {
    p = p.trim();
    // Don't wrap if already has HTML tags
    if (p.match(/^<[holu]/i)) {
      return p;
    }
    return `<p>${p}</p>`;
  }).join('\n');

  console.log('---- FINAL HTML OUTPUT ----');
  console.log(html);
  
  return html;
};

/**
 * Parses message content into structured elements
 * @param htmlContent - Raw HTML content from the AI
 * @returns Array of parsed message elements
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
      const level = parseInt(trimmed.charAt(2)) || 1;
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'heading', level, content });
    }
    // Parse paragraphs
    else if (trimmed.startsWith('<p>')) {
      const content = trimmed.replace(/<[^>]*>/g, '');
      elements.push({ type: 'paragraph', content, children: parseInlineElements(content) });
    }
    // Parse lists
    else if (trimmed.startsWith('<ul>') || trimmed.startsWith('<ol>')) {
      // Handle list parsing...
      elements.push({ type: 'list', content: trimmed });
    }
    // Default to text
    else {
      elements.push({ type: 'text', content: trimmed });
    }
  }
  
  return elements;
};

/**
 * Parses inline elements within text
 * @param text - Text to parse for inline elements
 * @returns Array of parsed inline elements
 */
export const parseInlineElements = (text: string): MessageElement[] => {
  const elements: MessageElement[] = [];
  let currentIndex = 0;
  
  // Simple regex patterns for bold and italic
  const patterns = [
    { regex: /\*\*(.*?)\*\*/g, type: 'strong' as const },
    { regex: /\*(.*?)\*/g, type: 'emphasis' as const },
    { regex: /<strong>(.*?)<\/strong>/g, type: 'strong' as const },
    { regex: /<em>(.*?)<\/em>/g, type: 'emphasis' as const }
  ];
  
  let remaining = text;
  
  for (const pattern of patterns) {
    remaining = remaining.replace(pattern.regex, (match, content) => {
      elements.push({ type: pattern.type, content });
      return `__${pattern.type}_${elements.length - 1}__`;
    });
  }
  
  // Add remaining text
  if (remaining.trim()) {
    elements.push({ type: 'text', content: remaining });
  }
  
  return elements;
};

/**
 * Parses Arabic comparison content into table data
 * @param lines - Lines of content to parse
 * @returns Structured table data
 */
export const parseArabicComparison = (lines: string[]): TableData => {
  const result: TableData = { headers: [], rows: [] };
  
  // Look for header indicators
  let processLines = lines;
  const firstLine = lines[0];
  if (firstLine && (firstLine.includes('مقارنة') || firstLine.includes('الفرق'))) {
    // Skip title line
    processLines = lines.slice(1);
  }
  
  // Try to identify comparison patterns
  const comparisonPatterns = [
    // Pattern: "الأول: ... | الثاني: ..."
    /^(.+?)[:：]\s*(.+?)(?:\s*\|\s*(.+?)[:：]\s*(.+?))?$/,
    // Pattern: "- النوع الأول: ... - النوع الثاني: ..."
    /^[-•]\s*(.+?)[:：]\s*(.+?)(?:\s*[-•]\s*(.+?)[:：]\s*(.+?))?$/,
    // Pattern: "1. ... 2. ..."
    /^(\d+)[.\-]\s*(.+?)(?:\s*(\d+)[.\-]\s*(.+?))?$/
  ];
  
  // Process each line
  for (const line of processLines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    
    for (const pattern of comparisonPatterns) {
      const match = trimmed.match(pattern);
      if (match) {
        // Extract comparison data
        if (result.headers.length === 0) {
          result.headers = ['الجانب الأول', 'الجانب الثاني'];
        }
        
        if (match[2] && match[4]) {
          result.rows.push([match[2], match[4]]);
        } else if (match[2]) {
          result.rows.push([match[1], match[2]]);
        }
        break;
      }
    }
  }
  
  return result;
};

/**
 * Generates comparison table HTML
 * @param data - Table data structure
 * @returns HTML table string
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
      html += `<td>${cell || '-'}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody>';
  html += '</table>';
  
  return html;
};

/**
 * Detects if content contains table structure
 * @param content - Content to analyze
 * @returns True if table structure is detected
 */
export const containsTableStructure = (content: string): boolean => {
  const tableIndicators = [
    /\|.*\|.*\|/,  // Pipe-separated values
    /مقارنة.*?:.*?مقابل/gi,  // Arabic comparison
    /الفرق.*?والــ/gi,  // Arabic difference
    /جدول/gi,  // Table in Arabic
    /vs\.?/gi,  // versus
    /^\s*[-\*]\s*.+?:\s*.+$/gm  // List with colons (potential table rows)
  ];
  
  return tableIndicators.some(pattern => pattern.test(content));
};

/**
 * HTML to React parser class for converting AI responses
 */
export class HTMLToReactParser {
  static parseHTML(htmlContent: string): ParsedElement[] {
    if (!htmlContent) return [];

    // Use browser's native DOMParser - most reliable
    const parser = new DOMParser();
    const doc = parser.parseFromString(`<div>${htmlContent}</div>`, 'text/html');
    const container = doc.body.firstChild as HTMLElement;
    
    if (!container) return [];

    const elements: ParsedElement[] = [];
    this.traverseNode(container, elements);
    return elements;
  }

  private static traverseNode(node: Node, elements: ParsedElement[]): void {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent?.trim();
      if (text) {
        elements.push({ type: 'text', content: text });
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node as Element;
      const tagName = element.tagName.toLowerCase();
      
      switch (tagName) {
        case 'h1':
        case 'h2':
        case 'h3':
        case 'h4':
        case 'h5':
        case 'h6':
          elements.push({
            type: 'heading',
            content: element.textContent || '',
            level: parseInt(tagName.charAt(1))
          });
          break;
        case 'p':
          elements.push({
            type: 'paragraph',
            content: element.textContent || ''
          });
          break;
        case 'strong':
        case 'b':
          elements.push({
            type: 'strong',
            content: element.textContent || ''
          });
          break;
        default:
          // Recursively parse child nodes
          node.childNodes.forEach(child => {
            this.traverseNode(child, elements);
          });
      }
    }
  }
}