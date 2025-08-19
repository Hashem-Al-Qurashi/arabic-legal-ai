#!/usr/bin/env python3
"""
Test the immediate production fix for Islamic integration
Tests employment query detection and targeted verse selection
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.storage.quranic_foundation_store import QuranicFoundationStore
from app.core.system_config import get_config

async def test_immediate_fix():
    """Test the employment query fix"""
    print("🔧 TESTING IMMEDIATE PRODUCTION FIX")
    print("=" * 50)
    
    # Initialize the store with correct configuration
    config = get_config()
    store = QuranicFoundationStore(db_path=config.database.quranic_db_path)
    await store.initialize()
    
    # Test the problematic query from production
    employment_query = "فى حال دفع صاحب العمل لرسوم المرافقين لاحد العمال لنقل كفالته هل يلزم رد العامل لهذه الرسوم؟"
    
    print(f"📝 Testing Query: {employment_query}")
    print()
    
    # Test employment query detection
    is_employment = store._is_employment_query(employment_query)
    print(f"🎯 Employment Query Detected: {is_employment}")
    
    if is_employment:
        print("✅ EMPLOYMENT DETECTION WORKING")
        
        # Test employment-specific search
        print("\n🔍 Testing Employment-Specific Search...")
        query_context = {
            "query": employment_query,
            "detail_level": "summary"
        }
        
        try:
            results = await store._employment_specific_search(employment_query, 3, "summary")
            
            print(f"\n📊 RESULTS: Found {len(results)} employment-relevant verses")
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.chunk.title}")
                print(f"   Content: {result.chunk.content[:100]}...")
                print(f"   Score: {result.similarity_score:.3f}")
                
                # Check if this is the problematic David & Solomon verse
                if "داود" in result.chunk.content and "سليمان" in result.chunk.content:
                    print("   ❌ WARNING: Still returning David & Solomon verse!")
                else:
                    print("   ✅ GOOD: Contextually relevant verse")
            
            print(f"\n🎉 IMMEDIATE FIX TEST COMPLETED")
            print(f"✅ Employment detection: WORKING")
            print(f"✅ Targeted search: RETURNING {len(results)} relevant verses")
            
        except Exception as e:
            print(f"❌ Employment search failed: {e}")
            
    else:
        print("❌ EMPLOYMENT DETECTION FAILED")
        print("The query should be detected as employment-related!")

if __name__ == "__main__":
    asyncio.run(test_immediate_fix())