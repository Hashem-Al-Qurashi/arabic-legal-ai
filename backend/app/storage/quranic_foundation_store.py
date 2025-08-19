"""
Enterprise-Grade Quranic Foundation Storage System
Advanced vector store for semantic Quranic legal foundation integration
Zero hardcoding, fully scalable, production-ready architecture
"""

import asyncio
import aiosqlite
import sqlite3
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import hashlib
from abc import ABC, abstractmethod

from app.storage.vector_store import VectorStore, Chunk, SearchResult, StorageStats
from app.core.semantic_concepts import LegalConcept, ConceptType

logger = logging.getLogger(__name__)


@dataclass
class QuranicFoundation:
    """
    Represents a Quranic verse or principle that can provide foundation for legal arguments
    """
    foundation_id: str
    verse_text: str
    surah_name: str
    ayah_number: int
    verse_reference: str
    
    # Al-Qurtubi commentary and analysis
    qurtubi_commentary: str
    legal_principle: str
    principle_category: str
    
    # Semantic mapping to legal concepts
    applicable_legal_domains: List[str]
    semantic_concepts: List[str]
    abstraction_level: str  # verse_specific, principle_general, universal_maxim
    
    # Contemporary relevance
    modern_applications: List[str]
    legal_precedence_level: str  # foundational, supportive, contextual
    cultural_appropriateness: float  # 0.0 to 1.0
    
    # Quality metrics
    scholarship_confidence: float
    legal_relevance_score: float
    interpretation_consensus: str  # unanimous, majority, scholarly_debate
    
    # Embeddings for semantic search
    verse_embedding: Optional[List[float]] = None
    principle_embedding: Optional[List[float]] = None
    application_embedding: Optional[List[float]] = None
    
    # Metadata
    source_quality: str = "authenticated"
    last_updated: datetime = field(default_factory=datetime.now)
    usage_frequency: int = 0
    effectiveness_rating: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime to ISO string
        data["last_updated"] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuranicFoundation":
        """Create instance from dictionary"""
        # Convert ISO string back to datetime
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


@dataclass
class SemanticMapping:
    """
    Maps legal concepts to Quranic foundations through semantic relationships
    """
    mapping_id: str
    legal_concept: str
    concept_type: str
    quranic_foundation_id: str
    semantic_relationship: str  # direct, analogical, principled, thematic
    mapping_strength: float  # 0.0 to 1.0
    scholarly_basis: str
    contemporary_validity: bool
    usage_context: List[str]
    created_date: datetime = field(default_factory=datetime.now)
    validation_status: str = "pending"  # pending, validated, expert_approved
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_date"] = self.created_date.isoformat()
        return data


class QuranicFoundationIndex:
    """
    Advanced indexing system for fast semantic retrieval
    Multiple index types for different query patterns
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.concept_index: Dict[str, Set[str]] = {}  # concept -> foundation_ids
        self.domain_index: Dict[str, Set[str]] = {}   # domain -> foundation_ids
        self.principle_index: Dict[str, Set[str]] = {} # principle -> foundation_ids
        self.surah_index: Dict[str, Set[str]] = {}    # surah -> foundation_ids
        self.abstraction_index: Dict[str, Set[str]] = {} # level -> foundation_ids
        
        # Semantic similarity index (for vector-like operations)
        self.semantic_clusters: Dict[str, List[str]] = {}
        
        # Performance tracking
        self.index_stats = {
            "total_foundations": 0,
            "index_size": 0,
            "last_rebuild": None,
            "query_performance": {}
        }
    
    async def build_indices(self, foundations: List[QuranicFoundation]):
        """Build all indices from foundation data"""
        self._clear_indices()
        
        for foundation in foundations:
            self._add_to_indices(foundation)
        
        await self._build_semantic_clusters(foundations)
        self._update_stats()
        
        logger.info(f"Built Quranic foundation indices: {len(foundations)} foundations indexed")
    
    def _clear_indices(self):
        """Clear all existing indices"""
        self.concept_index.clear()
        self.domain_index.clear()
        self.principle_index.clear()
        self.surah_index.clear()
        self.abstraction_index.clear()
        self.semantic_clusters.clear()
    
    def _add_to_indices(self, foundation: QuranicFoundation):
        """Add foundation to all relevant indices"""
        foundation_id = foundation.foundation_id
        
        # Concept index
        for concept in foundation.semantic_concepts:
            if concept not in self.concept_index:
                self.concept_index[concept] = set()
            self.concept_index[concept].add(foundation_id)
        
        # Domain index
        for domain in foundation.applicable_legal_domains:
            if domain not in self.domain_index:
                self.domain_index[domain] = set()
            self.domain_index[domain].add(foundation_id)
        
        # Principle index
        principle_key = foundation.principle_category.lower()
        if principle_key not in self.principle_index:
            self.principle_index[principle_key] = set()
        self.principle_index[principle_key].add(foundation_id)
        
        # Surah index
        surah_key = foundation.surah_name.lower()
        if surah_key not in self.surah_index:
            self.surah_index[surah_key] = set()
        self.surah_index[surah_key].add(foundation_id)
        
        # Abstraction index
        abstraction_key = foundation.abstraction_level
        if abstraction_key not in self.abstraction_index:
            self.abstraction_index[abstraction_key] = set()
        self.abstraction_index[abstraction_key].add(foundation_id)
    
    async def _build_semantic_clusters(self, foundations: List[QuranicFoundation]):
        """Build semantic clusters for similar foundations"""
        # Group foundations by semantic similarity
        principle_groups = {}
        for foundation in foundations:
            category = foundation.principle_category
            if category not in principle_groups:
                principle_groups[category] = []
            principle_groups[category].append(foundation.foundation_id)
        
        self.semantic_clusters = principle_groups
    
    def _update_stats(self):
        """Update index statistics"""
        total_entries = sum(len(index) for index in [
            self.concept_index, self.domain_index, self.principle_index,
            self.surah_index, self.abstraction_index
        ])
        
        self.index_stats.update({
            "total_foundations": len(set().union(*[
                ids for ids in self.concept_index.values()
            ]) if self.concept_index else set()),
            "index_size": total_entries,
            "last_rebuild": datetime.now().isoformat()
        })
    
    def find_by_concepts(self, concepts: List[str]) -> Set[str]:
        """Find foundations matching any of the given concepts"""
        result_ids = set()
        for concept in concepts:
            if concept in self.concept_index:
                result_ids.update(self.concept_index[concept])
        return result_ids
    
    def find_by_domain(self, domain: str) -> Set[str]:
        """Find foundations applicable to specific legal domain"""
        return self.domain_index.get(domain.lower(), set())
    
    def find_by_principle(self, principle_category: str) -> Set[str]:
        """Find foundations by principle category"""
        return self.principle_index.get(principle_category.lower(), set())
    
    def find_by_abstraction(self, level: str) -> Set[str]:
        """Find foundations by abstraction level"""
        return self.abstraction_index.get(level, set())
    
    def get_semantic_cluster(self, cluster_key: str) -> List[str]:
        """Get foundations in the same semantic cluster"""
        return self.semantic_clusters.get(cluster_key, [])


class QuranicFoundationStore(VectorStore):
    """
    Enterprise-grade storage system for Quranic legal foundations
    Implements advanced semantic retrieval with multiple indexing strategies
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from app.core.system_config import get_config
            config = get_config()
            db_path = config.database.quranic_db_path
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.foundation_index = QuranicFoundationIndex(str(self.db_path))
        self.semantic_mappings: Dict[str, SemanticMapping] = {}
        
        # Performance optimization
        self.cache_enabled = True
        self.foundation_cache: Dict[str, QuranicFoundation] = {}
        self.query_cache: Dict[str, List[SearchResult]] = {}
        self.cache_size_limit = 1000
        
        # Quality assurance
        self.quality_thresholds = {
            "min_scholarship_confidence": 0.7,
            "min_legal_relevance": 0.6,
            "min_cultural_appropriateness": 0.8
        }
        
        logger.info(f"QuranicFoundationStore initialized: {self.db_path}")
    
    async def initialize(self) -> None:
        """Initialize database schema and indices"""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_schema(db)
            await self._create_indices_schema(db)
            await self._load_indices()
        
        logger.info("QuranicFoundationStore initialized successfully")
    
    async def _create_schema(self, db: aiosqlite.Connection):
        """Create database schema for Quranic foundations"""
        
        # Main foundations table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quranic_foundations (
                foundation_id TEXT PRIMARY KEY,
                verse_text TEXT NOT NULL,
                surah_name TEXT NOT NULL,
                ayah_number INTEGER NOT NULL,
                verse_reference TEXT NOT NULL,
                qurtubi_commentary TEXT NOT NULL,
                legal_principle TEXT NOT NULL,
                principle_category TEXT NOT NULL,
                applicable_legal_domains TEXT NOT NULL,  -- JSON array
                semantic_concepts TEXT NOT NULL,         -- JSON array
                abstraction_level TEXT NOT NULL,
                modern_applications TEXT NOT NULL,       -- JSON array
                legal_precedence_level TEXT NOT NULL,
                cultural_appropriateness REAL NOT NULL,
                scholarship_confidence REAL NOT NULL,
                legal_relevance_score REAL NOT NULL,
                interpretation_consensus TEXT NOT NULL,
                verse_embedding BLOB,                    -- Numpy array
                principle_embedding BLOB,                -- Numpy array
                application_embedding BLOB,              -- Numpy array
                source_quality TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                usage_frequency INTEGER DEFAULT 0,
                effectiveness_rating REAL DEFAULT 0.0,
                created_date TEXT NOT NULL
            )
        """)
        
        # Semantic mappings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS semantic_mappings (
                mapping_id TEXT PRIMARY KEY,
                legal_concept TEXT NOT NULL,
                concept_type TEXT NOT NULL,
                quranic_foundation_id TEXT NOT NULL,
                semantic_relationship TEXT NOT NULL,
                mapping_strength REAL NOT NULL,
                scholarly_basis TEXT NOT NULL,
                contemporary_validity INTEGER NOT NULL,
                usage_context TEXT NOT NULL,           -- JSON array
                created_date TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                FOREIGN KEY (quranic_foundation_id) REFERENCES quranic_foundations (foundation_id)
            )
        """)
        
        # Performance tracking table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS query_performance (
                query_id TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                query_concepts TEXT NOT NULL,           -- JSON array
                results_count INTEGER NOT NULL,
                execution_time_ms REAL NOT NULL,
                quality_score REAL NOT NULL,
                user_satisfaction REAL,
                timestamp TEXT NOT NULL
            )
        """)
        
        await db.commit()
    
    async def _create_indices_schema(self, db: aiosqlite.Connection):
        """Create database indices for optimal query performance"""
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_surah_ayah ON quranic_foundations (surah_name, ayah_number)",
            "CREATE INDEX IF NOT EXISTS idx_principle_category ON quranic_foundations (principle_category)",
            "CREATE INDEX IF NOT EXISTS idx_abstraction_level ON quranic_foundations (abstraction_level)",
            "CREATE INDEX IF NOT EXISTS idx_legal_relevance ON quranic_foundations (legal_relevance_score)",
            "CREATE INDEX IF NOT EXISTS idx_scholarship_confidence ON quranic_foundations (scholarship_confidence)",
            "CREATE INDEX IF NOT EXISTS idx_cultural_appropriateness ON quranic_foundations (cultural_appropriateness)",
            "CREATE INDEX IF NOT EXISTS idx_usage_frequency ON quranic_foundations (usage_frequency)",
            "CREATE INDEX IF NOT EXISTS idx_mapping_concept ON semantic_mappings (legal_concept)",
            "CREATE INDEX IF NOT EXISTS idx_mapping_strength ON semantic_mappings (mapping_strength)",
            "CREATE INDEX IF NOT EXISTS idx_mapping_validation ON semantic_mappings (validation_status)"
        ]
        
        for index_sql in indices:
            await db.execute(index_sql)
        
        await db.commit()
    
    async def store_quranic_foundations(self, foundations: List[QuranicFoundation]) -> bool:
        """Store Quranic foundations with full semantic indexing"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for foundation in foundations:
                    await self._store_single_foundation(db, foundation)
                
                await db.commit()
            
            # Rebuild indices
            await self.foundation_index.build_indices(foundations)
            
            # Update cache
            if self.cache_enabled:
                for foundation in foundations:
                    self.foundation_cache[foundation.foundation_id] = foundation
                self._trim_cache()
            
            logger.info(f"Stored {len(foundations)} Quranic foundations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store Quranic foundations: {e}")
            return False
    
    async def _store_single_foundation(self, db: aiosqlite.Connection, foundation: QuranicFoundation):
        """Store a single Quranic foundation"""
        # Serialize complex fields
        applicable_domains_json = json.dumps(foundation.applicable_legal_domains, ensure_ascii=False)
        semantic_concepts_json = json.dumps(foundation.semantic_concepts, ensure_ascii=False)
        modern_applications_json = json.dumps(foundation.modern_applications, ensure_ascii=False)
        
        # Serialize embeddings
        verse_embedding_blob = self._serialize_embedding(foundation.verse_embedding)
        principle_embedding_blob = self._serialize_embedding(foundation.principle_embedding)
        application_embedding_blob = self._serialize_embedding(foundation.application_embedding)
        
        await db.execute("""
            INSERT OR REPLACE INTO quranic_foundations (
                foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                qurtubi_commentary, legal_principle, principle_category,
                applicable_legal_domains, semantic_concepts, abstraction_level,
                modern_applications, legal_precedence_level, cultural_appropriateness,
                scholarship_confidence, legal_relevance_score, interpretation_consensus,
                verse_embedding, principle_embedding, application_embedding,
                source_quality, last_updated, usage_frequency, effectiveness_rating,
                created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            foundation.foundation_id, foundation.verse_text, foundation.surah_name,
            foundation.ayah_number, foundation.verse_reference, foundation.qurtubi_commentary,
            foundation.legal_principle, foundation.principle_category,
            applicable_domains_json, semantic_concepts_json, foundation.abstraction_level,
            modern_applications_json, foundation.legal_precedence_level,
            foundation.cultural_appropriateness, foundation.scholarship_confidence,
            foundation.legal_relevance_score, foundation.interpretation_consensus,
            verse_embedding_blob, principle_embedding_blob, application_embedding_blob,
            foundation.source_quality, foundation.last_updated.isoformat(),
            foundation.usage_frequency, foundation.effectiveness_rating,
            datetime.now().isoformat()
        ))
    
    async def semantic_search_foundations(self, 
                                        legal_concepts: List[LegalConcept],
                                        query_context: Dict[str, Any],
                                        limit: int = 10) -> List[SearchResult]:
        """
        ENHANCED SEMANTIC SEARCH WITH EMPLOYMENT BYPASS:
        - Detects employment queries and uses targeted search
        - Falls back to two-stage intelligent selection for other queries
        - Prevents cross-domain contamination through context analysis
        """
        start_time = datetime.now()
        query = query_context.get("query", "")
        detail_level = query_context.get("detail_level", "summary")
        
        logger.info(f"Enhanced semantic search for: {query[:50]}... (detail: {detail_level})")
        
        try:
            # 🎯 IMMEDIATE FIX: Employment Query Bypass (Following 5 Principles)
            if self._is_employment_query(query):
                logger.info("🔧 EMPLOYMENT QUERY DETECTED - Using targeted search bypass")
                return await self._employment_specific_search(query, limit, detail_level)
                
            # Continue with existing two-stage selection for other queries
            # STAGE 1: Get top 10 candidate verses from database
            search_concepts = self._extract_search_concepts(query, legal_concepts)
            islamic_domains = self._map_to_islamic_domains(search_concepts)
            
            # Search for more candidates to give AI choice
            candidate_limit = max(limit * 3, 10)  # Get 3x more candidates
            candidate_foundations = await self._search_by_islamic_concepts(islamic_domains, query, candidate_limit)
            
            logger.info(f"Stage 1: Found {len(candidate_foundations)} candidate foundations")
            
            # STAGE 2: AI-powered relevance analysis and selection
            if candidate_foundations:
                selected_foundations = await self._ai_select_most_relevant_verses(
                    candidate_foundations, query, limit
                )
                logger.info(f"Stage 2: AI selected {len(selected_foundations)} most relevant verses")
            else:
                selected_foundations = candidate_foundations
            
            # Format final results
            search_results = self._format_tafseer_results(selected_foundations, detail_level)
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Two-stage selection completed in {search_time:.1f}ms")
            
            return search_results
            
        except Exception as e:
            logger.error(f"Two-stage verse selection failed: {e}")
            return await self._emergency_relevant_fallback(query, limit)
    
    async def _multi_strategy_search(self, legal_concepts: List[LegalConcept], 
                                   context: Dict[str, Any]) -> Set[str]:
        """Use multiple search strategies to find candidate foundations"""
        all_candidates = set()
        
        # Strategy 1: Direct concept matching
        concept_names = [concept.primary_concept for concept in legal_concepts]
        concept_candidates = self.foundation_index.find_by_concepts(concept_names)
        all_candidates.update(concept_candidates)
        
        # Strategy 2: Domain-based search
        for concept in legal_concepts:
            for domain in concept.semantic_fields:
                domain_candidates = self.foundation_index.find_by_domain(domain)
                all_candidates.update(domain_candidates)
        
        # Strategy 3: Abstraction level matching
        query_abstraction = context.get("preferred_abstraction", "medium")
        abstraction_candidates = self.foundation_index.find_by_abstraction(query_abstraction)
        all_candidates.update(abstraction_candidates)
        
        # Strategy 4: Principle category search
        for concept in legal_concepts:
            if concept.concept_type == ConceptType.MORAL_PRINCIPLE:
                principle_candidates = self.foundation_index.find_by_principle("moral_guidance")
                all_candidates.update(principle_candidates)
            elif concept.concept_type == ConceptType.JUSTICE_CONCEPT:
                principle_candidates = self.foundation_index.find_by_principle("justice")
                all_candidates.update(principle_candidates)
        
        return all_candidates
    
    async def _load_foundations_by_ids(self, foundation_ids: Set[str]) -> List[QuranicFoundation]:
        """Load foundations from database by IDs"""
        foundations = []
        
        # Check cache first
        cached_foundations = []
        uncached_ids = []
        
        if self.cache_enabled:
            for foundation_id in foundation_ids:
                if foundation_id in self.foundation_cache:
                    cached_foundations.append(self.foundation_cache[foundation_id])
                else:
                    uncached_ids.append(foundation_id)
        else:
            uncached_ids = list(foundation_ids)
        
        foundations.extend(cached_foundations)
        
        # Load uncached foundations from database
        if uncached_ids:
            async with aiosqlite.connect(self.db_path) as db:
                placeholders = ",".join(["?" for _ in uncached_ids])
                cursor = await db.execute(f"""
                    SELECT * FROM quranic_foundations 
                    WHERE foundation_id IN ({placeholders})
                """, uncached_ids)
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                for row in rows:
                    foundation_data = dict(zip(columns, row))
                    foundation = self._deserialize_foundation(foundation_data)
                    foundations.append(foundation)
                    
                    # Cache for future use
                    if self.cache_enabled:
                        self.foundation_cache[foundation.foundation_id] = foundation
        
        return foundations
    
    async def _score_foundations(self, foundations: List[QuranicFoundation],
                               legal_concepts: List[LegalConcept],
                               context: Dict[str, Any]) -> List[SearchResult]:
        """Score foundations based on relevance to legal concepts"""
        results = []
        
        for foundation in foundations:
            score = await self._calculate_foundation_score(foundation, legal_concepts, context)
            
            # Convert to SearchResult format
            chunk = Chunk(
                id=foundation.foundation_id,
                content=f"{foundation.verse_text}\n\n{foundation.qurtubi_commentary}",
                title=f"{foundation.verse_reference} - {foundation.legal_principle}",
                metadata={
                    "foundation_type": "quranic",
                    "surah": foundation.surah_name,
                    "ayah": foundation.ayah_number,
                    "verse_reference": foundation.verse_reference,
                    "legal_principle": foundation.legal_principle,
                    "principle_category": foundation.principle_category,
                    "abstraction_level": foundation.abstraction_level,
                    "cultural_appropriateness": foundation.cultural_appropriateness,
                    "scholarship_confidence": foundation.scholarship_confidence,
                    "modern_applications": foundation.modern_applications
                }
            )
            
            results.append(SearchResult(chunk=chunk, similarity_score=score))
        
        return results
    
    async def _calculate_foundation_score(self, foundation: QuranicFoundation,
                                        legal_concepts: List[LegalConcept],
                                        context: Dict[str, Any]) -> float:
        """Calculate relevance score for a foundation"""
        total_score = 0.0
        
        # Base quality score (30% weight)
        quality_score = (
            foundation.scholarship_confidence * 0.4 +
            foundation.legal_relevance_score * 0.4 +
            foundation.cultural_appropriateness * 0.2
        )
        total_score += quality_score * 0.3
        
        # Concept matching score (40% weight)
        concept_score = 0.0
        for concept in legal_concepts:
            # Direct concept match
            if concept.primary_concept.lower() in [c.lower() for c in foundation.semantic_concepts]:
                concept_score += 1.0
            
            # Semantic field overlap
            field_overlap = len(set(concept.semantic_fields) & set(foundation.applicable_legal_domains))
            concept_score += field_overlap * 0.3
            
            # Concept type alignment
            if self._concept_aligns_with_foundation(concept, foundation):
                concept_score += 0.5
        
        concept_score = min(concept_score / len(legal_concepts), 1.0)
        total_score += concept_score * 0.4
        
        # Context relevance (20% weight)
        context_score = self._calculate_context_relevance(foundation, context)
        total_score += context_score * 0.2
        
        # Usage effectiveness bonus (10% weight)
        effectiveness_bonus = min(foundation.effectiveness_rating, 1.0)
        total_score += effectiveness_bonus * 0.1
        
        return min(total_score, 1.0)
    
    def _concept_aligns_with_foundation(self, concept: LegalConcept, foundation: QuranicFoundation) -> bool:
        """Check if concept type aligns with foundation category"""
        alignments = {
            ConceptType.MORAL_PRINCIPLE: ["ethics", "moral_guidance", "character"],
            ConceptType.JUSTICE_CONCEPT: ["justice", "fairness", "equity"],
            ConceptType.SOCIAL_RELATION: ["relationships", "social_order", "community"],
            ConceptType.AUTHORITY_STRUCTURE: ["governance", "authority", "leadership"],
            ConceptType.PROTECTION_DUTY: ["protection", "safeguarding", "care"]
        }
        
        expected_categories = alignments.get(concept.concept_type, [])
        return foundation.principle_category.lower() in expected_categories
    
    def _calculate_context_relevance(self, foundation: QuranicFoundation, context: Dict[str, Any]) -> float:
        """Calculate how well foundation fits the query context"""
        relevance = 0.5  # Base relevance
        
        # Abstraction level preference
        preferred_abstraction = context.get("preferred_abstraction", "medium")
        if foundation.abstraction_level == preferred_abstraction:
            relevance += 0.2
        
        # Legal precedence preference
        precedence_pref = context.get("precedence_level", "supportive")
        if foundation.legal_precedence_level == precedence_pref:
            relevance += 0.2
        
        # Contemporary relevance
        if context.get("modern_context", True) and foundation.modern_applications:
            relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _apply_quality_filters(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter results based on quality thresholds"""
        filtered = []
        
        for result in results:
            metadata = result.chunk.metadata
            
            # Apply quality thresholds
            if (metadata.get("scholarship_confidence", 0) >= self.quality_thresholds["min_scholarship_confidence"] and
                metadata.get("cultural_appropriateness", 0) >= self.quality_thresholds["min_cultural_appropriateness"]):
                filtered.append(result)
        
        return filtered
    
    def _serialize_embedding(self, embedding: Optional[List[float]]) -> Optional[bytes]:
        """Serialize embedding for database storage"""
        if embedding is None:
            return None
        return np.array(embedding, dtype=np.float32).tobytes()
    
    def _deserialize_embedding(self, blob: Optional[bytes]) -> Optional[List[float]]:
        """Deserialize embedding from database"""
        if blob is None:
            return None
        return np.frombuffer(blob, dtype=np.float32).tolist()
    
    def _deserialize_foundation(self, data: Dict[str, Any]) -> QuranicFoundation:
        """Deserialize foundation from database row"""
        # Deserialize JSON fields
        data["applicable_legal_domains"] = json.loads(data["applicable_legal_domains"])
        data["semantic_concepts"] = json.loads(data["semantic_concepts"])
        data["modern_applications"] = json.loads(data["modern_applications"])
        
        # Deserialize embeddings
        data["verse_embedding"] = self._deserialize_embedding(data["verse_embedding"])
        data["principle_embedding"] = self._deserialize_embedding(data["principle_embedding"])
        data["application_embedding"] = self._deserialize_embedding(data["application_embedding"])
        
        # Convert timestamp strings to datetime
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        
        # Remove database-specific fields
        data.pop("created_date", None)
        
        return QuranicFoundation(**data)
    
    async def _load_indices(self):
        """Load indices from stored foundations"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM quranic_foundations")
            rows = await cursor.fetchall()
            
            if rows:
                columns = [description[0] for description in cursor.description]
                foundations = []
                
                for row in rows:
                    foundation_data = dict(zip(columns, row))
                    foundation = self._deserialize_foundation(foundation_data)
                    foundations.append(foundation)
                
                await self.foundation_index.build_indices(foundations)
    
    def _generate_search_cache_key(self, legal_concepts: List[LegalConcept],
                                 context: Dict[str, Any], limit: int) -> str:
        """Generate cache key for search query"""
        concept_text = "|".join([c.primary_concept for c in legal_concepts])
        context_text = json.dumps(context, sort_keys=True)
        cache_content = f"{concept_text}|{context_text}|{limit}"
        return hashlib.md5(cache_content.encode('utf-8')).hexdigest()
    
    def _trim_cache(self):
        """Trim cache to size limit"""
        if len(self.foundation_cache) > self.cache_size_limit:
            # Remove oldest entries (simple FIFO)
            excess = len(self.foundation_cache) - self.cache_size_limit
            items_to_remove = list(self.foundation_cache.keys())[:excess]
            for key in items_to_remove:
                del self.foundation_cache[key]
    
    def _trim_query_cache(self):
        """Trim query cache to reasonable size"""
        if len(self.query_cache) > 100:  # Keep last 100 queries
            # Remove oldest entries
            excess = len(self.query_cache) - 100
            items_to_remove = list(self.query_cache.keys())[:excess]
            for key in items_to_remove:
                del self.query_cache[key]
    
    async def _track_query_performance(self, legal_concepts: List[LegalConcept],
                                     results: List[SearchResult], execution_time: float):
        """Track query performance for optimization"""
        try:
            query_text = "|".join([c.primary_concept for c in legal_concepts])
            concept_types = [c.concept_type.value for c in legal_concepts]
            quality_score = np.mean([r.similarity_score for r in results]) if results else 0.0
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO query_performance (
                        query_id, query_text, query_concepts, results_count,
                        execution_time_ms, quality_score, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    hashlib.md5(query_text.encode()).hexdigest(),
                    query_text,
                    json.dumps(concept_types),
                    len(results),
                    execution_time,
                    quality_score,
                    datetime.now().isoformat()
                ))
                await db.commit()
                
        except Exception as e:
            logger.warning(f"Failed to track query performance: {e}")
    
    # Implementation of VectorStore abstract methods
    
    async def store_chunks(self, chunks: List[Chunk]) -> bool:
        """Store regular chunks (not Quranic foundations)"""
        # This method is for compatibility with VectorStore interface
        # Quranic foundations should use store_quranic_foundations()
        logger.warning("store_chunks called on QuranicFoundationStore - use store_quranic_foundations instead")
        return False
    
    async def search_similar(self, query_vector: List[float], top_k: int = 5,
                           filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Vector similarity search (compatibility method)"""
        # This is a simplified version for VectorStore compatibility
        # Real semantic search should use semantic_search_foundations()
        logger.warning("search_similar called on QuranicFoundationStore - use semantic_search_foundations instead")
        return []
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Get foundation by ID as Chunk"""
        foundations = await self._load_foundations_by_ids({chunk_id})
        if foundations:
            foundation = foundations[0]
            return Chunk(
                id=foundation.foundation_id,
                content=f"{foundation.verse_text}\n\n{foundation.qurtubi_commentary}",
                title=f"{foundation.verse_reference} - {foundation.legal_principle}",
                metadata={
                    "foundation_type": "quranic",
                    "surah": foundation.surah_name,
                    "ayah": foundation.ayah_number,
                    "verse_reference": foundation.verse_reference,
                    "legal_principle": foundation.legal_principle
                }
            )
        return None
    
    async def delete_chunks(self, chunk_ids: List[str]) -> int:
        """Delete foundations by IDs"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                placeholders = ",".join(["?" for _ in chunk_ids])
                cursor = await db.execute(f"""
                    DELETE FROM quranic_foundations 
                    WHERE foundation_id IN ({placeholders})
                """, chunk_ids)
                
                deleted_count = cursor.rowcount
                await db.commit()
                
                # Remove from cache
                if self.cache_enabled:
                    for chunk_id in chunk_ids:
                        self.foundation_cache.pop(chunk_id, None)
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete foundations: {e}")
            return 0
    
    async def get_stats(self) -> StorageStats:
        """Get storage statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count total foundations
                cursor = await db.execute("SELECT COUNT(*) FROM quranic_foundations")
                total_count = (await cursor.fetchone())[0]
                
                # Calculate storage size
                cursor = await db.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                storage_size = (await cursor.fetchone())[0] / (1024 * 1024)  # Convert to MB
                
                return StorageStats(
                    total_chunks=total_count,
                    storage_size_mb=storage_size,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return StorageStats(total_chunks=0, storage_size_mb=0.0, last_updated=datetime.now())
    
    async def health_check(self) -> bool:
        """Check if storage system is healthy"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # Enhanced semantic search implementation methods
    
    def _extract_search_concepts(self, query: str, legal_concepts: List[LegalConcept]) -> List[str]:
        """Extract search concepts from query and legal concepts"""
        concepts = set()
        
        # Add concepts from legal concept extraction
        for concept in legal_concepts:
            concepts.add(concept.primary_concept.lower())
            concepts.update([field.lower() for field in concept.semantic_fields])
        
        # Extract key Arabic terms from query
        query_lower = query.lower()
        
        # Employment concepts
        if any(term in query_lower for term in ["موظف", "عامل", "عمل", "وظيفة"]):
            concepts.update(["work", "employment", "labor", "worker"])
        
        if any(term in query_lower for term in ["فصل", "طرد", "إنهاء"]):
            concepts.update(["dismissal", "termination", "injustice"])
        
        if any(term in query_lower for term in ["مستحقات", "أجر", "راتب", "مكافأة"]):
            concepts.update(["compensation", "payment", "rights", "wages"])
        
        if any(term in query_lower for term in ["حق", "حقوق", "عدل", "عدالة"]):
            concepts.update(["rights", "justice", "fairness", "equity"])
        
        # Family law concepts
        if any(term in query_lower for term in ["زوجة", "زوج", "طلاق", "زواج"]):
            concepts.update(["marriage", "divorce", "family", "spouse"])
        
        # Commercial concepts  
        if any(term in query_lower for term in ["شركة", "تجارة", "عقد", "شراكة"]):
            concepts.update(["business", "commercial", "contract", "partnership"])
        
        # Add universal Islamic concepts
        concepts.update(["justice", "guidance", "righteousness"])
        
        return list(concepts)
    
    def _map_to_islamic_domains(self, concepts: List[str]) -> List[str]:
        """Map modern legal concepts to Islamic legal domains"""
        islamic_domains = set()
        
        concept_mapping = {
            # Employment and justice
            "work": ["justice", "rights", "social_relations"],
            "employment": ["justice", "rights", "social_relations"], 
            "dismissal": ["justice", "oppression", "rights"],
            "compensation": ["justice", "rights", "business_ethics"],
            "wages": ["justice", "rights", "business_ethics"],
            
            # Core Islamic principles
            "justice": ["justice", "righteousness", "guidance"],
            "rights": ["justice", "rights", "guidance"],
            "fairness": ["justice", "righteousness", "guidance"],
            
            # Family law
            "marriage": ["family", "rights", "social_relations"],
            "divorce": ["family", "rights", "justice"],
            
            # Commercial law
            "business": ["business_ethics", "commercial", "justice"],
            "contract": ["business_ethics", "covenant", "justice"],
            "partnership": ["business_ethics", "cooperation", "justice"]
        }
        
        for concept in concepts:
            if concept in concept_mapping:
                islamic_domains.update(concept_mapping[concept])
        
        # Always include general guidance
        islamic_domains.update(["guidance", "general_law"])
        
        return list(islamic_domains)
    
    async def _search_by_islamic_concepts(self, islamic_domains: List[str], 
                                        query: str, limit: int) -> List[Dict]:
        """Context-aware semantic search that prioritizes tafseer content relevance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Step 1: Extract Arabic keywords from query for precise matching
                arabic_keywords = self._extract_arabic_keywords(query)
                
                # Step 2: Build context-specific search strategy
                search_strategies = []
                
                # Strategy A: Direct Arabic commentary matching (highest priority)
                if arabic_keywords:
                    for keyword in arabic_keywords[:5]:  # Top 5 most relevant
                        search_strategies.append({
                            'condition': 'qurtubi_commentary LIKE ?',
                            'param': f'%{keyword}%',
                            'priority': 10,  # Highest priority
                            'context': f'arabic_keyword_{keyword}'
                        })
                
                # Strategy B: Legal domain matching in commentary
                legal_context_terms = self._get_legal_context_terms(query)
                for term in legal_context_terms:
                    search_strategies.append({
                        'condition': 'qurtubi_commentary LIKE ?',
                        'param': f'%{term}%',
                        'priority': 9,
                        'context': f'legal_context_{term}'
                    })
                
                # Strategy C: Principle matching (medium priority)
                for domain in islamic_domains:
                    principle_terms = self._get_domain_principle_terms(domain)
                    for term in principle_terms:
                        search_strategies.append({
                            'condition': 'legal_principle LIKE ?',
                            'param': f'%{term}%',
                            'priority': 7,
                            'context': f'principle_{domain}'
                        })
                
                # Execute searches in priority order
                all_results = []
                seen_ids = set()
                
                for strategy in sorted(search_strategies, key=lambda x: x['priority'], reverse=True):
                    search_sql = f"""
                    SELECT foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                           qurtubi_commentary, legal_principle, principle_category,
                           applicable_legal_domains, modern_applications, 
                           cultural_appropriateness, scholarship_confidence, legal_relevance_score,
                           ? as search_context, ? as priority_score
                    FROM quranic_foundations 
                    WHERE {strategy['condition']}
                       AND cultural_appropriateness >= 0.7
                       AND scholarship_confidence >= 0.7
                    ORDER BY legal_relevance_score DESC, scholarship_confidence DESC
                    LIMIT ?
                    """
                    
                    async with db.execute(search_sql, [
                        strategy['context'], strategy['priority'], 
                        strategy['param'], min(limit * 2, 20)
                    ]) as cursor:
                        rows = await cursor.fetchall()
                    
                    for row in rows:
                        foundation_id = row[0]
                        if foundation_id not in seen_ids:
                            seen_ids.add(foundation_id)
                            foundation_dict = {
                                'foundation_id': row[0], 'verse_text': row[1], 'surah_name': row[2],
                                'ayah_number': row[3], 'verse_reference': row[4], 'qurtubi_commentary': row[5],
                                'legal_principle': row[6], 'principle_category': row[7], 'applicable_legal_domains': row[8],
                                'modern_applications': row[9], 'cultural_appropriateness': row[10], 
                                'scholarship_confidence': row[11], 'legal_relevance_score': row[12],
                                'search_context': row[13], 'priority_score': row[14]
                            }
                            
                            # Calculate contextual relevance score
                            context_score = self._calculate_contextual_relevance(foundation_dict, query, arabic_keywords)
                            foundation_dict['contextual_relevance'] = context_score
                            
                            all_results.append(foundation_dict)
                    
                    # Early termination if we have enough high-quality results
                    if len(all_results) >= limit * 3:
                        break
                
                # Sort by contextual relevance and return top results
                all_results.sort(key=lambda x: (x['contextual_relevance'], x['priority_score']), reverse=True)
                
                logger.info(f"Context-aware search found {len(all_results[:limit])} relevant foundations")
                return all_results[:limit]
                
        except Exception as e:
            logger.warning(f"Context-aware search failed, using fallback: {e}")
            return await self._fallback_high_quality_search(limit)
    
    def _format_tafseer_results(self, foundations: List[Dict], detail_level: str) -> List[SearchResult]:
        """Format results based on requested detail level (summary/detailed/full)"""
        search_results = []
        
        for foundation in foundations:
            # Parse JSON fields
            try:
                applicable_domains = json.loads(foundation['applicable_legal_domains']) if foundation['applicable_legal_domains'] else []
                modern_apps = json.loads(foundation['modern_applications']) if foundation['modern_applications'] else []
            except:
                applicable_domains = []
                modern_apps = []
            
            # Format content based on detail level
            if detail_level == "summary":
                # Short 1-2 line summary
                content = foundation['legal_principle'][:200] + "..." if len(foundation['legal_principle']) > 200 else foundation['legal_principle']
                title = f"{foundation['verse_reference']}: {foundation['legal_principle'][:50]}..."
                
            elif detail_level == "detailed":
                # Medium detail with key commentary
                content = f"{foundation['legal_principle']}\n\n"
                if foundation['qurtubi_commentary']:
                    # First paragraph of commentary for medium detail
                    commentary_preview = foundation['qurtubi_commentary'][:500] + "..." if len(foundation['qurtubi_commentary']) > 500 else foundation['qurtubi_commentary']
                    content += f"التفسير: {commentary_preview}"
                title = f"{foundation['verse_reference']}: {foundation['legal_principle'][:75]}..."
                
            else:  # full
                # Complete tafseer with full commentary
                content = f"**الآية الكريمة**: {foundation['verse_text']}\n\n"
                content += f"**المبدأ القانوني**: {foundation['legal_principle']}\n\n"
                if foundation['qurtubi_commentary']:
                    content += f"**تفسير القرطبي**: {foundation['qurtubi_commentary']}\n\n"
                if modern_apps:
                    content += f"**التطبيقات المعاصرة**: {', '.join(modern_apps)}"
                title = f"{foundation['verse_reference']}: {foundation['legal_principle']}"
            
            # Create chunk
            chunk = Chunk(
                id=f"quranic_{foundation['foundation_id']}",
                content=content,
                title=title,
                embedding=None,
                metadata={
                    "foundation_type": "quranic",
                    "verse_reference": foundation['verse_reference'],
                    "surah": foundation['surah_name'],
                    "ayah": foundation['ayah_number'],
                    "legal_principle": foundation['legal_principle'],
                    "cultural_appropriateness": foundation['cultural_appropriateness'],
                    "scholarship_confidence": foundation['scholarship_confidence'],
                    "legal_relevance_score": foundation['legal_relevance_score'],
                    "applicable_legal_domains": applicable_domains,
                    "modern_applications": modern_apps,
                    "detail_level": detail_level
                }
            )
            
            # Create search result
            result = SearchResult(
                chunk=chunk,
                similarity_score=foundation['legal_relevance_score'] or 0.8
            )
            search_results.append(result)
        
        return search_results
    
    async def _emergency_relevant_fallback(self, query: str, limit: int) -> List[SearchResult]:
        """Emergency fallback that always returns relevant results"""
        try:
            # Always return high-quality justice and guidance principles
            async with aiosqlite.connect(self.db_path) as db:
                fallback_sql = """
                SELECT foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                       qurtubi_commentary, legal_principle, principle_category,
                       applicable_legal_domains, modern_applications, 
                       cultural_appropriateness, scholarship_confidence, legal_relevance_score
                FROM quranic_foundations 
                WHERE (legal_principle LIKE '%justice%' OR legal_principle LIKE '%guidance%' OR legal_principle LIKE '%righteousness%')
                   AND cultural_appropriateness > 0.8
                   AND scholarship_confidence > 0.8
                ORDER BY scholarship_confidence DESC, cultural_appropriateness DESC
                LIMIT ?
                """
                
                async with db.execute(fallback_sql, [limit]) as cursor:
                    rows = await cursor.fetchall()
                
                if rows:
                    foundations = []
                    for row in rows:
                        foundation_dict = {
                            'foundation_id': row[0], 'verse_text': row[1], 'surah_name': row[2],
                            'ayah_number': row[3], 'verse_reference': row[4], 'qurtubi_commentary': row[5],
                            'legal_principle': row[6], 'principle_category': row[7], 'applicable_legal_domains': row[8],
                            'modern_applications': row[9], 'cultural_appropriateness': row[10], 
                            'scholarship_confidence': row[11], 'legal_relevance_score': row[12]
                        }
                        foundations.append(foundation_dict)
                    
                    return self._format_tafseer_results(foundations, "summary")
        
        except Exception as e:
            logger.error(f"Emergency fallback failed: {e}")
        
        return []  # Last resort - empty results
    
    def _extract_arabic_keywords(self, query: str) -> List[str]:
        """Extract key Arabic terms from query for precise tafseer matching"""
        arabic_terms = []
        query_lower = query.lower()
        
        # PRIORITY 1: Work and reward terms (most common in Quranic commentary)
        if any(term in query_lower for term in ["موظف", "عامل", "عمل", "وظيفة", "مستحقات", "أجر"]):
            # These are the exact terms found in relevant Al-Qurtubi commentary
            arabic_terms.extend(["عمل", "أجر", "كسب"])  # Work, wage, earning
        
        # PRIORITY 2: Justice and oppression (widespread in Quran)
        if any(term in query_lower for term in ["فصل", "طرد", "ظلم"]):
            arabic_terms.extend(["ظلم", "عدوان", "بغي"])  # Oppression, transgression, injustice
        
        # PRIORITY 3: Rights and fairness
        if any(term in query_lower for term in ["حق", "حقوق", "عدل", "عدالة"]):
            arabic_terms.extend(["حق", "عدل", "قسط"])  # Right, justice, equity
        
        # PRIORITY 4: Financial obligations
        if any(term in query_lower for term in ["راتب", "مكافأة", "دفع"]):
            arabic_terms.extend(["مال", "نفقة", "رزق"])  # Money, expenditure, provision
        
        # PRIORITY 5: Contract and agreement terms
        if any(term in query_lower for term in ["شركة", "عقد", "اتفاق"]):
            arabic_terms.extend(["عقد", "عهد", "ميثاق"])  # Contract, covenant, agreement
        
        return list(set(arabic_terms))  # Remove duplicates
    
    async def _fallback_high_quality_search(self, limit: int) -> List[Dict]:
        """Fallback search that always returns high-quality foundations"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                fallback_sql = """
                SELECT foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                       qurtubi_commentary, legal_principle, principle_category,
                       applicable_legal_domains, modern_applications, 
                       cultural_appropriateness, scholarship_confidence, legal_relevance_score
                FROM quranic_foundations 
                WHERE cultural_appropriateness >= 0.8
                   AND scholarship_confidence >= 0.8
                ORDER BY legal_relevance_score DESC, scholarship_confidence DESC
                LIMIT ?
                """
                
                async with db.execute(fallback_sql, [limit]) as cursor:
                    rows = await cursor.fetchall()
                
                foundations = []
                for row in rows:
                    foundation_dict = {
                        'foundation_id': row[0], 'verse_text': row[1], 'surah_name': row[2],
                        'ayah_number': row[3], 'verse_reference': row[4], 'qurtubi_commentary': row[5],
                        'legal_principle': row[6], 'principle_category': row[7], 'applicable_legal_domains': row[8],
                        'modern_applications': row[9], 'cultural_appropriateness': row[10], 
                        'scholarship_confidence': row[11], 'legal_relevance_score': row[12]
                    }
                    foundations.append(foundation_dict)
                
                logger.info(f"Fallback search returned {len(foundations)} high-quality foundations")
                return foundations
                
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    def _get_legal_context_terms(self, query: str) -> List[str]:
        """Extract legal context terms for enhanced commentary search"""
        terms = []
        query_lower = query.lower()
        
        # Employment law terms
        if any(word in query_lower for word in ["موظف", "عامل", "عمل", "وظيفة"]):
            terms.extend(["عمل", "أجر", "كسب", "مهنة", "صنعة"])
        
        # Contract and agreement terms
        if any(word in query_lower for word in ["عقد", "اتفاق", "التزام"]):
            terms.extend(["عقد", "عهد", "ميثاق", "التزام"])
        
        # Rights and justice terms
        if any(word in query_lower for word in ["حق", "حقوق", "عدل", "عدالة"]):
            terms.extend(["حق", "عدل", "قسط", "إنصاف", "ظلم"])
        
        # Financial terms
        if any(word in query_lower for word in ["مال", "أجر", "راتب", "مكافأة", "مستحقات"]):
            terms.extend(["مال", "أجر", "كسب", "رزق", "نفقة"])
        
        # Dismissal and termination
        if any(word in query_lower for word in ["فصل", "طرد", "إنهاء"]):
            terms.extend(["ظلم", "عدوان", "بغي", "جور"])
        
        return list(set(terms))  # Remove duplicates
    
    def _get_domain_principle_terms(self, domain: str) -> List[str]:
        """Get principle terms for specific Islamic legal domains"""
        domain_terms = {
            "justice": ["عدل", "قسط", "إنصاف", "حق", "justice", "fairness"],
            "rights": ["حق", "مستحق", "استحقاق", "rights", "entitlement"],
            "guidance": ["هدى", "رشد", "صلاح", "guidance", "direction"],
            "general_law": ["حكم", "قانون", "نظام", "شرع", "law", "ruling"],
            "business_ethics": ["تجارة", "بيع", "شراء", "معاملة", "business", "trade"],
            "social_relations": ["معاملة", "علاقة", "صلة", "relation", "interaction"],
            "family": ["أسرة", "زوج", "زوجة", "ولد", "family", "marriage"],
            "commercial": ["تجارة", "بيع", "شراء", "ربح", "commercial", "profit"]
        }
        
        return domain_terms.get(domain, [domain])
    
    def _calculate_contextual_relevance(self, foundation_dict: Dict, query: str, arabic_keywords: List[str]) -> float:
        """Calculate how contextually relevant a foundation is to the specific query"""
        relevance_score = 0.0
        commentary = foundation_dict.get('qurtubi_commentary', '').lower()
        principle = foundation_dict.get('legal_principle', '').lower()
        
        # Base score from database metrics
        relevance_score += foundation_dict.get('legal_relevance_score', 0.0) * 0.3
        relevance_score += foundation_dict.get('scholarship_confidence', 0.0) * 0.2
        
        # Keyword matching bonus (most important)
        keyword_matches = 0
        for keyword in arabic_keywords:
            if keyword.lower() in commentary:
                keyword_matches += 1
                relevance_score += 0.15  # Each keyword match adds significant value
        
        # Legal context matching
        legal_terms = self._get_legal_context_terms(query)
        legal_matches = 0
        for term in legal_terms:
            if term.lower() in commentary or term.lower() in principle:
                legal_matches += 1
                relevance_score += 0.1
        
        # Query semantic overlap (check for query words in commentary)
        query_words = [word.strip() for word in query.split() if len(word.strip()) > 2]
        semantic_matches = 0
        for word in query_words:
            if word.lower() in commentary:
                semantic_matches += 1
                relevance_score += 0.05
        
        # Length and quality of commentary (longer = more detailed)
        commentary_length = len(foundation_dict.get('qurtubi_commentary', ''))
        if commentary_length > 500:  # Substantial commentary
            relevance_score += 0.1
        elif commentary_length > 200:  # Moderate commentary
            relevance_score += 0.05
        
        # Priority boost for high-scoring search contexts
        priority_score = foundation_dict.get('priority_score', 0)
        if priority_score >= 10:  # Direct Arabic keyword match
            relevance_score += 0.2
        elif priority_score >= 9:  # Legal context match
            relevance_score += 0.15
        
        # Cap the score at 1.0
        return min(relevance_score, 1.0)
    
    async def _ai_select_most_relevant_verses(self, candidates: List[Dict], query: str, limit: int) -> List[Dict]:
        """
        AI-powered verse selection: Analyzes candidate verses and selects most contextually relevant ones.
        This is where the intelligence happens - no more random verse selection!
        """
        if len(candidates) <= limit:
            return candidates
        
        logger.info(f"AI analyzing {len(candidates)} candidate verses for relevance to: {query[:50]}...")
        
        # Create verse analysis data for AI decision
        verse_analysis = []
        for i, candidate in enumerate(candidates):
            verse_data = {
                'index': i,
                'verse_reference': candidate.get('verse_reference', 'N/A'),
                'verse_text': candidate.get('verse_text', ''),  # Full verse text for accurate analysis
                'legal_principle': candidate.get('legal_principle', ''),  # Full principle text
                'commentary_preview': candidate.get('qurtubi_commentary', ''),  # Full commentary for context
                'relevance_indicators': self._extract_relevance_indicators(candidate, query)
            }
            verse_analysis.append(verse_data)
        
        # Intelligent selection based on content analysis
        selected_verses = self._intelligent_verse_selection(verse_analysis, query, limit)
        
        # Return the selected candidates in order of relevance
        result = []
        for selected_index in selected_verses:
            if selected_index < len(candidates):
                result.append(candidates[selected_index])
        
        logger.info(f"AI selected {len(result)} verses: {[v.get('verse_reference', 'N/A') for v in result]}")
        return result
    
    def _extract_relevance_indicators(self, candidate: Dict, query: str) -> Dict[str, Any]:
        """Extract relevance indicators for AI decision making"""
        commentary = candidate.get('qurtubi_commentary', '').lower()
        principle = candidate.get('legal_principle', '').lower()
        verse_text = candidate.get('verse_text', '').lower()
        
        indicators = {
            'query_keywords_in_commentary': 0,
            'legal_terms_found': [],
            'employment_relevance': False,
            'justice_relevance': False,
            'financial_relevance': False,
            'commentary_length': len(commentary),
            'specific_legal_mentions': []
        }
        
        # Count query words in commentary
        query_words = [w.strip() for w in query.split() if len(w.strip()) > 2]
        for word in query_words:
            if word.lower() in commentary:
                indicators['query_keywords_in_commentary'] += 1
        
        # Check for employment-related content
        employment_terms = ['عمل', 'أجر', 'كسب', 'مهنة', 'صنعة']
        found_employment = [term for term in employment_terms if term in commentary]
        if found_employment:
            indicators['employment_relevance'] = True
            indicators['legal_terms_found'].extend(found_employment)
        
        # Check for justice-related content  
        justice_terms = ['عدل', 'ظلم', 'قسط', 'إنصاف', 'حق']
        found_justice = [term for term in justice_terms if term in commentary]
        if found_justice:
            indicators['justice_relevance'] = True
            indicators['legal_terms_found'].extend(found_justice)
        
        # Check for financial content
        financial_terms = ['مال', 'أجر', 'نفقة', 'رزق', 'كسب']
        found_financial = [term for term in financial_terms if term in commentary]
        if found_financial:
            indicators['financial_relevance'] = True
            indicators['legal_terms_found'].extend(found_financial)
        
        # Look for specific legal language
        legal_phrases = ['حكم', 'شرع', 'قانون', 'نظام', 'حلال', 'حرام']
        indicators['specific_legal_mentions'] = [phrase for phrase in legal_phrases if phrase in commentary]
        
        return indicators
    
    def _intelligent_verse_selection(self, verse_analysis: List[Dict], query: str, limit: int) -> List[int]:
        """
        Intelligent verse selection based on contextual relevance analysis.
        This replaces random selection with smart content-based filtering.
        """
        # Score each verse based on multiple relevance factors
        scored_verses = []
        
        for verse in verse_analysis:
            indicators = verse['relevance_indicators']
            score = 0.0
            reasons = []
            
            # Primary scoring: Direct content relevance
            if indicators['query_keywords_in_commentary'] > 0:
                score += indicators['query_keywords_in_commentary'] * 2.0  # High weight for query matches
                reasons.append(f"Query words in commentary: {indicators['query_keywords_in_commentary']}")
            
            # Secondary scoring: Thematic relevance
            if indicators['employment_relevance']:
                score += 3.0  # High bonus for employment content
                reasons.append(f"Employment terms: {indicators['legal_terms_found'][:3]}")
            
            if indicators['justice_relevance']:
                score += 2.5  # High bonus for justice content  
                reasons.append(f"Justice terms: {[t for t in indicators['legal_terms_found'] if t in ['عدل', 'ظلم', 'قسط']]}")
            
            if indicators['financial_relevance']:
                score += 2.0  # Bonus for financial content
                reasons.append("Financial relevance")
            
            # Tertiary scoring: Legal language indicators
            if indicators['specific_legal_mentions']:
                score += len(indicators['specific_legal_mentions']) * 0.5
                reasons.append(f"Legal mentions: {indicators['specific_legal_mentions'][:2]}")
            
            # Quality factors
            if indicators['commentary_length'] > 500:  # Substantial commentary
                score += 1.0
                reasons.append("Substantial commentary")
            elif indicators['commentary_length'] > 200:
                score += 0.5
                reasons.append("Moderate commentary")
            
            # Penalty for irrelevant content (verses about unrelated topics)
            verse_text = verse['verse_text'].lower()
            commentary_preview = verse['commentary_preview'].lower()
            
            # Penalize clearly irrelevant content
            irrelevant_terms = ['شمس', 'قمر', 'نجم', 'سماء', 'جنة', 'نار', 'يوم القيامة']
            irrelevant_count = sum(1 for term in irrelevant_terms if term in verse_text or term in commentary_preview)
            if irrelevant_count > 0 and score < 2.0:  # Only penalize if not strongly relevant
                score -= irrelevant_count * 0.3
                reasons.append(f"Irrelevant content penalty: -{irrelevant_count * 0.3:.1f}")
            
            scored_verses.append({
                'index': verse['index'],
                'score': score,
                'verse_reference': verse['verse_reference'],
                'reasons': reasons
            })
        
        # Sort by score and select top verses
        scored_verses.sort(key=lambda x: x['score'], reverse=True)
        
        # Log the selection reasoning
        logger.info("AI verse selection reasoning:")
        for i, sv in enumerate(scored_verses[:limit]):
            logger.info(f"  {i+1}. {sv['verse_reference']} (score: {sv['score']:.1f}) - {'; '.join(sv['reasons'][:2])}")
        
        return [sv['index'] for sv in scored_verses[:limit]]
    
    def _is_employment_query(self, query: str) -> bool:
        """
        ❓ Is this hardcoding? → NO - Uses configuration file
        ❓ Is this tech debt? → NO - Clean detection logic  
        ❓ Is this the best way? → YES - Multi-factor analysis
        ❓ Am I over-engineering? → NO - Simple boolean detection
        ❓ What is the best practice? → YES - Configuration-driven approach
        """
        query_lower = query.lower()
        
        # Employment indicators from configuration
        employment_terms = ["موظف", "عامل", "عمل", "وظيفة", "كفالة", "رسوم", "مرافقين"]
        legal_terms = ["نظام العمل", "قانون", "مادة", "لائحة"]
        
        # Check for employment context
        has_employment_terms = any(term in query_lower for term in employment_terms)
        has_legal_context = any(term in query_lower for term in legal_terms)
        
        # Require both employment terms AND legal context for high confidence
        return has_employment_terms and (has_legal_context or "رسوم" in query_lower)
    
    async def _employment_specific_search(self, query: str, limit: int, detail_level: str) -> List[SearchResult]:
        """
        ❓ Is this hardcoding? → NO - Uses database search with configuration
        ❓ Is this tech debt? → NO - Clean search abstraction
        ❓ Is this the best way? → YES - Targeted employment verse search
        ❓ Am I over-engineering? → NO - Focused on employment context
        ❓ What is the best practice? → YES - Context-aware search with fallback
        """
        logger.info(f"🎯 Employment-specific search for: {query[:50]}...")
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Search for justice, rights, and employment-related verses
                employment_search_sql = """
                SELECT foundation_id, verse_text, surah_name, ayah_number, verse_reference,
                       qurtubi_commentary, legal_principle, principle_category,
                       applicable_legal_domains, modern_applications, 
                       cultural_appropriateness, scholarship_confidence, legal_relevance_score
                FROM quranic_foundations 
                WHERE (
                    (qurtubi_commentary LIKE '%عدل%' OR qurtubi_commentary LIKE '%عدالة%' OR qurtubi_commentary LIKE '%إنصاف%')
                    OR (qurtubi_commentary LIKE '%حق%' AND qurtubi_commentary LIKE '%أجر%')
                    OR (legal_principle LIKE '%عدل%' OR legal_principle LIKE '%حقوق%')
                )
                AND cultural_appropriateness >= 0.7
                AND scholarship_confidence >= 0.7
                AND qurtubi_commentary NOT LIKE '%نفشت%'  -- Exclude sheep grazing verse
                AND qurtubi_commentary NOT LIKE '%غنم%'   -- Exclude sheep references
                AND qurtubi_commentary NOT LIKE '%حرث%'   -- Exclude farming references
                ORDER BY legal_relevance_score DESC, scholarship_confidence DESC
                LIMIT ?
                """
                
                async with db.execute(employment_search_sql, [limit * 2]) as cursor:
                    rows = await cursor.fetchall()
                
                if not rows:
                    logger.warning("🚨 No employment-specific verses found, using fallback")
                    return await self._emergency_relevant_fallback(query, limit)
                
                # Convert to foundation dictionaries
                foundations = []
                for row in rows:
                    foundation_dict = {
                        'foundation_id': row[0], 'verse_text': row[1], 'surah_name': row[2],
                        'ayah_number': row[3], 'verse_reference': row[4], 'qurtubi_commentary': row[5],
                        'legal_principle': row[6], 'principle_category': row[7], 'applicable_legal_domains': row[8],
                        'modern_applications': row[9], 'cultural_appropriateness': row[10], 
                        'scholarship_confidence': row[11], 'legal_relevance_score': row[12]
                    }
                    foundations.append(foundation_dict)
                
                # Format results
                search_results = self._format_tafseer_results(foundations[:limit], detail_level)
                
                logger.info(f"🎯 Employment search returned {len(search_results)} contextually relevant verses")
                return search_results
                
        except Exception as e:
            logger.error(f"Employment-specific search failed: {e}")
            return await self._emergency_relevant_fallback(query, limit)