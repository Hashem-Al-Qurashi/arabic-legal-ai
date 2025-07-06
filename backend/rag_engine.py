"""
Optimized Multi-Domain RAG Engine - Fast & Reliable
Balanced approach: Quality responses with reasonable speed
Supports: Legal, Financial, Administrative, and Technical consultations
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import markdown
from typing import List, Dict

# Load env variables
load_dotenv(".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ API key missing")

# Init DeepSeek
deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

def ask_question(query: str) -> str:
    """
    Optimized consultation with smart category detection and balanced prompting.
    """
    print(f"🤖 سؤال المستخدم: {query}")

    # Detect legal litigation for strategic response
    if any(phrase in query for phrase in ["الرد القانونى على دعوى", "رد على الدعوى"]):
        enhanced_query = f"""قم بإعداد رد قانوني شامل ومتقدم:

{query}

مطلوب: رد قانوني متكامل يتضمن:
- دفوع موضوعية وشكلية قوية
- استشهادات بالمواد النظامية
- استراتيجية إثبات وأدلة
- طلبات مضادة مناسبة
- صيغة رسمية قابلة للتقديم للمحكمة"""

    # Detect financial/business questions
    elif any(word in query for word in ["جدوى", "مشروع", "استثمار", "مالية", "ربح", "خسارة"]):
        enhanced_query = f"""قدم تحليلاً مالياً شاملاً ومتخصصاً:

{query}

مطلوب: دراسة مالية متكاملة تشمل:
- تحليل التكاليف والإيرادات
- دراسة الجدوى الاقتصادية
- تقييم المخاطر والفرص
- توصيات استراتيجية عملية
- خطة تنفيذية واضحة"""

    # Detect administrative questions
    elif any(word in query for word in ["إجراءات", "رخصة", "تصريح", "وزارة", "موافقة"]):
        enhanced_query = f"""قدم دليلاً إدارياً شاملاً:

{query}

مطلوب: دليل إداري متكامل يشمل:
- خطوات تنفيذية مفصلة
- المستندات المطلوبة
- الجهات المختصة
- الجدول الزمني
- نصائح عملية مفيدة"""

    # Detect technical questions  
    elif any(word in query for word in ["نظام", "تقنية", "برمجة", "شبكة", "أمان"]):
        enhanced_query = f"""قدم استشارة تقنية متخصصة:

{query}

مطلوب: حل تقني شامل يتضمن:
- تحليل المتطلبات التقنية
- الحلول المتاحة والمقترحة
- خطة التنفيذ العملية
- إجراءات الأمان والحماية
- أفضل الممارسات"""

    else:
        # General legal/business consultation
        enhanced_query = f"""قدم استشارة شاملة ومتخصصة:

{query}

مطلوب: استشارة متكاملة تشمل التحليل القانوني والعملي مع توصيات واضحة وقابلة للتطبيق."""

    try:
        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": enhanced_query}],
            temperature=0.3,   # Balanced for speed and quality
            max_tokens=4000,   # Optimized for speed while maintaining quality
            timeout=90         # 90 second timeout to prevent hanging
        )

        answer_raw = response.choices[0].message.content
        print("✅ الرد (نص خام):", answer_raw[:200] + "...")

        # Convert Markdown to HTML for the frontend
        answer_html = markdown.markdown(answer_raw)
        return answer_html

    except Exception as e:
        print(f"❌ خطأ في الاستعلام: {e}")
        return f"<p>عذراً، حدث خطأ تقني أثناء معالجة السؤال. يرجى المحاولة مرة أخرى.</p><p>تفاصيل الخطأ: {str(e)}</p>"


def ask_question_with_context(query: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    Optimized conversational consultation with context awareness.
    """
    print("🧠 USING OPTIMIZED CONSULTANT!")
    print(f"🤖 سؤال المستخدم مع السياق: {query}")
    print(f"📚 عدد الرسائل السابقة: {len(conversation_history)}")

    # Build messages with conversation history
    messages = []
    
    # Add recent conversation history (limit to last 6 messages for speed)
    recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
    for msg in recent_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Smart enhancement based on question type
    if any(phrase in query for phrase in ["الرد القانونى على دعوى", "رد على الدعوى"]):
        enhanced_query = f"""بناءً على السياق السابق، قم بإعداد رد قانوني متقدم:

{query}

مطلوب: رد قانوني شامل يراعي المناقشات السابقة ويتضمن استراتيجية دفاعية متكاملة وأدلة قوية."""

    elif any(word in query for word in ["جدوى", "مشروع", "استثمار", "مالية"]):
        enhanced_query = f"""بناءً على السياق السابق، قدم تحليلاً مالياً متقدماً:

{query}

مطلوب: تحليل مالي شامل يراعي المناقشات السابقة مع توصيات استراتيجية عملية."""

    else:
        enhanced_query = f"""بناءً على السياق السابق، قدم استشارة شاملة:

{query}

مطلوب: استشارة متكاملة تراعي المناقشات السابقة مع توصيات عملية واضحة."""

    # Add current enhanced question
    messages.append({
        "role": "user",
        "content": enhanced_query
    })

    try:
        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,   # Balanced for speed and quality
            max_tokens=4000,   # Optimized for speed
            timeout=90         # 90 second timeout
        )

        answer_raw = response.choices[0].message.content
        print("✅ الرد مع السياق (نص خام):", answer_raw[:200] + "...")

        # Convert Markdown to HTML for the frontend
        answer_html = markdown.markdown(answer_raw)
        return answer_html

    except Exception as e:
        print(f"❌ خطأ في الاستعلام مع السياق: {e}")
        return f"<p>عذراً، حدث خطأ تقني أثناء معالجة السؤال. يرجى المحاولة مرة أخرى.</p><p>تفاصيل الخطأ: {str(e)}</p>"


def generate_conversation_title(first_message: str) -> str:
    """
    Fast conversation title generation.
    """
    try:
        prompt = f"اقترح عنواناً مختصراً (أقل من 40 حرف): {first_message[:100]}"

        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50,    # Very small for speed
            timeout=30        # Quick timeout for titles
        )

        title = response.choices[0].message.content.strip()
        title = title.strip('"').strip("'").strip()
        
        # Remove common prefixes
        prefixes = ["العنوان:", "المقترح:", "الاستشارة:"]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        return title if len(title) <= 40 else title[:37] + "..."
        
    except Exception as e:
        print(f"❌ خطأ في توليد العنوان: {e}")
        return first_message[:37] + "..." if len(first_message) > 40 else first_message