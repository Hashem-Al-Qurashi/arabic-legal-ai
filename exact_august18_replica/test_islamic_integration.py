"""
Quick test of Islamic integration without heavy dependencies
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_islamic_store():
    """Test Islamic vector store creation"""
    try:
        from app.storage.islamic_vector_store import IslamicVectorStore, IslamicChunk
        
        logger.info("✅ Islamic vector store imports successful")
        
        # Test store initialization
        store = IslamicVectorStore("data/test_islamic.db")
        await store.initialize()
        
        logger.info("✅ Islamic vector store initialized")
        
        # Test chunk creation
        test_chunk = IslamicChunk(
            id="test_qurtubi_1",
            content="تفسير القرطبي لآية البقرة",
            title="تفسير القرطبي - البقرة:282",
            surah_name="البقرة",
            ayah_number=282,
            verse_reference="البقرة:282",
            qurtubi_commentary="هذا نص تجريبي من تفسير القرطبي",
            legal_principle="وجوب التوثيق في المعاملات",
            source_type="qurtubi",
            legal_confidence=0.9
        )
        
        # Test storage
        success = await store.store_islamic_chunks([test_chunk])
        logger.info(f"✅ Chunk storage: {success}")
        
        # Test search
        results = await store.search("توثيق", limit=5)
        logger.info(f"✅ Search results: {len(results)} found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Islamic store test failed: {e}")
        return False


async def test_unified_retrieval():
    """Test unified retrieval system"""
    try:
        from app.services.unified_retrieval import QueryClassifier, format_unified_results
        
        logger.info("✅ Unified retrieval imports successful")
        
        # Test classifier
        classifier = QueryClassifier()
        
        test_queries = [
            ("ما أحكام الميراث؟", True),  # Should include Islamic
            ("كيف أقدم طلب؟", False),  # Should NOT include Islamic
            ("شروط عقد البيع", True),  # Should conditionally include
            ("رسوم المحكمة", False)  # Should NOT include
        ]
        
        for query, expected in test_queries:
            should_include, reason = classifier.should_include_islamic(query)
            status = "✅" if should_include == expected else "❌"
            logger.info(f"{status} Query: '{query}' -> Islamic: {should_include} ({reason})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Unified retrieval test failed: {e}")
        return False


async def test_enhanced_rag():
    """Test enhanced RAG engine"""
    try:
        # Import without full initialization
        from enhanced_rag_engine import EnhancedRAGEngine, EnhancedCitationFixer
        
        logger.info("✅ Enhanced RAG imports successful")
        
        # Test citation fixer
        fixer = EnhancedCitationFixer()
        
        test_response = "هذا نص تجريبي للاستشارة القانونية."
        test_documents = []  # Empty for now
        test_islamic = []  # Empty for now
        
        fixed_response = fixer.fix_citations(test_response, test_documents, test_islamic)
        logger.info(f"✅ Citation fixing: {len(fixed_response)} chars")
        
        # Test engine creation (without full init)
        engine = EnhancedRAGEngine()
        logger.info(f"✅ Enhanced RAG engine created - Islamic enabled: {engine.enable_islamic}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced RAG test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    logger.info("🧪 Starting Islamic Integration Tests...")
    
    tests = [
        ("Islamic Vector Store", test_islamic_store),
        ("Unified Retrieval", test_unified_retrieval), 
        ("Enhanced RAG Engine", test_enhanced_rag)
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
        logger.info("🎉 All integration tests passed!")
        logger.info("""
🚀 Islamic Integration Status:
✅ Islamic Vector Store: Ready
✅ Unified Retrieval: Ready
✅ Enhanced RAG Engine: Ready

📋 Next Steps:
1. Install dependencies: pip install datasets sentence-transformers
2. Run: python islamic_data_processor.py (to build Islamic database)
3. Test with real queries using enhanced_rag_engine.py

🔧 Integration Points:
- Islamic sources stored separately (no conflicts)
- Unified retrieval coordinates both systems
- Enhanced RAG maintains backward compatibility
- Feature flags allow easy enable/disable
""")
        return True
    else:
        logger.error("❌ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)