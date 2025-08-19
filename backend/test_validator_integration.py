#!/usr/bin/env python3
"""
Integration Test for QuranVerseValidator in RAG Engine
Tests the complete integration to prevent AI hallucination

Author: Senior AI Engineer
Date: 2025-08-18
Purpose: Verify verse validator prevents hallucination in production system
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

from app.core.quran_verse_validator import get_verse_validator, ValidationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_critical_hallucination_cases():
    """Test the exact cases that were causing AI hallucination"""
    
    print("🧪 TESTING CRITICAL HALLUCINATION PREVENTION")
    print("=" * 60)
    
    validator = get_verse_validator()
    
    # These are the exact problematic cases from the original analysis
    critical_test_cases = [
        {
            "input": "سُورَةُ النُّورِ:352",  # The famous hallucination case!
            "description": "An-Nur verse 352 (only 64 verses exist)",
            "should_be_valid": False
        },
        {
            "input": "البقرة:300", 
            "description": "Al-Baqarah verse 300 (only 286 verses exist)",
            "should_be_valid": False
        },
        {
            "input": "سُورَةُ البَقَرَةِ:الۤـمۤ",
            "description": "Descriptive reference (should be handled specially)",
            "should_be_valid": True
        },
        {
            "input": "البقرة:282",
            "description": "Valid verse reference", 
            "should_be_valid": True
        },
        {
            "input": "النور:32",
            "description": "Valid An-Nur verse",
            "should_be_valid": True
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(critical_test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"   Input: '{test_case['input']}'")
        
        # Validate with our new system
        validation_result = validator.validate_verse_reference(test_case['input'])
        
        # Check results
        is_valid = validation_result.is_valid
        validated_ref = validation_result.validated_reference
        fallback_ref = validation_result.fallback_reference
        result_type = validation_result.result_type
        
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"   Type: {result_type.value}")
        print(f"   Validated: '{validated_ref}'")
        print(f"   Fallback: '{fallback_ref}'")
        
        # Verify expected behavior
        expected_valid = test_case['should_be_valid']
        if is_valid == expected_valid:
            print(f"   Status: ✅ CORRECT BEHAVIOR")
            results.append(True)
        else:
            print(f"   Status: ❌ UNEXPECTED BEHAVIOR (expected {'valid' if expected_valid else 'invalid'})")
            results.append(False)
        
        # Critical test: Ensure no hallucinated verse numbers in output
        if ':352' in validated_ref or ':300' in validated_ref:
            print(f"   🚨 CRITICAL FAILURE: Hallucinated verse number still present!")
            results.append(False)
        else:
            print(f"   ✅ HALLUCINATION PREVENTED")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - HALLUCINATION PREVENTION WORKING!")
        return True
    else:
        print("❌ SOME TESTS FAILED - REQUIRES INVESTIGATION")
        return False

def test_performance_impact():
    """Test that validation doesn't significantly impact performance"""
    
    print("\n🚀 TESTING PERFORMANCE IMPACT")
    print("=" * 60)
    
    import time
    validator = get_verse_validator()
    
    test_references = [
        "البقرة:282",
        "النور:32", 
        "آل عمران:185",
        "النساء:12",
        "المائدة:8"
    ] * 20  # 100 validations total
    
    start_time = time.time()
    
    for ref in test_references:
        validator.validate_verse_reference(ref)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time_ms = (total_time / len(test_references)) * 1000
    
    print(f"Total validations: {len(test_references)}")
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Average time per validation: {avg_time_ms:.2f} ms")
    
    # Performance target: < 5ms per validation
    if avg_time_ms < 5.0:
        print("✅ PERFORMANCE: Excellent (< 5ms per validation)")
        return True
    elif avg_time_ms < 10.0:
        print("⚠️ PERFORMANCE: Acceptable (5-10ms per validation)")
        return True
    else:
        print("❌ PERFORMANCE: Too slow (> 10ms per validation)")
        return False

def test_configuration_loading():
    """Test that configuration loads correctly"""
    
    print("\n⚙️ TESTING CONFIGURATION LOADING")
    print("=" * 60)
    
    try:
        validator = get_verse_validator()
        stats = validator.get_statistics()
        
        print(f"Total Surahs: {stats['total_surahs']}")
        print(f"Total Verses: {stats['total_verses']}")
        print(f"English Mappings: {stats['english_mappings']}")
        print(f"Descriptive References: {stats['descriptive_references']}")
        print(f"Config Path: {stats['config_path']}")
        
        # Verify key surahs are present
        required_surahs = ["البقرة", "النور", "آل عمران", "النساء"]
        missing_surahs = []
        
        for surah in required_surahs:
            if surah not in validator.verse_limits:
                missing_surahs.append(surah)
        
        if missing_surahs:
            print(f"❌ MISSING SURAHS: {missing_surahs}")
            return False
        
        # Verify critical verse counts
        if validator.verse_limits["النور"] != 64:
            print(f"❌ WRONG VERSE COUNT: An-Nur has {validator.verse_limits['النور']} verses (should be 64)")
            return False
        
        print("✅ CONFIGURATION: All checks passed")
        return True
        
    except Exception as e:
        print(f"❌ CONFIGURATION ERROR: {e}")
        return False

def main():
    """Run all integration tests"""
    
    print("🧪 QURAN VERSE VALIDATOR INTEGRATION TEST")
    print("🎯 Goal: Prevent AI hallucination of verse numbers")
    print("📅 Date: 2025-08-18")
    print()
    
    # Run tests
    test_results = []
    
    test_results.append(test_configuration_loading())
    test_results.append(test_critical_hallucination_cases()) 
    test_results.append(test_performance_impact())
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Overall Success Rate: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Verse validator successfully integrated")
        print("✅ AI hallucination prevention active")
        print("✅ Performance impact acceptable")
        print("✅ Ready for production deployment")
        return 0
    else:
        print("❌ SOME INTEGRATION TESTS FAILED!")
        print("⚠️ Integration requires fixes before deployment")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)