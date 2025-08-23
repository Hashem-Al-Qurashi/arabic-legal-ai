"""
Enhanced RAG Engine with Islamic Integration
Extends existing RAG engine to include Islamic legal sources
Zero breaking changes to existing functionality
"""
import os
import logging
import asyncio
from typing import List, Dict, Optional, Any, AsyncIterator
from datetime import datetime

# Import existing components
from rag_engine import (
    get_rag_engine as get_base_rag_engine,
    ProcessingMode,
    SimpleCitationFixer,
    PROMPT_TEMPLATES,
    ai_client,
    ai_model,
    classification_model
)

# Import new Islamic components
from app.services.unified_retrieval import UnifiedRetrievalOrchestrator, format_unified_results
from app.storage.islamic_vector_store import IslamicVectorStore, create_islamic_citation

logger = logging.getLogger(__name__)


class EnhancedCitationFixer(SimpleCitationFixer):
    """
    Enhanced citation fixer that handles both civil and Islamic sources
    """
    
    def __init__(self):
        super().__init__()
        self.islamic_enabled = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
    
    def fix_citations(self, ai_response: str, available_documents: List, 
                     islamic_sources: List = None) -> str:
        """
        Enhanced citation fixing for both civil and Islamic sources
        """
        # First apply existing civil law citation fixing
        response = super().fix_citations(ai_response, available_documents)
        
        # Then add Islamic citations if available
        if self.islamic_enabled and islamic_sources:
            response = self.add_islamic_citations(response, islamic_sources)
        
        return response
    
    def add_islamic_citations(self, response: str, islamic_sources: List) -> str:
        """
        Add Islamic citations to the response
        """
        import re
        
        for source in islamic_sources:
            try:
                # Create formatted citation
                if hasattr(source.chunk, 'verse_reference') and source.chunk.verse_reference:
                    citation = create_islamic_citation(source.chunk)
                    
                    # Smart insertion points for Islamic citations
                    insertion_patterns = [
                        # After legal principles
                        (r'(المبدأ|الأصل|القاعدة)[^.]*\.', r'\1\n' + citation),
                        
                        # After rulings
                        (r'(الحكم|يحكم|نحكم)[^.]*\.', r'\1\n' + citation),
                        
                        # Before conclusion
                        (r'(وعليه|لذلك|خلاصة)', citation + r'\n\1'),
                    ]
                    
                    # Try to insert citation contextually
                    inserted = False
                    for pattern, replacement in insertion_patterns:
                        if re.search(pattern, response):
                            response = re.sub(pattern, replacement, response, count=1)
                            inserted = True
                            break
                    
                    # If no contextual insertion, add at the end of first paragraph
                    if not inserted:
                        paragraphs = response.split('\n\n')
                        if len(paragraphs) > 0:
                            paragraphs[0] += f'\n{citation}'
                            response = '\n\n'.join(paragraphs)
                
            except Exception as e:
                logger.warning(f"Failed to add Islamic citation: {e}")
                continue
        
        return response


class EnhancedRAGEngine:
    """
    Enhanced RAG Engine with Islamic integration
    Backward compatible with existing system
    """
    
    def __init__(self):
        # Feature flags
        self.enable_islamic = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
        self.islamic_timeout = int(os.getenv("ISLAMIC_TIMEOUT", "2000"))  # 2s timeout
        
        # Initialize components
        self.unified_retrieval = None
        self.citation_fixer = EnhancedCitationFixer()
        
        # Performance tracking
        self.performance_metrics = {
            "total_queries": 0,
            "islamic_enhanced_queries": 0,
            "avg_response_time": 0.0,
            "islamic_retrieval_failures": 0
        }
        
        logger.info(f"Enhanced RAG Engine initialized - Islamic enabled: {self.enable_islamic}")
    
    async def initialize(self):
        """Initialize enhanced RAG engine"""
        try:
            if self.enable_islamic:
                self.unified_retrieval = UnifiedRetrievalOrchestrator()
                await self.unified_retrieval.initialize()
                logger.info("✅ Enhanced RAG Engine with Islamic sources initialized")
            else:
                logger.info("✅ Enhanced RAG Engine initialized (Islamic disabled)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced RAG Engine: {e}")
            # Fallback to base engine
            self.enable_islamic = False
            logger.warning("Falling back to base RAG engine without Islamic sources")
    
    async def process_query(self, query: str, conversation_history: List[Dict] = None, 
                          mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
        """
        Enhanced query processing with optional Islamic context
        """
        start_time = datetime.now()
        self.performance_metrics["total_queries"] += 1
        
        try:
            # Retrieve documents using enhanced or base retrieval
            if self.enable_islamic and self.unified_retrieval:
                # Use enhanced retrieval with Islamic sources
                search_results = await asyncio.wait_for(
                    self.unified_retrieval.retrieve(query, limit=15),
                    timeout=self.islamic_timeout / 1000.0
                )
                
                # Format results for processing
                formatted_results = format_unified_results(search_results)
                civil_chunks = [result.chunk for result in search_results 
                              if not (result.metadata and result.metadata.get('source_type') == 'islamic')]
                islamic_sources = [result for result in search_results 
                                 if result.metadata and result.metadata.get('source_type') == 'islamic']
                
                self.performance_metrics["islamic_enhanced_queries"] += 1
                logger.info(f"Enhanced retrieval: {len(civil_chunks)} civil + {len(islamic_sources)} Islamic")
                
            else:
                # Fallback to base engine retrieval
                base_engine = get_base_rag_engine()
                search_results = await base_engine.vector_store.search(query, limit=10)
                civil_chunks = [result.chunk for result in search_results]
                islamic_sources = []
                formatted_results = {'civil_sources': civil_chunks, 'islamic_sources': [], 'has_islamic_context': False}
                logger.info(f"Base retrieval: {len(civil_chunks)} civil sources")
            
            # Generate AI response using existing logic
            ai_response = await self.generate_ai_response(query, civil_chunks, conversation_history, mode)
            
            # Enhanced citation fixing
            final_response = self.citation_fixer.fix_citations(
                ai_response, 
                civil_chunks,
                islamic_sources
            )
            
            # Calculate performance metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_performance_metrics(response_time)
            
            # Prepare response
            response_data = {
                "answer": final_response,
                "sources": {
                    "civil": [{"title": chunk.title, "content": chunk.content[:200]} for chunk in civil_chunks[:5]],
                    "islamic": [{"title": source.chunk.title, 
                               "content": getattr(source.chunk, 'legal_principle', '')[:200],
                               "verse_reference": getattr(source.chunk, 'verse_reference', '')} 
                              for source in islamic_sources[:3]]
                },
                "has_islamic_context": len(islamic_sources) > 0,
                "processing_time_ms": int(response_time * 1000),
                "mode": mode.value,
                "enhanced": self.enable_islamic
            }
            
            return response_data
            
        except asyncio.TimeoutError:
            logger.warning("Islamic retrieval timeout, falling back to civil only")
            self.performance_metrics["islamic_retrieval_failures"] += 1
            return await self.fallback_to_base_engine(query, conversation_history, mode)
        
        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}")
            return await self.fallback_to_base_engine(query, conversation_history, mode)
    
    async def fallback_to_base_engine(self, query: str, conversation_history: List[Dict] = None,
                                    mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
        """
        Fallback to base RAG engine when enhanced processing fails
        """
        try:
            logger.info("Using fallback base RAG engine")
            base_engine = get_base_rag_engine()
            
            # Use base engine processing
            search_results = await base_engine.vector_store.search(query, limit=10)
            chunks = [result.chunk for result in search_results]
            
            ai_response = await self.generate_ai_response(query, chunks, conversation_history, mode)
            final_response = base_engine.citation_fixer.fix_citations(ai_response, chunks)
            
            return {
                "answer": final_response,
                "sources": {"civil": [{"title": chunk.title, "content": chunk.content[:200]} for chunk in chunks[:5]]},
                "has_islamic_context": False,
                "processing_time_ms": 1000,  # Estimate
                "mode": mode.value,
                "enhanced": False,
                "fallback": True
            }
            
        except Exception as fallback_error:
            logger.error(f"Even fallback failed: {fallback_error}")
            return {
                "answer": "عذراً، حدث خطأ في معالجة استفسارك. يرجى المحاولة مرة أخرى.",
                "sources": {"civil": []},
                "has_islamic_context": False,
                "processing_time_ms": 0,
                "mode": mode.value,
                "enhanced": False,
                "error": True
            }
    
    async def generate_ai_response(self, query: str, chunks: List, 
                                 conversation_history: List[Dict] = None,
                                 mode: ProcessingMode = ProcessingMode.STRATEGIC) -> str:
        """
        Generate AI response using existing prompt templates
        """
        try:
            # Use existing classification logic
            from rag_engine import classify_query_intent, select_context_documents
            
            # Classify query
            classification = await classify_query_intent(query)
            intent_category = classification.get("category", "GENERAL_QUESTION")
            
            # Select and score documents  
            selected_docs = await select_context_documents(chunks, query, intent_category)
            
            # Build context
            context = "\n\n".join([f"المرجع {i+1}: {doc.title}\n{doc.content[:1000]}" 
                                  for i, doc in enumerate(selected_docs[:8])])
            
            # Use existing prompt template
            prompt_template = PROMPT_TEMPLATES.get(intent_category, PROMPT_TEMPLATES["GENERAL_QUESTION"])
            
            # Add conversation history if available
            history_context = ""
            if conversation_history:
                recent_history = conversation_history[-3:]  # Last 3 messages
                history_context = "\n".join([f"{msg['role']}: {msg['content'][:200]}" 
                                           for msg in recent_history])
            
            # Build final prompt
            history_section = f"السياق السابق للمحادثة:\n{history_context}\n" if history_context else ""
            
            final_prompt = f"""{prompt_template}

المراجع القانونية المتاحة:
{context}

{history_section}

السؤال: {query}

اعطِ إجابة شاملة ومفصلة مع الاستشهاد المناسب من المراجع:"""

            # Generate response
            response = await ai_client.chat.completions.create(
                model=ai_model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return "عذراً، لم أتمكن من إنتاج إجابة مناسبة لاستفسارك. يرجى إعادة صياغة السؤال."
    
    def update_performance_metrics(self, response_time: float):
        """Update performance metrics"""
        if self.performance_metrics["total_queries"] > 0:
            # Rolling average
            current_avg = self.performance_metrics["avg_response_time"]
            total_queries = self.performance_metrics["total_queries"]
            
            self.performance_metrics["avg_response_time"] = (
                (current_avg * (total_queries - 1) + response_time) / total_queries
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        status = {
            "enhanced_rag": {
                "status": "healthy",
                "islamic_enabled": self.enable_islamic,
                "performance": self.performance_metrics.copy()
            }
        }
        
        if self.enable_islamic and self.unified_retrieval:
            status["unified_retrieval"] = await self.unified_retrieval.health_check()
        
        return status


# Global enhanced engine instance
_enhanced_engine = None

async def get_enhanced_rag_engine() -> EnhancedRAGEngine:
    """
    Get or create enhanced RAG engine instance
    """
    global _enhanced_engine
    
    if _enhanced_engine is None:
        _enhanced_engine = EnhancedRAGEngine()
        await _enhanced_engine.initialize()
    
    return _enhanced_engine


# Backward compatibility function
async def process_query_enhanced(query: str, conversation_history: List[Dict] = None,
                               mode: ProcessingMode = ProcessingMode.STRATEGIC) -> Dict[str, Any]:
    """
    Main function for enhanced query processing
    Maintains backward compatibility while adding Islamic context
    """
    engine = await get_enhanced_rag_engine()
    return await engine.process_query(query, conversation_history, mode)


# Streaming support for chat interface
async def process_query_enhanced_streaming(query: str, conversation_history: List[Dict] = None,
                                         mode: ProcessingMode = ProcessingMode.STRATEGIC) -> AsyncIterator[str]:
    """
    Streaming version for chat interface
    """
    try:
        # Get full response first
        result = await process_query_enhanced(query, conversation_history, mode)
        answer = result.get("answer", "")
        
        # Stream the response word by word
        words = answer.split()
        for i, word in enumerate(words):
            if i == 0:
                yield word
            else:
                yield f" {word}"
            
            # Small delay for streaming effect
            await asyncio.sleep(0.02)
        
        # Send metadata at the end
        if result.get("has_islamic_context"):
            yield f"\n\n📚 المراجع الإسلامية: {len(result['sources']['islamic'])} مصدر"
        
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        yield "عذراً، حدث خطأ في معالجة استفسارك."


# Health check endpoint
async def health_check_enhanced() -> Dict[str, Any]:
    """
    Health check for enhanced RAG system
    """
    try:
        engine = await get_enhanced_rag_engine()
        return await engine.get_health_status()
    except Exception as e:
        return {
            "enhanced_rag": {
                "status": "error",
                "error": str(e)
            }
        }


if __name__ == "__main__":
    # Test the enhanced engine
    async def test_enhanced_engine():
        test_queries = [
            "ما هي أحكام الميراث في النظام السعودي؟",
            "كيف أقدم دعوى قضائية؟", 
            "شروط صحة عقد البيع",
            "أحكام الطلاق"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            result = await process_query_enhanced(query)
            print(f"✅ Response length: {len(result['answer'])} chars")
            print(f"🏛️ Civil sources: {len(result['sources']['civil'])}")
            print(f"🕌 Islamic sources: {len(result['sources']['islamic'])}")
            print(f"⏱️ Processing time: {result['processing_time_ms']}ms")
        
        # Health check
        health = await health_check_enhanced()
        print(f"\n🏥 Health Status: {health}")
    
    asyncio.run(test_enhanced_engine())