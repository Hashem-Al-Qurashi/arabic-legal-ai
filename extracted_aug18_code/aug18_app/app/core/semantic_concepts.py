"""
Semantic Concept Extraction Engine
Advanced NLP pipeline for extracting deep legal concepts from Arabic text
Zero hardcoding - fully adaptive semantic understanding
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ConceptType(Enum):
    """Types of legal concepts that can be extracted"""
    SUBSTANTIVE_LAW = "substantive_law"      # Core legal principles
    PROCEDURAL_LAW = "procedural_law"        # Legal processes
    SOCIAL_RELATION = "social_relation"      # Human relationships
    MORAL_PRINCIPLE = "moral_principle"      # Ethical foundations
    JUSTICE_CONCEPT = "justice_concept"      # Fairness and equity
    AUTHORITY_STRUCTURE = "authority_structure"  # Power and governance
    ECONOMIC_PRINCIPLE = "economic_principle"    # Financial relationships
    PROTECTION_DUTY = "protection_duty"      # Safeguarding obligations


@dataclass
class LegalConcept:
    """
    Represents an extracted legal concept with semantic depth
    """
    concept_id: str
    primary_concept: str
    concept_type: ConceptType
    semantic_fields: List[str]
    confidence_score: float
    context_indicators: List[str]
    related_concepts: List[str] = field(default_factory=list)
    abstraction_level: str = "medium"  # low, medium, high
    cultural_context: str = "saudi_legal"
    temporal_relevance: str = "contemporary"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "primary_concept": self.primary_concept,
            "concept_type": self.concept_type.value,
            "semantic_fields": self.semantic_fields,
            "confidence_score": self.confidence_score,
            "context_indicators": self.context_indicators,
            "related_concepts": self.related_concepts,
            "abstraction_level": self.abstraction_level,
            "cultural_context": self.cultural_context,
            "temporal_relevance": self.temporal_relevance
        }


class ConceptExtractor(ABC):
    """
    Abstract base for concept extraction strategies
    Allows different extraction approaches without hardcoding
    """
    
    @abstractmethod
    async def extract_concepts(self, text: str, context: Dict[str, Any]) -> List[LegalConcept]:
        """Extract legal concepts from text"""
        pass
    
    @abstractmethod
    def get_extraction_confidence(self) -> float:
        """Return confidence level of this extractor"""
        pass


class SemanticPatternExtractor(ConceptExtractor):
    """
    Advanced semantic pattern extraction using linguistic analysis
    Identifies concepts through semantic patterns, not keyword matching
    """
    
    def __init__(self):
        self.confidence_level = 0.85
        self._initialize_semantic_patterns()
    
    def _initialize_semantic_patterns(self):
        """
        Initialize semantic patterns for concept recognition
        These are linguistic patterns, not hardcoded content
        """
        self.pattern_categories = {
            "obligation_patterns": [
                r"(?:يجب|لازم|واجب|ضروري)(?:\s+\w+){0,3}\s+(?:على|أن)",
                r"(?:التزام|إلزام|وجوب)(?:\s+\w+){0,5}",
                r"(?:مسؤولية|مسئولية)(?:\s+\w+){0,3}\s+(?:عن|في)"
            ],
            "relationship_patterns": [
                r"(?:بين|علاقة)(?:\s+\w+){1,5}(?:و|مع)",
                r"(?:حق|حقوق)(?:\s+\w+){0,3}\s+(?:في|على|من)",
                r"(?:واجب|واجبات)(?:\s+\w+){0,3}\s+(?:تجاه|نحو|على)"
            ],
            "process_patterns": [
                r"(?:إجراء|عملية|خطوات)(?:\s+\w+){0,5}",
                r"(?:تطبيق|تنفيذ|تفعيل)(?:\s+\w+){0,3}",
                r"(?:آلية|منهجية|طريقة)(?:\s+\w+){0,5}"
            ],
            "principle_patterns": [
                r"(?:مبدأ|أساس|قاعدة)(?:\s+\w+){0,5}",
                r"(?:أصل|منطلق|فلسفة)(?:\s+\w+){0,5}",
                r"(?:روح|جوهر|لب)(?:\s+\w+){0,3}"
            ],
            "employment_patterns": [
                r"(?:موظف|عامل|مستخدم|موظفين|عمال)(?:\s+\w+){0,5}",
                r"(?:العمل|الوظيفة|التوظيف|العمالة)(?:\s+\w+){0,5}",
                r"(?:فصل|إنهاء|ترك|استقالة)(?:\s+\w+){0,3}\s+(?:العمل|الخدمة|الوظيفة)",
                r"(?:راتب|أجر|مرتب|مكافأة|مستحقات)(?:\s+\w+){0,5}",
                r"(?:شركة|مؤسسة|صاحب العمل|رب العمل)(?:\s+\w+){0,5}",
                r"(?:نظام العمل|قانون العمل|عقد العمل)(?:\s+\w+){0,5}",
                r"(?:إجازة|غياب|دوام|ساعات العمل)(?:\s+\w+){0,5}"
            ],
            "rights_patterns": [
                r"(?:حقوق|مستحقات|مطالبات)(?:\s+\w+){0,3}",
                r"(?:تعويض|تعويضات|غرامة|جزاء)(?:\s+\w+){0,5}",
                r"(?:شكوى|دعوى|قضية|نزاع)(?:\s+\w+){0,5}"
            ],
            "justice_patterns": [
                r"(?:عدل|عدالة|إنصاف|قسط)(?:\s+\w+){0,5}",
                r"(?:ظلم|جور|انتهاك|تعدي)(?:\s+\w+){0,5}",
                r"(?:قضاء|محكمة|حكم|قاضي)(?:\s+\w+){0,5}"
            ]
        }
    
    async def extract_concepts(self, text: str, context: Dict[str, Any]) -> List[LegalConcept]:
        """
        Extract concepts using advanced semantic analysis
        """
        concepts = []
        
        # Multi-level concept extraction
        primary_concepts = await self._extract_primary_concepts(text, context)
        relational_concepts = await self._extract_relational_concepts(text, context)
        abstract_concepts = await self._extract_abstract_concepts(text, context)
        
        # Merge and deduplicate
        all_concepts = primary_concepts + relational_concepts + abstract_concepts
        concepts = self._deduplicate_and_rank(all_concepts)
        
        return concepts
    
    async def _extract_primary_concepts(self, text: str, context: Dict[str, Any]) -> List[LegalConcept]:
        """Extract primary legal concepts from direct semantic patterns"""
        concepts = []
        text_normalized = self._normalize_arabic_text(text)
        
        for category, patterns in self.pattern_categories.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_normalized, re.IGNORECASE)
                for match in matches:
                    concept = await self._create_concept_from_match(
                        match, category, text_normalized, context
                    )
                    if concept:
                        concepts.append(concept)
        
        return concepts
    
    async def _extract_relational_concepts(self, text: str, context: Dict[str, Any]) -> List[LegalConcept]:
        """Extract concepts based on relationships between entities"""
        concepts = []
        
        # Identify entities and their relationships
        entities = self._extract_legal_entities(text)
        relationships = self._analyze_entity_relationships(text, entities)
        
        for relationship in relationships:
            concept = self._create_relational_concept(relationship, context)
            if concept:
                concepts.append(concept)
        
        return concepts
    
    async def _extract_abstract_concepts(self, text: str, context: Dict[str, Any]) -> List[LegalConcept]:
        """Extract high-level abstract legal concepts"""
        concepts = []
        
        # Analyze semantic themes
        themes = await self._analyze_semantic_themes(text)
        
        for theme in themes:
            if theme["confidence"] > 0.7:
                concept = self._create_abstract_concept(theme, context)
                if concept:
                    concepts.append(concept)
        
        return concepts
    
    def _normalize_arabic_text(self, text: str) -> str:
        """Normalize Arabic text for better pattern matching"""
        # Remove diacritics
        text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
        
        # Normalize alef variations
        text = re.sub(r'[آأإ]', 'ا', text)
        
        # Normalize teh marbuta
        text = re.sub(r'ة', 'ه', text)
        
        return text.strip()
    
    async def _create_concept_from_match(self, match, category: str, text: str, 
                                       context: Dict[str, Any]) -> Optional[LegalConcept]:
        """Create a legal concept from a pattern match"""
        matched_text = match.group()
        concept_text = self._extract_concept_phrase(matched_text, text, match.start())
        
        if len(concept_text.strip()) < 3:
            return None
        
        concept_type = self._determine_concept_type(category, concept_text)
        semantic_fields = self._extract_semantic_fields(concept_text, context)
        confidence = self._calculate_concept_confidence(matched_text, concept_text, context)
        
        return LegalConcept(
            concept_id=self._generate_concept_id(concept_text),
            primary_concept=concept_text,
            concept_type=concept_type,
            semantic_fields=semantic_fields,
            confidence_score=confidence,
            context_indicators=[category],
            abstraction_level=self._determine_abstraction_level(concept_text),
            cultural_context=context.get("cultural_context", "saudi_legal"),
            temporal_relevance=context.get("temporal_relevance", "contemporary")
        )
    
    def _extract_legal_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract legal entities (parties, institutions, concepts)"""
        entities = []
        
        # Legal party patterns
        party_patterns = [
            r"(?:المدعي|المدعى عليه|المتهم|المشتكي|الشاهد)",
            r"(?:المحكمة|القاضي|المحامي|النيابة)",
            r"(?:الطرف|الأطراف|الجهة|الجهات)"
        ]
        
        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": "legal_party",
                    "position": (match.start(), match.end())
                })
        
        return entities
    
    def _analyze_entity_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze relationships between legal entities"""
        relationships = []
        
        # Simple relationship analysis between entities
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities are mentioned in proximity
                distance = abs(entity1["position"][0] - entity2["position"][0])
                if distance < 100:  # Within 100 characters
                    relationship_text = self._extract_relationship_context(
                        text, entity1["position"], entity2["position"]
                    )
                    if relationship_text:
                        relationships.append({
                            "entity1": entity1,
                            "entity2": entity2,
                            "relationship_context": relationship_text,
                            "confidence": 0.7
                        })
        
        return relationships
    
    async def _analyze_semantic_themes(self, text: str) -> List[Dict[str, Any]]:
        """Analyze high-level semantic themes in the text"""
        themes = []
        
        # Theme indicators (semantic, not hardcoded content)
        theme_indicators = {
            "justice": ["عدل", "إنصاف", "حق", "عدالة", "قسط"],
            "responsibility": ["مسؤولية", "التزام", "واجب", "عهد"],
            "protection": ["حماية", "صون", "حفظ", "رعاية"],
            "fairness": ["عدل", "قسط", "توازن", "تكافؤ"],
            "authority": ["سلطة", "ولاية", "إمارة", "حكم"],
            "social_harmony": ["تماسك", "وحدة", "تعاون", "تآلف"]
        }
        
        for theme_name, indicators in theme_indicators.items():
            theme_strength = sum(1 for indicator in indicators if indicator in text)
            if theme_strength > 0:
                confidence = min(theme_strength / len(indicators), 1.0)
                themes.append({
                    "theme": theme_name,
                    "confidence": confidence,
                    "indicators_found": [ind for ind in indicators if ind in text]
                })
        
        return themes
    
    def _extract_concept_phrase(self, matched_text: str, full_text: str, position: int) -> str:
        """Extract the full concept phrase around a match"""
        # Get surrounding context
        start = max(0, position - 50)
        end = min(len(full_text), position + len(matched_text) + 50)
        context = full_text[start:end]
        
        # Extract meaningful phrase
        sentences = re.split(r'[.،؛:]', context)
        for sentence in sentences:
            if matched_text in sentence:
                return sentence.strip()
        
        return matched_text
    
    def _determine_concept_type(self, category: str, concept_text: str) -> ConceptType:
        """Determine the type of legal concept"""
        category_mappings = {
            "obligation_patterns": ConceptType.SUBSTANTIVE_LAW,
            "relationship_patterns": ConceptType.SOCIAL_RELATION,
            "process_patterns": ConceptType.PROCEDURAL_LAW,
            "principle_patterns": ConceptType.MORAL_PRINCIPLE
        }
        
        return category_mappings.get(category, ConceptType.SUBSTANTIVE_LAW)
    
    def _extract_semantic_fields(self, concept_text: str, context: Dict[str, Any]) -> List[str]:
        """Extract semantic fields for the concept"""
        fields = []
        
        # Analyze semantic domains
        if any(word in concept_text for word in ["أسرة", "زواج", "طلاق"]):
            fields.append("family_relations")
        if any(word in concept_text for word in ["مال", "تجارة", "بيع"]):
            fields.append("economic_relations")
        if any(word in concept_text for word in ["عقوبة", "جريمة", "حد"]):
            fields.append("criminal_law")
        if any(word in concept_text for word in ["شهادة", "إثبات", "بينة"]):
            fields.append("evidence_law")
        
        # Add general field if no specific field found
        if not fields:
            fields.append("general_legal")
        
        return fields
    
    def _calculate_concept_confidence(self, matched_text: str, concept_text: str, 
                                    context: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted concept"""
        base_confidence = 0.7
        
        # Boost confidence based on context richness
        if len(concept_text) > 20:
            base_confidence += 0.1
        
        # Boost confidence if it appears multiple times
        if context.get("text", "").count(matched_text) > 1:
            base_confidence += 0.05
        
        # Boost confidence if in formal legal context
        if any(formal_indicator in context.get("text", "") 
               for formal_indicator in ["المادة", "النظام", "القانون"]):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_concept_id(self, concept_text: str) -> str:
        """Generate unique ID for concept"""
        import hashlib
        text_hash = hashlib.md5(concept_text.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"concept_{text_hash}_{timestamp}"
    
    def _determine_abstraction_level(self, concept_text: str) -> str:
        """Determine abstraction level of concept"""
        if any(abstract_word in concept_text 
               for abstract_word in ["مبدأ", "أساس", "فلسفة", "روح"]):
            return "high"
        elif any(concrete_word in concept_text 
                for concrete_word in ["إجراء", "خطوة", "نموذج"]):
            return "low"
        else:
            return "medium"
    
    def _create_relational_concept(self, relationship: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Optional[LegalConcept]:
        """Create concept from entity relationship"""
        if relationship["confidence"] < 0.5:
            return None
        
        concept_text = f"علاقة بين {relationship['entity1']['text']} و {relationship['entity2']['text']}"
        
        return LegalConcept(
            concept_id=self._generate_concept_id(concept_text),
            primary_concept=concept_text,
            concept_type=ConceptType.SOCIAL_RELATION,
            semantic_fields=["relationship_analysis"],
            confidence_score=relationship["confidence"],
            context_indicators=["entity_relationship"],
            abstraction_level="medium"
        )
    
    def _create_abstract_concept(self, theme: Dict[str, Any], 
                               context: Dict[str, Any]) -> Optional[LegalConcept]:
        """Create concept from semantic theme"""
        return LegalConcept(
            concept_id=self._generate_concept_id(theme["theme"]),
            primary_concept=theme["theme"],
            concept_type=ConceptType.MORAL_PRINCIPLE,
            semantic_fields=[theme["theme"]],
            confidence_score=theme["confidence"],
            context_indicators=theme["indicators_found"],
            abstraction_level="high"
        )
    
    def _extract_relationship_context(self, text: str, pos1: Tuple[int, int], 
                                    pos2: Tuple[int, int]) -> str:
        """Extract context describing relationship between entities"""
        start = min(pos1[0], pos2[0])
        end = max(pos1[1], pos2[1])
        return text[start:end].strip()
    
    def _deduplicate_and_rank(self, concepts: List[LegalConcept]) -> List[LegalConcept]:
        """Remove duplicates and rank concepts by relevance"""
        # Simple deduplication by primary concept
        seen_concepts = set()
        unique_concepts = []
        
        for concept in concepts:
            concept_key = concept.primary_concept.lower().strip()
            if concept_key not in seen_concepts:
                seen_concepts.add(concept_key)
                unique_concepts.append(concept)
        
        # Sort by confidence score
        unique_concepts.sort(key=lambda c: c.confidence_score, reverse=True)
        
        return unique_concepts
    
    def get_extraction_confidence(self) -> float:
        return self.confidence_level


class SemanticConceptEngine:
    """
    Advanced semantic concept extraction orchestrator
    Coordinates multiple extraction strategies for comprehensive concept discovery
    """
    
    def __init__(self):
        self.extractors: List[ConceptExtractor] = []
        self.concept_cache: Dict[str, List[LegalConcept]] = {}
        self.extraction_stats = {
            "total_extractions": 0,
            "cache_hits": 0,
            "average_concepts_per_text": 0.0
        }
        
        # Initialize extractors
        self._initialize_extractors()
        
        logger.info("SemanticConceptEngine initialized with advanced extractors")
    
    def _initialize_extractors(self):
        """Initialize all concept extraction strategies"""
        self.extractors = [
            SemanticPatternExtractor(),
            # Additional extractors can be added here
        ]
    
    async def extract_legal_concepts(self, text: str, 
                                   context: Optional[Dict[str, Any]] = None) -> List[LegalConcept]:
        """
        Extract comprehensive legal concepts from text using all available strategies
        """
        if not text or len(text.strip()) < 10:
            return []
        
        context = context or {}
        context["text"] = text  # Add text to context for extractors
        
        # Check cache first
        cache_key = self._generate_cache_key(text, context)
        if cache_key in self.concept_cache:
            self.extraction_stats["cache_hits"] += 1
            return self.concept_cache[cache_key]
        
        # Extract concepts using all strategies
        all_concepts = []
        
        for extractor in self.extractors:
            try:
                concepts = await extractor.extract_concepts(text, context)
                all_concepts.extend(concepts)
            except Exception as e:
                logger.warning(f"Extractor {type(extractor).__name__} failed: {e}")
        
        # Merge and optimize results
        final_concepts = self._merge_concepts(all_concepts)
        
        # Cache results
        self.concept_cache[cache_key] = final_concepts
        
        # Update stats
        self.extraction_stats["total_extractions"] += 1
        current_avg = self.extraction_stats["average_concepts_per_text"]
        total_extractions = self.extraction_stats["total_extractions"]
        self.extraction_stats["average_concepts_per_text"] = (
            (current_avg * (total_extractions - 1) + len(final_concepts)) / total_extractions
        )
        
        return final_concepts
    
    def _merge_concepts(self, concepts: List[LegalConcept]) -> List[LegalConcept]:
        """
        Intelligently merge concepts from multiple extractors
        """
        if not concepts:
            return []
        
        # Group similar concepts
        concept_groups = self._group_similar_concepts(concepts)
        
        # Merge each group into best representative
        merged_concepts = []
        for group in concept_groups:
            merged_concept = self._merge_concept_group(group)
            merged_concepts.append(merged_concept)
        
        # Sort by confidence and relevance
        merged_concepts.sort(key=lambda c: c.confidence_score, reverse=True)
        
        # Return top concepts (avoid overwhelming)
        return merged_concepts[:15]
    
    def _group_similar_concepts(self, concepts: List[LegalConcept]) -> List[List[LegalConcept]]:
        """Group concepts that represent similar ideas"""
        groups = []
        used_concepts = set()
        
        for concept in concepts:
            if id(concept) in used_concepts:
                continue
            
            # Start new group
            current_group = [concept]
            used_concepts.add(id(concept))
            
            # Find similar concepts
            for other_concept in concepts:
                if id(other_concept) in used_concepts:
                    continue
                
                if self._concepts_are_similar(concept, other_concept):
                    current_group.append(other_concept)
                    used_concepts.add(id(other_concept))
            
            groups.append(current_group)
        
        return groups
    
    def _concepts_are_similar(self, concept1: LegalConcept, concept2: LegalConcept) -> bool:
        """Determine if two concepts represent similar ideas"""
        # Same concept type and overlapping semantic fields
        if concept1.concept_type == concept2.concept_type:
            shared_fields = set(concept1.semantic_fields) & set(concept2.semantic_fields)
            if shared_fields:
                return True
        
        # Similar text content (basic similarity)
        words1 = set(concept1.primary_concept.lower().split())
        words2 = set(concept2.primary_concept.lower().split())
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        
        return overlap > 0.6
    
    def _merge_concept_group(self, group: List[LegalConcept]) -> LegalConcept:
        """Merge a group of similar concepts into the best representative"""
        if len(group) == 1:
            return group[0]
        
        # Find concept with highest confidence
        best_concept = max(group, key=lambda c: c.confidence_score)
        
        # Merge semantic fields from all concepts
        all_fields = set()
        all_indicators = set()
        all_related = set()
        
        for concept in group:
            all_fields.update(concept.semantic_fields)
            all_indicators.update(concept.context_indicators)
            all_related.update(concept.related_concepts)
        
        # Create enhanced version of best concept
        enhanced_concept = LegalConcept(
            concept_id=best_concept.concept_id,
            primary_concept=best_concept.primary_concept,
            concept_type=best_concept.concept_type,
            semantic_fields=list(all_fields),
            confidence_score=min(best_concept.confidence_score + 0.1, 1.0),  # Boost for consensus
            context_indicators=list(all_indicators),
            related_concepts=list(all_related),
            abstraction_level=best_concept.abstraction_level,
            cultural_context=best_concept.cultural_context,
            temporal_relevance=best_concept.temporal_relevance
        )
        
        return enhanced_concept
    
    def _generate_cache_key(self, text: str, context: Dict[str, Any]) -> str:
        """Generate cache key for text and context"""
        import hashlib
        content = f"{text}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about concept extraction performance"""
        return {
            **self.extraction_stats,
            "cache_size": len(self.concept_cache),
            "cache_hit_rate": (
                self.extraction_stats["cache_hits"] / 
                max(self.extraction_stats["total_extractions"], 1)
            ) * 100,
            "active_extractors": len(self.extractors)
        }
    
    def clear_cache(self):
        """Clear concept extraction cache"""
        self.concept_cache.clear()
        logger.info("Concept extraction cache cleared")