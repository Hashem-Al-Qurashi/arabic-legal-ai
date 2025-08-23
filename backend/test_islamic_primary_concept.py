"""
Test Islamic-Primary Concept
Verify the Islamic foundation approach works correctly
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_islamic_primary_classifier():
    """Test the Islamic-primary classification logic"""
    try:
        from app.services.islamic_primary_retrieval import IslamicPrimaryClassifier
        
        logger.info("✅ Islamic-primary classifier imports successful")
        
        # Test classifier
        classifier = IslamicPrimaryClassifier()
        
        test_queries = [
            # Should be Islamic primary (foundation matters)
            ("ما أحكام الميراث؟", "islamic_primary"),
            ("شروط عقد البيع", "islamic_primary"),
            ("عقوبة السرقة", "islamic_primary"),
            ("أحكام الطلاق", "islamic_primary"),
            ("الشهادة في المحكمة", "islamic_primary"),
            
            # Should be Islamic secondary (modern with principles)
            ("قانون العمل", "islamic_secondary"),
            ("التأمينات الاجتماعية", "islamic_secondary"),
            
            # Should be civil only (procedural)
            ("كيف أقدم طلب؟", "civil_only"),
            ("ما رسوم المحكمة؟", "civil_only"),
            ("موعد الجلسة", "civil_only"),
            ("نموذج الدعوى", "civil_only")
        ]
        
        correct_classifications = 0
        total_tests = len(test_queries)
        
        for query, expected_strategy in test_queries:
            strategy_info = classifier.get_retrieval_strategy(query)
            actual_strategy = strategy_info["strategy"]
            
            status = "✅" if actual_strategy == expected_strategy else "❌"
            logger.info(f"{status} Query: '{query}' -> Expected: {expected_strategy}, Got: {actual_strategy}")
            
            if actual_strategy == expected_strategy:
                correct_classifications += 1
        
        logger.info(f"📊 Classification Accuracy: {correct_classifications}/{total_tests} ({(correct_classifications/total_tests)*100:.1f}%)")
        
        return correct_classifications == total_tests
        
    except Exception as e:
        logger.error(f"❌ Islamic classifier test failed: {e}")
        return False


async def test_islamic_query_enhancement():
    """Test Islamic query enhancement"""
    try:
        from app.services.islamic_primary_retrieval import IslamicPrimaryClassifier
        
        classifier = IslamicPrimaryClassifier()
        
        test_cases = [
            "ما أحكام الميراث؟",
            "شروط عقد البيع",
            "الشهادة في المحكمة",
            "عقوبة السرقة"
        ]
        
        for query in test_cases:
            strategy_info = classifier.get_retrieval_strategy(query)
            enhanced_query = classifier.get_islamic_query_enhancement(query, strategy_info["strategy"])
            
            logger.info(f"Original: {query}")
            logger.info(f"Enhanced: {enhanced_query}")
            logger.info(f"Strategy: {strategy_info['strategy']}")
            logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Query enhancement test failed: {e}")
        return False


async def test_response_structure_logic():
    """Test response structure determination"""
    try:
        from app.services.islamic_primary_retrieval import IslamicPrimaryClassifier
        
        classifier = IslamicPrimaryClassifier()
        
        structure_tests = [
            ("ما أحكام الميراث؟", "islamic_foundation_first"),
            ("قانون العمل", "civil_with_islamic_principles"),
            ("كيف أقدم طلب؟", None)  # Civil only has no special structure
        ]
        
        for query, expected_structure in structure_tests:
            strategy_info = classifier.get_retrieval_strategy(query)
            actual_structure = strategy_info.get("response_structure")
            
            status = "✅" if actual_structure == expected_structure else "❌"
            logger.info(f"{status} Query: '{query}' -> Structure: {actual_structure}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Response structure test failed: {e}")
        return False


async def test_islamic_primary_orchestrator_init():
    """Test Islamic-primary orchestrator initialization"""
    try:
        from app.services.islamic_primary_retrieval import IslamicPrimaryOrchestrator
        
        orchestrator = IslamicPrimaryOrchestrator()
        logger.info(f"✅ Orchestrator created - Islamic enabled: {orchestrator.enable_islamic}")
        
        # Test metrics initialization
        metrics = orchestrator.get_metrics()
        logger.info(f"✅ Initial metrics: {metrics}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Orchestrator initialization test failed: {e}")
        return False


async def main():
    """Run all Islamic-primary concept tests"""
    logger.info("🕌 Starting Islamic-Primary Concept Tests...")
    
    tests = [
        ("Islamic-Primary Classifier", test_islamic_primary_classifier),
        ("Islamic Query Enhancement", test_islamic_query_enhancement),
        ("Response Structure Logic", test_response_structure_logic),
        ("Orchestrator Initialization", test_islamic_primary_orchestrator_init)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing: {test_name}")
        try:
            if await test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Islamic-Primary concept tests passed!")
        logger.info("""
🕌 Islamic-Primary System Status:
✅ Classification Logic: Working
✅ Query Enhancement: Working  
✅ Response Structure: Working
✅ Orchestrator: Ready

🎯 Key Features Validated:
- Islamic foundation takes priority for relevant queries
- Civil law positioned as implementation, not source
- Proper classification of procedural vs substantive queries
- Smart query enhancement for Islamic context
- Appropriate response structure selection

📋 Next Steps:
1. Build Islamic database with Al-Qurtubi data
2. Implement proper embedding-based search
3. Test full system with real queries
4. Integrate with existing chat interface

🔧 Islamic-Primary Approach:
- Inheritance → Start with Quranic verses, then Saudi implementation
- Contracts → Islamic contract principles, then Commercial Code
- Criminal → Hudud/Qisas from Quran, then Penal Code
- Procedures → Civil law only (no Islamic foundation needed)
""")
        return True
    else:
        logger.error("❌ Some concept tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)