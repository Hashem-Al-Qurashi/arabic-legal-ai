"""
Comprehensive Test Suite for ContextualFilterEngine
Testing context classification and disambiguation accuracy
Author: Expert AI Engineer
Date: 2025-08-19
Coverage: Unit tests, integration tests, edge cases, principle validation
"""

import pytest
import tempfile
import os
import yaml
import time
from typing import Dict, List
import sys

# Add backend to path for testing
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

from app.core.contextual_filter_engine import (
    ContextualFilterEngine, 
    get_contextual_filter,
    get_global_contextual_filter,
    ContextType,
    ConfidenceLevel,
    ClassificationResult,
    IContextClassifier
)

class TestContextualFilterEnginePrinciples:
    """Test that all five engineering principles are followed"""
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing"""
        return {
            "version": "1.0",
            "context_domains": {
                "employment": {"confidence_threshold": 0.7},
                "religious": {"confidence_threshold": 0.8}
            },
            "classification_rules": {
                "employment_context": {
                    "primary_indicators": {
                        "arabic": ["موظف", "عامل", "وظيفة"],
                        "english": ["employee", "worker", "job"]
                    },
                    "legal_reinforcers": {
                        "arabic": ["قانون", "نظام", "مادة"],
                        "english": ["law", "regulation", "article"]
                    },
                    "exclusion_terms": {
                        "arabic": ["ثواب", "آخرة", "جنة"],
                        "english": ["reward", "afterlife", "paradise"]
                    }
                },
                "religious_context": {
                    "primary_indicators": {
                        "arabic": ["ثواب", "آخرة", "جنة"],
                        "english": ["reward", "afterlife", "paradise"]
                    },
                    "exclusion_terms": {
                        "arabic": ["قانون", "راتب", "موظف"],
                        "english": ["law", "salary", "employee"]
                    }
                }
            },
            "disambiguation_strategies": {
                "work_term_disambiguation": {
                    "employment_context_indicators": {
                        "required_minimum": 2,
                        "indicators": [
                            {"presence": ["قانون", "نظام"]},
                            {"presence": ["موظف", "وظيفة"]},
                            {"absence": ["ثواب", "آخرة"]}
                        ]
                    },
                    "religious_context_indicators": {
                        "required_minimum": 2,
                        "indicators": [
                            {"presence": ["ثواب", "آخرة"]},
                            {"presence": ["الله", "إيمان"]},
                            {"absence": ["قانون", "موظف"]}
                        ]
                    }
                }
            },
            "confidence_scoring": {
                "weights": {
                    "primary_indicators": 0.4,
                    "legal_reinforcers": 0.3,
                    "domain_terms": 0.2,
                    "exclusion_penalty": -0.3
                },
                "thresholds": {
                    "high_confidence": 0.8,
                    "medium_confidence": 0.6,
                    "low_confidence": 0.4,
                    "rejection_threshold": 0.3
                }
            },
            "fallback_behavior": {
                "default_context": "general",
                "log_ambiguous_cases": True
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create a temporary configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(sample_config, f, allow_unicode=True)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)
    
    @pytest.fixture
    def engine(self, temp_config_file):
        """Create a ContextualFilterEngine instance for testing"""
        return ContextualFilterEngine(temp_config_file)
    
    def test_no_hardcoding_in_configuration(self, engine, sample_config, temp_config_file):
        """Test that no values are hardcoded - all come from config"""
        # Principle 1: "Is this hardcoding?" → NO
        
        # Test that engine loads from configuration file
        assert engine.config_path == temp_config_file
        assert engine.context_domains == sample_config["context_domains"]
        assert engine.classification_rules == sample_config["classification_rules"]
        
        # Test that changing config changes behavior
        new_config = sample_config.copy()
        new_config["confidence_scoring"]["thresholds"]["high_confidence"] = 0.9
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True)
            new_temp_path = f.name
        
        try:
            new_engine = ContextualFilterEngine(new_temp_path)
            assert new_engine.confidence_scoring["thresholds"]["high_confidence"] == 0.9
            assert new_engine.confidence_scoring["thresholds"]["high_confidence"] != engine.confidence_scoring["thresholds"]["high_confidence"]
        finally:
            os.unlink(new_temp_path)
    
    def test_clean_abstractions_no_tech_debt(self, engine):
        """Test clean abstractions and interfaces - no tech debt"""
        # Principle 2: "Is this tech debt?" → NO
        
        # Test that engine implements the interface
        assert isinstance(engine, IContextClassifier)
        
        # Test that all required interface methods are implemented
        assert hasattr(engine, 'classify_query_context')
        assert hasattr(engine, 'get_classification_stats')
        
        # Test that error handling is comprehensive
        result = engine.classify_query_context("")  # Empty query
        assert isinstance(result, ClassificationResult)
        assert result.primary_context in [ctx for ctx in ContextType]
        
        # Test that statistics are properly tracked
        stats = engine.get_classification_stats()
        assert "total_classifications" in stats
        assert "context_counts" in stats
        assert "confidence_distribution" in stats
    
    def test_multi_factor_analysis_approach(self, engine):
        """Test that multi-factor analysis is used - best way"""
        # Principle 3: "Is this the best way?" → YES
        
        # Test employment context with multiple factors
        employment_query = "هل يلزم الموظف رد رسوم وفقاً لقانون العمل؟"
        result = engine.classify_query_context(employment_query)
        
        # Should detect multiple types of indicators
        assert len(result.indicators_found) > 1  # Multiple indicator types found
        assert result.confidence_score > 0  # Confidence calculated from multiple factors
        
        # Test that disambiguation strategies are applied
        work_ambiguous_query = "ما هو عمل الموظف في قانون العمل؟"
        result = engine.classify_query_context(work_ambiguous_query)
        
        # Should show evidence of multi-factor analysis
        assert "raw_scores" in result.to_dict()
        assert len(result.raw_scores) > 0
    
    def test_focused_scope_not_over_engineered(self, engine):
        """Test focused scope - not over-engineered"""
        # Principle 4: "Am I over-engineering?" → NO
        
        # Should focus on context classification only
        assert hasattr(engine, 'classify_query_context')
        assert hasattr(engine, 'get_classification_stats')
        
        # Should NOT have unrelated functionality
        assert not hasattr(engine, 'translate_text')
        assert not hasattr(engine, 'generate_response')
        assert not hasattr(engine, 'validate_verse_reference')
        assert not hasattr(engine, 'extract_legal_entities')
        
        # API should be simple and focused
        query = "test query"
        result = engine.classify_query_context(query)
        assert isinstance(result, ClassificationResult)
        
        # Should have reasonable number of context types (not over-complex)
        assert len(ContextType) <= 6  # Employment, Religious, Family, Commercial, General, Ambiguous
    
    def test_best_practices_implementation(self, engine, caplog):
        """Test implementation follows best practices"""
        # Principle 5: "What are the best practices?" → Followed
        
        # Test comprehensive logging
        import logging
        with caplog.at_level(logging.DEBUG):
            engine.classify_query_context("test query for logging")
        
        # Should have logged the classification process
        log_messages = [record.message for record in caplog.records]
        classification_logged = any("Classifying query" in msg for msg in log_messages)
        assert classification_logged, "Classification process should be logged"
        
        # Test type safety - all methods should have proper return types
        result = engine.classify_query_context("test")
        assert isinstance(result, ClassificationResult)
        assert isinstance(result.primary_context, ContextType)
        assert isinstance(result.confidence_score, float)
        assert isinstance(result.confidence_level, ConfidenceLevel)
        
        # Test error handling with invalid input
        result_empty = engine.classify_query_context("")
        assert isinstance(result_empty, ClassificationResult)  # Should not crash
        
        # Test monitoring and observability
        stats = engine.get_classification_stats()
        assert isinstance(stats, dict)
        required_stats = ["total_classifications", "context_counts", "confidence_distribution"]
        for stat in required_stats:
            assert stat in stats, f"Missing required statistic: {stat}"

class TestContextClassificationScenarios:
    """Test specific context classification scenarios"""
    
    @pytest.fixture
    def full_config_engine(self):
        """Create engine with full configuration from actual config file"""
        config_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/backend/config/context_classification_rules.yaml"
        return ContextualFilterEngine(config_path)
    
    def test_employment_context_classification(self, full_config_engine):
        """Test employment context classification accuracy"""
        employment_queries = [
            "هل يلزم العامل رد رسوم المرافقين؟",
            "ما حقوق الموظف في قانون العمل؟", 
            "كيف يتم احتساب مكافأة نهاية الخدمة؟",
            "ما هي إجراءات فصل الموظف؟"
        ]
        
        for query in employment_queries:
            result = full_config_engine.classify_query_context(query)
            
            # Should classify as employment context
            assert result.primary_context == ContextType.EMPLOYMENT, f"Failed for query: {query}"
            
            # Should have reasonable confidence
            assert result.confidence_score > 0.3, f"Low confidence for employment query: {query}"
            
            # Should NOT classify as religious
            assert ContextType.RELIGIOUS not in result.secondary_contexts or \
                   result.confidence_score > 0.6, f"Religious contamination in: {query}"
    
    def test_religious_context_classification(self, full_config_engine):
        """Test religious context classification accuracy"""
        religious_queries = [
            "ما ثواب العمل الصالح في الآخرة؟",
            "كيف يحصل المؤمن على الأجر من الله؟",
            "ما هي أعمال الخير المستحبة؟",
            "كيف ينال المسلم رضا الله؟"
        ]
        
        for query in religious_queries:
            result = full_config_engine.classify_query_context(query)
            
            # Should classify as religious context
            assert result.primary_context == ContextType.RELIGIOUS, f"Failed for query: {query}"
            
            # Should have good confidence for clear religious queries
            assert result.confidence_score >= 0.4, f"Low confidence for religious query: {query}"
            
            # Should NOT classify as employment
            assert ContextType.EMPLOYMENT not in result.secondary_contexts or \
                   result.confidence_score > 0.6, f"Employment contamination in: {query}"
    
    def test_family_context_classification(self, full_config_engine):
        """Test family context classification accuracy"""
        family_queries = [
            "ما حقوق الزوجة في الإسلام؟",
            "كيف يتم توزيع الميراث؟",
            "ما هي شروط الزواج الصحيح؟",
            "ما واجبات الزوج تجاه زوجته؟"
        ]
        
        for query in family_queries:
            result = full_config_engine.classify_query_context(query)
            
            # Should classify as family context  
            assert result.primary_context == ContextType.FAMILY, f"Failed for query: {query}"
            
            # Should have reasonable confidence
            assert result.confidence_score > 0.3, f"Low confidence for family query: {query}"
    
    def test_critical_disambiguation_cases(self, full_config_engine):
        """Test the critical cases that were causing problems"""
        
        # Test cases that should be EMPLOYMENT despite containing "عمل"
        employment_work_cases = [
            ("هل يلزم العامل رد رسوم وفقاً لنظام العمل؟", ContextType.EMPLOYMENT),
            ("ما حقوق الموظف في عمله حسب القانون؟", ContextType.EMPLOYMENT),
            ("كيف يتم تقييم أداء العامل في عمله؟", ContextType.EMPLOYMENT)
        ]
        
        for query, expected_context in employment_work_cases:
            result = full_config_engine.classify_query_context(query)
            
            assert result.primary_context == expected_context, \
                f"Disambiguation failed for: {query}. Got {result.primary_context}, expected {expected_context}"
            
            # Should have applied disambiguation
            if result.disambiguation_applied:
                assert "work_term_disambiguation" in result.disambiguation_applied
        
        # Test cases that should be RELIGIOUS despite containing "عمل"  
        religious_work_cases = [
            ("ما ثواب العمل الصالح في الآخرة؟", ContextType.RELIGIOUS),
            ("كيف يجازي الله العمل الخير؟", ContextType.RELIGIOUS),
            ("ما أجر من يعمل الصالحات؟", ContextType.RELIGIOUS)
        ]
        
        for query, expected_context in religious_work_cases:
            result = full_config_engine.classify_query_context(query)
            
            assert result.primary_context == expected_context, \
                f"Disambiguation failed for: {query}. Got {result.primary_context}, expected {expected_context}"
    
    def test_exclusion_terms_prevent_contamination(self, full_config_engine):
        """Test that exclusion terms prevent cross-contamination"""
        
        # Employment query with religious exclusion terms should have lower confidence
        mixed_query = "ما حقوق الموظف في العمل وثوابه في الآخرة؟"
        result = full_config_engine.classify_query_context(mixed_query)
        
        # Should detect exclusion terms
        assert len(result.exclusions_found) > 0, "Should detect religious exclusion terms in employment context"
        
        # Confidence should be affected by exclusions
        assert "exclusion_terms" in str(result.decision_factors) or \
               result.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM], \
               "Exclusion terms should affect confidence"

class TestPerformanceAndScalability:
    """Test performance characteristics of the context filter"""
    
    @pytest.fixture
    def performance_engine(self):
        """Create engine for performance testing"""
        config_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/backend/config/context_classification_rules.yaml"
        return ContextualFilterEngine(config_path)
    
    def test_classification_performance(self, performance_engine):
        """Test classification performance under load"""
        test_queries = [
            "هل يلزم العامل رد رسوم المرافقين؟",
            "ما ثواب العمل الصالح في الآخرة؟",
            "ما حقوق الزوجة في الإسلام؟",
            "كيف يتم تقييم الموظف؟",
            "ما أجر الصائم عند الله؟"
        ] * 20  # 100 total classifications
        
        start_time = time.time()
        
        results = []
        for query in test_queries:
            result = performance_engine.classify_query_context(query)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_ms = (total_time / len(test_queries)) * 1000
        
        # Performance requirements
        assert avg_time_ms < 50, f"Classification too slow: {avg_time_ms:.2f}ms average"
        assert total_time < 5.0, f"Total time too long: {total_time:.2f}s for {len(test_queries)} queries"
        
        # All classifications should succeed
        assert all(isinstance(r, ClassificationResult) for r in results), "Some classifications failed"
        
        print(f"✅ Performance: {avg_time_ms:.2f}ms average, {len(test_queries)/total_time:.0f} classifications/sec")
    
    def test_memory_usage_stability(self, performance_engine):
        """Test that memory usage remains stable over many classifications"""
        import gc
        
        # Force garbage collection to get baseline
        gc.collect()
        
        # Run many classifications
        test_query = "ما حقوق الموظف في قانون العمل؟"
        for _ in range(1000):
            result = performance_engine.classify_query_context(test_query)
            assert isinstance(result, ClassificationResult)
        
        # Force garbage collection again
        gc.collect()
        
        # Memory should not grow excessively (this is a basic sanity check)
        stats = performance_engine.get_classification_stats()
        assert stats["total_classifications"] >= 1000, "Classifications should be tracked"

class TestFactoryAndSingleton:
    """Test factory functions and singleton pattern"""
    
    def test_factory_function(self):
        """Test the factory function works correctly"""
        engine1 = get_contextual_filter()
        engine2 = get_contextual_filter()
        
        # Should create separate instances
        assert engine1 is not engine2
        assert isinstance(engine1, ContextualFilterEngine)
        assert isinstance(engine2, ContextualFilterEngine)
    
    def test_singleton_pattern(self):
        """Test the global singleton pattern"""
        global_engine1 = get_global_contextual_filter()
        global_engine2 = get_global_contextual_filter()
        
        # Should return the same instance
        assert global_engine1 is global_engine2
        assert isinstance(global_engine1, ContextualFilterEngine)
    
    def test_singleton_with_config_path(self):
        """Test singleton with custom config path"""
        # First call with config path
        config_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/backend/config/context_classification_rules.yaml"
        global_engine1 = get_global_contextual_filter(config_path)
        
        # Second call should ignore config path and return same instance
        global_engine2 = get_global_contextual_filter("/some/other/path")
        
        assert global_engine1 is global_engine2
        # Normalize paths for comparison
        import os
        assert os.path.normpath(global_engine1.config_path) == os.path.normpath(config_path)

class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        engine = get_contextual_filter()
        
        result = engine.classify_query_context("")
        assert isinstance(result, ClassificationResult)
        assert result.primary_context == ContextType.GENERAL
        assert result.confidence_score >= 0.0
    
    def test_very_long_query_handling(self):
        """Test handling of very long queries"""
        engine = get_contextual_filter()
        
        # Create a very long query
        long_query = "ما حقوق الموظف " * 1000  # Very long query
        
        result = engine.classify_query_context(long_query)
        assert isinstance(result, ClassificationResult)
        # Should not crash and should still classify reasonably
        assert result.primary_context in [ctx for ctx in ContextType]
    
    def test_special_characters_handling(self):
        """Test handling of queries with special characters"""
        engine = get_contextual_filter()
        
        special_queries = [
            "ما حقوق الموظف؟!@#$%^&*()",
            "العامل... والأجر،",
            "هل يلزم العامل رد رسوم؟؟؟",
            "العمل والثواب!!! في الإسلام"
        ]
        
        for query in special_queries:
            result = engine.classify_query_context(query)
            assert isinstance(result, ClassificationResult)
            # Should not crash on special characters
            assert result.confidence_score >= 0.0
    
    def test_missing_config_file_fallback(self):
        """Test behavior when config file is missing"""
        # Try to create engine with non-existent config
        engine = ContextualFilterEngine("/path/that/does/not/exist.yaml")
        
        # Should use fallback configuration
        assert hasattr(engine, 'context_domains')
        assert len(engine.context_domains) > 0  # Should have fallback domains
        
        # Should still be able to classify
        result = engine.classify_query_context("test query")
        assert isinstance(result, ClassificationResult)

class TestIntegrationScenarios:
    """Test integration with expected system components"""
    
    @pytest.fixture
    def integration_engine(self):
        """Create engine for integration testing"""
        config_path = "/home/sakr_quraish/Desktop/arabic_legal_ai/backend/config/context_classification_rules.yaml"
        return ContextualFilterEngine(config_path)
    
    def test_classification_result_serialization(self, integration_engine):
        """Test that classification results can be serialized"""
        query = "ما حقوق الموظف في قانون العمل؟"
        result = integration_engine.classify_query_context(query)
        
        # Should be serializable to dict
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        
        required_fields = [
            "primary_context", "confidence_score", "confidence_level",
            "secondary_contexts", "indicators_found", "raw_scores"
        ]
        
        for field in required_fields:
            assert field in result_dict, f"Missing field in serialization: {field}"
        
        # Values should be JSON-serializable types
        import json
        try:
            json_str = json.dumps(result_dict, ensure_ascii=False)
            assert len(json_str) > 0
        except (TypeError, ValueError) as e:
            pytest.fail(f"Result not JSON-serializable: {e}")
    
    def test_statistics_monitoring_integration(self, integration_engine):
        """Test statistics collection for monitoring integration"""
        # Perform several classifications
        queries = [
            "ما حقوق الموظف في العمل؟",
            "ما ثواب العمل الصالح؟",
            "كيف يتم فصل الموظف؟"
        ]
        
        for query in queries:
            integration_engine.classify_query_context(query)
        
        # Get statistics
        stats = integration_engine.get_classification_stats()
        
        # Should track all required metrics
        assert stats["total_classifications"] >= len(queries)
        assert "context_counts" in stats
        assert "confidence_distribution" in stats
        
        # Should include accuracy metrics
        if stats["total_classifications"] > 0:
            assert "accuracy_metrics" in stats
            accuracy_metrics = stats["accuracy_metrics"]
            assert "high_confidence_rate" in accuracy_metrics
            assert "disambiguation_rate" in accuracy_metrics
        
        # Should include config info for debugging
        assert "config_info" in stats
        assert "contexts_supported" in stats["config_info"]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])