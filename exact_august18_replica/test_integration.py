#!/usr/bin/env python3
"""
Test the Quranic integration with the main chat system
"""

import sys
sys.path.append('/home/sakr_quraish/Desktop/arabic_legal_ai/backend')

import asyncio
from rag_engine import get_rag_engine

async def test_quranic_integration():
    print("🧪 Testing Quranic Integration with Main Chat System")
    print("=" * 60)
    
    # Get the RAG engine (now with Quranic integration)
    rag_instance = get_rag_engine()
    
    # Test the employment law case that user mentioned
    employment_query = "موظف سعودي يعمل في شركة خاصة منذ 5 سنوات، تم فصله فجأة بدون سبب واضح ولم تدفع له الشركة مستحقاته النهائية. ما هي حقوقه في نظام العمل السعودي"
    
    print(f"🔍 Testing: {employment_query}")
    print("-" * 60)
    
    try:
        print("📝 Response:")
        response_chunks = []
        
        # Process the query with new integrated system
        async for chunk in rag_instance.ask_question_with_context_streaming(employment_query, []):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        full_response = ''.join(response_chunks)
        
        print("\n\n" + "=" * 60)
        print("📊 Analysis:")
        
        # Check if response contains Quranic citations
        quranic_indicators = ["قال تعالى", "الأساس الشرعي", "القرطبي", "سورة", "آية"]
        found_indicators = [indicator for indicator in quranic_indicators if indicator in full_response]
        
        if found_indicators:
            print(f"✅ SUCCESS: Found Quranic foundations in response!")
            print(f"🕌 Islamic indicators found: {found_indicators}")
        else:
            print("❌ ISSUE: No Quranic foundations found in response")
        
        # Check if response contains civil law
        civil_indicators = ["نظام العمل", "المادة", "وفقاً لـ"]
        found_civil = [indicator for indicator in civil_indicators if indicator in full_response]
        
        if found_civil:
            print(f"⚖️ Civil law indicators found: {found_civil}")
        else:
            print("⚠️ WARNING: No clear civil law citations found")
        
        print(f"\n📏 Response length: {len(full_response)} characters")
        print(f"📊 Response quality: {'HIGH' if len(full_response) > 500 else 'LOW'}")
        
        # Summary
        if found_indicators and found_civil:
            print("\n🎉 INTEGRATION SUCCESS: Response contains both Islamic foundations and civil law!")
        elif found_civil:
            print("\n⚠️ PARTIAL SUCCESS: Response contains civil law but missing Islamic foundations")
        else:
            print("\n❌ INTEGRATION FAILED: Response lacks proper legal citations")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quranic_integration())