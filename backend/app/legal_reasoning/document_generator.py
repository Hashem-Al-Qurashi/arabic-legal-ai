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
    
    def _generate_execution_dispute_prompt(
    self, 
    query: str, 
    retrieved_chunks: List[Chunk], 
    legal_issue: LegalIssue,
    document_type: DocumentType
) -> str:
        """Generate execution court dispute memo with 5-defense structure"""
        legal_context = self._format_legal_context(retrieved_chunks)
        return f"""أنت محامي متخصص في قضاء التنفيذ. اكتب منازعة تنفيذ رسمية بالهيكل المعتمد
📚 **الأساس القانوني:**
{legal_context}

🏛️ **منازعة التنفيذ:**
{query}

**مطلوب: منازعة تنفيذ كاملة وجاهزة للتقديم**

---

**منازعة تنفيذ**

**إلى فضيلة رئيس محكمة التنفيذ**

**الموضوع:** منازعة تنفيذ

**إشارة إلى:** [رقم الصك أو القرار]

**الدفع الأول:** [أقوى دفع إجرائي]
- **الأساس النظامي:** وفقاً للمادة (X) من نظام التنفيذ
- **التطبيق:** [تطبيق محدد على وقائع القضية]

**الدفع الثاني:** [دفع موضوعي قوي]
- **الأساس النظامي:** بموجب المادة (Y) من اللائحة التنفيذية
- **التطبيق:** [التطبيق المحدد]

**الدفع الثالث:** [دفع شرعي أو نظامي]
- **الأساس الشرعي/النظامي:** استناداً للمادة (Z)
- **التطبيق:** [التطبيق على الحالة]

**الدفع الرابع:** [دفع إضافي حسب القضية]
- **الأساس النظامي:** حسب المادة (W)
- **التطبيق:** [التطبيق المناسب]

**الدفع الخامس:** [الدفع الاحتياطي]
- **الأساس النظامي:** وفقاً للمادة (V)
- **التطبيق:** [التطبيق الاحتياطي]

**بناءً على ذلك نطلب من فضيلتكم:**
١- وقف إجراءات التنفيذ
٢- رفض طلب التنفيذ لعدم توفر الشروط النظامية
٣- تحميل طالب التنفيذ الرسوم والمصاريف

**والله الموفق**

---

**⚠️ تعليمات حاسمة:**
- استخدم فقط المواد القانونية من المراجع المرفقة
- اربط كل دفع بمادة نظامية محددة
- اكتب منازعة جاهزة للتقديم مباشرة
- لا نصائح أو شروحات - فقط المذكرة القانونية"""

    def generate_document_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate family court memo with intensive fiqh integration"""
        legal_context = self._format_legal_context(retrieved_chunks)
        return f"""أنت محامي متخصص في الأحوال الشخصية. اكتب مذكرة جوابية بالأصول الشرعية.

📚 **الأساس الشرعي والنظامي:**
{legal_context}

👨‍👩‍👧‍👦 **قضية الأحوال الشخصية:**
{query}

**مطلوب: مذكرة جوابية شرعية كاملة**

---

**مذكرة جوابية**

**إلى صاحب الفضيلة رئيس دائرة الأحوال الشخصية**

**الموضوع:** [موضوع القضية]

**أولاً: إنكار ما جاء في الدعوى جملة وتفصيلاً**

**ثانياً: الدفوع الشرعية والنظامية:**

**١-** [الدفع الإجرائي الأول]
- **الأساس الشرعي:** قال في المبسوط: [نص فقهي مناسب]
- **الأساس النظامي:** وفقاً للمادة (X) من نظام المرافعات الشرعية
- **التطبيق:** [التطبيق على وقائع القضية]

**٢-** [دفع موضوعي بالأدلة الشرعية]
- **الأساس الشرعي:** جاء في العناية شرح الهداية: [نص فقهي]
- **الأساس النظامي:** بموجب المادة (Y) من نظام الأحوال الشخصية
- **التطبيق:** [التطبيق المحدد]

**٣-** [دفع بالبينة الشرعية]
- **الأساس الشرعي:** قال في التاج والإكليل: [نص فقهي]
- **قاعدة شرعية:** البينة على من ادعى واليمين على من أنكر
- **التطبيق:** [كيف ينطبق على القضية]

**٤-** [دفع بأصول الشريعة]
- **الأساس الشرعي:** ذكر في مواهب الجليل: [نص فقهي]
- **المبدأ الشرعي:** الأصل في العقود السلامة والصحة
- **التطبيق:** [التطبيق الشرعي]

**٥-** [الدفع الاحتياطي]
- **الأساس الشرعي:** نص في المغني لابن قدامة: [نص فقهي]
- **القاعدة:** من سعى لنقض ما تم على يده فسعيه مردود عليه
- **التطبيق:** [التطبيق النهائي]

**ثالثاً: الطلبات:**
أولاً: رفض الدعوى لعدم صحتها شرعاً ونظاماً
ثانياً: تحميل المدعي الرسوم والمصاريف
ثالثاً: [طلبات إضافية حسب القضية]

**والله أعلم وأحكم**

---

**⚠️ تعليمات شرعية حاسمة:**
- استخدم فقط المصادر الفقهية من المراجع المرفقة
- اربط كل دفع بنص فقهي محدد + مادة نظامية
- اكتب مذكرة جاهزة للتقديم للمحكمة الشرعية
- استخدم المصطلحات الفقهية الدقيقة"""

    def generate_document_prompt(
        self, 
        query: str, 
        retrieved_chunks: List[Chunk], 
        legal_issue: LegalIssue,
        document_type: DocumentType
    ) -> str:
        """Generate document-specific prompt based on document type analysis"""
        
        if document_type.specific_type == 'execution_dispute':
            return self._generate_execution_dispute_prompt(query, retrieved_chunks, legal_issue, document_type)
    
    # Your existing conditions continue...
        elif document_type.specific_type == 'defense_memo':
            return self._generate_defense_memo_prompt(query, retrieved_chunks, legal_issue, document_type)
    
        elif document_type.specific_type == 'lawsuit':
            return self._generate_lawsuit_prompt(query, retrieved_chunks, legal_issue, document_type)
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
        
    
        elif document_type.specific_type == 'execution_dispute':
            return self._generate_execution_dispute_prompt(query, retrieved_chunks, legal_issue, document_type)
    
        elif document_type.specific_type == 'family_inheritance_challenge':
            return self._generate_family_inheritance_memo(query, retrieved_chunks, legal_issue, document_type)
    
    # Your existing conditions continue...
        
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
    

    def _generate_appeal_prompt(
    self, 
    query: str, 
    retrieved_chunks: List[Chunk], 
    legal_issue: LegalIssue,
    document_type: DocumentType
) -> str:
        """Generate appeal memo prompt"""
        legal_context = self._format_legal_context(retrieved_chunks)
    
        return f"""أنت محامي استئناف متخصص. اكتب لائحة اعتراضية كاملة وجاهزة للتقديم
📚 **الأساس القانوني:**
{legal_context}

⚖️ **موضوع الاستئناف:**
{query}

**مطلوب: لائحة اعتراضية رسمية وكاملة**

---

**لائحة اعتراضية**

**إلى فضيلة رئيس وأعضاء محكمة الاستئناف**

**الموضوع:** لائحة اعتراضية على [موضوع الحكم]

**أولاً: عدم صحة الحكم المستأنف**
- **الأساس النظامي:** وفقاً للمادة (X) من نظام المرافعات الشرعية
- **التطبيق:** [تطبيق محدد على وقائع القضية]

**ثانياً: مخالفة أحكام الشريعة الإسلامية**
- **الأساس الشرعي:** [النص الشرعي المناسب]
- **التطبيق:** [كيف تم انتهاك الحكم الشرعي]

**ثالثاً: الفساد في الاستدلال والعوار**
- **الأساس النظامي:** بموجب المادة (Y) من النظام
- **التطبيق:** [تحديد أوجه الفساد في الاستدلال]

**بناءً على ذلك نطلب من فضيلتكم:**
أولاً: نقض الحكم المستأنف
ثانياً: الحكم بـ [الطلب المحدد]
ثالثاً: تحميل المدعي المصاريف والرسوم

**والله الموفق**

---

**تعليمات:**
- استخدم فقط المواد القانونية من المراجع المرفقة
- اربط كل اعتراض بمادة نظامية محددة
- اكتب لائحة جاهزة للتقديم مباشرة"""

    def _format_legal_context(self, retrieved_chunks: List[Chunk]) -> str:
        """Format retrieved legal documents for context"""
        if not retrieved_chunks:
            return "سيتم الاعتماد على المعرفة القانونية العامة بالأنظمة السعودية."
        
        formatted_context = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            formatted_context.append(f"📄 **المرجع {i}: {chunk.title}**\n{chunk.content}")
        
        return "\n\n".join(formatted_context)