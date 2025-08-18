"""
Islamic-Primary Retrieval System
Islamic law as foundation, civil law as implementation
Reflects the true nature of Saudi legal system
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


class IslamicPrimaryClassifier:
    """
    Classify queries based on Islamic legal framework
    Every legal matter has Islamic foundation
    """
    
    def __init__(self):
        # Legal domains that ALWAYS need Islamic foundation
        self.islamic_foundation_required = [
            # Family Law (الأحوال الشخصية)
            "زواج", "نكاح", "طلاق", "خلع", "فسخ", "عدة", "نفقة", "حضانة", "مهر",
            "marriage", "divorce", "custody", "alimony", "dowry",
            
            # Inheritance Law (المواريث)
            "ميراث", "وراثة", "تركة", "وصية", "حجب", "عصبة", "فرائض",
            "inheritance", "estate", "will", "heirs",
            
            # Financial Law (المعاملات المالية)
            "ربا", "فوائد", "غرر", "مضاربة", "مرابحة", "إجارة", "سلم", "استصناع",
            "riba", "interest", "usury", "islamic banking", "sukuk",
            
            # Contract Law (العقود)
            "عقد", "بيع", "شراء", "إيجار", "شركة", "وكالة", "كفالة", "رهن",
            "contract", "sale", "purchase", "lease", "partnership", "guarantee",
            
            # Criminal Law (الجنايات والحدود)
            "حدود", "قصاص", "دية", "تعزير", "جناية", "قتل", "سرقة", "زنا", "قذف",
            "hudud", "qisas", "diyya", "crime", "punishment", "theft",
            
            # Evidence Law (البينات والشهادات)
            "شهادة", "إثبات", "بينة", "يمين", "قرينة", "إقرار",
            "testimony", "evidence", "witness", "oath", "proof",
            
            # Property Law (الملكية والحقوق)
            "ملكية", "حق", "انتفاع", "ارتفاق", "حيازة", "تصرف",
            "property", "ownership", "rights", "possession",
            
            # Commercial Law (التجارة)
            "تجارة", "بضاعة", "أسهم", "شركات", "إفلاس", "تأمين",
            "commerce", "trade", "stocks", "companies", "bankruptcy", "insurance"
        ]
        
        # Only procedural matters don't need Islamic foundation
        self.procedural_only = [
            "إجراءات", "نموذج", "استمارة", "خطوات", "موعد", "تاريخ",
            "رسوم", "تكلفة", "مدة", "كيف أقدم", "أين أذهب", "متى",
            "deadline", "procedure", "form", "steps", "fee", "how to submit", "where to go"
        ]
        
        # Modern legal areas that still have Islamic principles
        self.modern_with_islamic = [
            "قانون العمل", "تأمينات", "ضرائب", "جمارك", "بيئة", "طيران", "تأمينات اجتماعية",
            "labor law", "insurance", "tax", "customs", "environment", "aviation", "social insurance"
        ]
    
    def get_retrieval_strategy(self, query: str) -> Dict[str, Any]:
        """
        Determine retrieval strategy based on Islamic legal framework
        """
        query_lower = query.lower()
        
        # Check if purely procedural
        is_procedural = any(term in query_lower for term in self.procedural_only)
        if is_procedural:
            return {
                "strategy": "civil_only",
                "reason": "procedural_matter",
                "islamic_priority": 0.0,
                "civil_priority": 1.0
            }
        
        # Check if has Islamic foundation
        has_islamic_foundation = any(term in query_lower for term in self.islamic_foundation_required)
        
        # Check if modern area with Islamic principles
        is_modern_islamic = any(term in query_lower for term in self.modern_with_islamic)
        
        if has_islamic_foundation:
            return {
                "strategy": "islamic_primary",
                "reason": "direct_islamic_foundation",
                "islamic_priority": 0.8,  # High priority for Islamic sources
                "civil_priority": 0.6,   # Medium priority for implementation
                "response_structure": "islamic_foundation_first"
            }
        
        elif is_modern_islamic:
            return {
                "strategy": "islamic_secondary", 
                "reason": "modern_with_islamic_principles",
                "islamic_priority": 0.5,  # Medium priority for principles
                "civil_priority": 0.8,   # High priority for modern implementation
                "response_structure": "civil_with_islamic_principles"
            }
        
        else:
            # Default: every legal matter has some Islamic foundation
            return {
                "strategy": "islamic_context",
                "reason": "general_legal_matter",
                "islamic_priority": 0.3,  # Low but present
                "civil_priority": 0.9,   # High priority for civil
                "response_structure": "civil_with_islamic_context"
            }
    
    def get_islamic_query_enhancement(self, query: str, strategy: str) -> str:
        """
        Enhance query for Islamic retrieval based on strategy
        """
        enhancements = []
        query_lower = query.lower()
        
        # Add Islamic context terms based on detected domain
        if any(term in query_lower for term in ["عقد", "contract", "بيع", "sale"]):
            enhancements.extend(["العقود في الشريعة", "البيع والشراء في الفقه"])
        
        if any(term in query_lower for term in ["ميراث", "inheritance", "وراثة"]):
            enhancements.extend(["أحكام الميراث", "الفرائض", "المواريث"])
        
        if any(term in query_lower for term in ["زواج", "marriage", "نكاح"]):
            enhancements.extend(["أحكام النكاح", "الزواج في الفقه"])
        
        if any(term in query_lower for term in ["شهادة", "testimony", "إثبات"]):
            enhancements.extend(["أحكام الشهادة", "البينات في الفقه"])
        
        if any(term in query_lower for term in ["ربا", "interest", "فوائد"]):
            enhancements.extend(["تحريم الربا", "المعاملات المصرفية الإسلامية"])
        
        if any(term in query_lower for term in ["عقوبة", "punishment", "جريمة"]):
            enhancements.extend(["الحدود والتعازير", "العقوبات في الشريعة"])
        
        # Add general Islamic legal terms for broader context
        if strategy == "islamic_primary":
            enhancements.extend(["الأحكام الشرعية", "الفقه الإسلامي"])
        elif strategy == "islamic_secondary":
            enhancements.extend(["المبادئ الشرعية", "الأسس الفقهية"])
        
        if enhancements:
            enhanced_query = f"{query} {' '.join(enhancements)}"
            return enhanced_query
        
        return query


class IslamicPrimaryOrchestrator:
    """
    Islamic-Primary Retrieval Orchestrator
    Islamic foundation → Civil implementation
    """
    
    def __init__(self):
        # Initialize stores
        self.civil_store = SqliteVectorStore("data/vectors.db")
        self.islamic_store = IslamicVectorStore("data/islamic_vectors.db")
        
        # Initialize classifier
        self.classifier = IslamicPrimaryClassifier()
        
        # Configuration
        self.enable_islamic = os.getenv("ENABLE_ISLAMIC_SOURCES", "true").lower() == "true"
        self.islamic_max_results = int(os.getenv("ISLAMIC_MAX_RESULTS", "5"))  # Increased
        self.civil_max_results = int(os.getenv("CIVIL_MAX_RESULTS", "8"))
        
        # Performance monitoring
        self.metrics = {
            "islamic_primary_queries": 0,
            "islamic_secondary_queries": 0,
            "civil_only_queries": 0,
            "total_queries": 0
        }
        
        logger.info("Islamic-Primary Retrieval initialized - Islamic foundation approach")
    
    async def initialize(self):
        """Initialize both stores"""
        try:
            await self.civil_store.initialize()
            if self.enable_islamic:
                await self.islamic_store.initialize()
            logger.info("✅ Islamic-Primary Retrieval stores initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize stores: {e}")
            raise
    
    async def retrieve(self, query: str, limit: int = 15) -> Dict[str, Any]:
        """
        Islamic-primary retrieval with proper hierarchy
        """
        self.metrics["total_queries"] += 1
        
        try:
            # Determine retrieval strategy
            strategy_info = self.classifier.get_retrieval_strategy(query)
            strategy = strategy_info["strategy"]
            
            # Update metrics
            if strategy == "islamic_primary":
                self.metrics["islamic_primary_queries"] += 1
            elif strategy in ["islamic_secondary", "islamic_context"]:
                self.metrics["islamic_secondary_queries"] += 1
            else:
                self.metrics["civil_only_queries"] += 1
            
            if strategy == "civil_only":
                # Civil only for purely procedural matters
                civil_results = await self.civil_store.search(query, limit=limit)
                
                return {
                    "results": civil_results,
                    "strategy": strategy,
                    "islamic_sources": [],
                    "civil_sources": [r.chunk for r in civil_results],
                    "response_structure": "civil_only",
                    "foundation_type": "procedural"
                }
            
            # For all other cases, get both Islamic and civil sources
            enhanced_query = self.classifier.get_islamic_query_enhancement(query, strategy)
            
            # Parallel retrieval with different priorities
            islamic_limit = int(limit * strategy_info["islamic_priority"])
            civil_limit = int(limit * strategy_info["civil_priority"])
            
            islamic_task = self.islamic_store.search(
                enhanced_query,
                limit=max(1, islamic_limit),
                threshold=0.3  # Lower threshold for more results
            )
            
            # For now, use a simple search since we don't have embeddings ready
            # TODO: Replace with proper embedding-based search
            civil_task = self._simple_civil_search(query, max(1, civil_limit))
            
            # Wait for both results
            islamic_results, civil_results = await asyncio.gather(
                islamic_task,
                civil_task,
                return_exceptions=True
            )
            
            # Handle exceptions gracefully
            if isinstance(islamic_results, Exception):
                logger.error(f"Islamic retrieval failed: {islamic_results}")
                islamic_results = []
            
            if isinstance(civil_results, Exception):
                logger.error(f"Civil retrieval failed: {civil_results}")
                civil_results = []
            
            # Merge with Islamic priority
            merged_results = self.merge_with_islamic_priority(
                islamic_results, 
                civil_results, 
                strategy_info
            )
            
            logger.info(f"Islamic-Primary retrieval: {len(islamic_results)} Islamic + {len(civil_results)} civil = {len(merged_results)} total (strategy: {strategy})")
            
            return {
                "results": merged_results,
                "strategy": strategy,
                "islamic_sources": islamic_results,
                "civil_sources": [r.chunk for r in civil_results],
                "response_structure": strategy_info.get("response_structure"),
                "foundation_type": "islamic_primary" if islamic_results else "civil_primary"
            }
            
        except Exception as e:
            logger.error(f"Islamic-Primary retrieval failed: {e}")
            # Fallback to civil only
            civil_results = await self._simple_civil_search(query, limit)
            return {
                "results": civil_results,
                "strategy": "fallback_civil",
                "islamic_sources": [],
                "civil_sources": [r.chunk for r in civil_results],
                "response_structure": "civil_only",
                "foundation_type": "fallback"
            }
    
    def merge_with_islamic_priority(self, islamic_results: List, civil_results: List, 
                                  strategy_info: Dict) -> List[SearchResult]:
        """
        Merge results with Islamic sources taking priority
        """
        merged = []
        strategy = strategy_info["strategy"]
        
        if strategy == "islamic_primary":
            # Islamic foundation first, then civil implementation
            for i, islamic_result in enumerate(islamic_results):
                islamic_result.metadata = islamic_result.metadata or {}
                islamic_result.metadata.update({
                    'source_type': 'islamic',
                    'display_priority': 'foundation',  # Highest priority
                    'position': f'foundation_{i+1}',
                    'citation_style': 'quranic'
                })
                merged.append(islamic_result)
            
            # Add civil sources as implementation
            for i, civil_result in enumerate(civil_results):
                civil_result.metadata = civil_result.metadata or {}
                civil_result.metadata.update({
                    'source_type': 'civil',
                    'display_priority': 'implementation',
                    'position': f'implementation_{i+1}',
                    'citation_style': 'legal'
                })
                merged.append(civil_result)
        
        elif strategy in ["islamic_secondary", "islamic_context"]:
            # Civil primary, but with Islamic context
            for i, civil_result in enumerate(civil_results):
                civil_result.metadata = civil_result.metadata or {}
                civil_result.metadata.update({
                    'source_type': 'civil',
                    'display_priority': 'primary',
                    'position': f'primary_{i+1}',
                    'citation_style': 'legal'
                })
                merged.append(civil_result)
            
            # Add Islamic context
            for i, islamic_result in enumerate(islamic_results):
                islamic_result.metadata = islamic_result.metadata or {}
                islamic_result.metadata.update({
                    'source_type': 'islamic',
                    'display_priority': 'context',
                    'position': f'context_{i+1}',
                    'citation_style': 'quranic'
                })
                merged.append(islamic_result)
        
        return merged
    
    async def _simple_civil_search(self, query: str, limit: int) -> List[SearchResult]:
        """
        Simple civil search helper method
        TODO: Replace with proper embedding search when available
        """
        try:
            # For now, return empty list since we need to implement proper search
            # This is a placeholder for the civil law search
            logger.warning(f"Civil search not yet implemented for query: {query}")
            return []
        except Exception as e:
            logger.error(f"Civil search failed: {e}")
            return []
    
    async def get_islamic_foundation_only(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Get only Islamic foundation for a query"""
        if not self.enable_islamic:
            return []
        
        enhanced_query = self.classifier.get_islamic_query_enhancement(query, "islamic_primary")
        return await self.islamic_store.search(enhanced_query, limit=limit, threshold=0.2)
    
    def get_metrics(self) -> Dict:
        """Get retrieval metrics"""
        total = self.metrics["total_queries"]
        if total == 0:
            return self.metrics
        
        return {
            **self.metrics,
            "islamic_primary_percentage": (self.metrics["islamic_primary_queries"] / total) * 100,
            "islamic_usage_percentage": ((self.metrics["islamic_primary_queries"] + 
                                        self.metrics["islamic_secondary_queries"]) / total) * 100
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Islamic-primary system"""
        health = {
            "islamic_primary_system": {"status": "healthy"},
            "civil_store": {"status": "unknown"},
            "islamic_store": {"status": "unknown"},
            "metrics": self.get_metrics()
        }
        
        # Check stores
        try:
            civil_stats = await self.civil_store.get_stats()
            health["civil_store"] = {
                "status": "healthy",
                "chunks": civil_stats.total_chunks
            }
        except Exception as e:
            health["civil_store"] = {"status": "error", "error": str(e)}
        
        if self.enable_islamic:
            try:
                islamic_stats = await self.islamic_store.get_stats()
                health["islamic_store"] = {
                    "status": "healthy",
                    "chunks": islamic_stats.total_chunks,
                    "avg_confidence": islamic_stats.metadata.get('avg_legal_confidence', 0)
                }
            except Exception as e:
                health["islamic_store"] = {"status": "error", "error": str(e)}
        
        return health


def format_islamic_primary_results(retrieval_data: Dict) -> Dict[str, Any]:
    """
    Format results with Islamic-primary structure
    """
    strategy = retrieval_data["strategy"]
    islamic_sources = retrieval_data["islamic_sources"]
    civil_sources = retrieval_data["civil_sources"]
    foundation_type = retrieval_data["foundation_type"]
    
    formatted = {
        'strategy': strategy,
        'foundation_type': foundation_type,
        'response_structure': retrieval_data.get("response_structure"),
        'sources': {
            'islamic_foundation': [],
            'civil_implementation': [],
            'total_sources': len(islamic_sources) + len(civil_sources)
        }
    }
    
    # Format Islamic sources as foundation
    for result in islamic_sources:
        formatted['sources']['islamic_foundation'].append({
            'content': result.chunk.content,
            'title': result.chunk.title,
            'verse_reference': getattr(result.chunk, 'verse_reference', ''),
            'legal_principle': getattr(result.chunk, 'legal_principle', ''),
            'citation': create_islamic_citation(result.chunk) if hasattr(result.chunk, 'verse_reference') else '',
            'confidence': result.similarity_score,
            'type': 'foundation'
        })
    
    # Format civil sources as implementation
    for chunk in civil_sources:
        formatted['sources']['civil_implementation'].append({
            'content': chunk.content[:300],
            'title': chunk.title,
            'type': 'implementation'
        })
    
    return formatted


async def test_islamic_primary():
    """Test Islamic-primary retrieval"""
    orchestrator = IslamicPrimaryOrchestrator()
    await orchestrator.initialize()
    
    test_queries = [
        "ما أحكام الميراث في النظام السعودي؟",  # Should be Islamic primary
        "شروط عقد البيع",  # Should be Islamic primary
        "كيف أقدم طلب للمحكمة؟",  # Should be civil only
        "عقوبة السرقة",  # Should be Islamic primary
        "رسوم التقاضي"  # Should be civil only
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        result = await orchestrator.retrieve(query)
        formatted = format_islamic_primary_results(result)
        
        print(f"   Strategy: {result['strategy']}")
        print(f"   Foundation: {result['foundation_type']}")
        print(f"   Islamic sources: {len(result['islamic_sources'])}")
        print(f"   Civil sources: {len(result['civil_sources'])}")
    
    print(f"\n📊 Metrics: {orchestrator.get_metrics()}")


if __name__ == "__main__":
    asyncio.run(test_islamic_primary())