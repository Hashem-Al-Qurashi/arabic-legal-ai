"""
Unit tests for Multi-Modal Search System
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List

from app.core.enhancements.multi_modal_search import (
    MultiModalSearchEngine,
    VectorSearchStrategy,
    KeywordSearchStrategy,
    SearchStrategy,
    SearchResult,
    create_multi_modal_search_engine
)


class TestVectorSearchStrategy:
    """Test vector search strategy"""
    
    @pytest.fixture
    def mock_vector_store(self):
        store = Mock()
        store.search_similar = AsyncMock()
        return store
    
    @pytest.fixture
    def mock_embedding_client(self):
        client = Mock()
        return client
    
    @pytest.fixture
    def vector_strategy(self, mock_vector_store, mock_embedding_client):
        return VectorSearchStrategy(mock_vector_store, mock_embedding_client)
    
    @pytest.mark.asyncio
    async def test_vector_search_success(self, vector_strategy, mock_vector_store):
        # Setup mock results
        mock_results = [
            Mock(foundation_id="test1", content="test content 1", score=0.9),
            Mock(foundation_id="test2", content="test content 2", score=0.8)
        ]
        mock_vector_store.search_similar.return_value = mock_results
        
        # Execute search
        results = await vector_strategy.search("test query", [], 5)
        
        # Assertions
        assert len(results) == 2
        assert results[0].foundation_id == "test1"
        assert results[0].relevance_score == 0.9
        assert results[0].strategy_used == SearchStrategy.VECTOR_ONLY
        assert results[0].confidence_level == 0.85
    
    @pytest.mark.asyncio
    async def test_vector_search_failure(self, vector_strategy, mock_vector_store):
        # Setup mock to raise exception
        mock_vector_store.search_similar.side_effect = Exception("Vector search failed")
        
        # Execute search
        results = await vector_strategy.search("test query", [], 5)
        
        # Should return empty list on failure
        assert results == []
    
    def test_get_confidence(self, vector_strategy):
        assert vector_strategy.get_confidence() == 0.85


class TestKeywordSearchStrategy:
    """Test keyword search strategy"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def keyword_strategy(self, mock_db):
        return KeywordSearchStrategy(mock_db)
    
    def test_extract_keywords_arabic(self, keyword_strategy):
        query = "موظف سعودي تم فصله ولم تدفع له الشركة مستحقاته"
        concepts = []
        
        keywords = keyword_strategy._extract_keywords(query, concepts)
        
        # Should extract Arabic legal terms
        assert any("عدالة" in keywords or "justice" in keywords for term in ["عدالة", "justice"])
    
    def test_extract_keywords_from_concepts(self, keyword_strategy):
        mock_concept = Mock()
        mock_concept.primary_concept = "employment_rights"
        mock_concept.semantic_fields = ["justice", "fairness"]
        
        keywords = keyword_strategy._extract_keywords("test query", [mock_concept])
        
        assert "employment_rights" in keywords
        assert "justice" in keywords
        assert "fairness" in keywords
    
    @pytest.mark.asyncio
    async def test_keyword_search_no_keywords(self, keyword_strategy):
        # Query with no relevant keywords
        results = await keyword_strategy.search("irrelevant query", [], 5)
        
        # Should return empty list
        assert results == []
    
    def test_get_confidence(self, keyword_strategy):
        assert keyword_strategy.get_confidence() == 0.70


class TestMultiModalSearchEngine:
    """Test multi-modal search orchestration"""
    
    @pytest.fixture
    def mock_strategies(self):
        vector_strategy = Mock()
        vector_strategy.search = AsyncMock()
        
        keyword_strategy = Mock()
        keyword_strategy.search = AsyncMock()
        
        return {
            SearchStrategy.VECTOR_ONLY: vector_strategy,
            SearchStrategy.KEYWORD_ONLY: keyword_strategy
        }
    
    @pytest.fixture
    def search_engine(self, mock_strategies):
        engine = MultiModalSearchEngine()
        engine.strategies = mock_strategies
        return engine
    
    @pytest.mark.asyncio
    async def test_search_vector_success(self, search_engine, mock_strategies):
        # Setup vector search to succeed
        mock_results = [SearchResult(
            foundation_id="test1",
            content="test content",
            relevance_score=0.9,
            strategy_used=SearchStrategy.VECTOR_ONLY,
            confidence_level=0.85
        )]
        mock_strategies[SearchStrategy.VECTOR_ONLY].search.return_value = mock_results
        
        # Execute search
        results = await search_engine.search("test query", [], 5)
        
        # Should return vector results
        assert len(results) == 1
        assert results[0].strategy_used == SearchStrategy.VECTOR_ONLY
        
        # Keyword search should not be called (fallback not needed)
        mock_strategies[SearchStrategy.KEYWORD_ONLY].search.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_search_fallback_to_keyword(self, search_engine, mock_strategies):
        # Setup vector search to fail, keyword to succeed
        mock_strategies[SearchStrategy.VECTOR_ONLY].search.return_value = []
        
        mock_keyword_results = [SearchResult(
            foundation_id="test1",
            content="test content",
            relevance_score=0.7,
            strategy_used=SearchStrategy.KEYWORD_ONLY,
            confidence_level=0.70
        )]
        mock_strategies[SearchStrategy.KEYWORD_ONLY].search.return_value = mock_keyword_results
        
        # Execute search
        results = await search_engine.search("test query", [], 5)
        
        # Should return keyword results
        assert len(results) == 1
        assert results[0].strategy_used == SearchStrategy.KEYWORD_ONLY
    
    @pytest.mark.asyncio
    async def test_search_all_strategies_fail(self, search_engine, mock_strategies):
        # Setup all strategies to fail
        mock_strategies[SearchStrategy.VECTOR_ONLY].search.return_value = []
        mock_strategies[SearchStrategy.KEYWORD_ONLY].search.return_value = []
        
        # Execute search
        results = await search_engine.search("test query", [], 5)
        
        # Should return empty list
        assert results == []
    
    def test_merge_and_rank_results(self, search_engine):
        # Create test results with duplicates
        results = [
            SearchResult("id1", "content1", 0.9, SearchStrategy.VECTOR_ONLY, 0.85),
            SearchResult("id2", "content2", 0.8, SearchStrategy.KEYWORD_ONLY, 0.70),
            SearchResult("id1", "content1", 0.7, SearchStrategy.KEYWORD_ONLY, 0.70),  # Duplicate
            SearchResult("id3", "content3", 0.95, SearchStrategy.VECTOR_ONLY, 0.85),
        ]
        
        merged = search_engine._merge_and_rank_results(results, 5)
        
        # Should remove duplicates and sort by relevance
        assert len(merged) == 3
        assert merged[0].foundation_id == "id3"  # Highest score
        assert merged[1].foundation_id == "id1"  # Second highest
        assert merged[2].foundation_id == "id2"  # Lowest score
    
    def test_get_search_statistics(self, search_engine):
        stats = search_engine.get_search_statistics()
        
        assert "available_strategies" in stats
        assert "fallback_order" in stats
        assert "strategy_confidence" in stats


class TestFactoryFunction:
    """Test factory function"""
    
    def test_create_multi_modal_search_engine(self):
        engine = create_multi_modal_search_engine()
        
        assert isinstance(engine, MultiModalSearchEngine)
        assert SearchStrategy.VECTOR_ONLY in engine.strategies
        assert SearchStrategy.KEYWORD_ONLY in engine.strategies


# Integration test
class TestMultiModalSearchIntegration:
    """Integration tests for multi-modal search"""
    
    @pytest.mark.asyncio
    async def test_employment_rights_query(self):
        """Test realistic employment rights query"""
        # This would be an integration test with real components
        # For now, we'll mock the components
        
        mock_vector_store = Mock()
        mock_vector_store.search_similar = AsyncMock(return_value=[])
        
        mock_db = Mock()
        
        engine = MultiModalSearchEngine(
            vector_store=mock_vector_store,
            database_connection=mock_db
        )
        
        query = "موظف سعودي تم فصله بدون سبب ولم تدفع له الشركة مستحقاته"
        results = await engine.search(query, [], 5)
        
        # Should not crash and should attempt fallback
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_justice_query(self):
        """Test justice-related query"""
        mock_vector_store = Mock()
        mock_vector_store.search_similar = AsyncMock(return_value=[])
        
        mock_db = Mock()
        
        engine = MultiModalSearchEngine(
            vector_store=mock_vector_store,
            database_connection=mock_db
        )
        
        query = "العدالة في القضاء السعودي"
        results = await engine.search(query, [], 5)
        
        # Should not crash
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__])