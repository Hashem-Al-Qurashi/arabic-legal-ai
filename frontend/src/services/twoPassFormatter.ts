/**
 * Two-Pass Formatting System for Ultimate Quality
 * Inspired by ChatGPT's own methodology
 */

import { chatAPI } from './api';

export const FORMATTER_SYSTEM_PROMPT = `أنت منسق Markdown صارم للنصوص القانونية العربية. لا تغير المعنى أو تضيف حقائق. أعد تنسيق النص المقدم ليطيع هذا العقد بالضبط:

## مهمتك
- أعد تنسيق النص فقط، لا تغير المحتوى أو المعنى
- حول النص إلى Markdown مثالي مع تنظيم احترافي
- **أصلح الكلمات المكسورة** - تأكد أن كل كلمة عربية كاملة في سطر واحد

## قواعد التنسيق الصارمة
- ابدأ بخلاصة من سطر واحد إذا لم تكن موجودة
- استخدم العناوين (# للعناوين الرئيسية، ## للفرعية، ### للتفاصيل)
- **مهم جداً**: تأكد أن العناوين كاملة في سطر واحد بدون كسر الكلمات
- حول أي قوائم إلى نقاط منظمة (- للنقاط)
- ضع **النص الهام** بين نجمتين للتأكيد
- استخدم فقرات قصيرة منفصلة بأسطر فارغة
- نظم الأرقام والنقاط بوضوح

## إصلاح النص العربي
- إذا رأيت كلمة مكسورة عبر أسطر (مثل "المقدم" + سطر جديد + "ة") اجمعها: "المقدمة"
- إذا رأيت "القانون" + سطر جديد + "ي" اجمعها: "القانوني"
- تأكد أن كل عنوان كامل في سطر واحد

## للمحتوى القانوني
- نظم المواد القانونية تحت عناوين واضحة
- ضع المراجع والاقتباسات في تنسيق منظم
- استخدم قوائم للخطوات والإجراءات
- اجعل كل قسم منفصل ومرقم

## إذا كان النص منظماً بالفعل
- أرجعه كما هو دون تغيير

عالج النص التالي:`;

/**
 * Apply two-pass formatting to content for ultimate quality
 */
export async function applyTwoPassFormatting(content: string): Promise<string> {
  try {
    // Pass 1: Check if content needs formatting
    const needsFormatting = checkIfNeedsFormatting(content);
    
    if (!needsFormatting) {
      console.log('✅ Content already well-formatted, skipping second pass');
      return content;
    }

    console.log('🔄 Applying two-pass formatting for ultimate quality...');
    
    // Pass 2: Send to AI for perfect formatting
    const formattedContent = await formatWithAI(content);
    
    return formattedContent;
  } catch (error) {
    console.warn('⚠️ Two-pass formatting failed, using original:', error);
    return content; // Fallback to original content
  }
}

/**
 * Check if content needs AI formatting
 */
function checkIfNeedsFormatting(content: string): boolean {
  // Quick heuristics to determine if content needs better formatting
  const hasProperHeaders = /^#{1,3}\s+.+$/m.test(content);
  const hasProperBullets = /^-\s+.+$/m.test(content);
  const hasProperParagraphs = content.split('\n\n').length > 2;
  const isCrammedText = /[^.\n][أ-ي].*?[أ-ي][^.\n]/g.test(content.replace(/\s+/g, ''));
  
  // If text is cramped or lacks proper structure, it needs formatting
  return isCrammedText || (!hasProperHeaders && !hasProperBullets && !hasProperParagraphs);
}

/**
 * Send content to AI for perfect formatting
 */
async function formatWithAI(content: string): Promise<string> {
  const formData = new FormData();
  formData.append('message', content);
  formData.append('system_prompt', FORMATTER_SYSTEM_PROMPT);
  formData.append('skip_history', 'true'); // Don't save this formatting conversation

  const response = await fetch('https://d2c979d13bkvf4.cloudfront.net/api/chat/message', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      ...(localStorage.getItem('access_token') && { 
        'Authorization': `Bearer ${localStorage.getItem('access_token')}` 
      }),
    },
    body: formData
  });

  if (!response.ok) {
    throw new Error(`Formatting API failed: ${response.status}`);
  }

  const data = await response.json();
  return data.ai_message?.content || data.answer || content;
}

/**
 * Enhanced streaming formatter with optional two-pass
 */
export async function enhancedStreamingFormatter(
  content: string,
  enableTwoPass: boolean = true
): Promise<string> {
  // Always apply basic cleanup first
  const basicFormatted = applyBasicFormatting(content);
  
  // If two-pass is enabled and content needs it, apply AI formatting
  if (enableTwoPass) {
    return await applyTwoPassFormatting(basicFormatted);
  }
  
  return basicFormatted;
}

/**
 * Basic formatting that always runs (lightweight)
 */
function applyBasicFormatting(content: string): string {
  return content
    .replace(/\r\n/g, '\n')           // Normalize line endings
    .replace(/\\\s*$/gm, '')          // Remove trailing backslashes
    .replace(/\n{4,}/g, '\n\n\n')     // Max 3 consecutive newlines
    .replace(/([^\n])(#{1,4}\s)/g, '$1\n\n$2') // Space before headers
    .replace(/([^\n])(أولاً|ثانياً|ثالثاً|رابعاً|خامساً):/g, '$1\n\n## $2:') // Arabic ordinals
    .trim();
}