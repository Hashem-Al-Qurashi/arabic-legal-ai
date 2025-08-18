"""
Concept Mapping System for Islamic Legal AI
Bridges modern legal concepts with classical Islamic principles
"""

import json
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class ConceptDomain(Enum):
    """Legal domains for concept mapping"""
    EMPLOYMENT = "employment"
    CRIMINAL = "criminal"
    COMMERCIAL = "commercial"
    FAMILY = "family"
    ADMINISTRATIVE = "administrative"
    CIVIL_RIGHTS = "civil_rights"
    JUSTICE = "justice"


@dataclass
class IslamicConcept:
    """Represents an Islamic legal concept"""
    arabic_term: str
    english_term: str
    quranic_references: List[str]
    relevance_weight: float
    domain: ConceptDomain
    explanation: str


@dataclass
class ConceptMapping:
    """Maps modern legal concept to Islamic principles"""
    modern_concept: str
    islamic_concepts: List[IslamicConcept]
    mapping_confidence: float
    context_indicators: List[str]


class IslamicConceptHierarchy:
    """
    Hierarchical mapping system for Islamic legal concepts
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/islamic_concept_hierarchy.json"
        self.concept_mappings: Dict[str, ConceptMapping] = {}
        self.domain_mappings: Dict[ConceptDomain, List[IslamicConcept]] = {}
        self._load_concept_hierarchy()
    
    def _load_concept_hierarchy(self):
        """Load concept hierarchy from configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._parse_concept_config(config)
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self._create_default_mappings()
        
        except Exception as e:
            logger.error(f"Failed to load concept hierarchy: {e}")
            self._create_default_mappings()
    
    def _parse_concept_config(self, config: Dict):
        """Parse concept configuration from JSON"""
        for modern_term, mapping_data in config.get("concept_mappings", {}).items():
            islamic_concepts = []
            
            for ic_data in mapping_data.get("islamic_concepts", []):
                islamic_concept = IslamicConcept(
                    arabic_term=ic_data.get("arabic_term", ""),
                    english_term=ic_data.get("english_term", ""),
                    quranic_references=ic_data.get("quranic_references", []),
                    relevance_weight=ic_data.get("relevance_weight", 0.5),
                    domain=ConceptDomain(ic_data.get("domain", "justice")),
                    explanation=ic_data.get("explanation", "")
                )
                islamic_concepts.append(islamic_concept)
            
            concept_mapping = ConceptMapping(
                modern_concept=modern_term,
                islamic_concepts=islamic_concepts,
                mapping_confidence=mapping_data.get("mapping_confidence", 0.7),
                context_indicators=mapping_data.get("context_indicators", [])
            )
            
            self.concept_mappings[modern_term] = concept_mapping
    
    def _create_default_mappings(self):
        """Create default concept mappings for key legal areas"""
        
        # Employment Rights Mappings
        employment_rights_concepts = [
            IslamicConcept(
                arabic_term="العدالة",
                english_term="justice",
                quranic_references=["4:58", "16:90", "5:8"],
                relevance_weight=0.9,
                domain=ConceptDomain.EMPLOYMENT,
                explanation="Fair treatment and justice in employer-employee relations"
            ),
            IslamicConcept(
                arabic_term="الوفاء بالعهد",
                english_term="covenant_keeping",
                quranic_references=["17:34", "23:8", "5:1"],
                relevance_weight=0.85,
                domain=ConceptDomain.EMPLOYMENT,
                explanation="Honoring employment contracts and agreements"
            ),
            IslamicConcept(
                arabic_term="كرامة الإنسان",
                english_term="human_dignity",
                quranic_references=["17:70", "2:30"],
                relevance_weight=0.8,
                domain=ConceptDomain.EMPLOYMENT,
                explanation="Respecting human dignity in workplace"
            )
        ]
        
        self.concept_mappings["employment_dismissal"] = ConceptMapping(
            modern_concept="employment_dismissal",
            islamic_concepts=employment_rights_concepts,
            mapping_confidence=0.85,
            context_indicators=["فصل", "طرد", "إنهاء خدمة", "dismissal", "termination"]
        )
        
        self.concept_mappings["unpaid_wages"] = ConceptMapping(
            modern_concept="unpaid_wages",
            islamic_concepts=[
                IslamicConcept(
                    arabic_term="أداء الحق",
                    english_term="fulfilling_rights",
                    quranic_references=["2:282", "4:29"],
                    relevance_weight=0.9,
                    domain=ConceptDomain.EMPLOYMENT,
                    explanation="Obligation to pay workers their due wages"
                ),
                IslamicConcept(
                    arabic_term="أكل أموال الناس بالباطل",
                    english_term="unlawful_consumption",
                    quranic_references=["2:188", "4:29"],
                    relevance_weight=0.85,
                    domain=ConceptDomain.EMPLOYMENT,
                    explanation="Prohibition of withholding rightful wages"
                )
            ],
            mapping_confidence=0.9,
            context_indicators=["مستحقات", "راتب", "أجر", "wages", "salary", "compensation"]
        )
        
        # Criminal Justice Mappings
        criminal_justice_concepts = [
            IslamicConcept(
                arabic_term="القصاص",
                english_term="retribution",
                quranic_references=["2:178", "5:45"],
                relevance_weight=0.9,
                domain=ConceptDomain.CRIMINAL,
                explanation="Just retribution in criminal matters"
            ),
            IslamicConcept(
                arabic_term="الشورى",
                english_term="consultation",
                quranic_references=["42:38", "3:159"],
                relevance_weight=0.7,
                domain=ConceptDomain.CRIMINAL,
                explanation="Consultation and due process in justice"
            )
        ]
        
        self.concept_mappings["criminal_justice"] = ConceptMapping(
            modern_concept="criminal_justice",
            islamic_concepts=criminal_justice_concepts,
            mapping_confidence=0.8,
            context_indicators=["جريمة", "عقوبة", "جزاء", "crime", "punishment", "penalty"]
        )
        
        # Commercial Law Mappings
        commercial_concepts = [
            IslamicConcept(
                arabic_term="تحريم الربا",
                english_term="prohibition_of_usury",
                quranic_references=["2:275", "3:130"],
                relevance_weight=0.9,
                domain=ConceptDomain.COMMERCIAL,
                explanation="Islamic prohibition of interest and usury"
            ),
            IslamicConcept(
                arabic_term="التجارة بالتراضي",
                english_term="mutual_consent_trade",
                quranic_references=["4:29", "2:282"],
                relevance_weight=0.85,
                domain=ConceptDomain.COMMERCIAL,
                explanation="Trade and commerce based on mutual consent"
            )
        ]
        
        self.concept_mappings["commercial_contracts"] = ConceptMapping(
            modern_concept="commercial_contracts",
            islamic_concepts=commercial_concepts,
            mapping_confidence=0.8,
            context_indicators=["تجارة", "بيع", "شراء", "عقد", "trade", "commerce", "contract"]
        )
    
    def map_concepts_to_islamic_principles(self, extracted_concepts: List[str], 
                                        query_context: str) -> List[ConceptMapping]:
        """
        Map extracted modern legal concepts to Islamic principles
        """
        relevant_mappings = []
        query_lower = query_context.lower()
        
        for concept in extracted_concepts:
            concept_lower = concept.lower()
            
            # Direct mapping lookup
            if concept_lower in self.concept_mappings:
                mapping = self.concept_mappings[concept_lower]
                relevant_mappings.append(mapping)
                continue
            
            # Fuzzy matching based on context indicators
            for mapping_key, mapping in self.concept_mappings.items():
                for indicator in mapping.context_indicators:
                    if indicator.lower() in query_lower or indicator.lower() in concept_lower:
                        relevant_mappings.append(mapping)
                        break
        
        return self._deduplicate_and_rank(relevant_mappings)
    
    def get_quranic_search_terms(self, mappings: List[ConceptMapping]) -> List[Tuple[str, float]]:
        """
        Extract Quranic search terms with relevance weights
        """
        search_terms = []
        
        for mapping in mappings:
            for islamic_concept in mapping.islamic_concepts:
                weight = islamic_concept.relevance_weight * mapping.mapping_confidence
                search_terms.append((islamic_concept.arabic_term, weight))
                search_terms.append((islamic_concept.english_term, weight * 0.8))  # Lower weight for English
        
        # Sort by relevance weight
        search_terms.sort(key=lambda x: x[1], reverse=True)
        return search_terms
    
    def _deduplicate_and_rank(self, mappings: List[ConceptMapping]) -> List[ConceptMapping]:
        """Remove duplicates and rank by confidence"""
        seen = set()
        unique_mappings = []
        
        for mapping in mappings:
            if mapping.modern_concept not in seen:
                seen.add(mapping.modern_concept)
                unique_mappings.append(mapping)
        
        # Sort by mapping confidence
        unique_mappings.sort(key=lambda x: x.mapping_confidence, reverse=True)
        return unique_mappings
    
    def explain_relevance(self, mapping: ConceptMapping) -> str:
        """Generate explanation for why this mapping is relevant"""
        explanations = []
        
        for islamic_concept in mapping.islamic_concepts:
            explanations.append(
                f"- {islamic_concept.arabic_term} ({islamic_concept.english_term}): "
                f"{islamic_concept.explanation}"
            )
        
        return f"Islamic legal foundations for '{mapping.modern_concept}':\n" + "\n".join(explanations)


class ConceptMappingEngine:
    """
    Main engine for concept mapping integration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.hierarchy = IslamicConceptHierarchy(config_path)
        self.mapping_cache: Dict[str, List[ConceptMapping]] = {}
    
    async def enhance_query_with_islamic_concepts(self, extracted_concepts: List[str], 
                                                query: str) -> Dict[str, any]:
        """
        Enhance a legal query with relevant Islamic concepts
        """
        cache_key = f"{str(sorted(extracted_concepts))}_{hash(query)}"
        
        if cache_key in self.mapping_cache:
            mappings = self.mapping_cache[cache_key]
        else:
            mappings = self.hierarchy.map_concepts_to_islamic_principles(extracted_concepts, query)
            self.mapping_cache[cache_key] = mappings
        
        if not mappings:
            return {
                "enhanced_concepts": [],
                "quranic_search_terms": [],
                "relevance_explanations": [],
                "confidence": 0.0
            }
        
        quranic_terms = self.hierarchy.get_quranic_search_terms(mappings)
        explanations = [self.hierarchy.explain_relevance(m) for m in mappings]
        
        overall_confidence = sum(m.mapping_confidence for m in mappings) / len(mappings)
        
        return {
            "enhanced_concepts": [m.modern_concept for m in mappings],
            "quranic_search_terms": quranic_terms,
            "relevance_explanations": explanations,
            "confidence": overall_confidence,
            "mappings": mappings
        }
    
    def get_mapping_statistics(self) -> Dict[str, any]:
        """Get statistics about concept mappings"""
        return {
            "total_mappings": len(self.hierarchy.concept_mappings),
            "domains_covered": list(set(
                ic.domain.value 
                for mapping in self.hierarchy.concept_mappings.values()
                for ic in mapping.islamic_concepts
            )),
            "cache_size": len(self.mapping_cache)
        }


# Factory function for easy integration
def create_concept_mapping_engine(config_path: Optional[str] = None) -> ConceptMappingEngine:
    """
    Factory function to create configured concept mapping engine
    """
    return ConceptMappingEngine(config_path)