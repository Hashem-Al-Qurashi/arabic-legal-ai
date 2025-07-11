"""
Legal Document Generator - The Core of Lawyer Extinction System
Generates court-ready, professional legal documents that rival senior lawyers
"""

from typing import List, Dict, Any, Optional
from app.storage.vector_store import Chunk
from app.legal_reasoning.issue_analyzer import LegalIssue
from app.legal_reasoning.document_type_analyzer import DocumentType

class LegalDocumentGenerator:
    """Generates production-ready legal documents for specific use cases"""
    
    def __init__(self):
        """Initialize document generation templates and strategies"""
        pass
    
    def generate_document_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate document-specific prompt based on document type analysis"""
        
        # Route to specific document generator
        if document_type.specific_type == 'defense_memo':
            return self._generate_defense_memo_prompt(query, retrieved_chunks, legal_issue, document_type)
        
        elif document_type.specific_type == 'lawsuit':
            return self._generate_lawsuit_prompt(query, retrieved_chunks, legal_issue, document_type)
        
        elif document_type.specific_type == 'appeal':
            return self._generate_appeal_prompt(query, retrieved_chunks, legal_issue, document_type)
        
        elif document_type.specific_type in ['sale_contract', 'employment_contract', 'lease_contract']:
            return self._generate_contract_prompt(query, retrieved_chunks, legal_issue, document_type)
        
        elif document_type.specific_type == 'demand_letter':
            return self._generate_demand_letter_prompt(query, retrieved_chunks, legal_issue, document_type)
        
        else:
            # Fallback to consultation
            return self._generate_consultation_prompt(query, retrieved_chunks, legal_issue)
    
    def _generate_defense_memo_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
) -> str:
        """Generate court-ready defense memo - PURE COURT DOCUMENT"""
    
        legal_context = self._format_legal_context(retrieved_chunks)
    
        return f"""أنت أفضل محامي دفاع في المحاكم السعودية. اكتب مذكرة دفاع رسمية جاهزة للتقديم مباشرة للمحكمة.

📚 **الأساس القانوني:**
{legal_context}

📋 **وقائع الدعوى:**
{query}

**اكتب مذكرة دفاع كاملة وجاهزة للتقديم:**

---

**مذكرة دفاع**

**أولاً: الوقائع**
تتلخص وقائع الدعوى في: [اكتب الوقائع باختصار وبناءً على المعطيات - التواريخ والمبالغ والأطراف المحددة]

**ثانياً: الدفوع القانونية**

**الدفع الأول:** [اكتب الدفع الأقوى بناءً على الوقائع]
- الأساس القانوني: [المادة المحددة من الأنظمة المرفقة]
- التطبيق: [كيف ينطبق على هذه القضية تحديداً]

**الدفع الثاني:** [اكتب الدفع الثاني]
- الأساس القانوني: [المادة المحددة]
- التطبيق: [التطبيق على الوقائع]

**الدفع الثالث:** [اكتب الدفع الثالث إن وجد]
- الأساس القانوني: [المادة المحددة]
- التطبيق: [التطبيق على الوقائع]

**ثالثاً: المرفقات**
- مرفق (1): [حدد المستند الأول المطلوب]
- مرفق (2): [حدد المستند الثاني المطلوب]
- مرفق (3): [حدد المستند الثالث إن وجد]

**رابعاً: الطلبات**
بناءً على ما تقدم، ألتمس من الدائرة الموقرة:

1. الحكم برفض الدعوى لعدم صحتها قانوناً
2. تحميل المدعي كافة الرسوم والمصاريف القضائية
3. [أي طلبات إضافية مناسبة للقضية]

**والله الموفق**

---

**قواعد الكتابة الصارمة:**
- اكتب مذكرة دفاع فقط - لا نصائح ولا تحذيرات ولا شروحات
- استخدم الوقائع المحددة في القضية فقط (التواريخ والمبالغ والأسماء)
- اربط كل دفع بمادة قانونية محددة من المراجع المرفقة
- اكتب طلبات واضحة ومحددة في النهاية
- لا تذكر "خطوات عملية" أو "تحذيرات" - هذه مذكرة قضائية وليست استشارة"""

    def _generate_lawsuit_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate court-ready lawsuit filing"""
        
        legal_context = self._format_legal_context(retrieved_chunks)
        
        return f"""أنت أفضل محامي تقاضي في المملكة العربية السعودية. مطلوب منك كتابة لائحة دعوى جاهزة للتقديم مباشرة للمحكمة.

📚 **الأساس القانوني:**
{legal_context}

📋 **تفاصيل القضية المطلوب رفع دعوى بها:**
{query}

**مطلوب منك: كتابة صحيفة دعوى رسمية وكاملة**

**🏛️ قواعد الكتابة الإجبارية:**
1. اكتب صحيفة دعوى كاملة وجاهزة للتقديم
2. حدد المحكمة المختصة بدقة
3. اكتب البيانات والوقائع والطلبات بوضوح
4. اربط كل طلب بالأساس القانوني المحدد

**📋 الهيكل الإجباري لصحيفة الدعوى:**

**صحيفة دعوى مدنية**

**إلى فضيلة رئيس [المحكمة المختصة]**

**بيانات المدعي:**
الاسم: [حسب القضية]
الصفة: [حسب القضية]
العنوان: [حسب القضية]

**بيانات المدعى عليه:**
الاسم: [حسب القضية]
الصفة: [حسب القضية]
العنوان: [حسب القضية إن وجد]

**موضوع الدعوى:**
[وصف موجز ودقيق]

**الوقائع:**
[ترقيم الوقائع وترتيبها زمنياً]

**الأسانيد القانونية:**
[ربط الوقائع بالمواد القانونية من المراجع المرفقة]

**الطلبات:**
بناءً على ما تقدم، ألتمس من فضيلتكم:
أولاً: [الطلب الأساسي]
ثانياً: [الطلبات الفرعية]
ثالثاً: تحميل المدعى عليه المصاريف وأتعاب المحاماة

**التوقيع:** 
التاريخ:

**هذه دعواي والله الموفق**

**⚠️ تعليمات حاسمة:**
- اكتب صحيفة دعوى كاملة وقابلة للتقديم فوراً
- استخدم الوقائع المحددة من القضية فقط
- اربط كل طلب بالمادة القانونية المناسبة
- حدد المحكمة المختصة بدقة"""

    def _generate_contract_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate complete legal contract"""
        
        contract_type_map = {
            'sale_contract': 'بيع',
            'employment_contract': 'عمل', 
            'lease_contract': 'إيجار',
            'partnership_contract': 'شراكة',
            'service_contract': 'خدمات'
        }
        
        contract_name = contract_type_map.get(document_type.specific_type, 'تعاقد')
        legal_context = self._format_legal_context(retrieved_chunks)
        
        return f"""أنت أفضل محامي عقود في المملكة العربية السعودية. مطلوب منك كتابة عقد {contract_name} كامل وجاهز للتوقيع.

📚 **الأساس القانوني للعقد:**
{legal_context}

📋 **تفاصيل العقد المطلوب:**
{query}

**مطلوب منك: كتابة عقد {contract_name} كامل وجاهز للتوقيع**

**🏛️ قواعد الكتابة الإجبارية:**
1. اكتب عقد {contract_name} كامل مع جميع البنود الأساسية
2. استخدم الصياغة القانونية الدقيقة
3. ضع بنود واضحة لحماية الطرفين
4. اربط العقد بالأنظمة السعودية المعمول بها

**📋 هيكل العقد:**

**عقد {contract_name}**

**الطرف الأول:** [بيانات الطرف الأول]
**الطرف الثاني:** [بيانات الطرف الثاني]

**تمهيد:**
[وصف موجز لطبيعة العقد والغرض منه]

**البنود والشروط:**

**البند الأول: موضوع العقد**
[تفصيل موضوع العقد بدقة]

**البند الثاني: التزامات الطرف الأول**
[التزامات محددة وواضحة]

**البند الثالث: التزامات الطرف الثاني**  
[التزامات محددة وواضحة]

**البند الرابع: المقابل المالي** 
[تحديد دقيق للمبالغ والمواعيد]

**البند الخامس: مدة العقد**
[تحديد دقيق للمدة وشروط التجديد]

**البند السادس: شروط الإنهاء**
[حالات وإجراءات إنهاء العقد]

**البند السابع: حل النزاعات**
[آلية حل النزاعات والقانون الحاكم]

**البند الثامن: أحكام عامة**
[البنود العامة والختامية]

**التوقيعات:**
الطرف الأول: _________________ التاريخ: _________
الطرف الثاني: _________________ التاريخ: _________

**⚠️ تعليمات حاسمة:**
- اكتب عقد {contract_name} كامل وجاهز للتوقيع
- استخدم فقط التفاصيل الواردة في الطلب
- اجعل العقد متوازناً ويحمي الطرفين
- اربط البنود بالأنظمة السعودية المناسبة"""

    def _generate_demand_letter_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate formal demand letter"""
        
        legal_context = self._format_legal_context(retrieved_chunks)
        
        return f"""أنت محامي متخصص في كتابة الخطابات القانونية. مطلوب منك كتابة خطاب إنذار رسمي وقوي.

📚 **الأساس القانوني:**
{legal_context}

📋 **تفاصيل الإنذار المطلوب:**
{query}

**مطلوب منك: كتابة خطاب إنذار رسمي وجاهز للإرسال**

**📋 هيكل خطاب الإنذار:**

**خطاب إنذار قانوني**

**إلى السيد/السيدة:** [اسم المرسل إليه]
**العنوان:** [عنوان المرسل إليه]

**الموضوع:** إنذار قانوني - [موضوع الإنذار]

**المحترم/المحترمة،**

**أولاً: الوقائع**
[سرد الوقائع بوضوح وترتيب زمني]

**ثانياً: الأساس القانوني**  
[الاستناد للمواد القانونية المناسبة]

**ثالثاً: المطالبة**
[تحديد المطالبة بوضوح ودقة]

**رابعاً: الإنذار**
عليه، أنذركم بضرورة [تحديد الإجراء المطلوب] خلال مدة [تحديد المدة] من تاريخ تسلم هذا الإنذار.

**خامساً: التحذير**
في حالة عدم الاستجابة للمطالبة خلال المدة المحددة، سنضطر لاتخاذ الإجراءات القانونية اللازمة لحفظ الحقوق.

**وتفضلوا بقبول فائق الاحترام**

**التوقيع:** ________________
**التاريخ:** ________________

**⚠️ تعليمات حاسمة:**
- اكتب خطاب إنذار رسمي وقوي
- استخدم لغة قانونية مؤثرة ومقنعة
- حدد المطالبة والمدة بوضوح
- اربط الإنذار بالأساس القانوني المناسب"""

    def _generate_consultation_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue
    ) -> str:
        """Generate legal consultation for advisory queries"""
        
        legal_context = self._format_legal_context(retrieved_chunks)
        
        return f"""أنت مستشار قانوني سعودي خبير. مطلوب منك تقديم استشارة قانونية شاملة ومفيدة.

📚 **المراجع القانونية:**
{legal_context}

❓ **الاستفسار القانوني:**
{query}

**مطلوب منك: استشارة قانونية شاملة وعملية**

قدم استشارة قانونية تشمل:
- تحليل الوضع القانوني بناءً على الأنظمة السعودية
- الحقوق والالتزامات ذات الصلة
- الخطوات العملية المطلوبة إن وجدت
- التحذيرات والاحتياطات المهمة
- المراجع القانونية المناسبة

استخدم لغة واضحة ومباشرة مع التركيز على الحلول العملية."""

    def _format_legal_context(self, retrieved_chunks: List[Chunk]) -> str:
        """Format retrieved legal documents for context"""
        if not retrieved_chunks:
            return "سيتم الاعتماد على المعرفة القانونية العامة بالأنظمة السعودية."
        
        formatted_context = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            formatted_context.append(f"📄 **المرجع {i}: {chunk.title}**\n{chunk.content}")
        
        return "\n\n".join(formatted_context)