"""
Comprehensive Integration Test Suite
Prevents configuration regressions and ensures system reliability
Senior-level testing approach: Real scenarios, no mocks
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.system_config import validate_system_health, get_database_paths, get_config
from app.core.retrieval_orchestrator import RetrievalOrchestrator
from app.api.enhanced_chat import process_enhanced_chat_query, initialize_enhanced_chat


class TestSystemConfiguration:
    """Test system configuration and health"""
    
    def test_system_health_validation(self):
        """Test that system health validation passes"""
        health = validate_system_health()
        assert health["configuration_valid"], "System configuration must be valid"
        assert health["database_paths_exist"], "Database paths must exist"
        assert len(health["issues"]) == 0, f"System has issues: {health['issues']}"
    
    def test_database_paths_correct(self):
        """Test that database paths point to existing locations"""
        db_paths = get_database_paths()
        
        required_dbs = ["civil", "quranic", "islamic"]
        for db_name in required_dbs:
            assert db_name in db_paths, f"Missing {db_name} database path"
            
            db_path = Path(db_paths[db_name])
            assert db_path.parent.exists(), f"{db_name} database directory doesn't exist: {db_path.parent}"
            
            # For critical databases, ensure they exist
            if db_name in ["civil", "quranic"]:
                assert db_path.exists(), f"Critical database missing: {db_path}"
    
    def test_configuration_consistency(self):
        """Test that configuration is internally consistent"""
        config = get_config()
        
        # Test performance settings
        assert config.max_civil_results > 0, "Civil results limit must be positive"
        assert config.max_quranic_results > 0, "Quranic results limit must be positive"
        assert isinstance(config.parallel_search_enabled, bool), "Parallel search setting must be boolean"
        assert isinstance(config.quranic_integration_enabled, bool), "Integration setting must be boolean"


class TestOrchestratorIntegration:
    """Test orchestrator integration and functionality"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_default_initialization(self):
        """Test that orchestrator initializes correctly with defaults"""
        orchestrator = RetrievalOrchestrator()
        await orchestrator.initialize()
        
        # Verify configuration
        assert orchestrator.civil_store is not None, "Civil store must be initialized"
        assert orchestrator.quranic_store is not None, "Quranic store must be initialized"
        assert orchestrator.quranic_integration_enabled, "Integration must be enabled"
    
    @pytest.mark.asyncio
    async def test_orchestrator_path_configuration(self):
        """Test that orchestrator uses correct database paths"""
        orchestrator = RetrievalOrchestrator()
        db_paths = get_database_paths()
        
        # Verify paths match configuration
        assert str(orchestrator.civil_store.db_path) == db_paths["civil"], "Civil store path mismatch"
        assert str(orchestrator.quranic_store.db_path) == db_paths["quranic"], "Quranic store path mismatch"
    
    @pytest.mark.asyncio
    async def test_orchestrator_search_functionality(self):
        """Test that orchestrator returns results for legal queries"""
        orchestrator = RetrievalOrchestrator()
        await orchestrator.initialize()
        
        # Test with employment law query
        query = "موظف فصل بدون سبب"
        response = await orchestrator.retrieve_integrated(query, {}, limit=5)
        
        # Verify response structure
        assert hasattr(response, 'civil_results'), "Response must have civil results"
        assert hasattr(response, 'quranic_results'), "Response must have quranic results"
        assert hasattr(response, 'strategy'), "Response must have strategy"
        assert hasattr(response, 'total_sources'), "Response must have total sources"
        
        # Verify results are returned
        total_results = len(response.civil_results) + len(response.quranic_results)
        assert total_results > 0, f"Query must return results, got {total_results}"
        
        # Verify quality metrics
        assert 0 <= response.integration_quality <= 1, "Integration quality must be between 0-1"
        assert 0 <= response.cultural_appropriateness <= 1, "Cultural appropriateness must be between 0-1"


class TestEnhancedChatIntegration:
    """Test enhanced chat API integration"""
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_initialization(self):
        """Test that enhanced chat initializes successfully"""
        result = await initialize_enhanced_chat()
        assert result, "Enhanced chat initialization must succeed"
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_returns_sources(self):
        """Test that enhanced chat returns sources for legal queries"""
        test_queries = [
            "موظف فصل بدون سبب",
            "حقوق العامل في الشركة",
            "عقد العمل والراتب",
            "قانون العمل السعودي"
        ]
        
        for query in test_queries:
            result = await process_enhanced_chat_query(query)
            
            # Verify response structure
            assert isinstance(result, dict), "Response must be a dictionary"
            assert "enhancement_info" in result, "Response must have enhancement_info"
            assert "answer" in result, "Response must have answer"
            assert "response_type" in result, "Response must have response_type"
            
            # Verify sources are returned
            enhancement_info = result["enhancement_info"]
            quranic_count = enhancement_info.get("quranic_sources_count", 0)
            civil_count = enhancement_info.get("civil_sources_count", 0)
            total_sources = quranic_count + civil_count
            
            assert total_sources > 0, f"Query '{query}' must return sources, got {total_sources}"
            assert quranic_count >= 0, "Quranic source count must be non-negative"
            assert civil_count >= 0, "Civil source count must be non-negative"
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_response_quality(self):
        """Test response quality metrics"""
        query = "موظف فصل بدون سبب"
        result = await process_enhanced_chat_query(query)
        
        enhancement_info = result["enhancement_info"]
        
        # Test response has meaningful content
        answer = result.get("answer", "")
        assert len(answer) > 100, "Answer must be substantive"
        
        # Test integration metrics
        assert "integration_quality" in enhancement_info, "Must have integration quality metric"
        assert "cultural_appropriateness" in enhancement_info, "Must have cultural appropriateness metric"
        assert "processing_time_ms" in enhancement_info, "Must have processing time metric"
        
        # Test metric ranges
        integration_quality = enhancement_info.get("integration_quality", 0)
        cultural_appropriateness = enhancement_info.get("cultural_appropriateness", 0)
        
        assert 0 <= integration_quality <= 1, "Integration quality must be between 0-1"
        assert 0 <= cultural_appropriateness <= 1, "Cultural appropriateness must be between 0-1"


class TestConcurrentLoad:
    """Test system behavior under concurrent load"""
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test system handles concurrent queries correctly"""
        queries = [
            "موظف فصل بدون سبب",
            "حقوق العامل في الشركة", 
            "عقد العمل والراتب",
            "نزاع مع صاحب العمل",
            "قانون العمل السعودي"
        ]
        
        # Execute queries concurrently
        tasks = [process_enhanced_chat_query(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all queries succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(queries), f"All queries must succeed, got {len(successful_results)}/{len(queries)}"
        
        # Verify each result has sources
        for i, result in enumerate(successful_results):
            enhancement_info = result["enhancement_info"]
            total_sources = enhancement_info.get("quranic_sources_count", 0) + enhancement_info.get("civil_sources_count", 0)
            assert total_sources > 0, f"Concurrent query {i+1} must return sources"


class TestRegressionPrevention:
    """Test for specific regression scenarios"""
    
    @pytest.mark.asyncio
    async def test_path_configuration_regression(self):
        """Test that database paths don't regress to wrong values"""
        # Test direct orchestrator paths
        orchestrator = RetrievalOrchestrator()
        
        civil_path = str(orchestrator.civil_store.db_path)
        quranic_path = str(orchestrator.quranic_store.db_path)
        
        # Ensure paths don't contain the wrong 'data/' prefix
        assert not civil_path.startswith("data/"), f"Civil path regression detected: {civil_path}"
        assert not quranic_path.startswith("data/"), f"Quranic path regression detected: {quranic_path}"
        
        # Ensure paths contain correct 'backend/data/' prefix
        assert "backend/data/" in civil_path, f"Civil path must contain backend/data/: {civil_path}"
        assert "backend/data/" in quranic_path, f"Quranic path must contain backend/data/: {quranic_path}"
    
    @pytest.mark.asyncio
    async def test_zero_results_regression(self):
        """Test that system doesn't regress to returning zero results"""
        query = "موظف فصل بدون سبب"
        result = await process_enhanced_chat_query(query)
        
        enhancement_info = result["enhancement_info"]
        total_sources = enhancement_info.get("quranic_sources_count", 0) + enhancement_info.get("civil_sources_count", 0)
        
        # This is the specific regression we fixed
        assert total_sources > 0, "REGRESSION: System returned to zero results behavior"
        assert total_sources >= 10, f"Expected significant results, got only {total_sources}"


if __name__ == "__main__":
    # Run specific tests for immediate validation
    async def run_immediate_tests():
        print("🧪 Running immediate integration tests...")
        
        # Test system health
        print("1. Testing system health...")
        health = validate_system_health()
        assert health["configuration_valid"], "Health check failed"
        print("   ✅ System health OK")
        
        # Test orchestrator
        print("2. Testing orchestrator...")
        orchestrator = RetrievalOrchestrator()
        await orchestrator.initialize()
        response = await orchestrator.retrieve_integrated("موظف فصل بدون سبب", {})
        total = len(response.civil_results) + len(response.quranic_results)
        assert total > 0, f"Orchestrator test failed: {total} results"
        print(f"   ✅ Orchestrator OK: {total} results")
        
        # Test enhanced chat
        print("3. Testing enhanced chat...")
        result = await process_enhanced_chat_query("موظف فصل بدون سبب")
        enhancement_info = result["enhancement_info"]
        total = enhancement_info.get("quranic_sources_count", 0) + enhancement_info.get("civil_sources_count", 0)
        assert total > 0, f"Enhanced chat test failed: {total} sources"
        print(f"   ✅ Enhanced chat OK: {total} sources")
        
        print("🎉 All immediate tests passed!")
    
    asyncio.run(run_immediate_tests())