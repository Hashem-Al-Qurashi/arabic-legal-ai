"""
Enhanced RAG engine with conversation context support.
Maintains conversation memory for better legal advice.
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
    Original function - single question without context.
    Kept for backward compatibility.
    """
    print(f"🤖 سؤال المستخدم: {query}")

    prompt = f"""أنت مساعد قانوني ومالي وإداري ذكي سعودي. أجب باحترافية ودقة باللغة العربية واللهجة السعودية فقط بناءً على معرفتك بالقوانين والأنظمة السعودية مع الاستدلال بالمادة. لغتك عربية فصيحة وأدبية ولست كأنك مترجم.

السؤال:
{query}

الإجابة:"""

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    answer_raw = response.choices[0].message.content
    print("✅ الرد (نص خام):", answer_raw)

    # Convert Markdown to HTML for the frontend
    answer_html = markdown.markdown(answer_raw)
    return answer_html


def ask_question_with_context(query: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    Enhanced function - question with full conversation context.
    Provides context-aware legal advice based on conversation history.
    """
    print(f"🤖 سؤال المستخدم مع السياق: {query}")
    print(f"📚 عدد الرسائل السابقة: {len(conversation_history)}")

    # Build conversation context for AI
    messages = [
        {
            "role": "system", 
            "content": """أنت مساعد قانوني ومالي وإداري ذكي سعودي متخصص. 

خصائصك:
- تجيب باحترافية ودقة باللغة العربية الفصيحة
- تستند إلى القوانين والأنظمة السعودية مع ذكر المواد
- تحافظ على سياق المحادثة السابقة
- تربط إجاباتك بما سبق مناقشته
- تقدم نصائح قانونية متدرجة ومفصلة

إرشادات:
- إذا كان السؤال مرتبطاً بموضوع سابق، اربط إجابتك به
- إذا كان السؤال جديداً، قدم إجابة شاملة
- استخدم عبارات مثل "بناءً على ما ذكرناه سابقاً" أو "تكملة لما تحدثنا عنه"
- قدم نصائح عملية وقابلة للتطبيق"""
        }
    ]
    
    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current question
    messages.append({
        "role": "user",
        "content": query
    })

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,  # Slightly more creative for conversational responses
        max_tokens=2000   # Longer responses for detailed legal advice
    )

    answer_raw = response.choices[0].message.content
    print("✅ الرد مع السياق (نص خام):", answer_raw[:100] + "...")

    # Convert Markdown to HTML for the frontend
    answer_html = markdown.markdown(answer_raw)
    return answer_html


def generate_conversation_title(first_message: str) -> str:
    """
    Generate a concise title for a conversation based on the first message.
    """
    try:
        prompt = f"""اقترح عنواناً مختصراً ومفيداً لهذه المحادثة القانونية (أقل من 50 حرف):

الرسالة الأولى: {first_message}

العنوان المقترح:"""

        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50
        )

        title = response.choices[0].message.content.strip()
        # Remove quotes if present
        title = title.strip('"').strip("'")
        
        return title if len(title) <= 50 else title[:47] + "..."
        
    except Exception as e:
        print(f"❌ خطأ في توليد العنوان: {e}")
        # Fallback to first 50 characters of message
        return first_message[:47] + "..." if len(first_message) > 50 else first_message