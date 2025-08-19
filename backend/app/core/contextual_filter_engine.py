"""
Contextual Filter Engine
Smart context classification to prevent cross-domain verse contamination
Zero-hardcoding, configuration-driven approach with multi-factor analysis

Author: Expert AI Engineer
Date: 2025-08-19
Purpose: Fix employment vs religious context disambiguation

Principles Applied:
- No hardcoding (all config-driven)
- No tech debt (clean abstractions)
- Best way (multi-factor analysis)
- Not over-engineering (focused scope)
- Best practices (type hints, logging, error handling)
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# Logging setup
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Enumeration of possible context types"""
    EMPLOYMENT = "employment"
    RELIGIOUS = "religious"  
    FAMILY = "family"
    COMMERCIAL = "commercial"
    GENERAL = "general"
    AMBIGUOUS = "ambiguous"

class ConfidenceLevel(Enum):
    """Enumeration of confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REJECTED = "rejected"

@dataclass
class ClassificationResult:
    """Result of context classification with confidence metrics"""
    primary_context: ContextType
    confidence_score: float
    confidence_level: ConfidenceLevel
    secondary_contexts: List[ContextType]
    indicators_found: Dict[str, List[str]]
    exclusions_found: List[str]
    disambiguation_applied: List[str]
    raw_scores: Dict[str, float]
    decision_factors: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/serialization"""
        return {
            "primary_context": self.primary_context.value,
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level.value,
            "secondary_contexts": [ctx.value for ctx in self.secondary_contexts],
            "indicators_found": self.indicators_found,
            "exclusions_found": self.exclusions_found,
            "disambiguation_applied": self.disambiguation_applied,
            "raw_scores": self.raw_scores,
            "decision_factors": self.decision_factors
        }

class IContextClassifier(ABC):
    """Interface for context classification engines"""
    
    @abstractmethod
    def classify_query_context(self, query: str) -> ClassificationResult:
        """Classify the context of a given query"""
        pass
    
    @abstractmethod
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics for monitoring"""
        pass

class ContextualFilterEngine(IContextClassifier):
    """
    Production-grade context filter preventing cross-domain contamination
    
    Core Features:
    - Multi-factor analysis for accurate disambiguation  
    - Configuration-driven rules (no hardcoding)
    - Confidence scoring with weighted factors
    - Comprehensive logging and monitoring
    - Graceful error handling and fallbacks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the context filter engine
        
        Args:
            config_path: Path to context classification rules YAML file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '../../config/context_classification_rules.yaml'
        )
        
        # Statistics for monitoring
        self._classification_stats = {
            "total_classifications": 0,
            "context_counts": {ctx.value: 0 for ctx in ContextType},
            "confidence_distribution": {level.value: 0 for level in ConfidenceLevel},
            "disambiguation_events": 0,
            "low_confidence_cases": 0,
            "errors": 0
        }
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"🔧 ContextualFilterEngine initialized with config: {self.config_path}")
    
    def _load_configuration(self):
        """Load classification rules from YAML configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            # Extract key configuration sections
            self.context_domains = self.config.get('context_domains', {})
            self.classification_rules = self.config.get('classification_rules', {})
            self.disambiguation_strategies = self.config.get('disambiguation_strategies', {})
            self.confidence_scoring = self.config.get('confidence_scoring', {})
            self.fallback_behavior = self.config.get('fallback_behavior', {})
            self.quality_checks = self.config.get('quality_checks', {})
            
            logger.info(f"✅ Configuration loaded successfully")
            logger.debug(f"📊 Loaded {len(self.context_domains)} context domains")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration from {self.config_path}: {e}")
            # Use minimal fallback configuration
            self._use_fallback_configuration()
    
    def _use_fallback_configuration(self):
        """Use minimal hardcoded configuration as last resort"""
        logger.warning("🚨 Using fallback configuration - limited functionality")
        
        self.context_domains = {
            "employment": {"confidence_threshold": 0.7},
            "religious": {"confidence_threshold": 0.8}
        }
        self.classification_rules = {}
        self.disambiguation_strategies = {}
        self.confidence_scoring = {"weights": {"primary_indicators": 0.5}}
        self.fallback_behavior = {"default_context": "general"}
        self.quality_checks = {}
    
    def classify_query_context(self, query: str) -> ClassificationResult:
        """
        Classify the context of a query using multi-factor analysis
        
        Args:
            query: The input query to classify
            
        Returns:
            ClassificationResult with confidence metrics and decision factors
        """
        self._classification_stats["total_classifications"] += 1
        
        try:
            logger.debug(f"🔍 Classifying query: '{query[:50]}...'")
            
            # Step 1: Extract indicators for each context type
            context_indicators = self._extract_context_indicators(query)
            
            # Step 2: Apply disambiguation strategies
            disambiguation_results = self._apply_disambiguation_strategies(query, context_indicators)
            
            # Step 3: Calculate confidence scores
            context_scores = self._calculate_confidence_scores(context_indicators, disambiguation_results)
            
            # Step 4: Determine primary context
            primary_context, confidence_score = self._determine_primary_context(context_scores)
            
            # Step 5: Create classification result
            result = self._create_classification_result(
                primary_context, confidence_score, context_indicators, 
                disambiguation_results, context_scores, query
            )
            
            # Step 6: Update statistics
            self._update_classification_stats(result)
            
            # Step 7: Log decision
            self._log_classification_decision(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Classification error for query '{query[:30]}...': {e}")
            self._classification_stats["errors"] += 1
            
            # Return safe fallback result
            return self._create_fallback_result(query)
    
    def _extract_context_indicators(self, query: str) -> Dict[str, Dict[str, List[str]]]:
        """Extract indicators for each context type from the query"""
        query_lower = query.lower()
        context_indicators = {}
        
        for context_name, context_rules in self.classification_rules.items():
            indicators = {}
            
            # Check each indicator type dynamically
            for indicator_type, indicator_lists in context_rules.items():
                if isinstance(indicator_lists, dict):
                    found_terms = []
                    # Handle both Arabic and English indicators
                    for lang, terms in indicator_lists.items():
                        if isinstance(terms, list):
                            found_terms.extend([term for term in terms if term.lower() in query_lower])
                    indicators[indicator_type] = found_terms
                else:
                    indicators[indicator_type] = []
            
            context_indicators[context_name] = indicators
        
        return context_indicators
    
    def _apply_disambiguation_strategies(self, query: str, context_indicators: Dict) -> Dict[str, Dict]:
        """Apply disambiguation strategies for ambiguous terms"""
        disambiguation_results = {}
        
        for strategy_name, strategy_config in self.disambiguation_strategies.items():
            try:
                strategy_result = self._apply_single_disambiguation_strategy(
                    query, context_indicators, strategy_name, strategy_config
                )
                disambiguation_results[strategy_name] = strategy_result
                
                if strategy_result.get("disambiguation_applied", False):
                    self._classification_stats["disambiguation_events"] += 1
                    logger.debug(f"🔧 Applied disambiguation: {strategy_name}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Disambiguation strategy '{strategy_name}' failed: {e}")
                disambiguation_results[strategy_name] = {"error": str(e)}
        
        return disambiguation_results
    
    def _apply_single_disambiguation_strategy(self, query: str, context_indicators: Dict, 
                                           strategy_name: str, strategy_config: Dict) -> Dict:
        """Apply a single disambiguation strategy"""
        
        if strategy_name == "work_term_disambiguation":
            return self._disambiguate_work_term(query, context_indicators, strategy_config)
        elif strategy_name == "reward_term_disambiguation":
            return self._disambiguate_reward_term(query, context_indicators, strategy_config)
        else:
            return {"applied": False, "reason": f"Unknown strategy: {strategy_name}"}
    
    def _disambiguate_work_term(self, query: str, context_indicators: Dict, config: Dict) -> Dict:
        """Disambiguate 'عمل' between employment and religious contexts"""
        query_lower = query.lower()
        
        # Check for employment context indicators
        employment_indicators = config.get("employment_context_indicators", {}).get("indicators", [])
        employment_score = 0
        employment_evidence = []
        
        for indicator_group in employment_indicators:
            for check_type, terms in indicator_group.items():
                if check_type == "presence":
                    found = [term for term in terms if term in query_lower]
                    if found:
                        employment_score += 1
                        employment_evidence.extend(found)
                elif check_type == "absence":
                    found = [term for term in terms if term in query_lower]
                    if found:
                        employment_score -= 1  # Penalty for religious terms
        
        # Check for religious context indicators  
        religious_indicators = config.get("religious_context_indicators", {}).get("indicators", [])
        religious_score = 0
        religious_evidence = []
        
        for indicator_group in religious_indicators:
            for check_type, terms in indicator_group.items():
                if check_type == "presence":
                    found = [term for term in terms if term in query_lower]
                    if found:
                        religious_score += 1
                        religious_evidence.extend(found)
                elif check_type == "absence":
                    found = [term for term in terms if term in query_lower]
                    if found:
                        religious_score -= 1  # Penalty for employment terms
        
        # Determine disambiguation result
        required_min = config.get("employment_context_indicators", {}).get("required_minimum", 2)
        
        if employment_score >= required_min:
            return {
                "disambiguation_applied": True,
                "preferred_context": "employment",
                "confidence": employment_score / (required_min + 1),
                "evidence": employment_evidence,
                "alternative_rejected": "religious"
            }
        elif religious_score >= required_min:
            return {
                "disambiguation_applied": True,
                "preferred_context": "religious",
                "confidence": religious_score / (required_min + 1),
                "evidence": religious_evidence,
                "alternative_rejected": "employment"
            }
        else:
            return {
                "disambiguation_applied": False,
                "reason": "Insufficient evidence for either context",
                "employment_score": employment_score,
                "religious_score": religious_score
            }
    
    def _disambiguate_reward_term(self, query: str, context_indicators: Dict, config: Dict) -> Dict:
        """Disambiguate 'أجر' between salary and divine reward contexts"""
        query_lower = query.lower()
        
        # Check for salary context
        salary_indicators = config.get("salary_context_indicators", {}).get("indicators", [])
        salary_score = self._score_context_indicators(query_lower, salary_indicators)
        
        # Check for divine reward context
        divine_indicators = config.get("divine_reward_indicators", {}).get("indicators", [])
        divine_score = self._score_context_indicators(query_lower, divine_indicators)
        
        if salary_score > divine_score and salary_score > 0:
            return {
                "disambiguation_applied": True,
                "preferred_context": "employment",
                "confidence": salary_score / (salary_score + divine_score + 1),
                "reason": "Salary context detected"
            }
        elif divine_score > salary_score and divine_score > 0:
            return {
                "disambiguation_applied": True,
                "preferred_context": "religious", 
                "confidence": divine_score / (salary_score + divine_score + 1),
                "reason": "Divine reward context detected"
            }
        else:
            return {
                "disambiguation_applied": False,
                "reason": "Unable to disambiguate reward term",
                "salary_score": salary_score,
                "divine_score": divine_score
            }
    
    def _score_context_indicators(self, query_lower: str, indicators: List[Dict]) -> float:
        """Score context indicators based on presence/absence rules"""
        score = 0
        
        for indicator_group in indicators:
            for check_type, terms in indicator_group.items():
                if check_type == "presence":
                    found = [term for term in terms if term in query_lower]
                    score += len(found)
                elif check_type == "absence":
                    found = [term for term in terms if term in query_lower]
                    score -= len(found)  # Penalty for unwanted terms
        
        return max(0, score)  # Don't go below 0
    
    def _calculate_confidence_scores(self, context_indicators: Dict, 
                                   disambiguation_results: Dict) -> Dict[str, float]:
        """Calculate confidence scores for each context using weighted factors"""
        context_scores = {}
        weights = self.confidence_scoring.get("weights", {})
        
        for context_name, indicators in context_indicators.items():
            score = 0.0  # Ensure float
            
            # Primary indicators weight
            primary_weight = weights.get("primary_indicators", 0.4)
            score += len(indicators.get("primary_indicators", [])) * primary_weight
            
            # Reinforcers weight (handle different types)
            reinforcer_weight = weights.get("legal_reinforcers", 0.3)
            reinforcer_count = 0
            # Check for different reinforcer types
            for key in indicators.keys():
                if "reinforcer" in key:  # legal_reinforcers, religious_reinforcers, family_reinforcers
                    reinforcer_count += len(indicators.get(key, []))
            score += reinforcer_count * reinforcer_weight
            
            # Domain terms weight
            domain_weight = weights.get("domain_terms", 0.2)
            score += len(indicators.get("domain_terms", [])) * domain_weight
            
            # Exclusion penalty
            exclusion_penalty = weights.get("exclusion_penalty", -0.3)
            score += len(indicators.get("exclusion_terms", [])) * exclusion_penalty
            
            # Apply disambiguation boost
            for disambiguation_name, result in disambiguation_results.items():
                if (result.get("disambiguation_applied", False) and 
                    result.get("preferred_context") == context_name.replace("_context", "")):
                    score += float(result.get("confidence", 0)) * 0.2  # Disambiguation boost
            
            # Normalize score to 0-1 range
            normalized_score = float(max(0, min(1, score)))
            context_scores[context_name] = normalized_score
        
        return context_scores
    
    def _determine_primary_context(self, context_scores: Dict[str, float]) -> Tuple[ContextType, float]:
        """Determine the primary context based on confidence scores"""
        if not context_scores:
            return ContextType.GENERAL, 0.0
        
        # Find highest scoring context
        max_context_name = max(context_scores.keys(), key=lambda k: context_scores[k])
        max_score = context_scores[max_context_name]
        
        # Check if score meets minimum threshold
        thresholds = self.confidence_scoring.get("thresholds", {})
        rejection_threshold = thresholds.get("rejection_threshold", 0.3)
        
        if max_score < rejection_threshold:
            return ContextType.GENERAL, max_score
        
        # Map context name to ContextType
        context_mapping = {
            "employment_context": ContextType.EMPLOYMENT,
            "religious_context": ContextType.RELIGIOUS,
            "family_context": ContextType.FAMILY,
            "commercial_context": ContextType.COMMERCIAL
        }
        
        primary_context = context_mapping.get(max_context_name, ContextType.GENERAL)
        return primary_context, max_score
    
    def _create_classification_result(self, primary_context: ContextType, confidence_score: float,
                                    context_indicators: Dict, disambiguation_results: Dict,
                                    context_scores: Dict, query: str) -> ClassificationResult:
        """Create a comprehensive classification result"""
        
        # Determine confidence level
        thresholds = self.confidence_scoring.get("thresholds", {})
        if confidence_score >= thresholds.get("high_confidence", 0.8):
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= thresholds.get("medium_confidence", 0.6):
            confidence_level = ConfidenceLevel.MEDIUM
        elif confidence_score >= thresholds.get("low_confidence", 0.4):
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.REJECTED
        
        # Find secondary contexts
        sorted_scores = sorted(context_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_contexts = []
        for context_name, score in sorted_scores[1:3]:  # Top 2 secondary
            if score > 0.3:  # Only include meaningful alternatives
                context_mapping = {
                    "employment_context": ContextType.EMPLOYMENT,
                    "religious_context": ContextType.RELIGIOUS,
                    "family_context": ContextType.FAMILY,
                    "commercial_context": ContextType.COMMERCIAL
                }
                secondary_context = context_mapping.get(context_name, ContextType.GENERAL)
                secondary_contexts.append(secondary_context)
        
        # Collect indicators found
        indicators_found = {}
        for context_name, indicators in context_indicators.items():
            for indicator_type, terms in indicators.items():
                if terms:  # Only include non-empty lists
                    indicators_found[f"{context_name}_{indicator_type}"] = terms
        
        # Collect exclusions found
        exclusions_found = []
        for indicators in context_indicators.values():
            exclusions_found.extend(indicators.get("exclusion_terms", []))
        exclusions_found = list(set(exclusions_found))  # Remove duplicates
        
        # Collect disambiguation events
        disambiguation_applied = []
        for disambiguation_name, result in disambiguation_results.items():
            if result.get("disambiguation_applied", False):
                disambiguation_applied.append(disambiguation_name)
        
        # Create decision factors list
        decision_factors = []
        if confidence_score >= 0.8:
            decision_factors.append("High confidence classification")
        if disambiguation_applied:
            decision_factors.append(f"Disambiguation applied: {', '.join(disambiguation_applied)}")
        if exclusions_found:
            decision_factors.append(f"Exclusion terms detected: {', '.join(exclusions_found[:3])}")
        
        return ClassificationResult(
            primary_context=primary_context,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            secondary_contexts=secondary_contexts,
            indicators_found=indicators_found,
            exclusions_found=exclusions_found,
            disambiguation_applied=disambiguation_applied,
            raw_scores=context_scores,
            decision_factors=decision_factors
        )
    
    def _create_fallback_result(self, query: str) -> ClassificationResult:
        """Create a safe fallback result when classification fails"""
        return ClassificationResult(
            primary_context=ContextType.GENERAL,
            confidence_score=0.0,
            confidence_level=ConfidenceLevel.REJECTED,
            secondary_contexts=[],
            indicators_found={},
            exclusions_found=[],
            disambiguation_applied=[],
            raw_scores={},
            decision_factors=["Classification error - using fallback"]
        )
    
    def _update_classification_stats(self, result: ClassificationResult):
        """Update classification statistics for monitoring"""
        self._classification_stats["context_counts"][result.primary_context.value] += 1
        self._classification_stats["confidence_distribution"][result.confidence_level.value] += 1
        
        if result.confidence_level == ConfidenceLevel.LOW:
            self._classification_stats["low_confidence_cases"] += 1
    
    def _log_classification_decision(self, query: str, result: ClassificationResult):
        """Log classification decision with appropriate level"""
        query_preview = query[:30] + "..." if len(query) > 30 else query
        
        if result.confidence_level == ConfidenceLevel.HIGH:
            logger.info(f"✅ HIGH CONFIDENCE: '{query_preview}' → {result.primary_context.value} "
                       f"(confidence: {result.confidence_score:.3f})")
        elif result.confidence_level == ConfidenceLevel.MEDIUM:
            logger.info(f"🟡 MEDIUM CONFIDENCE: '{query_preview}' → {result.primary_context.value} "
                       f"(confidence: {result.confidence_score:.3f})")
        elif result.confidence_level == ConfidenceLevel.LOW:
            logger.warning(f"⚠️ LOW CONFIDENCE: '{query_preview}' → {result.primary_context.value} "
                          f"(confidence: {result.confidence_score:.3f})")
        else:
            logger.warning(f"❌ REJECTED: '{query_preview}' → fallback to general "
                          f"(confidence: {result.confidence_score:.3f})")
        
        # Log disambiguation events
        if result.disambiguation_applied:
            logger.info(f"🔧 DISAMBIGUATION: Applied {', '.join(result.disambiguation_applied)}")
        
        # Log decision factors for debugging
        if result.decision_factors:
            logger.debug(f"📊 DECISION FACTORS: {'; '.join(result.decision_factors)}")
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics for monitoring dashboards"""
        stats = self._classification_stats.copy()
        
        # Add derived metrics
        total = stats["total_classifications"]
        if total > 0:
            stats["accuracy_metrics"] = {
                "high_confidence_rate": stats["confidence_distribution"]["high"] / total,
                "disambiguation_rate": stats["disambiguation_events"] / total,
                "low_confidence_rate": stats["low_confidence_cases"] / total,
                "error_rate": stats["errors"] / total
            }
        
        stats["config_info"] = {
            "config_path": self.config_path,
            "contexts_supported": len(self.context_domains),
            "disambiguation_strategies": len(self.disambiguation_strategies)
        }
        
        return stats

# Factory function for easy instantiation
def get_contextual_filter(config_path: Optional[str] = None) -> ContextualFilterEngine:
    """
    Factory function to get a ContextualFilterEngine instance
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ContextualFilterEngine instance
    """
    return ContextualFilterEngine(config_path)

# Global instance for singleton pattern (optional)
_global_filter_instance: Optional[ContextualFilterEngine] = None

def get_global_contextual_filter(config_path: Optional[str] = None) -> ContextualFilterEngine:
    """
    Get a global singleton instance of ContextualFilterEngine
    
    Args:
        config_path: Optional path to configuration file (only used for first initialization)
        
    Returns:
        Global ContextualFilterEngine instance
    """
    global _global_filter_instance
    
    if _global_filter_instance is None:
        _global_filter_instance = ContextualFilterEngine(config_path)
        logger.info("🌐 Global ContextualFilterEngine instance created")
    
    return _global_filter_instance