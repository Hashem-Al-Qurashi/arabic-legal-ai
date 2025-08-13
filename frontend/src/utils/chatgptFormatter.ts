/**
 * ChatGPT-Level Post-Processing Formatter
 * Based on ChatGPT's own recommendations for perfect formatting
 */

const FENCE = "```";

function fixCodeFences(text: string): string {
  const lines = text.split(/\r?\n/);
  let open = false;
  const out: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    let ln = lines[i];

    if (ln.trim().startsWith(FENCE)) {
      open = !open;
      // Ensure language tag present for common code
      if (ln.trim() === FENCE && i + 1 < lines.length) {
        const nxt = lines[i + 1];
        let lang = '';
        if (/\b(def |class |import )/.test(nxt)) lang = 'python';
        else if (/\b(function|const|let)\b/.test(nxt)) lang = 'javascript';
        else if (/FROM .* AS |CMD \[/.test(nxt)) lang = 'dockerfile';
        else if (/\b(SELECT|INSERT|UPDATE|DELETE)\b/i.test(nxt)) lang = 'sql';
        else if (/^[#\s]*\w+/.test(nxt)) lang = 'bash';
        if (lang) ln = FENCE + lang;
      }
    }
    out.push(ln);
  }

  if (open) out.push(FENCE); // Close last fence
  return out.join('\n');
}

function normalizeBullets(text: string): string {
  // Convert different bullet styles to consistent "-"
  text = text.replace(/\n{3,}/g, '\n\n'); // Collapse excessive newlines
  text = text.replace(/^[\t ]*[•\*]\s+/gm, '- '); // Convert • and * to -
  text = text.replace(/^[\t ]*-\s+/gm, '- '); // Normalize existing -
  return text;
}

function ensureHeadingsSpacing(text: string): string {
  // Ensure blank line after headings
  text = text.replace(/^(#{1,3} .+)(?!\n\n)/gm, '$1\n');
  return text;
}

function normalizeArabicContent(text: string): string {
  // Fix common Arabic formatting issues
  text = text.replace(/([^\n])(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):/g, '$1\n\n## $2:');
  text = text.replace(/^(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً):/gm, '## $1:');
  
  // Fix numbered legal points
  text = text.replace(/([^\n])(\d+)\.\s+\*\*(.+?)\*\*/g, '$1\n\n$2. **$3**');
  
  return text;
}

function fixArabicWordBreaking(text: string): string {
  // Fix words broken across lines - more comprehensive approach
  let lines = text.split('\n');
  let fixed: string[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    let currentLine = lines[i].trim();
    
    // If current line ends with Arabic letter and next line starts with Arabic letter, join them
    if (i < lines.length - 1) {
      let nextLine = lines[i + 1]?.trim();
      
      // Check if we have a broken Arabic word
      if (currentLine && nextLine && 
          /[أ-ي]$/.test(currentLine) && 
          /^[أ-ي]/.test(nextLine) &&
          !currentLine.endsWith(':') && // Don't join if current line ends with :
          !nextLine.match(/^(أولاً|ثانياً|ثالثاً|رابعاً|خامساً)/)) { // Don't join ordinals
        
        // Join the lines
        currentLine = currentLine + nextLine;
        i++; // Skip next line since we merged it
      }
    }
    
    fixed.push(currentLine);
  }
  
  return fixed.join('\n');
}

function cleanupWhitespace(text: string): string {
  return text
    .replace(/\r\n/g, '\n')           // Normalize line endings
    .replace(/\r/g, '\n')             // Handle old Mac line endings
    .replace(/\\\s*$/gm, '')          // Remove trailing backslashes
    .replace(/\\\s*\n/g, '\n')        // Remove weird \ with newlines
    // Fix Arabic text broken across lines - join words that were split
    .replace(/([أ-ي])\n([أ-ي])/g, '$1$2') // Join Arabic letters split by newline
    .replace(/([a-zA-Z])\n([a-zA-Z])/g, '$1$2') // Join English letters split by newline
    .replace(/\n{4,}/g, '\n\n\n')     // Max 3 consecutive newlines
    .trim();
}

/**
 * Main ChatGPT-Level Formatter
 * This replaces our custom HTML formatter with proper markdown processing
 */
export function formatChatGPTStyle(text: string): string {
  let formatted = text;
  
  // Step 1: Fix Arabic word breaking FIRST (most important)
  formatted = fixArabicWordBreaking(formatted);
  
  // Step 2: Clean whitespace and normalize
  formatted = cleanupWhitespace(formatted);
  
  // Step 3: Handle Arabic-specific formatting
  formatted = normalizeArabicContent(formatted);
  
  // Step 4: Normalize bullets and lists
  formatted = normalizeBullets(formatted);
  
  // Step 5: Fix code fences
  formatted = fixCodeFences(formatted);
  
  // Step 6: Ensure proper heading spacing
  formatted = ensureHeadingsSpacing(formatted);
  
  // Step 7: Final cleanup
  formatted = formatted
    .replace(/\n{3,}/g, '\n\n')       // Final newline cleanup
    .replace(/^#{1,3} (.+)$/gm, '\n$&\n') // Ensure headings have space around them
    .replace(/^\n+/, '')              // Remove leading newlines
    .trim();
  
  return formatted;
}

/**
 * Lightweight streaming formatter - fixes critical issues without breaking partial content
 */
export function formatPartialChatGPTStyle(content: string): string {
  let formatted = content;
  
  // Only apply SAFE fixes during streaming that won't break partial content
  
  // 1. Fix immediate Arabic word breaks (most critical) - safer approach
  // Only join if we're confident it's a word break, not intentional formatting
  formatted = formatted
    .replace(/([أ-ي])\n([أ-ي][أ-ي])/g, '$1$2') // Join Arabic letter + newline + 2+ Arabic letters (safer)
    .replace(/([a-zA-Z])\n([a-zA-Z][a-zA-Z])/g, '$1$2') // Same for English
    
  // 2. Basic whitespace cleanup (safe)
  formatted = formatted
    .replace(/\r\n/g, '\n')           // Normalize line endings
    .replace(/\r/g, '\n')             // Handle old Mac line endings
    .replace(/\\\s*\n/g, '\n')        // Remove weird \ with newlines
    
  // 3. Fix obvious broken ordinals (safe during streaming)
  formatted = formatted
    .replace(/(أولاً|ثانياً|ثالثاً|رابعاً|خامساً|سادساً|سابعاً|ثامناً|تاسعاً|عاشراً)(\n)([أ-ي])/g, '$1: $3')
    
  // 4. Comprehensive Arabic word reconstruction for legal terms
  formatted = formatted
    // Common adjective endings
    .replace(/المقدم\n?ة/g, 'المقدمة')
    .replace(/القانون\n?ي/g, 'القانوني') 
    .replace(/القضائي\n?ة/g, 'القضائية')
    .replace(/الشرعي\n?ة/g, 'الشرعية')
    .replace(/النظامي\n?ة/g, 'النظامية')
    .replace(/القانوني\n?ة/g, 'القانونية')
    .replace(/التجاري\n?ة/g, 'التجارية')
    .replace(/المدني\n?ة/g, 'المدنية')
    .replace(/الجنائي\n?ة/g, 'الجنائية')
    .replace(/الإداري\n?ة/g, 'الإدارية')
    .replace(/الدستوري\n?ة/g, 'الدستورية')
    .replace(/التنفيذي\n?ة/g, 'التنفيذية')
    .replace(/القضائي\n?ة/g, 'القضائية')
    .replace(/التشريعي\n?ة/g, 'التشريعية')
    
    // Common legal nouns
    .replace(/المحكم\n?ة/g, 'المحكمة')
    .replace(/الدعو\n?ى/g, 'الدعوى')
    .replace(/القضي\n?ة/g, 'القضية')
    .replace(/الشك\n?وى/g, 'الشكوى')
    .replace(/الاستشار\n?ة/g, 'الاستشارة')
    .replace(/المراجع\n?ة/g, 'المراجعة')
    .replace(/الطعن\n?ة/g, 'الطعنة')
    .replace(/المخالف\n?ة/g, 'المخالفة')
    .replace(/العقوب\n?ة/g, 'العقوبة')
    .replace(/الغرام\n?ة/g, 'الغرامة')
    
    // Common verbs
    .replace(/المطلوب\n?ة/g, 'المطلوبة')
    .replace(/المرفوع\n?ة/g, 'المرفوعة')
    .replace(/المقدم\n?ة/g, 'المقدمة')
    .replace(/المرسل\n?ة/g, 'المرسلة')
    .replace(/المكتوب\n?ة/g, 'المكتوبة')
    
    // Generic patterns for -ية endings
    .replace(/([أ-ي]+)\n?ية/g, '$1ية')
    // Generic patterns for -ة endings  
    .replace(/([أ-ي]+)\n?ة/g, '$1ة')
    // Generic patterns for -ي endings
    .replace(/([أ-ي]+)\n?ي([^أ-ي]|$)/g, '$1ي$2')
    
  return formatted;
}