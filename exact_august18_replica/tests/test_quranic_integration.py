"""
Comprehensive Testing Framework for Quranic Integration System
Enterprise-grade testing suite for all components
"""

import asyncio
import pytest
import logging
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import all components to test
from app.core.semantic_concepts import SemanticConceptEngine, LegalConcept, ConceptType
from app.storage.quranic_foundation_store import QuranicFoundationStore, QuranicFoundation
from app.core.retrieval_orchestrator import RetrievalOrchestrator, IntegrationStrategy
from app.api.enhanced_chat import EnhancedChatProcessor
from app.processors.qurtubi_processor import QurtubiProcessor, SemanticLegalAnalyzer

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Generate test data for comprehensive testing"""
    
    @staticmethod
    def create_test_legal_concepts() -> List[LegalConcept]:
        """Create test legal concepts for testing"""
        return [
            LegalConcept(
                concept_id="test_concept_1",
                primary_concept="العدالة في القضاء",
                concept_type=ConceptType.JUSTICE_CONCEPT,
                semantic_fields=["justice", "court_proceedings"],
                confidence_score=0.9,
                context_indicators=["justice_theme"],
                abstraction_level="high"
            ),
            LegalConcept(
                concept_id="test_concept_2", 
                primary_concept="الوفاء بالعقود",
                concept_type=ConceptType.SUBSTANTIVE_LAW,
                semantic_fields=["contracts", "obligations"],
                confidence_score=0.85,
                context_indicators=["contractual_obligation"],
                abstraction_level="medium"
            ),
            LegalConcept(
                concept_id="test_concept_3",
                primary_concept="إجراءات التقاضي",
                concept_type=ConceptType.PROCEDURAL_LAW,
                semantic_fields=["court_procedures"],
                confidence_score=0.8,
                context_indicators=["procedural_matter"],
                abstraction_level="low"
            )
        ]
    
    @staticmethod
    def create_test_quranic_foundations() -> List[QuranicFoundation]:
        """Create test Quranic foundations"""
        return [
            QuranicFoundation(
                foundation_id="test_qf_1",
                verse_text="وَأَوْفُوا بِالْعُقُودِ",
                surah_name="المائدة",
                ayah_number=1,
                verse_reference="المائدة:1",
                qurtubi_commentary="قال القرطبي: هذا أمر بالوفاء بجميع العقود والعهود...",
                legal_principle="وجوب الوفاء بالعقود والالتزامات",
                principle_category="contractual_obligations",
                applicable_legal_domains=["commercial_law", "civil_contracts"],
                semantic_concepts=["contract_fulfillment", "legal_obligations"],
                abstraction_level="principle_general",
                modern_applications=["العقود التجارية", "التزامات الأطراف"],
                legal_precedence_level="foundational",
                cultural_appropriateness=0.95,
                scholarship_confidence=0.9,
                legal_relevance_score=0.88,
                interpretation_consensus="unanimous"
            ),
            QuranicFoundation(
                foundation_id="test_qf_2",
                verse_text="وَلَا تَأْكُلُوا أَمْوَالَكُم بَيْنَكُم بِالْبَاطِلِ",
                surah_name="البقرة",
                ayah_number=188,
                verse_reference="البقرة:188",
                qurtubi_commentary="قال القرطبي: نهي عن أكل المال بالباطل كالربا والغصب...",
                legal_principle="تحريم أكل المال بالباطل",
                principle_category="economic_justice",
                applicable_legal_domains=["commercial_law", "financial_law"],
                semantic_concepts=["financial_justice", "prohibited_transactions"],
                abstraction_level="principle_general",
                modern_applications=["قوانين مكافحة الغش", "العدالة المالية"],
                legal_precedence_level="foundational",
                cultural_appropriateness=0.98,
                scholarship_confidence=0.92,
                legal_relevance_score=0.9,
                interpretation_consensus="unanimous"
            )
        ]
    
    @staticmethod
    def create_test_queries() -> List[Dict[str, Any]]:
        """Create test queries with expected behaviors"""
        return [
            {
                "query": "ما هي أحكام العقود في النظام السعودي؟",
                "expected_strategy": IntegrationStrategy.FOUNDATION_FIRST,
                "expected_concepts": ["contractual_obligations", "legal_requirements"],
                "expected_quranic_sources": True,
                "test_type": "islamic_foundation"
            },
            {
                "query": "كيف أقدم دعوى في المحكمة؟",
                "expected_strategy": IntegrationStrategy.CIVIL_ONLY,
                "expected_concepts": ["court_procedures", "filing_requirements"],
                "expected_quranic_sources": False,
                "test_type": "procedural_only"
            },
            {
                "query": "العدالة في التعامل التجاري",
                "expected_strategy": IntegrationStrategy.CIVIL_WITH_FOUNDATION,
                "expected_concepts": ["commercial_justice", "fair_dealing"],
                "expected_quranic_sources": True,
                "test_type": "modern_with_principles"
            }
        ]


class TestSemanticConceptEngine:
    """Test the semantic concept extraction engine"""
    
    @pytest.fixture
    async def concept_engine(self):
        """Create concept engine for testing"""
        return SemanticConceptEngine()
    
    @pytest.mark.asyncio
    async def test_concept_extraction_basic(self, concept_engine):
        """Test basic concept extraction"""
        text = "يجب على الأطراف الوفاء بالتزاماتهم التعاقدية وفقاً لأحكام العقد"
        
        concepts = await concept_engine.extract_legal_concepts(text)
        
        assert len(concepts) > 0, "Should extract at least one concept"
        assert any("التزام" in concept.primary_concept.lower() or 
                  "عقد" in concept.primary_concept.lower() 
                  for concept in concepts), "Should extract contract-related concepts"
    
    @pytest.mark.asyncio
    async def test_concept_extraction_with_context(self, concept_engine):
        """Test concept extraction with context"""
        text = "العدالة أساس الحكم"
        context = {"domain": "judicial_system", "complexity": "high"}
        
        concepts = await concept_engine.extract_legal_concepts(text, context)
        
        assert len(concepts) > 0, "Should extract concepts with context"
        justice_concepts = [c for c in concepts if c.concept_type == ConceptType.JUSTICE_CONCEPT]
        assert len(justice_concepts) > 0, "Should extract justice concepts"
    
    @pytest.mark.asyncio
    async def test_concept_caching(self, concept_engine):
        """Test concept extraction caching"""
        text = "test caching text for legal concepts"
        
        # First extraction
        start_time = datetime.now()
        concepts1 = await concept_engine.extract_legal_concepts(text)
        first_time = (datetime.now() - start_time).total_seconds()
        
        # Second extraction (should be cached)
        start_time = datetime.now()
        concepts2 = await concept_engine.extract_legal_concepts(text)
        second_time = (datetime.now() - start_time).total_seconds()
        
        assert concepts1 == concepts2, "Cached results should be identical"
        assert second_time < first_time, "Cached extraction should be faster"
    
    def test_concept_engine_statistics(self, concept_engine):
        """Test concept engine statistics"""
        stats = concept_engine.get_extraction_stats()
        
        assert "total_extractions" in stats
        assert "cache_hits" in stats
        assert "average_concepts_per_text" in stats
        assert "cache_size" in stats


class TestQuranicFoundationStore:
    """Test the Quranic foundation storage system"""
    
    @pytest.fixture
    async def temp_store(self):
        """Create temporary store for testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            store = QuranicFoundationStore(tf.name)
            await store.initialize()
            yield store
            # Cleanup
            if os.path.exists(tf.name):
                os.unlink(tf.name)
    
    @pytest.mark.asyncio
    async def test_store_initialization(self, temp_store):
        """Test store initialization"""
        health = await temp_store.health_check()
        assert health, "Store should be healthy after initialization"
        
        stats = await temp_store.get_stats()
        assert stats.total_chunks == 0, "New store should be empty"
    
    @pytest.mark.asyncio
    async def test_store_quranic_foundations(self, temp_store):
        """Test storing Quranic foundations"""
        foundations = TestDataGenerator.create_test_quranic_foundations()
        
        success = await temp_store.store_quranic_foundations(foundations)
        assert success, "Should successfully store foundations"
        
        stats = await temp_store.get_stats()
        assert stats.total_chunks == len(foundations), "Should store all foundations"
    
    @pytest.mark.asyncio
    async def test_semantic_search_foundations(self, temp_store):
        """Test semantic search functionality"""
        # Store test data
        foundations = TestDataGenerator.create_test_quranic_foundations()
        await temp_store.store_quranic_foundations(foundations)
        
        # Create test concepts
        concepts = TestDataGenerator.create_test_legal_concepts()
        contract_concepts = [c for c in concepts if "عقد" in c.primary_concept]
        
        # Search
        results = await temp_store.semantic_search_foundations(
            contract_concepts, {"domain": "commercial_law"}, limit=5
        )
        
        assert len(results) > 0, "Should find relevant foundations"
        assert all(r.similarity_score > 0 for r in results), "Results should have positive scores"
    
    @pytest.mark.asyncio
    async def test_foundation_retrieval_by_id(self, temp_store):
        """Test retrieving foundations by ID"""
        foundations = TestDataGenerator.create_test_quranic_foundations()
        await temp_store.store_quranic_foundations(foundations)
        
        foundation_id = foundations[0].foundation_id
        retrieved = await temp_store.get_chunk_by_id(foundation_id)
        
        assert retrieved is not None, "Should retrieve foundation by ID"
        assert retrieved.id == foundation_id, "Should retrieve correct foundation"
    
    @pytest.mark.asyncio
    async def test_foundation_deletion(self, temp_store):
        """Test deleting foundations"""
        foundations = TestDataGenerator.create_test_quranic_foundations()
        await temp_store.store_quranic_foundations(foundations)
        
        foundation_ids = [f.foundation_id for f in foundations]
        deleted_count = await temp_store.delete_chunks(foundation_ids)
        
        assert deleted_count == len(foundations), "Should delete all foundations"
        
        stats = await temp_store.get_stats()
        assert stats.total_chunks == 0, "Store should be empty after deletion"


class TestRetrievalOrchestrator:
    """Test the retrieval orchestrator"""
    
    @pytest.fixture
    async def temp_orchestrator(self):
        """Create temporary orchestrator for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            civil_db = os.path.join(temp_dir, "civil.db")
            quranic_db = os.path.join(temp_dir, "quranic.db")
            
            orchestrator = RetrievalOrchestrator(civil_db, quranic_db)
            
            # Store test data
            foundations = TestDataGenerator.create_test_quranic_foundations()
            await orchestrator.quranic_store.initialize()
            await orchestrator.quranic_store.store_quranic_foundations(foundations)
            
            yield orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_orchestrator):
        """Test orchestrator initialization"""
        health = await temp_orchestrator.get_health_status()
        assert health["status"] in ["healthy", "degraded"], "Orchestrator should be operational"
    
    @pytest.mark.asyncio
    async def test_strategy_selection(self, temp_orchestrator):
        """Test integration strategy selection"""
        test_queries = TestDataGenerator.create_test_queries()
        
        for test_case in test_queries:
            query = test_case["query"]
            expected_strategy = test_case["expected_strategy"]
            
            # Extract concepts first
            concepts = await temp_orchestrator.concept_engine.extract_legal_concepts(query)
            
            # Test strategy selection
            selected_strategy = await temp_orchestrator.strategy_selector.select_strategy(
                query, concepts, {}
            )
            
            assert selected_strategy == expected_strategy, \
                f"Query '{query}' should select strategy {expected_strategy}, got {selected_strategy}"
    
    @pytest.mark.asyncio
    async def test_integrated_retrieval(self, temp_orchestrator):
        """Test integrated retrieval functionality"""
        query = "ما أحكام العقود في الشريعة والقانون؟"
        
        response = await temp_orchestrator.retrieve_integrated(query, limit=10)
        
        assert response.query == query, "Response should contain original query"
        assert response.execution_time_ms > 0, "Should track execution time"
        assert response.strategy in IntegrationStrategy, "Should have valid strategy"
        assert len(response.extracted_concepts) > 0, "Should extract concepts"
    
    @pytest.mark.asyncio
    async def test_performance_metrics_tracking(self, temp_orchestrator):
        """Test performance metrics tracking"""
        initial_queries = temp_orchestrator.performance_metrics["total_queries"]
        
        query = "test query for performance tracking"
        await temp_orchestrator.retrieve_integrated(query)
        
        final_queries = temp_orchestrator.performance_metrics["total_queries"]
        assert final_queries == initial_queries + 1, "Should increment query count"
        
        avg_time = temp_orchestrator.performance_metrics["average_response_time"]
        assert avg_time > 0, "Should track average response time"


class TestEnhancedChatProcessor:
    """Test the enhanced chat processor"""
    
    @pytest.fixture
    async def temp_chat_processor(self):
        """Create temporary chat processor for testing"""
        processor = EnhancedChatProcessor()
        
        # Mock the orchestrator to avoid complex setup
        class MockOrchestrator:
            async def initialize(self):
                pass
            
            async def retrieve_integrated(self, query, context=None, limit=15):
                from app.core.retrieval_orchestrator import IntegratedResponse
                return IntegratedResponse(
                    query=query,
                    strategy=IntegrationStrategy.CIVIL_WITH_FOUNDATION,
                    execution_time_ms=100.0,
                    civil_results=[],
                    quranic_results=[],
                    primary_sources=[],
                    supporting_sources=[],
                    contextual_sources=[],
                    integration_quality=0.8,
                    cultural_appropriateness=0.9,
                    legal_completeness=0.7,
                    extracted_concepts=[],
                    concept_coverage={},
                    civil_search_time=50.0,
                    quranic_search_time=30.0,
                    integration_time=20.0,
                    total_sources=0,
                    confidence_distribution={"high": 0, "medium": 0, "low": 0},
                    strategy_explanation="Mock response"
                )
        
        processor.orchestrator = MockOrchestrator()
        await processor.initialize()
        
        yield processor
    
    @pytest.mark.asyncio
    async def test_chat_processor_initialization(self, temp_chat_processor):
        """Test chat processor initialization"""
        health = await temp_chat_processor.get_health_status()
        assert health["status"] in ["healthy", "degraded"], "Chat processor should be operational"
    
    @pytest.mark.asyncio
    async def test_enhanced_query_processing(self, temp_chat_processor):
        """Test enhanced query processing"""
        query = "ما أحكام العدالة في القضاء؟"
        
        response = await temp_chat_processor.process_chat_query(query)
        
        assert "answer" in response, "Response should contain answer"
        assert "sources" in response, "Response should contain sources"
        assert "confidence" in response, "Response should contain confidence"
        assert response["response_type"] in ["enhanced", "traditional"], "Should have valid response type"
    
    @pytest.mark.asyncio
    async def test_user_preferences_application(self, temp_chat_processor):
        """Test user preferences application"""
        query = "test query"
        user_prefs = {
            "islamic_integration": "minimal",
            "response_length": "concise"
        }
        
        response = await temp_chat_processor.process_chat_query(
            query, user_preferences=user_prefs
        )
        
        assert "answer" in response, "Should process with user preferences"
        # More specific assertions would depend on mock implementation
    
    @pytest.mark.asyncio
    async def test_feature_flag_configuration(self, temp_chat_processor):
        """Test feature flag configuration"""
        initial_flags = temp_chat_processor.feature_flags.copy()
        
        new_config = {"quranic_integration": False}
        temp_chat_processor.configure_features(new_config)
        
        assert temp_chat_processor.feature_flags["quranic_integration"] == False
        
        # Restore original flags
        temp_chat_processor.configure_features(initial_flags)
    
    @pytest.mark.asyncio
    async def test_fallback_processing(self, temp_chat_processor):
        """Test fallback processing when enhancement fails"""
        # Disable integration to test fallback
        temp_chat_processor.enable_integration(False)
        
        query = "test fallback query"
        response = await temp_chat_processor.process_chat_query(query)
        
        assert response["response_type"] == "traditional", "Should use traditional processing"
        
        # Re-enable integration
        temp_chat_processor.enable_integration(True)


class TestSemanticLegalAnalyzer:
    """Test the semantic legal analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing"""
        return SemanticLegalAnalyzer()
    
    @pytest.mark.asyncio
    async def test_legal_content_analysis(self, analyzer):
        """Test legal content analysis"""
        legal_content = "قال القرطبي: إن العدالة أساس الحكم، ويجب على القاضي أن يحكم بالعدل"
        context = {"surah": "النساء", "ayah": 58}
        
        analysis = await analyzer.analyze_content(legal_content, context)
        
        assert analysis["is_legal_content"], "Should identify as legal content"
        assert analysis["legal_relevance_score"] > 0.5, "Should have high legal relevance"
        assert analysis["scholarship_confidence"] > 0.0, "Should have scholarship confidence"
        assert len(analysis["applicable_domains"]) > 0, "Should identify applicable domains"
    
    @pytest.mark.asyncio
    async def test_non_legal_content_analysis(self, analyzer):
        """Test analysis of non-legal content"""
        non_legal_content = "هذا نص عام عن الطبيعة والجمال"
        context = {}
        
        analysis = await analyzer.analyze_content(non_legal_content, context)
        
        assert not analysis["is_legal_content"], "Should not identify as legal content"
        assert analysis["legal_relevance_score"] < 0.6, "Should have low legal relevance"
    
    @pytest.mark.asyncio
    async def test_principle_extraction(self, analyzer):
        """Test legal principle extraction"""
        content = "إن الله يأمر بالعدل والإحسان"
        context = {"verse_context": True}
        
        analysis = await analyzer.analyze_content(content, context)
        
        if analysis["is_legal_content"]:
            assert analysis["legal_principle"], "Should extract legal principle"
            assert analysis["principle_category"], "Should categorize principle"


class TestIntegrationWorkflow:
    """Test complete integration workflow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This test verifies the entire pipeline works together
        
        # 1. Create test data
        foundations = TestDataGenerator.create_test_quranic_foundations()
        test_queries = TestDataGenerator.create_test_queries()
        
        # 2. Set up temporary system
        with tempfile.TemporaryDirectory() as temp_dir:
            quranic_db = os.path.join(temp_dir, "quranic_test.db")
            
            # Initialize store and add data
            store = QuranicFoundationStore(quranic_db)
            await store.initialize()
            await store.store_quranic_foundations(foundations)
            
            # Test each query type
            for test_case in test_queries:
                query = test_case["query"]
                
                # Test concept extraction
                concept_engine = SemanticConceptEngine()
                concepts = await concept_engine.extract_legal_concepts(query)
                
                assert len(concepts) > 0, f"Should extract concepts for: {query}"
                
                # Test semantic search
                results = await store.semantic_search_foundations(
                    concepts, {"test": True}, limit=5
                )
                
                if test_case["expected_quranic_sources"]:
                    assert len(results) > 0, f"Should find Quranic sources for: {query}"
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        # Test that operations complete within acceptable time limits
        
        concept_engine = SemanticConceptEngine()
        
        # Concept extraction should be fast
        start_time = datetime.now()
        concepts = await concept_engine.extract_legal_concepts("test legal query")
        extraction_time = (datetime.now() - start_time).total_seconds()
        
        assert extraction_time < 5.0, "Concept extraction should complete within 5 seconds"
        
        # Verify caching improves performance
        start_time = datetime.now()
        cached_concepts = await concept_engine.extract_legal_concepts("test legal query")
        cached_time = (datetime.now() - start_time).total_seconds()
        
        assert cached_time < extraction_time, "Cached extraction should be faster"
        assert concepts == cached_concepts, "Cached results should be identical"


class TestSystemResilience:
    """Test system resilience and error handling"""
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when components fail"""
        
        # Test chat processor with failed orchestrator
        processor = EnhancedChatProcessor()
        
        # Mock a failing orchestrator
        class FailingOrchestrator:
            async def initialize(self):
                raise Exception("Simulated failure")
        
        processor.orchestrator = FailingOrchestrator()
        
        # Should gracefully handle initialization failure
        try:
            await processor.initialize()
            assert False, "Should raise exception on initialization failure"
        except Exception:
            pass  # Expected
        
        # Should disable integration and continue working
        assert not processor.integration_enabled, "Should disable integration on failure"
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        
        concept_engine = SemanticConceptEngine()
        
        # Test empty input
        concepts = await concept_engine.extract_legal_concepts("")
        assert len(concepts) == 0, "Should handle empty input gracefully"
        
        # Test very short input
        concepts = await concept_engine.extract_legal_concepts("hi")
        assert len(concepts) == 0, "Should handle very short input gracefully"
        
        # Test None input
        concepts = await concept_engine.extract_legal_concepts(None)
        assert len(concepts) == 0, "Should handle None input gracefully"
    
    @pytest.mark.asyncio
    async def test_database_corruption_handling(self):
        """Test handling of database corruption/issues"""
        
        # Test with invalid database path
        store = QuranicFoundationStore("/invalid/path/db.db")
        
        try:
            await store.initialize()
            assert False, "Should fail with invalid path"
        except Exception:
            pass  # Expected
        
        # Test health check with corrupted store
        health = await store.health_check()
        assert not health, "Health check should fail for corrupted store"


# Performance and load testing
class TestPerformanceAndLoad:
    """Test performance under load"""
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent query processing"""
        
        concept_engine = SemanticConceptEngine()
        queries = [
            "ما أحكام العقود؟",
            "العدالة في القضاء",
            "إجراءات التقاضي",
            "الحقوق والواجبات",
            "النظام القانوني السعودي"
        ]
        
        # Process queries concurrently
        start_time = datetime.now()
        tasks = [concept_engine.extract_legal_concepts(query) for query in queries]
        results = await asyncio.gather(*tasks)
        concurrent_time = (datetime.now() - start_time).total_seconds()
        
        # Process queries sequentially
        start_time = datetime.now()
        sequential_results = []
        for query in queries:
            result = await concept_engine.extract_legal_concepts(query)
            sequential_results.append(result)
        sequential_time = (datetime.now() - start_time).total_seconds()
        
        # Concurrent should be at least as fast as sequential (due to caching)
        assert concurrent_time <= sequential_time * 1.1, "Concurrent processing should be efficient"
        assert len(results) == len(queries), "Should process all queries"
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively"""
        
        concept_engine = SemanticConceptEngine()
        
        # Process many queries to test memory usage
        for i in range(100):
            query = f"test query number {i} for memory testing"
            await concept_engine.extract_legal_concepts(query)
        
        # Check cache size is reasonable
        stats = concept_engine.get_extraction_stats()
        assert stats["cache_size"] <= 1000, "Cache size should be controlled"
        
        # Clear cache to verify memory cleanup
        concept_engine.clear_cache()
        post_clear_stats = concept_engine.get_extraction_stats()
        assert post_clear_stats["cache_size"] == 0, "Cache should be cleared"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])