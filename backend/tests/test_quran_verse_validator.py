"""
Comprehensive Test Suite for QuranVerseValidator
Testing all edge cases and principles compliance

Author: Senior AI Engineer  
Date: 2025-08-18
Coverage: Unit tests, integration tests, edge cases, performance tests
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core.quran_verse_validator import (
    QuranVerseValidator,
    ValidationResult,
    VerseValidationResponse,
    create_verse_validator,
    get_verse_validator,
    IVerseValidator
)


class TestQuranVerseValidator:
    """Test suite for QuranVerseValidator class"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            "verse_limits": {
                "البقرة": 286,
                "آل عمران": 200,
                "النور": 64,  # Key test case - not 352!
                "الإخلاص": 4
            },
            "english_to_arabic": {
                "Al-Baqarah": "البقرة",
                "Al-Imran": "آل عمران", 
                "An-Nur": "النور",
                "Al-Ikhlas": "الإخلاص"
            },
            "descriptive_references": [
                "الۤـمۤ",
                "الۤمۤص",
                "الۤر"
            ],
            "validation_config": {
                "strict_mode": True,
                "allow_descriptive": True,
                "default_fallback": "في القرآن الكريم",
                "log_validation_failures": True,
                "scholar_approval_required": True
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(sample_config, f, allow_unicode=True)
            return f.name
    
    @pytest.fixture
    def validator(self, temp_config_file):
        """Create validator instance with test config"""
        return QuranVerseValidator(temp_config_file)
    
    # Test Principle 1: No Hardcoding
    def test_no_hardcoding_in_configuration(self, validator):
        """Test that no values are hardcoded - all come from config"""
        assert validator.verse_limits["البقرة"] == 286
        assert validator.verse_limits["النور"] == 64  # Critical: not hardcoded as 352!
        assert "في القرآن الكريم" in validator.validation_config["default_fallback"]
    
    def test_configurable_fallback_text(self, sample_config):
        """Test that fallback text is configurable, not hardcoded"""
        # Modify config
        sample_config["validation_config"]["default_fallback"] = "مرجع قرآني"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(sample_config, f, allow_unicode=True)
            validator = QuranVerseValidator(f.name)
        
        result = validator.validate_verse_reference("invalid:999")
        assert result.fallback_reference == "مرجع قرآني"
    
    # Test Principle 2: No Tech Debt
    def test_clean_error_handling(self, validator):
        """Test comprehensive error handling without tech debt"""
        # Malformed reference
        result = validator.validate_verse_reference("malformed_reference")
        assert not result.is_valid
        assert result.result_type == ValidationResult.MALFORMED_REFERENCE
        assert result.error_message is not None
        
        # Invalid surah  
        result = validator.validate_verse_reference("nonexistent_surah:1")
        assert not result.is_valid
        assert result.result_type == ValidationResult.INVALID_SURAH
        
        # Invalid verse number
        result = validator.validate_verse_reference("البقرة:999")
        assert not result.is_valid
        assert result.result_type == ValidationResult.INVALID_VERSE_NUMBER
    
    def test_proper_abstractions_with_interface(self):
        """Test that validator implements proper interface (no tech debt)"""
        validator = create_verse_validator()
        assert isinstance(validator, IVerseValidator)
        
        # Interface methods exist
        assert hasattr(validator, 'validate_verse_reference')
        assert hasattr(validator, 'is_verse_number_valid')
    
    # Test Principle 3: Best Way
    def test_configuration_driven_design(self, temp_config_file):
        """Test that design is configuration-driven (best way)"""
        validator = QuranVerseValidator(temp_config_file)
        
        # All data comes from config
        assert len(validator.verse_limits) == 4  # From test config
        assert len(validator.english_to_arabic) == 4
        assert len(validator.descriptive_references) == 3
    
    def test_performance_with_caching(self, validator):
        """Test caching improves performance (best way)"""
        # First call - cache miss
        validator._normalize_surah_name("البقرة")
        assert "البقرة" in validator._surah_name_cache
        
        # Second call - cache hit (should be faster)
        result = validator._normalize_surah_name("البقرة")
        assert result == "البقرة"
    
    # Test Principle 4: Not Over-Engineering  
    def test_focused_scope_verse_validation_only(self, validator):
        """Test validator only does verse validation (not over-engineered)"""
        # Should NOT have unrelated functionality
        assert not hasattr(validator, 'translate_text')
        assert not hasattr(validator, 'generate_response')
        assert not hasattr(validator, 'classify_context')
        
        # Should have core validation methods
        core_methods = ['validate_verse_reference', 'is_verse_number_valid', 'get_statistics']
        for method in core_methods:
            assert hasattr(validator, method), f"Missing core method: {method}"
        
        # Config attributes are acceptable for observability
        config_attrs = ['config', 'config_path', 'verse_limits', 'english_to_arabic', 
                       'descriptive_references', 'validation_config']
        for attr in config_attrs:
            assert hasattr(validator, attr), f"Missing config attribute: {attr}"
    
    def test_simple_api_design(self, validator):
        """Test API is simple and focused (not over-engineered)"""
        # Main method has simple signature
        result = validator.validate_verse_reference("البقرة:282")
        assert isinstance(result, VerseValidationResponse)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'validated_reference')
        assert hasattr(result, 'fallback_reference')
    
    # Test Principle 5: Best Practices
    def test_comprehensive_logging(self, validator, caplog):
        """Test proper logging (best practice)"""
        with caplog.at_level("DEBUG"):
            validator.validate_verse_reference("البقرة:282")
        
        assert "Validating verse reference" in caplog.text
    
    def test_type_safety_and_hints(self, validator):
        """Test type hints are used properly (best practice)"""
        result = validator.validate_verse_reference("البقرة:282")
        assert isinstance(result, VerseValidationResponse)
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.confidence_score, float)
        assert isinstance(result.result_type, ValidationResult)
    
    def test_observable_statistics(self, validator):
        """Test observability through statistics (best practice)"""
        stats = validator.get_statistics()
        
        required_stats = ['total_surahs', 'total_verses', 'descriptive_references', 
                         'english_mappings', 'cache_size', 'config_path']
        for stat in required_stats:
            assert stat in stats
        
        assert stats['total_surahs'] == 4  # From test config
        assert stats['total_verses'] == 286 + 200 + 64 + 4  # Sum of test surahs


class TestValidationScenarios:
    """Test real-world validation scenarios"""
    
    @pytest.fixture
    def validator(self, temp_config_file):
        """Create validator with full config"""
        return QuranVerseValidator(temp_config_file)
    
    @pytest.fixture
    def temp_config_file(self):
        """Full test config"""
        config = {
            "verse_limits": {"البقرة": 286, "النور": 64, "الإخلاص": 4},
            "english_to_arabic": {"Al-Baqarah": "البقرة", "An-Nur": "النور"},
            "descriptive_references": ["الۤـمۤ", "الۤر"],
            "validation_config": {
                "default_fallback": "في القرآن الكريم",
                "strict_mode": True
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
            return f.name
    
    def test_valid_verse_scenarios(self, validator):
        """Test various valid verse formats"""
        test_cases = [
            # Arabic format
            ("البقرة:282", True, "البقرة:282"),
            ("النور:32", True, "النور:32"), 
            ("الإخلاص:1", True, "الإخلاص:1"),
            
            # With prefix
            ("سورة البقرة:282", True, "البقرة:282"),
            ("سُورَةُ النور:32", True, "النور:32"),
            
            # English format  
            ("Al-Baqarah:282", True, "البقرة:282"),
            ("An-Nur:32", True, "النور:32"),
        ]
        
        for reference, should_be_valid, expected_validated in test_cases:
            result = validator.validate_verse_reference(reference)
            assert result.is_valid == should_be_valid, f"Failed for {reference}"
            if should_be_valid:
                assert result.validated_reference == expected_validated
    
    def test_invalid_verse_scenarios(self, validator):
        """Test various invalid verse formats"""
        test_cases = [
            # Invalid verse numbers (too high) - should reference specific surah
            ("البقرة:999", ValidationResult.INVALID_VERSE_NUMBER, "في البقرة"),
            ("النور:352", ValidationResult.INVALID_VERSE_NUMBER, "في النور"),  # Critical test!
            ("الإخلاص:10", ValidationResult.INVALID_VERSE_NUMBER, "في الإخلاص"),
            
            # Invalid surah names - should use default fallback
            ("nonexistent:1", ValidationResult.INVALID_SURAH, "في القرآن الكريم"),
            ("fake_surah:5", ValidationResult.INVALID_SURAH, "في القرآن الكريم"),
            
            # Malformed references - should use default fallback
            ("no_colon_here", ValidationResult.MALFORMED_REFERENCE, "في القرآن الكريم"),
            ("multiple:colons:here", ValidationResult.INVALID_SURAH, "في القرآن الكريم"),  # Parses as surah:verse
            ("", ValidationResult.MALFORMED_REFERENCE, "في القرآن الكريم"),
        ]
        
        for reference, expected_result, expected_fallback in test_cases:
            result = validator.validate_verse_reference(reference)
            assert not result.is_valid, f"Should be invalid: {reference}"
            assert result.result_type == expected_result, f"Wrong result type for {reference}"
            assert result.fallback_reference == expected_fallback, f"Wrong fallback for {reference}"
    
    def test_descriptive_reference_scenarios(self, validator):
        """Test descriptive references like الۤـمۤ"""
        test_cases = [
            ("البقرة:الۤـمۤ", True, "في البقرة"),
            ("سورة البقرة:الۤر", True, "في البقرة"),
        ]
        
        for reference, should_be_valid, expected_fallback in test_cases:
            result = validator.validate_verse_reference(reference)
            assert result.is_valid == should_be_valid
            assert result.result_type == ValidationResult.DESCRIPTIVE_REFERENCE
            assert result.fallback_reference == expected_fallback
    
    def test_critical_hallucination_prevention(self, validator):
        """Test prevention of critical AI hallucination cases"""
        # These are the exact cases that were causing problems
        problem_cases = [
            ("النور:352", False),  # An-Nur only has 64 verses, not 352!
            ("البقرة:300", False), # Al-Baqarah has 286 verses, not 300
            ("الإخلاص:10", False), # Al-Ikhlas has 4 verses, not 10
        ]
        
        for reference, should_be_valid in problem_cases:
            result = validator.validate_verse_reference(reference)
            assert result.is_valid == should_be_valid, f"CRITICAL: Failed hallucination prevention for {reference}"
            if not should_be_valid:
                assert "في القرآن الكريم" in result.fallback_reference or "في " in result.fallback_reference


class TestPerformanceAndScalability:
    """Test performance characteristics"""
    
    @pytest.fixture
    def validator(self, temp_config_file):
        return QuranVerseValidator(temp_config_file)
    
    @pytest.fixture 
    def temp_config_file(self):
        config = {
            "verse_limits": {"البقرة": 286, "النور": 64},
            "english_to_arabic": {"Al-Baqarah": "البقرة"},
            "descriptive_references": ["الۤـمۤ"],
            "validation_config": {"default_fallback": "في القرآن الكريم"}
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
            return f.name
    
    def test_caching_improves_performance(self, validator):
        """Test that caching provides performance benefit"""
        import time
        
        # First call - cache miss
        start = time.time()
        result1 = validator.validate_verse_reference("البقرة:282")
        first_call_time = time.time() - start
        
        # Second call - cache hit  
        start = time.time()
        result2 = validator.validate_verse_reference("البقرة:283")
        second_call_time = time.time() - start
        
        # Both should be valid
        assert result1.is_valid
        assert result2.is_valid
        
        # Second call should be faster (cache hit for surah normalization)
        assert second_call_time <= first_call_time * 1.1  # Allow 10% variance
    
    def test_bulk_validation_performance(self, validator):
        """Test performance with bulk validations"""
        test_references = [
            "البقرة:1", "البقرة:2", "البقرة:3", "البقرة:4", "البقرة:5",
            "النور:1", "النور:2", "النور:3", "النور:4", "النور:5"
        ]
        
        import time
        start = time.time()
        
        results = [validator.validate_verse_reference(ref) for ref in test_references]
        
        total_time = time.time() - start
        
        # All should be valid
        assert all(result.is_valid for result in results)
        
        # Should complete within reasonable time (< 1 second for 10 validations)
        assert total_time < 1.0


class TestFactoryAndSingleton:
    """Test factory and singleton patterns"""
    
    def test_factory_function(self):
        """Test factory function creates validator"""
        validator = create_verse_validator()
        assert isinstance(validator, IVerseValidator)
    
    def test_singleton_pattern(self):
        """Test singleton returns same instance"""
        validator1 = get_verse_validator()
        validator2 = get_verse_validator()
        assert validator1 is validator2  # Same instance


# Integration tests
class TestIntegrationWithExistingSystem:
    """Test integration with existing RAG system"""
    
    def test_response_object_serialization(self):
        """Test that response objects can be serialized for logging"""
        from app.core.quran_verse_validator import VerseValidationResponse, ValidationResult
        
        response = VerseValidationResponse(
            is_valid=True,
            result_type=ValidationResult.VALID,
            original_reference="البقرة:282",
            validated_reference="البقرة:282", 
            fallback_reference="البقرة:282",
            confidence_score=1.0
        )
        
        # Should serialize without error
        serialized = response.to_dict()
        assert isinstance(serialized, dict)
        assert serialized['is_valid'] is True
        assert serialized['result_type'] == 'valid'


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_quran_verse_validator.py -v
    pytest.main([__file__])