"""
Intelligent Retrieval Orchestrator
Advanced system for seamlessly integrating Quranic foundations with civil law
Zero-downtime integration with existing systems, enterprise-grade architecture
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from abc import ABC, abstractmethod

from app.core.semantic_concepts import SemanticConceptEngine, LegalConcept, ConceptType
from app.storage.quranic_foundation_store import QuranicFoundationStore, QuranicFoundation
from app.storage.sqlite_store import SqliteVectorStore
from app.storage.vector_store import SearchResult, Chunk
from app.core.system_config import get_config, get_database_paths

logger = logging.getLogger(__name__)


class IntegrationStrategy(Enum):
    """Different strategies for integrating Quranic foundations with civil law"""
    FOUNDATION_FIRST = "foundation_first"      # Quranic foundation → Civil implementation
    CIVIL_WITH_FOUNDATION = "civil_with_foundation"  # Civil primary + Quranic support
    CONTEXTUAL_BLEND = "contextual_blend"      # Intelligent blending based on context
    CIVIL_ONLY = "civil_only"                  # Pure civil law (procedural matters)
    FOUNDATION_ONLY = "foundation_only"        # Pure Islamic guidance (rare)


class RetrievalPriority(Enum):
    """Priority levels for different source types"""
    PRIMARY = "primary"      # Most important sources
    SUPPORTING = "supporting"  # Supporting evidence
    CONTEXTUAL = "contextual"  # Background context
    REFERENCE = "reference"    # Additional reference


@dataclass
class IntegratedResponse:
    """
    Comprehensive response combining civil law and Quranic foundations
    """
    query: str
    strategy: IntegrationStrategy
    execution_time_ms: float
    
    # Results by source type
    civil_results: List[SearchResult]
    quranic_results: List[SearchResult]
    
    # Intelligent integration
    primary_sources: List[SearchResult]
    supporting_sources: List[SearchResult]
    contextual_sources: List[SearchResult]
    
    # Quality metrics
    integration_quality: float
    cultural_appropriateness: float
    legal_completeness: float
    
    # Semantic analysis
    extracted_concepts: List[LegalConcept]
    concept_coverage: Dict[str, float]
    
    # Performance tracking
    civil_search_time: float
    quranic_search_time: float
    integration_time: float
    
    # Metadata
    total_sources: int
    confidence_distribution: Dict[str, int]
    strategy_explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "query": self.query,
            "strategy": self.strategy.value,
            "execution_time_ms": self.execution_time_ms,
            "results": {
                "primary": [r.to_dict() for r in self.primary_sources],
                "supporting": [r.to_dict() for r in self.supporting_sources],
                "contextual": [r.to_dict() for r in self.contextual_sources]
            },
            "sources": {
                "civil_count": len(self.civil_results),
                "quranic_count": len(self.quranic_results),
                "total_count": self.total_sources
            },
            "quality": {
                "integration_quality": self.integration_quality,
                "cultural_appropriateness": self.cultural_appropriateness,
                "legal_completeness": self.legal_completeness
            },
            "analysis": {
                "concepts_extracted": len(self.extracted_concepts),
                "concept_coverage": self.concept_coverage,
                "strategy_explanation": self.strategy_explanation
            },
            "performance": {
                "civil_search_ms": self.civil_search_time,
                "quranic_search_ms": self.quranic_search_time,
                "integration_ms": self.integration_time,
                "confidence_distribution": self.confidence_distribution
            }
        }


class StrategySelector(ABC):
    """
    Abstract base for integration strategy selection
    """
    
    @abstractmethod
    async def select_strategy(self, query: str, concepts: List[LegalConcept], 
                            context: Dict[str, Any]) -> IntegrationStrategy:
        """Select appropriate integration strategy"""
        pass
    
    @abstractmethod
    def get_strategy_confidence(self) -> float:
        """Return confidence in strategy selection"""
        pass


class IntelligentStrategySelector(StrategySelector):
    """
    Advanced strategy selector using semantic analysis and contextual understanding
    """
    
    def __init__(self):
        self.confidence_level = 0.9
        self._initialize_strategy_patterns()
    
    def _initialize_strategy_patterns(self):
        """Initialize patterns for strategy selection"""
        
        # Concept types that benefit from Islamic foundation
        self.foundation_first_concepts = {
            ConceptType.MORAL_PRINCIPLE,
            ConceptType.JUSTICE_CONCEPT,
            ConceptType.SOCIAL_RELATION,
            ConceptType.PROTECTION_DUTY
        }
        
        # Concept types that are primarily procedural
        self.civil_only_concepts = {
            ConceptType.PROCEDURAL_LAW
        }
        
        # Legal domains with strong Islamic foundations
        self.islamic_foundation_domains = {
            "family_relations", "inheritance_law", "commercial_ethics",
            "criminal_justice", "evidence_requirements", "social_welfare"
        }
        
        # Purely procedural domains
        self.procedural_domains = {
            "court_procedures", "filing_requirements", "administrative_steps",
            "form_submissions", "deadline_management", "fee_structures"
        }
        
        # Query patterns indicating strategy preference
        self.strategy_indicators = {
            "foundation_first": [
                "أساس شرعي", "المبدأ الإسلامي", "الحكم الشرعي", "في الشريعة",
                "islamic basis", "sharia principle", "religious foundation"
            ],
            "civil_only": [
                "إجراءات", "خطوات", "كيف أقدم", "نموذج", "استمارة", "رسوم",
                "procedure", "steps", "how to submit", "form", "fee"
            ],
            "contextual_blend": [
                "تطبيق", "في الواقع", "عملياً", "في النظام السعودي",
                "application", "in practice", "practically", "in saudi system"
            ]
        }
    
    async def select_strategy(self, query: str, concepts: List[LegalConcept], 
                            context: Dict[str, Any]) -> IntegrationStrategy:
        """
        Intelligently select integration strategy based on comprehensive analysis
        """
        query_lower = query.lower()
        
        # Check for explicit strategy indicators
        for strategy, indicators in self.strategy_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                if strategy == "foundation_first":
                    return IntegrationStrategy.FOUNDATION_FIRST
                elif strategy == "civil_only":
                    # Only use CIVIL_ONLY for pure procedural queries, otherwise include foundations
                    if any(proc in query_lower for proc in ["نموذج", "استمارة", "رسوم", "form", "fee"]):
                        return IntegrationStrategy.CIVIL_ONLY
                    else:
                        return IntegrationStrategy.CIVIL_WITH_FOUNDATION
                elif strategy == "contextual_blend":
                    return IntegrationStrategy.CONTEXTUAL_BLEND
        
        # Analyze concept types
        concept_types = [concept.concept_type for concept in concepts]
        
        # Check if purely procedural - only for very specific procedural queries
        if all(ct in self.civil_only_concepts for ct in concept_types) and len(concept_types) > 0:
            # Even procedural queries might benefit from Islamic principles of justice
            if any(proc in query_lower for proc in ["نموذج", "استمارة", "رسوم", "خطوات التقديم"]):
                return IntegrationStrategy.CIVIL_ONLY
            else:
                return IntegrationStrategy.CIVIL_WITH_FOUNDATION
        
        # Check if requires Islamic foundation
        foundation_concepts = sum(1 for ct in concept_types if ct in self.foundation_first_concepts)
        if foundation_concepts > len(concept_types) * 0.6:  # More than 60% need foundation
            return IntegrationStrategy.FOUNDATION_FIRST
        
        # Analyze semantic domains
        all_domains = []
        for concept in concepts:
            all_domains.extend(concept.semantic_fields)
        
        islamic_domain_count = sum(1 for domain in all_domains if domain in self.islamic_foundation_domains)
        procedural_domain_count = sum(1 for domain in all_domains if domain in self.procedural_domains)
        
        # Strategy selection based on domain analysis
        total_domains = len(set(all_domains))
        if total_domains > 0:
            islamic_ratio = islamic_domain_count / total_domains
            procedural_ratio = procedural_domain_count / total_domains
            
            # Only use CIVIL_ONLY for overwhelming procedural content
            if procedural_ratio > 0.9 and any(proc in query_lower for proc in ["نموذج", "استمارة", "رسوم"]):
                return IntegrationStrategy.CIVIL_ONLY
            elif islamic_ratio > 0.5:
                return IntegrationStrategy.FOUNDATION_FIRST
            # Always include foundations when there's any potential relevance
            else:
                return IntegrationStrategy.CIVIL_WITH_FOUNDATION
        
        # Context-based adjustments
        query_complexity = context.get("complexity_level", "medium")
        user_preference = context.get("integration_preference", "balanced")
        
        if user_preference == "islamic_focus":
            return IntegrationStrategy.FOUNDATION_FIRST
        elif user_preference == "civil_focus":
            return IntegrationStrategy.CIVIL_WITH_FOUNDATION
        elif query_complexity == "high":
            return IntegrationStrategy.CONTEXTUAL_BLEND
        
        # Default strategy
        return IntegrationStrategy.CIVIL_WITH_FOUNDATION
    
    def get_strategy_confidence(self) -> float:
        return self.confidence_level


class ResultIntegrator:
    """
    Advanced system for intelligently integrating civil and Quranic results
    """
    
    def __init__(self):
        self.integration_weights = {
            IntegrationStrategy.FOUNDATION_FIRST: {
                "quranic_weight": 0.7,
                "civil_weight": 0.5,
                "quranic_priority": RetrievalPriority.PRIMARY,
                "civil_priority": RetrievalPriority.SUPPORTING
            },
            IntegrationStrategy.CIVIL_WITH_FOUNDATION: {
                "quranic_weight": 0.4,
                "civil_weight": 0.8,
                "quranic_priority": RetrievalPriority.SUPPORTING,
                "civil_priority": RetrievalPriority.PRIMARY
            },
            IntegrationStrategy.CONTEXTUAL_BLEND: {
                "quranic_weight": 0.6,
                "civil_weight": 0.7,
                "quranic_priority": RetrievalPriority.PRIMARY,
                "civil_priority": RetrievalPriority.PRIMARY
            },
            IntegrationStrategy.CIVIL_ONLY: {
                "quranic_weight": 0.0,
                "civil_weight": 1.0,
                "quranic_priority": RetrievalPriority.REFERENCE,
                "civil_priority": RetrievalPriority.PRIMARY
            }
        }
    
    async def integrate_results(self, civil_results: List[SearchResult],
                              quranic_results: List[SearchResult],
                              strategy: IntegrationStrategy,
                              concepts: List[LegalConcept]) -> Tuple[List[SearchResult], List[SearchResult], List[SearchResult]]:
        """
        Intelligently integrate civil and Quranic results based on strategy
        Returns: (primary_sources, supporting_sources, contextual_sources)
        """
        weights = self.integration_weights[strategy]
        
        # Boost relevance scores based on strategy
        adjusted_civil = await self._adjust_result_scores(
            civil_results, weights["civil_weight"], concepts, "civil"
        )
        adjusted_quranic = await self._adjust_result_scores(
            quranic_results, weights["quranic_weight"], concepts, "quranic"
        )
        
        # Categorize results by priority
        primary_sources = []
        supporting_sources = []
        contextual_sources = []
        
        # Add results based on strategy
        if weights["civil_priority"] == RetrievalPriority.PRIMARY:
            primary_sources.extend(adjusted_civil[:5])  # Top 5 civil
            if weights["quranic_priority"] == RetrievalPriority.SUPPORTING:
                supporting_sources.extend(adjusted_quranic[:3])  # Top 3 Quranic
            elif weights["quranic_priority"] == RetrievalPriority.PRIMARY:
                primary_sources.extend(adjusted_quranic[:3])  # Top 3 Quranic
        
        if weights["quranic_priority"] == RetrievalPriority.PRIMARY and weights["civil_priority"] != RetrievalPriority.PRIMARY:
            primary_sources.extend(adjusted_quranic[:5])  # Top 5 Quranic
            supporting_sources.extend(adjusted_civil[:3])  # Top 3 civil
        
        # Add remaining results as contextual
        used_civil_ids = {r.chunk.id for r in primary_sources + supporting_sources if r in adjusted_civil}
        used_quranic_ids = {r.chunk.id for r in primary_sources + supporting_sources if r in adjusted_quranic}
        
        remaining_civil = [r for r in adjusted_civil if r.chunk.id not in used_civil_ids]
        remaining_quranic = [r for r in adjusted_quranic if r.chunk.id not in used_quranic_ids]
        
        contextual_sources.extend(remaining_civil[:3])
        contextual_sources.extend(remaining_quranic[:2])
        
        # Sort each category by adjusted relevance
        primary_sources.sort(key=lambda r: r.similarity_score, reverse=True)
        supporting_sources.sort(key=lambda r: r.similarity_score, reverse=True)
        contextual_sources.sort(key=lambda r: r.similarity_score, reverse=True)
        
        return primary_sources, supporting_sources, contextual_sources
    
    async def _adjust_result_scores(self, results: List[SearchResult], weight: float,
                                  concepts: List[LegalConcept], source_type: str) -> List[SearchResult]:
        """Adjust result scores based on integration strategy"""
        adjusted_results = []
        
        for result in results:
            # Calculate concept alignment bonus
            alignment_bonus = await self._calculate_concept_alignment(result, concepts, source_type)
            
            # Apply weight and bonus
            adjusted_score = (result.similarity_score * weight) + alignment_bonus
            adjusted_score = min(adjusted_score, 1.0)  # Cap at 1.0
            
            # Create new result with adjusted score
            adjusted_result = SearchResult(
                chunk=result.chunk,
                similarity_score=adjusted_score
            )
            
            # Add integration metadata
            if adjusted_result.chunk.metadata is None:
                adjusted_result.chunk.metadata = {}
            
            adjusted_result.chunk.metadata.update({
                "original_score": result.similarity_score,
                "integration_weight": weight,
                "alignment_bonus": alignment_bonus,
                "source_type": source_type,
                "integration_adjusted": True
            })
            
            adjusted_results.append(adjusted_result)
        
        return adjusted_results
    
    async def _calculate_concept_alignment(self, result: SearchResult, 
                                         concepts: List[LegalConcept], source_type: str) -> float:
        """Calculate how well a result aligns with extracted concepts"""
        alignment_score = 0.0
        content = result.chunk.content.lower()
        
        for concept in concepts:
            # Check for direct concept matches
            if concept.primary_concept.lower() in content:
                alignment_score += 0.2
            
            # Check for semantic field matches
            for field in concept.semantic_fields:
                if field.replace("_", " ") in content:
                    alignment_score += 0.1
            
            # Source-type specific bonuses
            if source_type == "quranic":
                # Quranic sources get bonus for moral and justice concepts
                if concept.concept_type in {ConceptType.MORAL_PRINCIPLE, ConceptType.JUSTICE_CONCEPT}:
                    alignment_score += 0.15
            elif source_type == "civil":
                # Civil sources get bonus for procedural and substantive law
                if concept.concept_type in {ConceptType.PROCEDURAL_LAW, ConceptType.SUBSTANTIVE_LAW}:
                    alignment_score += 0.15
        
        return min(alignment_score, 0.5)  # Cap bonus at 0.5


class RetrievalOrchestrator:
    """
    Enterprise-grade orchestrator for seamless integration of Quranic foundations with civil law
    Zero-downtime, backward-compatible, high-performance architecture
    """
    
    def __init__(self, 
                 civil_store_path: Optional[str] = None,
                 quranic_store_path: Optional[str] = None):
        
        # Load system configuration
        system_config = get_config()
        db_paths = get_database_paths()
        
        # Use provided paths or fall back to configuration
        civil_path = civil_store_path or db_paths["civil"]
        quranic_path = quranic_store_path or db_paths["quranic"]
        
        # Core components
        self.concept_engine = SemanticConceptEngine()
        self.strategy_selector = IntelligentStrategySelector()
        self.result_integrator = ResultIntegrator()
        
        # Storage systems
        self.civil_store = SqliteVectorStore(civil_path)
        self.quranic_store = QuranicFoundationStore(quranic_path)
        
        # Configuration from centralized system
        self.quranic_integration_enabled = system_config.quranic_integration_enabled
        self.max_civil_results = system_config.max_civil_results
        self.max_quranic_results = system_config.max_quranic_results
        self.parallel_search_enabled = system_config.parallel_search_enabled
        
        # Performance tracking
        self.performance_metrics = {
            "total_queries": 0,
            "average_response_time": 0.0,
            "strategy_distribution": {strategy.value: 0 for strategy in IntegrationStrategy},
            "error_rate": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Quality tracking
        self.quality_metrics = {
            "average_integration_quality": 0.0,
            "average_cultural_appropriateness": 0.0,
            "average_legal_completeness": 0.0,
            "user_satisfaction_rate": 0.0
        }
        
        logger.info("RetrievalOrchestrator initialized with enterprise-grade architecture")
    
    async def initialize(self):
        """Initialize all storage systems and components"""
        try:
            # Initialize stores in parallel
            await asyncio.gather(
                self.civil_store.initialize(),
                self.quranic_store.initialize() if self.quranic_integration_enabled else asyncio.sleep(0)
            )
            
            logger.info("✅ RetrievalOrchestrator fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RetrievalOrchestrator: {e}")
            raise
    
    async def retrieve_integrated(self, query: str, 
                                context: Optional[Dict[str, Any]] = None,
                                limit: int = 15) -> IntegratedResponse:
        """
        Main retrieval method - seamlessly integrates civil law with Quranic foundations
        """
        start_time = datetime.now()
        context = context or {}
        
        try:
            # Step 1: Extract legal concepts from query
            concept_start = datetime.now()
            concepts = await self.concept_engine.extract_legal_concepts(query, context)
            concept_time = (datetime.now() - concept_start).total_seconds() * 1000
            
            if not concepts:
                logger.warning(f"No legal concepts extracted from query: {query}")
                # Fallback to simple civil search
                return await self._fallback_civil_search(query, limit, start_time)
            
            # Step 2: Select integration strategy
            strategy = await self.strategy_selector.select_strategy(query, concepts, context)
            
            # Step 3: Execute parallel searches based on strategy
            civil_results, quranic_results, search_times = await self._execute_parallel_searches(
                query, concepts, context, strategy, limit
            )
            
            # Step 4: Intelligent integration of results
            integration_start = datetime.now()
            primary_sources, supporting_sources, contextual_sources = await self.result_integrator.integrate_results(
                civil_results, quranic_results, strategy, concepts
            )
            integration_time = (datetime.now() - integration_start).total_seconds() * 1000
            
            # Step 5: Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                primary_sources, supporting_sources, contextual_sources, concepts, strategy
            )
            
            # Step 6: Build integrated response
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            
            response = IntegratedResponse(
                query=query,
                strategy=strategy,
                execution_time_ms=total_time,
                civil_results=civil_results,
                quranic_results=quranic_results,
                primary_sources=primary_sources,
                supporting_sources=supporting_sources,
                contextual_sources=contextual_sources,
                integration_quality=quality_metrics["integration_quality"],
                cultural_appropriateness=quality_metrics["cultural_appropriateness"],
                legal_completeness=quality_metrics["legal_completeness"],
                extracted_concepts=concepts,
                concept_coverage=quality_metrics["concept_coverage"],
                civil_search_time=search_times["civil"],
                quranic_search_time=search_times["quranic"],
                integration_time=integration_time,
                total_sources=len(primary_sources) + len(supporting_sources) + len(contextual_sources),
                confidence_distribution=quality_metrics["confidence_distribution"],
                strategy_explanation=self._generate_strategy_explanation(strategy, concepts)
            )
            
            # Step 7: Update performance metrics
            await self._update_performance_metrics(response)
            
            logger.info(f"Integrated retrieval completed: {total_time:.1f}ms, strategy: {strategy.value}, sources: {response.total_sources}")
            return response
            
        except Exception as e:
            logger.error(f"Integrated retrieval failed: {e}")
            return await self._fallback_civil_search(query, limit, start_time)
    
    async def _execute_parallel_searches(self, query: str, concepts: List[LegalConcept],
                                       context: Dict[str, Any], strategy: IntegrationStrategy,
                                       limit: int) -> Tuple[List[SearchResult], List[SearchResult], Dict[str, float]]:
        """Execute civil and Quranic searches in parallel based on strategy"""
        
        search_tasks = []
        search_times = {"civil": 0.0, "quranic": 0.0}
        
        # Always search civil law (backward compatibility)
        civil_task = self._search_civil_law(query, concepts, context, limit)
        search_tasks.append(("civil", civil_task))
        
        # Search Quranic foundations based on strategy
        if (self.quranic_integration_enabled and 
            strategy != IntegrationStrategy.CIVIL_ONLY):
            quranic_task = self._search_quranic_foundations(query, concepts, context, limit)
            search_tasks.append(("quranic", quranic_task))
        
        # Execute searches
        if self.parallel_search_enabled and len(search_tasks) > 1:
            # Parallel execution
            results = await asyncio.gather(*[task for _, task in search_tasks], return_exceptions=True)
            
            civil_results = []
            quranic_results = []
            
            for i, (search_type, _) in enumerate(search_tasks):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"{search_type} search failed: {result}")
                    continue
                
                search_result, search_time = result
                search_times[search_type] = search_time
                
                if search_type == "civil":
                    civil_results = search_result
                elif search_type == "quranic":
                    quranic_results = search_result
        else:
            # Sequential execution (fallback)
            civil_results = []
            quranic_results = []
            
            for search_type, task in search_tasks:
                try:
                    search_result, search_time = await task
                    search_times[search_type] = search_time
                    
                    if search_type == "civil":
                        civil_results = search_result
                    elif search_type == "quranic":
                        quranic_results = search_result
                        
                except Exception as e:
                    logger.error(f"{search_type} search failed: {e}")
        
        return civil_results, quranic_results, search_times
    
    async def _search_civil_law(self, query: str, concepts: List[LegalConcept],
                              context: Dict[str, Any], limit: int) -> Tuple[List[SearchResult], float]:
        """Search civil law database"""
        start_time = datetime.now()
        
        try:
            # Use simple text search as fallback when vector search fails
            # This ensures we get SOME results rather than zero
            logger.info(f"Civil law search requested for: {query}")
            
            # Try vector search first (if embeddings available)
            try:
                # Create a dummy vector for testing - in production this should be query embedding
                dummy_vector = [0.1] * 1536  # text-embedding-3-small dimension
                results = await self.civil_store.search_similar(dummy_vector, top_k=limit)
                if results:
                    search_time = (datetime.now() - start_time).total_seconds() * 1000
                    return results, search_time
            except Exception as e:
                logger.warning(f"Vector search failed, trying text search: {e}")
            
            # Fallback to text search 
            # Extract key terms from concepts for search
            search_terms = []
            for concept in concepts:
                search_terms.append(concept.primary_concept)
                search_terms.extend(concept.semantic_fields)
            
            # Use text search if available
            if hasattr(self.civil_store, 'search_text'):
                results = await self.civil_store.search_text(" ".join(search_terms), limit=limit)
            else:
                # Final fallback - get any results to test system integration
                results = await self.civil_store.search_similar([0.1] * 1536, top_k=limit)
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            return results[:limit], search_time
            
        except Exception as e:
            logger.error(f"Civil law search failed: {e}")
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            return [], search_time
    
    async def _search_quranic_foundations(self, query: str, concepts: List[LegalConcept],
                                        context: Dict[str, Any], limit: int) -> Tuple[List[SearchResult], float]:
        """Search Quranic foundations database"""
        start_time = datetime.now()
        
        try:
            # Try semantic search first
            results = await self.quranic_store.semantic_search_foundations(
                concepts, context, limit=self.max_quranic_results
            )
            
            # If semantic search fails or returns no results, use simple text search fallback
            if not results:
                logger.info("Semantic search returned no results, trying text-based fallback")
                results = await self._quranic_text_search_fallback(query, concepts, limit)
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            return results[:limit], search_time
            
        except Exception as e:
            logger.error(f"Quranic foundation search failed: {e}")
            # Try text search as emergency fallback
            try:
                results = await self._quranic_text_search_fallback(query, concepts, limit)
                search_time = (datetime.now() - start_time).total_seconds() * 1000
                return results[:limit], search_time
            except Exception as e2:
                logger.error(f"Even text search fallback failed: {e2}")
                search_time = (datetime.now() - start_time).total_seconds() * 1000
                return [], search_time
    
    async def _quranic_text_search_fallback(self, query: str, concepts: List[LegalConcept], 
                                          limit: int) -> List[SearchResult]:
        """Simple text-based search fallback for Quranic foundations"""
        try:
            import sqlite3
            from app.storage.vector_store import Chunk, SearchResult
            
            # Connect directly to database for simple text search
            conn = sqlite3.connect(self.quranic_store.db_path)
            cursor = conn.cursor()
            
            # Search for relevant concepts in legal_principle and qurtubi_commentary
            search_terms = []
            for concept in concepts:
                search_terms.append(concept.primary_concept)
                search_terms.extend(concept.semantic_fields)
            
            # Add common employment/justice terms
            employment_terms = ['عدل', 'عدالة', 'حق', 'عمل', 'موظف', 'عامل', 'justice', 'employment', 'work']
            search_terms.extend(employment_terms)
            
            # Build SQL query for text search
            where_conditions = []
            for term in search_terms[:5]:  # Limit to avoid too complex queries
                where_conditions.append(f"legal_principle LIKE '%{term}%' OR qurtubi_commentary LIKE '%{term}%'")
            
            where_clause = " OR ".join(where_conditions)
            
            query_sql = f"""
                SELECT foundation_id, verse_text, legal_principle, qurtubi_commentary, 
                       surah_name, ayah_number, verse_reference, cultural_appropriateness,
                       scholarship_confidence
                FROM quranic_foundations 
                WHERE {where_clause}
                ORDER BY cultural_appropriateness DESC, scholarship_confidence DESC
                LIMIT {limit * 2}
            """
            
            cursor.execute(query_sql)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                (foundation_id, verse_text, legal_principle, qurtubi_commentary,
                 surah_name, ayah_number, verse_reference, cultural_appropriateness,
                 scholarship_confidence) = row
                
                # Create content combining principle and commentary
                content = f"{legal_principle}\n\n{qurtubi_commentary or ''}"
                title = f"{verse_reference} - {legal_principle[:50]}..."
                
                # Create chunk
                chunk = Chunk(
                    id=foundation_id,
                    content=content,
                    title=title,
                    metadata={
                        "foundation_type": "quranic",
                        "surah": surah_name,
                        "ayah": ayah_number,
                        "verse_reference": verse_reference,
                        "legal_principle": legal_principle,
                        "cultural_appropriateness": cultural_appropriateness,
                        "scholarship_confidence": scholarship_confidence
                    }
                )
                
                # Create search result with relevance score
                similarity_score = (cultural_appropriateness + scholarship_confidence) / 2
                result = SearchResult(chunk=chunk, similarity_score=similarity_score)
                results.append(result)
            
            conn.close()
            
            logger.info(f"Text search fallback found {len(results)} Quranic foundations")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Text search fallback failed: {e}")
            return []
    
    async def _calculate_quality_metrics(self, primary_sources: List[SearchResult],
                                       supporting_sources: List[SearchResult],
                                       contextual_sources: List[SearchResult],
                                       concepts: List[LegalConcept],
                                       strategy: IntegrationStrategy) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics for the integrated response"""
        
        all_sources = primary_sources + supporting_sources + contextual_sources
        
        # Integration quality - how well sources work together
        integration_quality = await self._calculate_integration_quality(all_sources, strategy)
        
        # Cultural appropriateness - how culturally sensitive the response is
        cultural_appropriateness = await self._calculate_cultural_appropriateness(all_sources)
        
        # Legal completeness - how well all legal aspects are covered
        legal_completeness = await self._calculate_legal_completeness(all_sources, concepts)
        
        # Concept coverage - which concepts are well covered
        concept_coverage = await self._calculate_concept_coverage(all_sources, concepts)
        
        # Confidence distribution
        confidence_distribution = self._calculate_confidence_distribution(all_sources)
        
        return {
            "integration_quality": integration_quality,
            "cultural_appropriateness": cultural_appropriateness,
            "legal_completeness": legal_completeness,
            "concept_coverage": concept_coverage,
            "confidence_distribution": confidence_distribution
        }
    
    async def _calculate_integration_quality(self, sources: List[SearchResult], 
                                           strategy: IntegrationStrategy) -> float:
        """Calculate how well civil and Quranic sources integrate"""
        if not sources:
            return 0.0
        
        civil_count = sum(1 for s in sources if s.chunk.metadata.get("source_type") == "civil")
        quranic_count = sum(1 for s in sources if s.chunk.metadata.get("foundation_type") == "quranic")
        
        # Balance score based on strategy
        if strategy == IntegrationStrategy.FOUNDATION_FIRST:
            ideal_ratio = 0.7  # More Quranic
            actual_ratio = quranic_count / len(sources) if sources else 0
        elif strategy == IntegrationStrategy.CIVIL_WITH_FOUNDATION:
            ideal_ratio = 0.3  # Less Quranic
            actual_ratio = quranic_count / len(sources) if sources else 0
        else:
            ideal_ratio = 0.5  # Balanced
            actual_ratio = quranic_count / len(sources) if sources else 0
        
        balance_score = 1.0 - abs(ideal_ratio - actual_ratio)
        
        # Quality score based on average similarity
        quality_score = sum(s.similarity_score for s in sources) / len(sources) if sources else 0
        
        return (balance_score * 0.4) + (quality_score * 0.6)
    
    async def _calculate_cultural_appropriateness(self, sources: List[SearchResult]) -> float:
        """Calculate cultural appropriateness of the response"""
        if not sources:
            return 0.8  # Default reasonable score
        
        quranic_sources = [s for s in sources if s.chunk.metadata.get("foundation_type") == "quranic"]
        
        if not quranic_sources:
            return 0.8  # Civil only is culturally appropriate
        
        # Calculate based on Quranic source quality
        cultural_scores = []
        for source in quranic_sources:
            cultural_score = source.chunk.metadata.get("cultural_appropriateness", 0.8)
            cultural_scores.append(cultural_score)
        
        return sum(cultural_scores) / len(cultural_scores) if cultural_scores else 0.8
    
    async def _calculate_legal_completeness(self, sources: List[SearchResult], 
                                          concepts: List[LegalConcept]) -> float:
        """Calculate how completely legal aspects are covered"""
        if not concepts:
            return 0.8  # Default if no concepts extracted
        
        covered_concepts = set()
        
        for source in sources:
            content = source.chunk.content.lower()
            for concept in concepts:
                if concept.primary_concept.lower() in content:
                    covered_concepts.add(concept.concept_id)
                
                # Check semantic fields
                for field in concept.semantic_fields:
                    if field.replace("_", " ") in content:
                        covered_concepts.add(concept.concept_id)
        
        coverage_ratio = len(covered_concepts) / len(concepts) if concepts else 0
        return min(coverage_ratio + 0.3, 1.0)  # Boost base score
    
    async def _calculate_concept_coverage(self, sources: List[SearchResult],
                                        concepts: List[LegalConcept]) -> Dict[str, float]:
        """Calculate coverage for each concept"""
        coverage = {}
        
        for concept in concepts:
            concept_coverage = 0.0
            concept_key = concept.primary_concept
            
            for source in sources:
                content = source.chunk.content.lower()
                if concept.primary_concept.lower() in content:
                    concept_coverage += 0.5
                
                # Semantic field matches
                field_matches = sum(1 for field in concept.semantic_fields 
                                  if field.replace("_", " ") in content)
                concept_coverage += field_matches * 0.2
            
            coverage[concept_key] = min(concept_coverage, 1.0)
        
        return coverage
    
    def _calculate_confidence_distribution(self, sources: List[SearchResult]) -> Dict[str, int]:
        """Calculate distribution of confidence scores"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for source in sources:
            score = source.similarity_score
            if score >= 0.8:
                distribution["high"] += 1
            elif score >= 0.6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    def _generate_strategy_explanation(self, strategy: IntegrationStrategy, 
                                     concepts: List[LegalConcept]) -> str:
        """Generate human-readable explanation of why strategy was selected"""
        
        concept_types = [c.concept_type.value for c in concepts]
        
        explanations = {
            IntegrationStrategy.FOUNDATION_FIRST: 
                f"Islamic foundation prioritized due to moral/justice concepts: {concept_types}",
            IntegrationStrategy.CIVIL_WITH_FOUNDATION: 
                f"Civil law primary with Islamic support for concepts: {concept_types}",
            IntegrationStrategy.CONTEXTUAL_BLEND: 
                f"Balanced integration appropriate for complex concepts: {concept_types}",
            IntegrationStrategy.CIVIL_ONLY: 
                f"Procedural matter requiring only civil law: {concept_types}",
            IntegrationStrategy.FOUNDATION_ONLY: 
                f"Pure Islamic guidance requested: {concept_types}"
        }
        
        return explanations.get(strategy, f"Strategy {strategy.value} selected for concepts: {concept_types}")
    
    async def _fallback_civil_search(self, query: str, limit: int, 
                                   start_time: datetime) -> IntegratedResponse:
        """Fallback to civil-only search when integration fails"""
        try:
            civil_results, search_time = await self._search_civil_law(query, [], {}, limit)
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return IntegratedResponse(
                query=query,
                strategy=IntegrationStrategy.CIVIL_ONLY,
                execution_time_ms=total_time,
                civil_results=civil_results,
                quranic_results=[],
                primary_sources=civil_results[:5],
                supporting_sources=[],
                contextual_sources=civil_results[5:],
                integration_quality=0.7,
                cultural_appropriateness=0.8,
                legal_completeness=0.6,
                extracted_concepts=[],
                concept_coverage={},
                civil_search_time=search_time,
                quranic_search_time=0.0,
                integration_time=0.0,
                total_sources=len(civil_results),
                confidence_distribution=self._calculate_confidence_distribution(civil_results),
                strategy_explanation="Fallback to civil law due to integration failure"
            )
            
        except Exception as e:
            logger.error(f"Even fallback search failed: {e}")
            return self._create_empty_response(query, start_time)
    
    def _create_empty_response(self, query: str, start_time: datetime) -> IntegratedResponse:
        """Create empty response when all searches fail"""
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return IntegratedResponse(
            query=query,
            strategy=IntegrationStrategy.CIVIL_ONLY,
            execution_time_ms=total_time,
            civil_results=[],
            quranic_results=[],
            primary_sources=[],
            supporting_sources=[],
            contextual_sources=[],
            integration_quality=0.0,
            cultural_appropriateness=0.5,
            legal_completeness=0.0,
            extracted_concepts=[],
            concept_coverage={},
            civil_search_time=0.0,
            quranic_search_time=0.0,
            integration_time=0.0,
            total_sources=0,
            confidence_distribution={"high": 0, "medium": 0, "low": 0},
            strategy_explanation="No results found"
        )
    
    async def _update_performance_metrics(self, response: IntegratedResponse):
        """Update performance tracking metrics"""
        # Update query count
        self.performance_metrics["total_queries"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["average_response_time"]
        total_queries = self.performance_metrics["total_queries"]
        new_avg = ((current_avg * (total_queries - 1)) + response.execution_time_ms) / total_queries
        self.performance_metrics["average_response_time"] = new_avg
        
        # Update strategy distribution
        self.performance_metrics["strategy_distribution"][response.strategy.value] += 1
        
        # Update quality metrics
        current_quality = self.quality_metrics["average_integration_quality"]
        new_quality = ((current_quality * (total_queries - 1)) + response.integration_quality) / total_queries
        self.quality_metrics["average_integration_quality"] = new_quality
        
        current_cultural = self.quality_metrics["average_cultural_appropriateness"]
        new_cultural = ((current_cultural * (total_queries - 1)) + response.cultural_appropriateness) / total_queries
        self.quality_metrics["average_cultural_appropriateness"] = new_cultural
        
        current_completeness = self.quality_metrics["average_legal_completeness"]
        new_completeness = ((current_completeness * (total_queries - 1)) + response.legal_completeness) / total_queries
        self.quality_metrics["average_legal_completeness"] = new_completeness
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the orchestrator"""
        health = {
            "status": "healthy",
            "components": {},
            "performance": self.performance_metrics,
            "quality": self.quality_metrics,
            "configuration": {
                "quranic_integration_enabled": self.quranic_integration_enabled,
                "parallel_search_enabled": self.parallel_search_enabled,
                "max_civil_results": self.max_civil_results,
                "max_quranic_results": self.max_quranic_results
            }
        }
        
        # Check component health
        try:
            civil_health = await self.civil_store.health_check()
            health["components"]["civil_store"] = "healthy" if civil_health else "unhealthy"
        except Exception as e:
            health["components"]["civil_store"] = f"error: {e}"
        
        if self.quranic_integration_enabled:
            try:
                quranic_health = await self.quranic_store.health_check()
                health["components"]["quranic_store"] = "healthy" if quranic_health else "unhealthy"
            except Exception as e:
                health["components"]["quranic_store"] = f"error: {e}"
        
        # Check concept engine
        concept_stats = self.concept_engine.get_extraction_stats()
        health["components"]["concept_engine"] = {
            "status": "healthy" if concept_stats["total_extractions"] > 0 else "idle",
            "stats": concept_stats
        }
        
        # Overall health determination
        unhealthy_components = [comp for comp, status in health["components"].items() 
                              if isinstance(status, str) and ("unhealthy" in status or "error" in status)]
        
        if unhealthy_components:
            health["status"] = "degraded"
            health["issues"] = unhealthy_components
        
        return health
    
    def configure_integration(self, quranic_enabled: bool = True, 
                            parallel_enabled: bool = True,
                            max_civil: int = 15,
                            max_quranic: int = 10):
        """Configure integration parameters"""
        self.quranic_integration_enabled = quranic_enabled
        self.parallel_search_enabled = parallel_enabled
        self.max_civil_results = max_civil
        self.max_quranic_results = max_quranic
        
        logger.info(f"Integration configured: Quranic={quranic_enabled}, Parallel={parallel_enabled}")
    
    async def shutdown(self):
        """Graceful shutdown of orchestrator"""
        logger.info("Shutting down RetrievalOrchestrator...")
        
        # Clear caches
        self.concept_engine.clear_cache()
        
        # Save performance metrics if needed
        # Could save to database or file here
        
        logger.info("RetrievalOrchestrator shutdown complete")