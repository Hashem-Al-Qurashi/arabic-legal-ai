#!/usr/bin/env python3
"""
Test Quranic Integration in the Chat System
Direct test to verify the fixed semantic search is working
"""

import asyncio
import logging
from app.storage.quranic_foundation_store import QuranicFoundationStore
from app.core.semantic_concepts import LegalConcept, ConceptType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_quranic_integration():
    """Test the Quranic integration with employment query"""
    
    logger.info("🧪 Starting Quranic integration test...")
    
    try:
        # Initialize the Quranic store
        logger.info("📚 Initializing Quranic Foundation Store...")
        quranic_store = QuranicFoundationStore()
        await quranic_store.initialize()
        
        # Check health
        health = await quranic_store.health_check()
        logger.info(f"🏥 Health check: {health}")
        
        if health:
            stats = await quranic_store.get_stats()
            logger.info(f"📊 Database stats: {stats.total_chunks} foundations available")
        
        # Create test concepts for employment query
        employment_query = "موظف سعودي يعمل في شركة خاصة منذ 5 سنوات، تم فصله فجأة بدون سبب واضح ولم تدفع له الشركة مستحقاته النهائية"
        
        logger.info(f"🎯 Testing with employment query: {employment_query[:50]}...")
        
        # Create basic legal concepts (same as fallback method)
        concepts = [
            LegalConcept(
                concept_id="basic_فصل",
                primary_concept="justice",
                concept_type=ConceptType.JUSTICE_CONCEPT,
                semantic_fields=["general_law"],
                confidence_score=0.8,
                context_indicators=["فصل"],
                cultural_context="saudi_legal"
            ),
            LegalConcept(
                concept_id="basic_موظف",
                primary_concept="rights",
                concept_type=ConceptType.MORAL_PRINCIPLE,
                semantic_fields=["general_law"],
                confidence_score=0.8,
                context_indicators=["موظف"],
                cultural_context="saudi_legal"
            ),
            LegalConcept(
                concept_id="basic_employment_dispute",
                primary_concept="justice",
                concept_type=ConceptType.JUSTICE_CONCEPT,
                semantic_fields=["general_law"],
                confidence_score=0.9,
                context_indicators=["فصل", "موظف", "مستحقات"],
                cultural_context="saudi_legal"
            )
        ]
        
        logger.info(f"🔧 Created {len(concepts)} test concepts")
        for i, concept in enumerate(concepts):
            logger.info(f"  {i+1}. {concept.primary_concept} ({concept.concept_id})")
        
        # Test the semantic search method
        logger.info("🔍 Testing semantic_search_foundations method...")
        quranic_context = {"domain": "legal", "integration": True, "query": employment_query}
        
        results = await quranic_store.semantic_search_foundations(
            concepts, quranic_context, limit=5
        )
        
        logger.info(f"✅ Search returned {len(results)} results")
        
        if results:
            logger.info("🕌 Found Quranic foundations:")
            for i, result in enumerate(results):
                metadata = result.chunk.metadata if hasattr(result, 'chunk') else result.metadata
                verse_ref = metadata.get('verse_reference', 'غير محدد')
                principle = metadata.get('legal_principle', 'غير محدد')
                confidence = result.similarity_score if hasattr(result, 'similarity_score') else 0.0
                
                logger.info(f"  {i+1}. {verse_ref} - {principle[:100]}... (confidence: {confidence:.3f})")
        else:
            logger.warning("❌ No Quranic foundations returned - this is the problem!")
            
            # Debug: Try direct database search
            logger.info("🔧 DEBUG: Testing direct database search...")
            try:
                search_terms = ["عدالة", "حقوق", "عمل", "أجر"]
                for term in search_terms:
                    results = await quranic_store._search_by_islamic_concepts([term], employment_query, 3)
                    logger.info(f"  Direct search for '{term}': {len(results)} results")
                    if results:
                        break
            except Exception as e:
                logger.error(f"  Direct search failed: {e}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_quranic_integration())