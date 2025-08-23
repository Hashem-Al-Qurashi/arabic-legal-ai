#!/usr/bin/env python3
"""
Test specific employment query
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

import asyncio
from app.api.enhanced_chat import process_enhanced_chat_query, initialize_enhanced_chat

async def test_employment_query():
    print("🕌 Testing Employment Rights Query")
    print("=" * 60)
    
    try:
        # Initialize the enhanced chat system
        print("🔄 Initializing enhanced chat system...")
        success = await initialize_enhanced_chat()
        
        if not success:
            print("❌ Failed to initialize enhanced chat system")
            return
        
        print("✅ Enhanced chat system initialized successfully!")
        
        # Your specific employment query
        query = "موظف سعودي يعمل في شركة خاصة منذ 5 سنوات، تم فصله فجأة بدون سبب واضح ولم تدفع له الشركة مستحقاته النهائية. ما هي حقوقه في نظام العمل السعودي"
        
        print(f"\n🧪 Testing employment rights query...")
        print(f"Query: {query[:100]}...")
        print("-" * 60)
        
        result = await process_enhanced_chat_query(query)
        
        print(f"📋 Response Type: {result.get('response_type', 'unknown')}")
        print(f"🎯 Strategy: {result.get('strategy_used', 'N/A')}")
        print(f"📚 Quranic Sources: {result.get('quranic_sources_count', 0)}")
        print(f"📖 Civil Sources: {result.get('civil_sources_count', 0)}")
        print(f"🎨 Cultural Appropriateness: {result.get('cultural_appropriateness', 0):.2f}")
        print(f"⚡ Processing Time: {result.get('processing_time_ms', 0):.1f}ms")
        
        if result.get('quranic_sources_count', 0) > 0:
            print("\n🕌 Found Quranic foundations!")
            quranic_sources = result.get('enhanced_sources', {}).get('quranic_foundations', [])
            for i, source in enumerate(quranic_sources[:3], 1):
                print(f"  {i}. {source.get('title', 'N/A')}")
                print(f"     Relevance: {source.get('relevance_score', 0):.2f}")
        else:
            print("\n❌ No Quranic sources found")
        
        # Show preview of response
        answer = result.get('answer', '')
        if answer:
            print(f"\n💬 Answer Preview: {answer[:100]}...")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_employment_query())