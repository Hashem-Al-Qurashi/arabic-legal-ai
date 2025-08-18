"""
Islamic-Primary RAG Engine
Islamic law as foundation, civil law as implementation
True reflection of Saudi legal system
"""
import os
import logging
import asyncio
from typing import List, Dict, Optional, Any, AsyncIterator
from datetime import datetime

# Import existing components
from rag_engine import (
    ProcessingMode,
    PROMPT_TEMPLATES,
    ai_client,
    ai_model,
    classification_model
)

# Import Islamic-primary components
from app.services.islamic_primary_retrieval import IslamicPrimaryOrchestrator, format_islamic_primary_results
from app.storage.islamic_vector_store import create_islamic_citation

logger = logging.getLogger(__name__)


class IslamicPrimaryCitationFixer:
    """
    Citation fixer with Islamic foundation priority
    """
    
    def __init__(self):
        self.islamic_enabled = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
    
    def fix_citations(self, ai_response: str, retrieval_data: Dict) -> str:
        """
        Enhanced citation fixing with Islamic foundation first
        """
        if not self.islamic_enabled:
            return ai_response
        
        strategy = retrieval_data.get("strategy", "civil_only")
        islamic_sources = retrieval_data.get("islamic_sources", [])
        civil_sources = retrieval_data.get("civil_sources", [])
        
        if strategy == "islamic_primary":
            # Islamic foundation → Civil implementation structure
            return self.format_islamic_primary_citations(ai_response, islamic_sources, civil_sources)
        elif strategy in ["islamic_secondary", "islamic_context"]:
            # Civil primary with Islamic context
            return self.format_civil_with_islamic_citations(ai_response, civil_sources, islamic_sources)
        else:
            # Civil only
            return self.format_civil_only_citations(ai_response, civil_sources)
    
    def format_islamic_primary_citations(self, response: str, islamic_sources: List, civil_sources: List) -> str:
        """
        Format response with Islamic foundation first
        """
        import re
        
        # Structure: Islamic Foundation → Civil Implementation
        enhanced_response = response
        
        # Add Islamic foundation citations at the beginning of relevant sections
        if islamic_sources:
            for i, source in enumerate(islamic_sources[:3]):  # Top 3 Islamic sources
                citation = create_islamic_citation(source.chunk)
                
                # Insert after first substantive paragraph
                if i == 0:
                    # Insert primary Islamic citation early
                    paragraphs = enhanced_response.split('\n\n')
                    if len(paragraphs) > 0:
                        # Add after first paragraph
                        paragraphs.insert(1, f"\n{citation}")
                        enhanced_response = '\n\n'.join(paragraphs)
                else:
                    # Add additional citations contextually
                    enhanced_response += f"\n\n{citation}"
        
        # Add civil implementation citations
        if civil_sources:
            civil_citations = []
            for source in civil_sources[:3]:
                if hasattr(source, 'title') and 'نظام' in source.title:
                    civil_citations.append(f"وفقاً لـ{source.title}")
            
            if civil_citations:
                implementation_section = f"\n\nوقد نظم المشرع السعودي هذه الأحكام في {', '.join(civil_citations[:2])}"
                enhanced_response += implementation_section
        
        return enhanced_response
    
    def format_civil_with_islamic_citations(self, response: str, civil_sources: List, islamic_sources: List) -> str:
        """
        Format civil-primary response with Islamic context
        """
        enhanced_response = response
        
        # Add Islamic context after main civil content
        if islamic_sources:
            context_citations = []
            for source in islamic_sources[:2]:
                citation = create_islamic_citation(source.chunk)
                context_citations.append(citation)
            
            if context_citations:
                context_section = f"\n\nوالأصل الشرعي في هذه المسألة:\n" + "\n".join(context_citations)
                enhanced_response += context_section
        
        return enhanced_response
    
    def format_civil_only_citations(self, response: str, civil_sources: List) -> str:
        """
        Format civil-only response (for procedural matters)
        """
        # Keep existing civil citation logic
        return response


class IslamicPrimaryRAGEngine:
    """
    RAG Engine with Islamic law as primary foundation
    """
    
    def __init__(self):
        self.enable_islamic = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
        
        # Initialize components
        self.islamic_primary_retrieval = None
        self.citation_fixer = IslamicPrimaryCitationFixer()
        
        # Performance tracking
        self.performance_metrics = {
            "total_queries": 0,
            "islamic_foundation_responses": 0,
            "civil_implementation_responses": 0,
            "procedural_responses": 0,
            "avg_response_time": 0.0
        }
        
        logger.info(f"Islamic-Primary RAG Engine initialized")
    
    async def initialize(self):
        """Initialize Islamic-primary RAG engine"""
        try:
            if self.enable_islamic:
                self.islamic_primary_retrieval = IslamicPrimaryOrchestrator()
                await self.islamic_primary_retrieval.initialize()
                logger.info("✅ Islamic-Primary RAG Engine initialized")
            else:
                logger.warning("Islamic sources disabled - falling back to civil only")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Islamic-Primary RAG Engine: {e}")
            self.enable_islamic = False
    
    async def process_query(self, query: str, conversation_history: List[Dict] = None, 
                          mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
        """
        Process query with Islamic foundation priority
        """
        start_time = datetime.now()
        self.performance_metrics["total_queries"] += 1
        
        try:
            # Get retrieval data with Islamic-primary approach
            if self.enable_islamic and self.islamic_primary_retrieval:
                retrieval_data = await self.islamic_primary_retrieval.retrieve(query, limit=15)
            else:
                # Fallback to civil only
                from app.storage.sqlite_store import SqliteVectorStore
                civil_store = SqliteVectorStore()
                await civil_store.initialize()
                civil_results = await civil_store.search(query, limit=10)
                retrieval_data = {
                    "strategy": "civil_only",
                    "islamic_sources": [],
                    "civil_sources": [r.chunk for r in civil_results],
                    "response_structure": "civil_only",
                    "foundation_type": "civil_only"
                }
            
            # Generate AI response with Islamic-aware prompting
            ai_response = await self.generate_islamic_aware_response(
                query, retrieval_data, conversation_history, mode
            )
            
            # Apply Islamic-primary citation fixing
            final_response = self.citation_fixer.fix_citations(ai_response, retrieval_data)
            
            # Update metrics
            strategy = retrieval_data.get("strategy", "civil_only")
            if strategy == "islamic_primary":
                self.performance_metrics["islamic_foundation_responses"] += 1
            elif strategy in ["islamic_secondary", "islamic_context"]:
                self.performance_metrics["civil_implementation_responses"] += 1
            else:
                self.performance_metrics["procedural_responses"] += 1
            
            # Calculate performance
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_performance_metrics(response_time)
            
            # Format response data
            formatted_results = format_islamic_primary_results(retrieval_data)
            
            return {
                "answer": final_response,
                "sources": formatted_results['sources'],
                "strategy": strategy,
                "foundation_type": retrieval_data.get("foundation_type"),
                "response_structure": retrieval_data.get("response_structure"),
                "processing_time_ms": int(response_time * 1000),
                "mode": mode.value,
                "islamic_primary": True
            }
            
        except Exception as e:
            logger.error(f"Islamic-Primary processing failed: {e}")
            return await self.fallback_response(query, conversation_history, mode)
    
    async def generate_islamic_aware_response(self, query: str, retrieval_data: Dict,
                                            conversation_history: List[Dict] = None,
                                            mode: ProcessingMode = ProcessingMode.STRATEGIC) -> str:
        """
        Generate response with Islamic foundation awareness
        """
        strategy = retrieval_data.get("strategy", "civil_only")
        islamic_sources = retrieval_data.get("islamic_sources", [])
        civil_sources = retrieval_data.get("civil_sources", [])
        
        # Build context based on strategy
        if strategy == "islamic_primary":
            context = self.build_islamic_primary_context(islamic_sources, civil_sources)
            prompt_template = self.get_islamic_primary_prompt()
        elif strategy in ["islamic_secondary", "islamic_context"]:
            context = self.build_civil_with_islamic_context(civil_sources, islamic_sources)
            prompt_template = self.get_civil_with_islamic_prompt()
        else:
            context = self.build_civil_only_context(civil_sources)
            prompt_template = PROMPT_TEMPLATES.get("GENERAL_QUESTION", "")
        
        # Add conversation history
        history_context = ""
        if conversation_history:
            recent_history = conversation_history[-3:]
            history_context = "\n".join([f"{msg['role']}: {msg['content'][:200]}" 
                                       for msg in recent_history])
        
        # Build final prompt
        history_section = f"السياق السابق للمحادثة:\n{history_context}\n" if history_context else ""
        
        final_prompt = f"""{prompt_template}

{context}

{history_section}

السؤال: {query}

اجب وفقاً للمنهج المطلوب أعلاه:"""

        # Generate response
        try:
            response = await ai_client.chat.completions.create(
                model=ai_model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return "عذراً، لم أتمكن من إنتاج إجابة مناسبة لاستفسارك."
    
    def build_islamic_primary_context(self, islamic_sources: List, civil_sources: List) -> str:
        """Build context with Islamic foundation first"""
        context_parts = []
        
        # Islamic foundation first
        if islamic_sources:
            context_parts.append("الأسس الشرعية:")
            for i, source in enumerate(islamic_sources[:4]):
                verse_ref = getattr(source.chunk, 'verse_reference', '')
                legal_principle = getattr(source.chunk, 'legal_principle', '')
                commentary = getattr(source.chunk, 'qurtubi_commentary', source.chunk.content)
                
                context_parts.append(f"الأساس الشرعي {i+1}: {verse_ref}")
                if legal_principle:
                    context_parts.append(f"المبدأ: {legal_principle}")
                context_parts.append(f"التفسير: {commentary[:300]}")
                context_parts.append("")
        
        # Civil implementation second
        if civil_sources:
            context_parts.append("التطبيق في النظام السعودي:")
            for i, source in enumerate(civil_sources[:4]):
                context_parts.append(f"المرجع {i+1}: {source.title}")
                context_parts.append(f"النص: {source.content[:400]}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def build_civil_with_islamic_context(self, civil_sources: List, islamic_sources: List) -> str:
        """Build civil-primary context with Islamic background"""
        context_parts = []
        
        # Civil primary
        if civil_sources:
            context_parts.append("الأحكام القانونية:")
            for i, source in enumerate(civil_sources[:5]):
                context_parts.append(f"المرجع {i+1}: {source.title}")
                context_parts.append(f"النص: {source.content[:400]}")
                context_parts.append("")
        
        # Islamic context
        if islamic_sources:
            context_parts.append("السياق الشرعي:")
            for i, source in enumerate(islamic_sources[:2]):
                legal_principle = getattr(source.chunk, 'legal_principle', '')
                if legal_principle:
                    context_parts.append(f"المبدأ الشرعي: {legal_principle}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def build_civil_only_context(self, civil_sources: List) -> str:
        """Build civil-only context for procedural matters"""
        context_parts = ["المراجع القانونية:"]
        
        for i, source in enumerate(civil_sources[:6]):
            context_parts.append(f"المرجع {i+1}: {source.title}")
            context_parts.append(f"النص: {source.content[:500]}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_islamic_primary_prompt(self) -> str:
        """Get prompt template for Islamic-primary responses"""
        return """أنت مستشار قانوني سعودي متخصص في الفقه الإسلامي والأنظمة السعودية.

🕌 منهجك في الإجابة:
1. ابدأ بالأساس الشرعي من القرآن والسنة والفقه
2. اربط الحكم الشرعي بالواقع المعاصر
3. اذكر التطبيق في الأنظمة السعودية
4. قدم الحلول العملية

📚 هيكل الإجابة المطلوب:
• الحكم الشرعي: ما هو الأصل في الشريعة؟
• الدليل: الآيات والأحاديث ذات الصلة
• التطبيق المعاصر: كيف ينظم النظام السعودي هذه المسألة؟
• الحل العملي: ما الذي يجب على السائل فعله؟

⚖️ مبادئ مهمة:
- الشريعة هي الأساس، والنظام هو التطبيق
- اجمع بين الحكم الشرعي والممارسة القانونية
- كن واضحاً ومباشراً وعملياً
- استشهد بالمصادر الشرعية والقانونية"""
    
    def get_civil_with_islamic_prompt(self) -> str:
        """Get prompt template for civil-primary with Islamic context"""
        return """أنت مستشار قانوني سعودي.

🎯 منهجك في الإجابة:
1. اشرح الحكم القانوني في النظام السعودي
2. اذكر الإجراءات والخطوات المطلوبة
3. أضف السياق الشرعي عند الحاجة
4. قدم نصائح عملية

📋 هيكل الإجابة:
• الحكم القانوني: ما ينص عليه النظام السعودي
• الإجراءات: الخطوات العملية المطلوبة
• السياق الشرعي: الأساس الفقهي (إذا كان متصلاً)
• التوصيات: ما يجب فعله عملياً

استشهد بالأنظمة السعودية وأضف المبادئ الشرعية عند الحاجة."""
    
    def update_performance_metrics(self, response_time: float):
        """Update performance metrics"""
        if self.performance_metrics["total_queries"] > 0:
            current_avg = self.performance_metrics["avg_response_time"]
            total_queries = self.performance_metrics["total_queries"]
            
            self.performance_metrics["avg_response_time"] = (
                (current_avg * (total_queries - 1) + response_time) / total_queries
            )
    
    async def fallback_response(self, query: str, conversation_history: List[Dict] = None,
                               mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
        """Fallback response when Islamic-primary fails"""
        return {
            "answer": "عذراً، حدث خطأ في معالجة استفسارك. يرجى المحاولة مرة أخرى.",
            "sources": {"islamic_foundation": [], "civil_implementation": []},
            "strategy": "error",
            "foundation_type": "error",
            "processing_time_ms": 0,
            "islamic_primary": False,
            "error": True
        }


# Global instance
_islamic_primary_engine = None

async def get_islamic_primary_rag_engine() -> IslamicPrimaryRAGEngine:
    """Get or create Islamic-primary RAG engine instance"""
    global _islamic_primary_engine
    
    if _islamic_primary_engine is None:
        _islamic_primary_engine = IslamicPrimaryRAGEngine()
        await _islamic_primary_engine.initialize()
    
    return _islamic_primary_engine


async def process_query_islamic_primary(query: str, conversation_history: List[Dict] = None,
                                      mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
    """
    Main function for Islamic-primary query processing
    """
    engine = await get_islamic_primary_rag_engine()
    return await engine.process_query(query, conversation_history, mode)


async def test_islamic_primary_engine():
    """Test the Islamic-primary engine"""
    test_queries = [
        "ما أحكام الميراث؟",  # Should start with Quranic foundation
        "شروط عقد البيع",  # Should start with Islamic contract principles
        "كيف أقدم دعوى؟",  # Should be civil procedural
        "عقوبة السرقة",  # Should start with Quranic hudud
        "رسوم المحكمة"  # Should be civil only
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        result = await process_query_islamic_primary(query)
        
        print(f"✅ Strategy: {result.get('strategy')}")
        print(f"🕌 Foundation: {result.get('foundation_type')}")
        print(f"📊 Islamic sources: {len(result['sources']['islamic_foundation'])}")
        print(f"🏛️ Civil sources: {len(result['sources']['civil_implementation'])}")
        print(f"⏱️ Time: {result.get('processing_time_ms')}ms")
        print(f"📝 Response length: {len(result.get('answer', ''))} chars")


if __name__ == "__main__":
    asyncio.run(test_islamic_primary_engine())