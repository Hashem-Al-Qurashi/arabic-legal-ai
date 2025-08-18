"""
Unified Retrieval Orchestrator
Coordinates between civil law and Islamic sources
Smart routing with conflict prevention
"""
import asyncio
import logging
import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

from app.storage.sqlite_store import SqliteVectorStore
from app.storage.islamic_vector_store import IslamicVectorStore, IslamicChunk, create_islamic_citation
from app.storage.vector_store import SearchResult, Chunk

logger = logging.getLogger(__name__)


class QueryClassifier:
    """
    Smart classifier to determine when Islamic sources should be included
    """
    
    def __init__(self):
        # Terms that ALWAYS need Islamic context
        self.always_include = [
            # Arabic terms
            "ميراث", "وراثة", "تركة", "وصية",
            "زواج", "نكاح", "طلاق", "خلع", "عدة", "مهر", "نفقة",
            "ربا", "فوائد", "رباوي", "ربوي",
            "حلال", "حرام", "شرعي", "شريعة", "فقه", "أحكام",
            "شهادة", "إثبات", "بينة", "يمين",
            "حدود", "قصاص", "دية", "تعزير",
            
            # English terms
            "inheritance", "inherit", "will", "estate",
            "marriage", "divorce", "custody", "alimony",
            "interest", "riba", "usury", "islamic banking",
            "halal", "haram", "sharia", "islamic law", "fiqh",
            "testimony", "witness", "oath",
            "hudud", "qisas", "diyya"
        ]
        
        # Terms that CONDITIONALLY need Islamic context
        self.conditionally_include = [
            # Contract and business terms
            "عقد", "بيع", "شراء", "إيجار", "شركة", "مضاربة",
            "contract", "sale", "purchase", "rental", "partnership",
            
            # Property and ownership
            "ملكية", "أرض", "عقار", "حق", "انتفاع",
            "property", "ownership", "land", "real estate", "rights",
            
            # Dispute resolution
            "نزاع", "خلاف", "تحكيم", "صلح", "قضاء",
            "dispute", "conflict", "arbitration", "settlement", "court",
            
            # Criminal law
            "جريمة", "عقوبة", "جناية", "مخالفة",
            "crime", "punishment", "felony", "violation"
        ]
        
        # Terms that should NEVER include Islamic context
        self.never_include = [
            # Procedural questions
            "إجراءات", "نموذج", "خطوات", "كيفية", "طريقة",
            "procedure", "form", "steps", "how to", "process",
            
            # Administrative questions
            "موعد", "مدة", "وقت", "تاريخ", "deadline", "time", "date",
            "رسوم", "تكلفة", "سعر", "fee", "cost", "price",
            "مستندات", "أوراق", "documents", "papers",
            
            # Technical questions
            "نظام", "برنامج", "موقع", "تطبيق", "system", "software", "website", "app"
        ]
    
    def should_include_islamic(self, query: str) -> Tuple[bool, str]:
        """
        Determine if Islamic sources should be included
        Returns (should_include, reason)
        """
        query_lower = query.lower()
        
        # Check never include first (highest priority)
        for term in self.never_include:
            if term in query_lower:
                return False, f"procedural_question: {term}"
        
        # Check always include
        for term in self.always_include:
            if term in query_lower:
                return True, f"always_include: {term}"
        
        # Check conditional include
        conditional_matches = []
        for term in self.conditionally_include:
            if term in query_lower:
                conditional_matches.append(term)
        
        if conditional_matches:
            # Additional context analysis for conditional terms
            
            # Check for legal substance indicators
            legal_indicators = [
                "حكم", "قانون", "نظام", "شرعي", "فقهي", "حق", "واجب",
                "ruling", "law", "legal", "right", "obligation"
            ]
            
            has_legal_context = any(indicator in query_lower for indicator in legal_indicators)
            
            if has_legal_context:
                return True, f"conditional_with_legal_context: {conditional_matches[0]}"
            else:
                return False, f"conditional_without_legal_context: {conditional_matches[0]}"
        
        return False, "no_matching_terms"
    
    def get_islamic_query_enhancement(self, query: str) -> str:
        """
        Enhance query for better Islamic source matching
        """
        query_lower = query.lower()
        
        # Add Islamic context terms for better matching
        enhancements = []
        
        if any(term in query_lower for term in ["عقد", "contract"]):
            enhancements.append("العقود في الشريعة")
        
        if any(term in query_lower for term in ["ميراث", "inheritance"]):
            enhancements.append("أحكام الميراث")
        
        if any(term in query_lower for term in ["زواج", "marriage"]):
            enhancements.append("أحكام النكاح")
        
        if any(term in query_lower for term in ["شهادة", "testimony"]):
            enhancements.append("أحكام الشهادة")
        
        if enhancements:
            enhanced_query = f"{query} {' '.join(enhancements)}"
            return enhanced_query
        
        return query


class UnifiedRetrievalOrchestrator:
    """
    Coordinates retrieval between civil law and Islamic sources
    Prevents conflicts and ensures optimal performance
    """
    
    def __init__(self):
        # Initialize stores
        self.civil_store = SqliteVectorStore("backend/data/vectors.db")
        self.islamic_store = IslamicVectorStore("backend/data/islamic_vectors.db")
        
        # Initialize classifier
        self.classifier = QueryClassifier()
        
        # Feature flags
        self.enable_islamic = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
        self.islamic_max_results = int(os.getenv("ISLAMIC_MAX_RESULTS", "3"))
        self.islamic_threshold = float(os.getenv("ISLAMIC_THRESHOLD", "0.5"))
        
        # Performance monitoring
        self.metrics = {
            "civil_query_count": 0,
            "islamic_query_count": 0,
            "combined_query_count": 0,
            "islamic_inclusion_rate": 0.0
        }
        
        logger.info(f"Unified Retrieval initialized - Islamic enabled: {self.enable_islamic}")
    
    async def initialize(self):
        """Initialize both stores"""
        try:
            await self.civil_store.initialize()
            if self.enable_islamic:
                await self.islamic_store.initialize()
            logger.info("✅ Unified Retrieval stores initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize stores: {e}")
            raise
    
    async def retrieve(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Main retrieval method - coordinates between civil and Islamic sources
        """
        try:
            # Always get civil law results first
            civil_task = self.civil_store.search(query, limit=limit)
            
            # Determine if Islamic sources needed
            needs_islamic, reason = self.classifier.should_include_islamic(query)
            
            if self.enable_islamic and needs_islamic:
                # Enhanced query for Islamic search
                enhanced_query = self.classifier.get_islamic_query_enhancement(query)
                
                # Parallel retrieval for performance
                islamic_task = self.islamic_store.search(
                    enhanced_query,
                    limit=min(self.islamic_max_results, limit // 2),
                    threshold=self.islamic_threshold
                )
                
                # Wait for both results
                civil_results, islamic_results = await asyncio.gather(
                    civil_task,
                    islamic_task,
                    return_exceptions=True
                )
                
                # Handle exceptions gracefully
                if isinstance(civil_results, Exception):
                    logger.error(f"Civil retrieval failed: {civil_results}")
                    civil_results = []
                
                if isinstance(islamic_results, Exception):
                    logger.error(f"Islamic retrieval failed: {islamic_results}")
                    islamic_results = []
                
                # Merge results intelligently
                merged_results = self.smart_merge(civil_results, islamic_results, reason)
                
                # Update metrics
                self.metrics["combined_query_count"] += 1
                self.metrics["islamic_query_count"] += 1
                
                logger.info(f"Combined retrieval: {len(civil_results)} civil + {len(islamic_results)} Islamic = {len(merged_results)} total")
                
                return merged_results
            
            else:
                # Civil only
                civil_results = await civil_task
                
                # Update metrics
                self.metrics["civil_query_count"] += 1
                
                logger.info(f"Civil-only retrieval: {len(civil_results)} results (reason: {reason})")
                
                return civil_results
                
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            # Fallback to civil only
            try:
                return await self.civil_store.search(query, limit=limit)
            except Exception as fallback_error:
                logger.error(f"Fallback retrieval also failed: {fallback_error}")
                return []
    
    def smart_merge(self, civil_results: List[SearchResult], islamic_results: List[SearchResult], 
                   inclusion_reason: str) -> List[SearchResult]:
        """
        Intelligently merge civil and Islamic results
        """
        # Start with civil results (primary content)
        merged = civil_results.copy()
        
        # Process Islamic results
        for islamic_result in islamic_results:
            # Tag Islamic sources clearly
            islamic_result.metadata = islamic_result.metadata or {}
            islamic_result.metadata.update({
                'source_type': 'islamic',
                'display_priority': 'supporting',  # Not main answer
                'inclusion_reason': inclusion_reason,
                'citation_style': 'quranic'
            })
            
            # Add Islamic citation if it's a verse
            if hasattr(islamic_result.chunk, 'verse_reference'):
                islamic_chunk = islamic_result.chunk
                islamic_result.metadata['formatted_citation'] = create_islamic_citation(islamic_chunk)
            
            # Insert Islamic results strategically
            if inclusion_reason.startswith("always_include"):
                # High priority - insert early
                insert_position = min(2, len(merged))
                merged.insert(insert_position, islamic_result)
            else:
                # Lower priority - append at end
                merged.append(islamic_result)
        
        # Limit total results
        return merged[:15]  # Reasonable limit
    
    async def get_islamic_context_only(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Get only Islamic context for specific queries
        """
        if not self.enable_islamic:
            return []
        
        try:
            enhanced_query = self.classifier.get_islamic_query_enhancement(query)
            return await self.islamic_store.search(enhanced_query, limit=limit, threshold=0.4)
        except Exception as e:
            logger.error(f"Islamic-only retrieval failed: {e}")
            return []
    
    async def get_civil_context_only(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Get only civil law context
        """
        try:
            return await self.civil_store.search(query, limit=limit)
        except Exception as e:
            logger.error(f"Civil-only retrieval failed: {e}")
            return []
    
    def get_metrics(self) -> Dict:
        """Get retrieval metrics for monitoring"""
        total_queries = (self.metrics["civil_query_count"] + 
                        self.metrics["combined_query_count"])
        
        if total_queries > 0:
            self.metrics["islamic_inclusion_rate"] = (
                self.metrics["islamic_query_count"] / total_queries
            ) * 100
        
        return self.metrics.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for both stores
        """
        health = {
            "civil_store": {"status": "unknown", "error": None},
            "islamic_store": {"status": "unknown", "error": None},
            "unified_retrieval": {"status": "healthy"},
            "islamic_enabled": self.enable_islamic,
            "metrics": self.get_metrics()
        }
        
        # Check civil store
        try:
            civil_stats = await self.civil_store.get_stats()
            health["civil_store"] = {
                "status": "healthy",
                "chunks": civil_stats.total_chunks,
                "last_updated": civil_stats.last_updated
            }
        except Exception as e:
            health["civil_store"] = {"status": "error", "error": str(e)}
        
        # Check Islamic store
        if self.enable_islamic:
            try:
                islamic_stats = await self.islamic_store.get_stats()
                health["islamic_store"] = {
                    "status": "healthy",
                    "chunks": islamic_stats.total_chunks,
                    "last_updated": islamic_stats.last_updated,
                    "avg_confidence": islamic_stats.metadata.get('avg_legal_confidence', 0)
                }
            except Exception as e:
                health["islamic_store"] = {"status": "error", "error": str(e)}
        else:
            health["islamic_store"] = {"status": "disabled"}
        
        return health


# Utility functions
def format_unified_results(results: List[SearchResult]) -> Dict[str, Any]:
    """
    Format unified results for display
    """
    civil_results = []
    islamic_results = []
    
    for result in results:
        if result.metadata and result.metadata.get('source_type') == 'islamic':
            islamic_results.append({
                'content': result.chunk.content,
                'title': result.chunk.title,
                'score': result.score,
                'citation': result.metadata.get('formatted_citation', ''),
                'legal_principle': getattr(result.chunk, 'legal_principle', ''),
                'verse_reference': getattr(result.chunk, 'verse_reference', '')
            })
        else:
            civil_results.append({
                'content': result.chunk.content,
                'title': result.chunk.title,
                'score': result.score,
                'type': 'civil'
            })
    
    return {
        'civil_sources': civil_results,
        'islamic_sources': islamic_results,
        'total_results': len(results),
        'has_islamic_context': len(islamic_results) > 0
    }


async def test_unified_retrieval():
    """
    Test function for unified retrieval
    """
    orchestrator = UnifiedRetrievalOrchestrator()
    await orchestrator.initialize()
    
    test_queries = [
        "ما هي أحكام الميراث؟",  # Should include Islamic
        "كيف أقدم طلب للمحكمة؟",  # Should NOT include Islamic
        "شروط عقد البيع",  # Should conditionally include Islamic
        "رسوم القضايا",  # Should NOT include Islamic
        "أحكام الطلاق"  # Should include Islamic
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        results = await orchestrator.retrieve(query, limit=5)
        formatted = format_unified_results(results)
        print(f"   Civil: {len(formatted['civil_sources'])}, Islamic: {len(formatted['islamic_sources'])}")
    
    print(f"\n📊 Metrics: {orchestrator.get_metrics()}")
    print(f"🏥 Health: {await orchestrator.health_check()}")


if __name__ == "__main__":
    asyncio.run(test_unified_retrieval())