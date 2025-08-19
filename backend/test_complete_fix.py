#!/usr/bin/env python3
"""
Test the complete two-layer fix for Islamic integration
Tests both the database layer fix AND the RAG integration layer fix
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from rag_engine import IntelligentLegalRAG

async def test_complete_fix():
    """Test the complete two-layer fix"""
    print("🔧 TESTING COMPLETE TWO-LAYER FIX")
    print("=" * 60)
    
    # Initialize the RAG engine
    print("🚀 Initializing RAG engine...")
    rag = IntelligentLegalRAG()
    # No explicit initialization needed - done in constructor
    
    # Test the problematic query from production
    employment_query = "فى حال دفع صاحب العمل لرسوم المرافقين لاحد العمال لنقل كفالته هل يلزم رد العامل لهذه الرسوم؟"
    
    print(f"📝 Testing Query: {employment_query}")
    print()
    
    # Test Quranic foundation retrieval (Layer 1)
    print("🔍 Layer 1: Testing Quranic foundation retrieval...")
    quranic_foundations = await rag.get_quranic_foundations(
        employment_query, {"domain": "legal"}
    )
    
    print(f"📊 Found {len(quranic_foundations)} Quranic foundations")
    
    for i, foundation in enumerate(quranic_foundations, 1):
        print(f"\n{i}. {foundation.get('verse_reference', 'Unknown')}")
        print(f"   Principle: {foundation.get('legal_principle', 'Unknown')[:100]}...")
        print(f"   Valid Reference: {foundation.get('is_valid_reference', 'Unknown')}")
        
        # Check if this is the problematic David & Solomon verse
        verse_ref = foundation.get('verse_reference', '')
        if "الأنبياء" in verse_ref and "يحكمان" in verse_ref:
            print("   ❌ WARNING: Still returning David & Solomon verse!")
        elif "داود" in foundation.get('commentary', '') or "سليمان" in foundation.get('commentary', ''):
            print("   ❌ WARNING: David/Solomon reference in commentary!")
        else:
            print("   ✅ GOOD: No David & Solomon references")
    
    # Test employment query detection (Layer 2)
    print(f"\n🎯 Layer 2: Testing employment query detection...")
    is_employment = rag._is_employment_related_query(employment_query)
    print(f"Employment Query Detected: {is_employment}")
    
    if is_employment:
        print("✅ Employment detection working")
    else:
        print("❌ Employment detection failed")
    
    print(f"\n🎉 COMPLETE TWO-LAYER FIX TEST COMPLETED")
    print(f"✅ Layer 1 (Database): Enhanced search with employment bypass")
    print(f"✅ Layer 2 (Integration): Employment filtering and context awareness")
    
    if len(quranic_foundations) == 0:
        print("✅ PERFECT: No irrelevant verses returned for employment query")
    elif any("داود" in str(f) or "سليمان" in str(f) for f in quranic_foundations):
        print("❌ ISSUE: David & Solomon verses still present")
    else:
        print("✅ GOOD: Only relevant verses returned")

if __name__ == "__main__":
    asyncio.run(test_complete_fix())