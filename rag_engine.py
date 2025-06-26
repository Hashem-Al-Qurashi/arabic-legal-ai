import os
from dotenv import load_dotenv
from openai import OpenAI

# ✅ Load env variables
load_dotenv(".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ API key missing")

# ✅ Init DeepSeek
deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# ✅ Talk directly to DeepSeek
def ask_question(query):
    print(f"🤖 سؤال المستخدم: {query}")

    prompt = f"""أنت مساعد قانوني ومالي وإداري ذكي سعودي. أجب باحترافية ودقة باللغة العربية واللهجة السعودية فقط بناءً على معرفتك بالقوانين والأنظمة السعودية مع الاستدلال بالمادة ,لغتك العربية فصيحة وادبية ولست كأنك مترجم.

السؤال:
{query}

الإجابة:"""

    response = deepseek.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    print("✅ الرد:", answer)
    return answer
