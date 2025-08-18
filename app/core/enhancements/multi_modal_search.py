"""
Multi-Modal Search Implementation for Islamic Legal AI
Provides graceful degradation and multiple search strategies
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """Available search strategies"""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    SEMANTIC_ENHANCED = "semantic_enhanced"


@dataclass
class SearchResult:
    """Enhanced search result with confidence and strategy info"""
    foundation_id: str
    content: str
    relevance_score: float
    strategy_used: SearchStrategy
    confidence_level: float
    explanation: Optional[str] = None


class SearchStrategyInterface(ABC):
    """Interface for search strategy implementations"""
    
    @abstractmethod
    async def search(self, query: str, concepts: List[Any], max_results: int = 5) -> List[SearchResult]:
        """Execute search with this strategy"""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """Get confidence level for this strategy"""
        pass


class VectorSearchStrategy(SearchStrategyInterface):
    """Vector-based similarity search"""
    
    def __init__(self, vector_store, embedding_client):
        self.vector_store = vector_store
        self.embedding_client = embedding_client
        self.confidence = 0.85
    
    async def search(self, query: str, concepts: List[Any], max_results: int = 5) -> List[SearchResult]:
        """Perform vector similarity search"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search vector store
            results = await self.vector_store.search_similar(query_embedding, max_results)
            
            # Convert to SearchResult format
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    foundation_id=result.foundation_id,
                    content=result.content,
                    relevance_score=result.score,
                    strategy_used=SearchStrategy.VECTOR_ONLY,
                    confidence_level=self.confidence,
                    explanation=f"Vector similarity: {result.score:.3f}"
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query"""
        # Placeholder - will use actual embedding client
        return [0.0] * 1536  # Standard embedding dimension
    
    def get_confidence(self) -> float:
        return self.confidence


class KeywordSearchStrategy(SearchStrategyInterface):
    """Keyword-based search with Islamic legal terminology"""
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.confidence = 0.70
        self.islamic_legal_terms = {
            "عدالة": ["justice", "fairness", "equity"],
            "عقد": ["contract", "agreement", "covenant"],
            "حق": ["right", "entitlement", "due"],
            "واجب": ["duty", "obligation", "responsibility"],
            "ظلم": ["injustice", "oppression", "wrongdoing"]
        }
    
    async def search(self, query: str, concepts: List[Any], max_results: int = 5) -> List[SearchResult]:
        """Perform keyword-based search"""
        try:
            # Extract relevant keywords
            keywords = self._extract_keywords(query, concepts)
            
            # Build SQL query for keyword search
            sql_conditions = []
            for keyword in keywords:
                sql_conditions.append(f"(legal_principle LIKE '%{keyword}%' OR semantic_concepts LIKE '%{keyword}%')")
            
            if not sql_conditions:
                return []
            
            sql_query = f"""
                SELECT foundation_id, verse_text, legal_principle, legal_relevance_score
                FROM quranic_foundations 
                WHERE {' OR '.join(sql_conditions)}
                ORDER BY legal_relevance_score DESC
                LIMIT {max_results}
            """
            
            # Execute search (placeholder - would use actual DB)
            results = []  # Placeholder for actual DB results
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def _extract_keywords(self, query: str, concepts: List[Any]) -> List[str]:
        """Extract relevant Arabic keywords from query and concepts"""
        keywords = []
        query_lower = query.lower()
        
        # Extract from Islamic legal terms
        for arabic_term, english_terms in self.islamic_legal_terms.items():
            if arabic_term in query_lower:
                keywords.append(arabic_term)
                keywords.extend(english_terms)
        
        # Extract from concepts
        for concept in concepts:
            if hasattr(concept, 'primary_concept'):
                keywords.append(concept.primary_concept)
            if hasattr(concept, 'semantic_fields'):
                keywords.extend(concept.semantic_fields)
        
        return list(set(keywords))  # Remove duplicates
    
    def get_confidence(self) -> float:
        return self.confidence


class MultiModalSearchEngine:
    """
    Orchestrates multiple search strategies with fallback mechanisms
    """
    
    def __init__(self, vector_store=None, database_connection=None, embedding_client=None):
        self.strategies = {
            SearchStrategy.VECTOR_ONLY: VectorSearchStrategy(vector_store, embedding_client),
            SearchStrategy.KEYWORD_ONLY: KeywordSearchStrategy(database_connection),
        }
        self.fallback_order = [
            SearchStrategy.VECTOR_ONLY,
            SearchStrategy.KEYWORD_ONLY,
        ]
    
    async def search(self, query: str, concepts: List[Any], max_results: int = 5) -> List[SearchResult]:
        """
        Execute multi-modal search with fallback strategies
        """
        all_results = []
        
        for strategy_type in self.fallback_order:
            try:
                strategy = self.strategies[strategy_type]
                results = await strategy.search(query, concepts, max_results)
                
                if results:
                    logger.info(f"Search successful with strategy: {strategy_type.value}")
                    all_results.extend(results)
                    break  # Use first successful strategy
                else:
                    logger.warning(f"No results from strategy: {strategy_type.value}")
            
            except Exception as e:
                logger.error(f"Strategy {strategy_type.value} failed: {e}")
                continue
        
        if not all_results:
            logger.warning("All search strategies failed")
            return []
        
        # Deduplicate and rank results
        return self._merge_and_rank_results(all_results, max_results)
    
    def _merge_and_rank_results(self, results: List[SearchResult], max_results: int) -> List[SearchResult]:
        """Merge results from different strategies and rank by relevance"""
        # Remove duplicates based on foundation_id
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result.foundation_id not in seen_ids:
                seen_ids.add(result.foundation_id)
                unique_results.append(result)
        
        # Sort by relevance score (descending)
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results[:max_results]
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about search performance"""
        return {
            "available_strategies": [s.value for s in self.strategies.keys()],
            "fallback_order": [s.value for s in self.fallback_order],
            "strategy_confidence": {
                s.value: strategy.get_confidence() 
                for s, strategy in self.strategies.items()
            }
        }


# Factory function for easy integration
def create_multi_modal_search_engine(vector_store=None, database_connection=None, embedding_client=None) -> MultiModalSearchEngine:
    """
    Factory function to create configured multi-modal search engine
    """
    return MultiModalSearchEngine(
        vector_store=vector_store,
        database_connection=database_connection,
        embedding_client=embedding_client
    )