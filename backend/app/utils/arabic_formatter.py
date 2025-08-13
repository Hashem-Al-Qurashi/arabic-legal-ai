"""
Arabic Text Formatter - Server-Side Implementation
Boring solution that ensures ultimate formatting quality during streaming
"""

import re
import asyncio
from typing import Optional


class ArabicWordBreaker:
    """Fix Arabic words broken across streaming chunks"""
    
    def __init__(self):
        # Buffer to accumulate text
        self.buffer = ""
        self.last_processed = ""
    
    def add_chunk(self, new_chunk: str) -> str:
        """Add new chunk and return fixed content"""
        self.buffer += new_chunk
        
        # Process the buffer with smart Arabic reconstruction
        processed = self._process_buffer()
        self.last_processed = processed
        
        return processed
    
    def _process_buffer(self) -> str:
        text = self.buffer
        
        # 1. Fix Arabic word breaks in real-time
        text = self._fix_arabic_word_breaks(text)
        
        # 2. Clean up basic formatting issues
        text = self._basic_cleanup(text)
        
        # 3. Fix ordinals and headings
        text = self._fix_headings(text)
        
        return text
    
    def _fix_arabic_word_breaks(self, text: str) -> str:
        """Fix broken Arabic words"""
        # Most common broken patterns in Arabic legal text
        return text.replace('المقدم\nة', 'المقدمة') \
                   .replace('القانون\nي', 'القانوني') \
                   .replace('القضائي\nة', 'القضائية') \
                   .replace('الشرعي\nة', 'الشرعية') \
                   .replace('النظامي\nة', 'النظامية') \
                   .replace('التجاري\nة', 'التجارية') \
                   .replace('المدني\nة', 'المدنية') \
                   .replace('الجنائي\nة', 'الجنائية') \
                   .replace('الإداري\nة', 'الإدارية') \
                   .replace('الدستوري\nة', 'الدستورية') \
                   .replace('المحكم\nة', 'المحكمة') \
                   .replace('الدعو\nى', 'الدعوى') \
                   .replace('القضي\nة', 'القضية') \
                   .replace('الشك\nوى', 'الشكوى') \
                   .replace('الاستشار\nة', 'الاستشارة') \
                   .replace('المراجع\nة', 'المراجعة') \
                   .replace('الطعن\nة', 'الطعنة') \
                   .replace('المخالف\nة', 'المخالفة') \
                   .replace('العقوب\nة', 'العقوبة') \
                   .replace('الغرام\nة', 'الغرامة') \
                   .replace('المطلوب\nة', 'المطلوبة') \
                   .replace('المرفوع\nة', 'المرفوعة') \
                   .replace('المقدم\nة', 'المقدمة') \
                   .replace('المرسل\nة', 'المرسلة') \
                   .replace('المكتوب\nة', 'المكتوبة')
    
    def _basic_cleanup(self, text: str) -> str:
        """Basic text cleanup"""
        return text.replace('\r\n', '\n') \
                   .replace('\r', '\n') \
                   .replace('\\\n', '\n') \
                   .replace('\n\n\n\n', '\n\n\n')  # Max 3 consecutive newlines
    
    def _fix_headings(self, text: str) -> str:
        """Fix ordinal headings that may be broken"""
        ordinals = ['أولاً', 'ثانياً', 'ثالثاً', 'رابعاً', 'خامساً', 'سادساً', 'سابعاً', 'ثامناً', 'تاسعاً', 'عاشراً']
        
        for ordinal in ordinals:
            # Fix broken ordinals
            text = text.replace(f'{ordinal}\n:', f'{ordinal}:')
            # Fix ordinals followed by broken text
            pattern = f'({ordinal})(\n)([أ-ي])'
            text = re.sub(pattern, r'\1: \3', text)
        
        return text
    
    def get_processed_content(self) -> str:
        """Get the current processed content"""
        return self.last_processed
    
    def reset(self) -> None:
        """Reset the buffer"""
        self.buffer = ""
        self.last_processed = ""


def fix_arabic_word_breaking(text: str) -> str:
    """
    Fix words broken across lines - comprehensive approach
    This is the main function called from streaming
    """
    lines = text.split('\n')
    fixed = []
    
    for i in range(len(lines)):
        current_line = lines[i].strip()
        
        # If current line ends with Arabic letter and next line starts with Arabic letter, join them
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            
            # Only join if it's ACTUALLY a broken word (very specific cases)
            should_join = False
            
            # Only join in very specific broken word cases
            if (current_line and next_line and len(next_line) <= 3):  # Next line is very short (likely word ending)
                # Check for common Arabic word endings that get broken
                if (current_line.endswith('المقدم') and next_line == 'ة') or \
                   (current_line.endswith('القانون') and next_line == 'ي') or \
                   (current_line.endswith('القضائي') and next_line == 'ة') or \
                   (current_line.endswith('الشرعي') and next_line == 'ة') or \
                   (current_line.endswith('النظامي') and next_line == 'ة') or \
                   (current_line.endswith('التجاري') and next_line == 'ة') or \
                   (current_line.endswith('المدني') and next_line == 'ة') or \
                   (current_line.endswith('الجنائي') and next_line == 'ة') or \
                   (current_line.endswith('الإداري') and next_line == 'ة') or \
                   (current_line.endswith('الدستوري') and next_line == 'ة'):
                    should_join = True
            
            if should_join:
                
                # Join the lines
                current_line = current_line + next_line
                lines[i + 1] = ""  # Mark next line as processed
        
        if current_line:  # Only add non-empty lines
            fixed.append(current_line)
    
    return '\n'.join(fixed)


def cleanup_whitespace(text: str) -> str:
    """Clean up whitespace and normalize text"""
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n') 
    text = re.sub(r'\\\s*$', '', text, flags=re.MULTILINE)
    text = text.replace('\\\n', '\n')
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def normalize_arabic_content(text: str) -> str:
    """Fix common Arabic formatting issues"""
    # Simple and direct approach: fix the common patterns one by one
    
    # 1. Fix markdown headers combined with ordinals (#### أولاً:)
    ordinals = ['أولاً', 'ثانياً', 'ثالثاً', 'رابعاً', 'خامساً', 'سادساً', 'سابعاً', 'ثامناً', 'تاسعاً', 'عاشراً']
    for ordinal in ordinals:
        # Replace various markdown patterns with ordinals
        text = text.replace(f'#### {ordinal}:', f'\n\n## {ordinal}:')
        text = text.replace(f'####{ordinal}:', f'\n\n## {ordinal}:')
        text = text.replace(f'### {ordinal}:', f'\n\n## {ordinal}:')
        text = text.replace(f'###{ordinal}:', f'\n\n## {ordinal}:')
        # Also handle ordinals that appear mid-text without markdown
        text = re.sub(f'([^\n#]){ordinal}:', f'\\1\n\n## {ordinal}:', text)
    
    # 2. Fix numbered points (1. text)
    text = re.sub(r'(\d+)\.\s+([أ-ي])', r'\n\n\1. \2', text)
    
    # 3. Clean up any remaining stray markdown symbols
    text = re.sub(r'#{2,4}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2,4}\s*$', '', text, flags=re.MULTILINE)
    
    return text


def normalize_bullets(text: str) -> str:
    """Convert different bullet styles to consistent -"""
    text = re.sub(r'\n{3,}', '\n\n', text)  # Collapse excessive newlines
    text = re.sub(r'^[\t ]*[•\*]\s+', '- ', text, flags=re.MULTILINE)  # Convert • and * to -
    text = re.sub(r'^[\t ]*-\s+', '- ', text, flags=re.MULTILINE)  # Normalize existing -
    return text


def ensure_headings_spacing(text: str) -> str:
    """Ensure blank line after headings"""
    text = re.sub(r'^(#{1,3} .+)(?!\n\n)', r'\1\n', text, flags=re.MULTILINE)
    return text


def format_chatgpt_style(text: str) -> str:
    """
    Main ChatGPT-Level Formatter - Server Side
    This is the exact same logic as the frontend formatter
    """
    formatted = text
    
    # Step 1: Fix Arabic word breaking FIRST (most important)
    formatted = fix_arabic_word_breaking(formatted)
    
    # Step 2: Clean whitespace and normalize
    formatted = cleanup_whitespace(formatted)
    
    # Step 3: Handle Arabic-specific formatting
    formatted = normalize_arabic_content(formatted)
    
    # Step 4: Normalize bullets and lists
    formatted = normalize_bullets(formatted)
    
    # Step 5: Ensure proper heading spacing
    formatted = ensure_headings_spacing(formatted)
    
    # Step 6: Final cleanup
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)  # Final newline cleanup
    # DON'T remove markdown headers - they're needed for proper rendering!
    # formatted = re.sub(r'^#{1,3} (.+)$', r'\n\1\n', formatted, flags=re.MULTILINE)  # This was breaking headers
    formatted = re.sub(r'^\n+', '', formatted)  # Remove leading newlines
    formatted = formatted.strip()
    
    return formatted


# Two-pass formatting for ultimate quality
async def apply_two_pass_formatting(content: str) -> str:
    """
    Apply two-pass formatting to content for ultimate quality
    This mimics the frontend two-pass system
    """
    try:
        # Pass 1: Check if content needs formatting
        needs_formatting = check_if_needs_formatting(content)
        
        if not needs_formatting:
            return content
        
        # Pass 2: Apply comprehensive formatting
        formatted = format_chatgpt_style(content)
        return formatted
        
    except Exception as error:
        print(f"⚠️ Two-pass formatting failed: {error}")
        return content  # Fallback to original content


def check_if_needs_formatting(content: str) -> bool:
    """Check if content needs AI formatting"""
    # Quick heuristics to determine if content needs better formatting
    has_proper_headers = bool(re.search(r'^#{1,3}\s+.+$', content, re.MULTILINE))
    has_proper_bullets = bool(re.search(r'^-\s+.+$', content, re.MULTILINE))
    has_proper_paragraphs = len(content.split('\n\n')) > 2
    is_cramped_text = bool(re.search(r'[^.\n][أ-ي].*?[أ-ي][^.\n]', content.replace(' ', '')))
    
    # If text is cramped or lacks proper structure, it needs formatting
    return is_cramped_text or (not has_proper_headers and not has_proper_bullets and not has_proper_paragraphs)