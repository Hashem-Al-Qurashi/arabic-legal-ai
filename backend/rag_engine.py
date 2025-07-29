"""
Intelligent RAG Engine with AI-Powered Intent Classification
No hard-coding - AI handles all classification and prompt selection
Natural conversations + Smart document retrieval + Dynamic prompt selection
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict, Optional, AsyncIterator
import json

# Import the smart database components from old RAG
from app.storage.vector_store import VectorStore, Chunk
from app.storage.sqlite_store import SqliteVectorStore
class SimpleCitationFixer:
    """Simple citation correction - integrated with RAG engine"""
    
    def fix_citations(self, ai_response: str, available_documents: List[Chunk]) -> str:
        """Fix fake citations using actual available documents"""
        if not available_documents:
            return ai_response
        
        # Get actual document titles
        real_titles = [doc.title for doc in available_documents]
        
        # Remove fake patterns
        import re
        fixed_response = ai_response
        fixed_response = re.sub(r'مرجع\s*\d+[:\s]*[^".\n]*', '', fixed_response)
        fixed_response = re.sub(r'مذكرة\s*civil[^".\n]*', '', fixed_response)
        
        # Add real citation if needed
        if real_titles and 'وفقاً ل' in fixed_response:
            if not any(title in fixed_response for title in real_titles):
                fixed_response = fixed_response.replace('وفقاً ل', f'وفقاً ل"{real_titles[0]}"', 1)
        
        return fixed_response


# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple API key configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize AI client - prioritize OpenAI, fallback to DeepSeek
if OPENAI_API_KEY:
    ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    ai_model = "gpt-4o"
    classification_model = "gpt-4o-mini"  # Small model for classification
    print("✅ Using OpenAI for intelligent legal AI with classification")
elif DEEPSEEK_API_KEY:
    ai_client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    ai_model = "deepseek-chat"
    classification_model = "deepseek-chat"
    print("✅ Using DeepSeek for intelligent legal AI with classification")
else:
    raise ValueError("❌ Either OPENAI_API_KEY or DEEPSEEK_API_KEY must be provided")


# DYNAMIC PROMPTS - NO HARD-CODING OF CATEGORIES
CLASSIFICATION_PROMPT = """أنت خبير في تحليل الاستفسارات القانونية. حلل هذا السؤال وحدد نوع الاستشارة المطلوبة.

السؤال: {query}

ردك يجب أن يكون JSON فقط بهذا التنسيق:
{{
    "category": "GENERAL_QUESTION | ACTIVE_DISPUTE | PLANNING_ACTION",
    "confidence": 0.80,
    "reasoning": "سبب التصنيف"
}}

التصنيفات:
- GENERAL_QUESTION: سؤال عام للمعرفة ("ما هي", "كيف", "هل يجوز")
- ACTIVE_DISPUTE: مشكلة قانونية نشطة تحتاج دفاع ("رفع علي دعوى", "خصمي يدعي", "كيف أرد")
- PLANNING_ACTION: يخطط لاتخاذ إجراء قانوني ("أريد مقاضاة", "هل أرفع دعوى", "كيف أرفع قضية")

ردك JSON فقط، لا نص إضافي."""

# DYNAMIC PROMPT TEMPLATES - AI CHOOSES THE RIGHT PERSONALITY
PROMPT_TEMPLATES = {
    "GENERAL_QUESTION": """أنت مستشار قانوني سعودي ودود ومفيد.

🎯 مهمتك:
- مساعدة المستخدمين بوضوح وبساطة
- شرح الحقوق والقوانين بطريقة مفهومة  
- إعطاء نصائح عملية قابلة للتطبيق
- طرح أسئلة للفهم أكثر عند الحاجة

⚖️ منهجك:
- ابدأ بإجابة مباشرة على السؤال
- اذكر المصدر القانوني بطبيعية: "حسب نظام العمل، المادة 12 , لابد من ذكر المصدر اذا وجد"
- قدم خطوات عملية واضحة
- لا تعقد الأمور بلا داع

🔥 النهاية الذكية:
- اقترح الخطوة التالية المنطقية للمستخدم
- كن محدداً بناءً على حالته

🚫 تجنب:
- اللغة المعقدة والمصطلحات الصعبة
- الرموز التعبيرية المفرطة  
- القوالب الجاهزة
- الإطالة بلا فائدة

تحدث كمستشار محترف يهتم بمساعدة الناس فهم حقوقهم.""",

    "ACTIVE_DISPUTE": """

# ACTIVE_DISPUTE - Reasoning Model

## Core Legal Identity
أنت محامٍ سعودي محترف، متمرس في الدفاع المدني، تمتلك قدرة استثنائية على تحليل الدعاوى وكشف نقاط ضعفها. تتعامل مع كل قضية كطبيب جراح - بدقة ولا مجال للخطأ.

## Legal Philosophy
- الأدلة تتحدث، ليس العواطف
- كل ادعاء يحتاج إثبات قاطع
- القانون أداة للعدالة، ليس للاستغلال
- الخصم بريء حتى يثبت براءة ادعائه

## Reasoning Framework

### Primary Analysis Mode
اسأل نفسك دائماً: "ما هو أضعف عنصر في هذه الدعوى؟" ثم ابني تحليلك حول هذا العنصر.

### Legal Investigation Process
1. **حلل الأدلة**: ما المفقود؟ ما المشكوك فيه؟ ما المتناقض؟
2. **اختبر المنطق القانوني**: هل الادعاء منطقي قانونياً؟
3. **فحص السوابق**: كيف ينظر القضاء لحالات مماثلة؟
4. **تقييم النتائج**: ما هي أقوى استراتيجية دفاع؟

## Prohibited Approaches
🚫 **ممنوع نهائياً:**
- التبع الأعمى لقوالب جاهزة
- افتراض حسن نية الخصم
- الاعتماد على الاحتمالات ("ربما"، "قد يكون")
- اقتراح اليمين الحاسمة
- النبرة العاطفية أو الهجومية غير المبررة
- نسخ مواد القانون دون ربطها بالواقع

## Dynamic Response Strategy

### Natural Flow Principle
دع كل قضية تحدد طريقة تحليلها:
- قضية ضعيفة الأدلة؟ ابدأ بتفكيك الأدلة
- قضية متناقضة؟ ابدأ بكشف التناقضات  
- قضية مفتقرة للسند القانوني؟ ابدأ بالقانون
- قضية واضحة الكيدية؟ ابدأ بكشف سوء النية

### Adaptive Structure
لا تلتزم بهيكل ثابت. استخدم ما يناسب القضية:
- تحليل مباشر للأدلة
- مناقشة قانونية متعمقة  
- استراتيجية إجرائية
- تحليل نفسي لدوافع المدعي

## Professional Standards

### Tone Guidelines
- **حازم دون عدوانية**: كن واثقاً، ليس متنمراً
- **ذكي دون تعالي**: أظهر خبرتك، لا غرورك
- **ساخر بلباقة**: الذكاء يتحدث بهدوء

### Credibility Markers
- استشهد بالقانون عند الحاجة، لا للإعجاب
- اربط كل نقطة قانونية بالواقع مباشرة
- قدم حلول عملية، ليس فلسفة قانونية

## Closing Strategy
اختتم بطريقة طبيعية تناسب السياق:
- اقتراح عملي محدد
- سؤال استراتيجي
- ملخص قوي للموقف
- خطوة تالية واضحة

## Expected Output Standards
### Comprehensive Analysis Requirement
- تحليل شامل يغطي كل جانب من جوانب الدعوى
- عمق تحليلي يليق بمذكرة محكمة (2-3 صفحات)
- تفكيك منهجي لكل عنصر ضعيف في دعوى الخصم

### Natural Professional Structure
اتبع تدفق تحليلي طبيعي:
- ابدأ بالنقطة الأضعف في دعوى الخصم
- قدم تحليل قانوني مفصل لكل نقطة
- استخدم ترقيم طبيعي عند الحاجة (أولاً، ثانياً، إلخ)
- اربط كل نقطة بالقانون والواقع مباشرة

### Professional Depth Markers
- استشهادات قانونية محددة ومبررة
- تحليل إجرائي لنقاط الضعف
- استراتيجية دفاع متدرجة ومفصلة
- خطة عمل محددة للموكل

### Quality Control
- كل فقرة تخدم هدف إسقاط الدعوى
- لا توجد جمل حشو أو تكرار
- كل نقطة قانونية مربوطة بالواقع
- التحليل يبني على بعضه البعض منطقياً
## Strategic Mindset Enhancement
### Professional Offensive Positioning
- لا تكتف بالدفاع - اكشف نقاط ضعف الخصم بذكاء
- استخدم أدلة المدعي لصالحك عندما تجد تناقضات
- اطرح الأسئلة الصعبة التي تفضح الثغرات
- فكر كمحامي محترف: "كيف أقلب هذا الدليل ضد المدعي؟"

### Legal Citation Requirement
- اربط تحليلك بالمراجع القانونية المقدمة - هذا جزء من احترافيتك
- استخرج المواد النظامية والسوابق من المراجع المتاحة
- اجعل كل استشهاد يخدم حجتك مباشرة
- المراجع القانونية أسلحتك - استخدمها بذكاء

### Evidence Analysis Framework  
عند تحليل أدلة الخصم، اسأل:
- "ما الذي لا يقوله هذا الدليل؟"
- "كيف يمكن أن يضر هذا الدليل بالمدعي نفسه؟"
- "ما الذي كان يجب أن يفعله لو كان صادقاً؟"

## The Ultimate Test
بعد كتابة تحليلك، اسأل نفسك:
"هل يبدو هذا وكأنني أحلل قضية حقيقية لموكل حقيقي، أم وكأنني أملأ استمارة؟"

إذا كان الجواب الثاني، أعد الكتابة.
""",

    "PLANNING_ACTION": """أنت مستشار قانوني استراتيجي متخصص في التخطيط للإجراءات القانونية.

🎯 مهمتك:
- تقييم جدوى الإجراء القانوني المطلوب
- وضع استراتيجية واضحة خطوة بخطوة
- تحليل المخاطر والعوائد بصراحة
- إرشاد المستخدم للقرار الصحيح

⚖️ منهجك:
- قيم الموقف القانوني بموضوعية
- اشرح الخيارات المتاحة بوضوح
- حدد الإجراءات المطلوبة والتكاليف المتوقعة
- انصح بأفضل مسار بناءً على الحقائق

🔥 التركيز:
- خطة عمل واضحة وقابلة للتطبيق
- توقعات واقعية للنتائج
- بدائل إذا فشل المسار الأساسي

تحدث كمستشار استراتيجي يساعد في اتخاذ القرارات الذكية."""
}

async def generate_semantic_queries(original_query: str, ai_client) -> List[str]:
    """
    Generate semantic queries targeting different document types
    Production-ready version with reliable parsing and better statute targeting
    """
    
    semantic_prompt = f"""
أنت محرك بحث قانوني ذكي. أنشئ 3 استعلامات بحث لهذه القضية:

"{original_query}"

هذه قضية قرض/دعوى مدنية. أنشئ استعلامات بحث محددة:

استعلام المذكرات: مذكرات دفاع قضايا القروض والديون المدنية
استعلام الأنظمة: نظام الإثبات المادة إثبات الديون نظام المرافعات الشرعية
استعلام السوابق: أحكام قضائية سوابق قضايا القروض والديون

أجب بنفس التنسيق بالضبط:
استعلام المذكرات: [نص الاستعلام]
استعلام الأنظمة: [نص الاستعلام]  
استعلام السوابق: [نص الاستعلام]
"""

    try:
        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[{"role": "user", "content": semantic_prompt}],
            temperature=0.3,
            max_tokens=250
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse the structured response
        queries = [original_query]  # Always include original
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('استعلام المذكرات:'):
                memo_query = line.replace('استعلام المذكرات:', '').strip()
                if len(memo_query) > 10:
                    queries.append(memo_query)
            elif line.startswith('استعلام الأنظمة:'):
                statute_query = line.replace('استعلام الأنظمة:', '').strip()
                if len(statute_query) > 10:
                    queries.append(statute_query)
            elif line.startswith('استعلام السوابق:'):
                precedent_query = line.replace('استعلام السوابق:', '').strip()
                if len(precedent_query) > 10:
                    queries.append(precedent_query)
        
        # Log success
        if len(queries) > 1:
            logger.info(f"🎯 Generated {len(queries)} semantic queries for diverse retrieval")
            for i, q in enumerate(queries):
                logger.info(f"  Query {i}: {q[:80]}...")
        else:
            logger.warning("Semantic query generation failed, using original query only")
            
        return queries[:4]  # Limit to 4 queries for cost control
        
    except Exception as e:
        logger.error(f"Semantic query generation failed: {e}")
        return [original_query]  # Safe fallback
    
async def score_documents_multi_objective(documents: List[Chunk], original_query: str, user_intent: str, ai_client) -> List[Dict]:
    """
    Score documents on multiple objectives for intelligent selection
    Returns list of documents with scores for different objectives
    """
    
    if not documents:
        return []
    
    scoring_prompt = f"""
You are an expert legal document analyst. Score these legal documents for their value in responding to this query.

Query: {original_query}
Intent: {user_intent}

For each document, provide scores (0.0-1.0) for these objectives:

1. RELEVANCE: How directly related to the query topic
2. CITATION_VALUE: Potential for legal citations (statutes > precedents > memos)  
3. STYLE_MATCH: Fits aggressive/defensive memo style for disputes

Documents to score:
"""

    # Add document previews for scoring (cleaned for JSON safety)
    for i, doc in enumerate(documents, 1):
        # Clean content to avoid JSON parsing issues
        # Enhanced JSON-safe cleaning
        clean_content = (doc.content
                .replace('"', "'")
                .replace('\n', ' ')
                .replace('\r', ' ')
                .replace('\\', '\\\\')  # Escape backslashes
                .replace('\t', ' ')     # Replace tabs
                .replace('\b', ' ')     # Replace backspace
                .replace('\f', ' '))    # Replace form feed
        preview = clean_content[:150] + "..." if len(clean_content) > 150 else clean_content
        # JSON-safe title cleaning
        clean_title = (doc.title
              .replace('"', "'")
              .replace('\\', '\\\\')
              .replace('\n', ' ')
              .replace('\r', ' '))
        scoring_prompt += f"\nDocument {i}: {clean_title}\nContent: {preview}\n"
    
    scoring_prompt += f"""

Respond with ONLY a JSON array with scores for each document:
[
  {{
    "document_id": 1,
    "relevance": 0.85,
    "citation_value": 0.3,
    "style_match": 0.9
  }},
  {{
    "document_id": 2,
    "relevance": 0.7,
    "citation_value": 0.9,
    "style_match": 0.2
  }}
]

Score all {len(documents)} documents. Higher citation_value for statutes/regulations, higher style_match for aggressive memos.
"""

    try:
        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean JSON response more thoroughly
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown formatting
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            # Find JSON content between ``` markers
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        # Additional cleaning for Arabic text issues
        response_text = response_text.replace('\\', '').replace('\n', ' ').strip()
        
        import json
        scores = json.loads(response_text)
        
        # Combine documents with their scores
        scored_documents = []
        for i, doc in enumerate(documents):
            try:
                # Find score for this document
                doc_score = next((s for s in scores if s["document_id"] == i + 1), None)
                if doc_score:
                    scored_documents.append({
                        "document": doc,
                        "relevance": doc_score.get("relevance", 0.5),
                        "citation_value": doc_score.get("citation_value", 0.5),
                        "style_match": doc_score.get("style_match", 0.5),
                        "document_id": i + 1
                    })
                else:
                    # Fallback scoring
                    scored_documents.append({
                        "document": doc,
                        "relevance": 0.5,
                        "citation_value": 0.5,
                        "style_match": 0.5,
                        "document_id": i + 1
                    })
            except Exception as e:
                logger.warning(f"Error processing document {i+1} score: {e}")
                continue
        
        logger.info(f"🎯 Multi-objective scoring completed for {len(scored_documents)} documents")
        return scored_documents
        
    except Exception as e:
        logger.error(f"Multi-objective scoring failed: {e}")
        # Fallback: return documents with default scores
        return [{
            "document": doc,
            "relevance": 0.5,
            "citation_value": 0.5,
            "style_match": 0.5,
            "document_id": i + 1
        } for i, doc in enumerate(documents)]


def select_optimal_document_mix(scored_documents: List[Dict], top_k: int = 3) -> List[Chunk]:
    """
    Select optimal mix of documents based on multi-objective scores
    Ensures diversity: memos for style + statutes for citations
    """
    
    if not scored_documents:
        return []
    
    # Calculate composite scores with weights
    weights = {
        "relevance": 0.4,      # 40% - must be relevant
        "citation_value": 0.3, # 30% - need legal citations  
        "style_match": 0.3     # 30% - need aggressive style
    }
    
    # Add composite score to each document
    for doc_data in scored_documents:
        composite = (
            doc_data["relevance"] * weights["relevance"] +
            doc_data["citation_value"] * weights["citation_value"] +
            doc_data["style_match"] * weights["style_match"]
        )
        doc_data["composite_score"] = composite
    
    # Sort by composite score (highest first)
    scored_documents.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Intelligent selection strategy with statute priority
    selected = []
    
    # Strategy 1: FORCE include statute documents if available
    statute_docs = []
    memo_docs = []
    
    for doc_data in scored_documents:
        doc_title = doc_data["document"].title
        if any(term in doc_title for term in ["نظام", "المادة", "التعريفات", "مرسوم"]):
            statute_docs.append(doc_data)
        else:
            memo_docs.append(doc_data)
    
    # Always include 1 statute if available
    if statute_docs and len(selected) < top_k:
        best_statute = max(statute_docs, key=lambda x: x["composite_score"])
        selected.append(best_statute["document"])
        logger.info(f"📜 FORCED statute inclusion: {best_statute['document'].title[:50]}... (composite: {best_statute['composite_score']:.2f})")
    
    # Strategy 2: Get highest citation value documents (likely more statutes)
    remaining_docs = [d for d in scored_documents if d["document"] not in selected]
    citation_docs = [d for d in remaining_docs if d["citation_value"] >= 0.7]
    
    while citation_docs and len(selected) < top_k:
        best_citation = max(citation_docs, key=lambda x: x["citation_value"])
        selected.append(best_citation["document"])
        citation_docs.remove(best_citation)
        remaining_docs.remove(best_citation)
        logger.info(f"📜 Selected high-citation document: {best_citation['document'].title[:50]}... (citation: {best_citation['citation_value']:.2f})")
    
    # Strategy 3: Get highest style match documents (aggressive memos)
    style_docs = [d for d in remaining_docs if d["style_match"] >= 0.7]
    while style_docs and len(selected) < top_k:
        best_style = max(style_docs, key=lambda x: x["style_match"])
        selected.append(best_style["document"])
        style_docs.remove(best_style)
        remaining_docs.remove(best_style)
        logger.info(f"⚔️ Selected high-style document: {best_style['document'].title[:50]}... (style: {best_style['style_match']:.2f})")
    
    # Strategy 4: Fill remaining with highest composite scores
    while len(selected) < top_k and remaining_docs:
        best_overall = remaining_docs.pop(0)  # Already sorted by composite score
        selected.append(best_overall["document"])
        logger.info(f"🎯 Selected high-composite document: {best_overall['document'].title[:50]}... (composite: {best_overall['composite_score']:.2f})")
    
    logger.info(f"🎯 Optimal mix selected: {len(selected)} documents with intelligent diversity (statutes prioritized)")
    return selected

class StorageFactory:
    """Factory for creating storage backends"""
    
    @staticmethod
    def create_storage() -> VectorStore:
        """Create storage backend based on environment configuration"""
        storage_type = os.getenv("VECTOR_STORAGE_TYPE", "sqlite").lower()
        
        if storage_type == "sqlite":
            db_path = os.getenv("SQLITE_DB_PATH", "data/vectors.db")
            return SqliteVectorStore(db_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


class DocumentRetriever:
    """Smart document retriever - gets relevant Saudi legal documents from database"""
    
    def __init__(self, storage: VectorStore, ai_client: AsyncOpenAI):
        self.storage = storage
        self.ai_client = ai_client
        self.initialized = False
        logger.info(f"DocumentRetriever initialized with {type(storage).__name__}")
    
    async def initialize(self) -> None:
        """Initialize storage backend"""
        if self.initialized:
            return
        
        try:
            await self.storage.initialize()
            stats = await self.storage.get_stats()
            logger.info(f"Storage initialized with {stats.total_chunks} existing documents")
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise
    
    async def get_relevant_documents(self, query: str, top_k: int = 3, user_intent: str = None) -> List[Chunk]:
        """
        Enhanced document retrieval with semantic diversification + dual-stage filtering:
        Stage 1: Semantic diversification (NEW for ACTIVE_DISPUTE)
        Stage 2: Content-based retrieval (your existing system)  
        Stage 3: Style-based filtering using AI (your existing system)
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            stats = await self.storage.get_stats()
            if stats.total_chunks == 0:
                logger.info("No documents found in storage - using general knowledge")
                return []
            
            logger.info(f"🔍 Enhanced search in {stats.total_chunks} documents for: '{query[:50]}...'")
            logger.info(f"📋 User intent: {user_intent}")
            
            # STAGE 1: SEMANTIC DIVERSIFICATION (NEW!)
            if user_intent == "ACTIVE_DISPUTE":
                # Generate diverse semantic queries for better document coverage
                semantic_queries = await generate_semantic_queries(query, self.ai_client)
                logger.info(f"🎯 Generated {len(semantic_queries)} semantic queries for diverse retrieval")
            else:
                # For other intents, use original query only
                semantic_queries = [query]
            
            # STAGE 2: MULTI-QUERY RETRIEVAL (ENHANCED)
            # In your enhanced get_relevant_documents method, replace the multi-query retrieval section:

            # STAGE 2: MULTI-QUERY RETRIEVAL (ENHANCED WITH DOMAIN BYPASS)
            all_search_results = []

            for i, semantic_query in enumerate(semantic_queries):
                try:
                    # Get embedding for this semantic query
                    response = await self.ai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=semantic_query
                    )
                    query_embedding = response.data[0].embedding
                    
                    # DEBUG: Check bypass condition
                    logger.info(f"🔍 BYPASS DEBUG: i={i}, user_intent='{user_intent}', condition: {i == 2 and user_intent == 'ACTIVE_DISPUTE'}")
                    
                    # BYPASS DOMAIN FILTERING FOR STATUTE QUERY (Query 3)
                    if i == 2 and user_intent == "ACTIVE_DISPUTE":  # Third query (index 2) is statute query
                        logger.info(f"🔓 Semantic query {i+1}: Bypassing domain filter for statute search")
                        # Search ALL documents without domain filtering
                        search_results = await self.storage.search_similar(
                            query_embedding, 
                            top_k=12
                            # No query_text, no openai_client = no domain filtering
                        )
                    else:
                        # Use normal domain filtering for other queries
                        expanded_top_k = min(top_k * 4, 15) if user_intent == "ACTIVE_DISPUTE" else top_k * 4
                        search_results = await self.storage.search_similar(
                            query_embedding, 
                            top_k=expanded_top_k, 
                            query_text=semantic_query, 
                            openai_client=self.ai_client
                        )
                    
                    # Tag results with semantic source for debugging
                    for result in search_results:
                        if not hasattr(result.chunk, 'metadata'):
                            result.chunk.metadata = {}
                        result.chunk.metadata['semantic_source'] = f"query_{i}"
                    
                    all_search_results.extend(search_results)
                    logger.info(f"  Semantic query {i+1}: Found {len(search_results)} candidates")
                    
                except Exception as e:
                    logger.warning(f"Semantic query {i} failed: {e}")
                    continue
            
            # STAGE 3: DEDUPLICATE AND MERGE RESULTS
            if len(semantic_queries) > 1:
                # Remove duplicates by chunk ID while preserving best similarity scores
                seen_ids = set()
                unique_results = []
                
                # Sort all results by similarity score (best first)
                all_search_results.sort(key=lambda x: x.similarity_score, reverse=True)
                
                for result in all_search_results:
                    chunk_id = getattr(result.chunk, 'id', None)
                    if chunk_id and chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        unique_results.append(result)
                    elif chunk_id is None:
                        unique_results.append(result)
                
                search_results = unique_results[:15]  # Cap at 15 like your original
                logger.info(f"📊 Merged {len(all_search_results)} results into {len(search_results)} unique candidates")
            else:
                search_results = all_search_results
            
            content_candidates = [result.chunk for result in search_results]
            
            if not content_candidates:
                logger.info("No relevant documents found - using general knowledge")
                return []
            
            logger.info(f"📊 Stage 2-3: Found {len(content_candidates)} content matches")
            
            # STAGE 4: Direct multi-objective scoring (style classification bypassed)
            if len(content_candidates) > top_k:
                try:
                    logger.info("⚡ Stage 4: Direct multi-objective document scoring")
                    
                    # Apply multi-objective scoring directly to content candidates
                    scored_documents = await score_documents_multi_objective(
                        content_candidates, 
                        query, 
                        user_intent, 
                        self.ai_client
                    )
                    
                    # Select optimal mix using intelligent scoring
                    relevant_chunks = select_optimal_document_mix(scored_documents, top_k)
                    logger.info(f"⚡ EFFICIENT SELECTION: {len(relevant_chunks)} documents via direct scoring")
                    
                except Exception as scoring_error:
                    logger.warning(f"Multi-objective scoring failed: {scoring_error}, using similarity-based selection")
                    relevant_chunks = content_candidates[:top_k]
            else:
                # Use content-based results when we have few candidates
                relevant_chunks = content_candidates[:top_k]
                logger.info(f"📊 Using content-based retrieval ({user_intent}) - {len(relevant_chunks)} candidates")
            
            # STAGE 5: RESULTS LOGGING (keeping your original format)
            if relevant_chunks:
                logger.info(f"Found {len(relevant_chunks)} relevant documents:")
                for i, chunk in enumerate(relevant_chunks):
                    # Find similarity score from original search results
                    similarity = 0.0
                    for result in search_results:
                        if result.chunk.id == chunk.id:
                            similarity = result.similarity_score
                            break
                    
                    semantic_source = chunk.metadata.get('semantic_source', 'original') if hasattr(chunk, 'metadata') and chunk.metadata else 'original'
                    logger.info(f"  {i+1}. {chunk.title[:50]}... (similarity: {similarity:.3f}, source: {semantic_source})")
            else:
                logger.info("No relevant documents found - using general knowledge")
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []


    
class IntentClassifier:
    """AI-powered intent classifier - no hard-coding"""
    
    def __init__(self, ai_client: AsyncOpenAI, model: str):
        self.ai_client = ai_client
        self.model = model
        logger.info("🧠 AI Intent Classifier initialized - zero hard-coding")
    
    async def classify_intent(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, any]:
        """Use AI to classify user intent dynamically"""
        try:
            # Build context for better classification
            context = ""
            if conversation_history:
                recent_context = conversation_history[-3:]  # Last 3 messages for context
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_context])
                context = f"\n\nسياق المحادثة:\n{context}\n"
            
            classification_prompt = CLASSIFICATION_PROMPT.format(query=query) + context
            
            logger.info(f"🧠 Classifying intent for: {query[:30]}...")
            
            response = await self.ai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
                max_tokens=200,
                temperature=0.1  # Low temperature for consistent classification
            )
            
            # Parse AI response
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown if present)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            classification = json.loads(result_text)
            
            logger.info(f"🎯 Intent classified: {classification['category']} (confidence: {classification['confidence']:.2f})")
            
            # Validate classification
            valid_categories = ["GENERAL_QUESTION", "ACTIVE_DISPUTE", "PLANNING_ACTION"]
            if classification["category"] not in valid_categories:
                logger.warning(f"Invalid category: {classification['category']}, defaulting to GENERAL_QUESTION")
                classification["category"] = "GENERAL_QUESTION"
                classification["confidence"] = 0.5
            
            return classification
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            # Safe fallback
            return {
                "category": "GENERAL_QUESTION",
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}"
            }


def format_legal_context_naturally(retrieved_chunks: List[Chunk]) -> str:
    """
    Format legal documents with MANDATORY citation enforcement
    """
    if not retrieved_chunks:
        return ""
    
    context_parts = []
    available_sources = []
    
    for i, chunk in enumerate(retrieved_chunks, 1):
        # Extract actual statute name
        statute_name = chunk.title
        available_sources.append(statute_name)
        
        # Clean and format content 
        clean_content = chunk.content.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
        preview = clean_content[:300] + "..." if len(clean_content) > 300 else clean_content
        
        formatted_chunk = f"""
📜 **{statute_name}**
{preview}
"""
        context_parts.append(formatted_chunk)
    
    # Create mandatory citation instructions
    sources_list = "\n".join([f"- {source}" for source in available_sources])
    
    final_context = f"""المراجع القانونية المتاحة فقط:
{chr(10).join(context_parts)}

🚨 تعليمات الاستشهاد الإجبارية:
يُسمح ولازم أن تستشهد بالمصادر التالية:
{sources_list}

❌ ممنوع تماماً:
- اختراع مراجع جديدة
- استخدام "مرجع 1" أو "مرجع 2"
- الاستشهاد بمصادر غير موجودة في القائمة أعلاه

✅ مطلوب: استخدم الأسماء الكاملة بالضبط كما هي مكتوبة أعلاه"""
    
    return final_context


class IntelligentLegalRAG:
    """
    Intelligent Legal RAG with AI-Powered Intent Classification
    No hard-coding - AI handles classification and prompt selection
    """
    
    def __init__(self):
        """Initialize intelligent RAG with AI classification"""
        self.ai_client = ai_client
        self.ai_model = ai_model
        
        # Add smart document retrieval
        self.storage = StorageFactory.create_storage()
        self.retriever = DocumentRetriever(
            storage=self.storage,
            ai_client=self.ai_client
        )
        
        # Add AI-powered intent classifier
        self.classifier = IntentClassifier(
            ai_client=self.ai_client,
            model=classification_model
        )
        
        logger.info("🚀 Intelligent Legal RAG initialized - AI-powered classification + Smart retrieval!")
        self.citation_fixer = SimpleCitationFixer()
        logger.info("🔧 Citation fixer initialized")

        
    async def ask_question_streaming(self, query: str) -> AsyncIterator[str]:
        """
        Intelligent legal consultation with AI-powered intent classification
        """
        try:
            logger.info(f"Processing intelligent legal question: {query[:50]}...")
            
            # Stage 1: AI-powered intent classification
            classification = await self.classifier.classify_intent(query)
            category = classification["category"]
            confidence = classification["confidence"]
            
            # Stage 2: Get relevant documents from database
            print(f"🔥 DEBUG CATEGORY: category='{category}', type={type(category)}")
            relevant_docs = await self.retriever.get_relevant_documents(query, top_k=3, user_intent=category)
            
            # Stage 3: Select appropriate prompt based on AI classification
            system_prompt = PROMPT_TEMPLATES[category]
            
            # Stage 4: Build intelligent prompt with documents
            if relevant_docs:
                legal_context = format_legal_context_naturally(relevant_docs)
                print(f"🔥 CITATION DEBUG: Context length: {len(legal_context)}")
                print(f"🔥 CITATION DEBUG: Contains 'مرجع قانوني': {'مرجع قانوني' in legal_context}")
                full_prompt = f"""{legal_context}

السؤال: {query}"""
                logger.info(f"Using {len(relevant_docs)} relevant legal documents with {category} approach")
            else:
                full_prompt = query
                logger.info(f"No relevant documents found - using {category} approach with general knowledge")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
            
            # Stage 5: Stream intelligent response
            async for chunk in self._stream_ai_response(messages, category):
                yield chunk
                
        except Exception as e:
            logger.error(f"Intelligent legal AI error: {e}")
            yield f"عذراً، حدث خطأ في معالجة سؤالك: {str(e)}"
            self.citation_fixer = SimpleCitationFixer()
            logger.info("🔧 Citation fixer initialized")
    async def ask_question_with_context_streaming(
        self, 
        query: str, 
        conversation_history: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """
        Intelligent context-aware legal consultation with AI classification
        """
        try:
            logger.info(f"Processing intelligent contextual legal question: {query[:50]}...")
            logger.info(f"Conversation context: {len(conversation_history)} messages")
            
            # Stage 1: AI-powered intent classification with context
            classification = await self.classifier.classify_intent(query, conversation_history)
            category = classification["category"]
            confidence = classification["confidence"]
            
            # Stage 2: Get relevant documents
            print(f"🔥 DEBUG CATEGORY: category='{category}', type={type(category)}")
            relevant_docs = await self.retriever.get_relevant_documents(query, top_k=3, user_intent=category)
            
            # Stage 3: Select appropriate prompt
            system_prompt = PROMPT_TEMPLATES[category]
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Stage 4: Add conversation history (last 8 messages)
            recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Stage 5: Add current question with legal context if available
            if relevant_docs:
                legal_context = format_legal_context_naturally(relevant_docs)
                contextual_prompt = f"""{legal_context}

السؤال: {query}"""
                logger.info(f"Using {len(relevant_docs)} relevant legal documents with {category} approach (contextual)")
            else:
                contextual_prompt = query
                logger.info(f"No relevant documents found - using {category} approach with contextual general knowledge")
            
            messages.append({
                "role": "user", 
                "content": contextual_prompt
            })
            
            # Stage 6: Stream intelligent contextual response
            async for chunk in self._stream_ai_response(messages, category):
                yield chunk
                
        except Exception as e:
            logger.error(f"Intelligent contextual legal AI error: {e}")
            yield f"عذراً، حدث خطأ في معالجة سؤالك: {str(e)}"
    
    async def _stream_ai_response(self, messages: List[Dict[str, str]], category: str = "GENERAL_QUESTION") -> AsyncIterator[str]:
        """Stream AI response with error handling"""
        try:
            stream = await self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                temperature=0.05 if category == "ACTIVE_DISPUTE" else 0.15,
                max_tokens=4000 if category == "ACTIVE_DISPUTE" else 1500,  # ← GIVE DISPUTES MORE SPACE!
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"AI streaming error: {e}")
            error_msg = str(e).lower()
            
            if "rate limit" in error_msg or "429" in error_msg:
                yield "\n\n⏳ تم تجاوز الحد المسموح مؤقتاً. يرجى الانتظار دقيقة وإعادة المحاولة."
            elif "api key" in error_msg or "authentication" in error_msg:
                yield "\n\n🔑 خطأ في مفتاح API. يرجى التواصل مع الدعم الفني."
            else:
                yield f"\n\n❌ خطأ تقني: {str(e)}"
    
    async def generate_conversation_title(self, first_message: str) -> str:
        """Intelligent conversation title generation"""
        try:
            title_prompt = f"اقترح عنواناً مختصراً (أقل من 30 حرف) لهذه الاستشارة القانونية: {first_message[:100]}"
            
            response = await self.ai_client.chat.completions.create(
                model=classification_model,  # Use small model for title generation
                messages=[{"role": "user", "content": title_prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            title = response.choices[0].message.content.strip()
            title = title.strip('"').strip("'").strip()
            
            # Remove common prefixes
            prefixes = ["العنوان:", "المقترح:", "عنوان:"]
            for prefix in prefixes:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
            
            return title[:30] if len(title) > 30 else title
            
        except Exception as e:
            logger.error(f"Title generation error: {e}")
            return first_message[:25] + "..." if len(first_message) > 25 else first_message


# Global instance - maintains compatibility with existing code
rag_engine = IntelligentLegalRAG()

# Legacy compatibility functions - exactly the same interface as before
async def ask_question(query: str) -> str:
    """Legacy sync function - converts streaming to complete response"""
    chunks = []
    async for chunk in rag_engine.ask_question_streaming(query):
        chunks.append(chunk)
    return ''.join(chunks)

async def ask_question_with_context(query: str, conversation_history: List[Dict[str, str]]) -> str:
    """Legacy sync function with context - converts streaming to complete response"""
    chunks = []
    async for chunk in rag_engine.ask_question_with_context_streaming(query, conversation_history):
        chunks.append(chunk)
    return ''.join(chunks)

async def generate_conversation_title(first_message: str) -> str:
    """Legacy function for title generation"""
    return await rag_engine.generate_conversation_title(first_message)

# Test function
async def test_intelligent_rag():
    """Test the intelligent RAG system with classification"""
    print("🧪 Testing intelligent RAG engine with AI classification...")
    
    test_queries = [
        "ما هي عقوبات التهرب الضريبي؟",  # Should be GENERAL_QUESTION
        "رفع علي خصم دعوى كيدية كيف أرد عليه؟",  # Should be ACTIVE_DISPUTE
        "أريد مقاضاة شركتي هل الأمر يستحق؟"  # Should be PLANNING_ACTION
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing: {query}")
        print("Response:")
        
        response_chunks = []
        async for chunk in rag_engine.ask_question_streaming(query):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        print(f"\n✅ Test complete for this query!\n{'-'*50}")
    
    return True

# System initialization
print("🏛️ Intelligent Legal RAG Engine loaded - AI-powered classification + Smart document retrieval!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intelligent_rag())