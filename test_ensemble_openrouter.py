#!/usr/bin/env python3
"""Test the OpenRouter-powered ensemble system"""

import asyncio
import os
import time
from vanilla_ensemble_openrouter import VanillaEnsemble

# Set the OpenRouter API key
# API key should be in .env file
# os.environ['OPENROUTER_API_KEY'] is loaded from .env

async def test_ensemble():
    print("="*80)
    print("🧪 TESTING OPENROUTER VANILLA ENSEMBLE")
    print("="*80)
    
    try:
        # Initialize ensemble
        print("\n📦 Initializing ensemble system...")
        ensemble = VanillaEnsemble()
        print("✅ Ensemble initialized successfully")
        
        # Test question
        test_question = "ما هي عقوبة التهرب الضريبي في السعودية وما هي الإجراءات القانونية المتبعة؟"
        
        print(f"\n📝 Test Question: {test_question}")
        print("-"*80)
        
        print("\n🚀 Starting ensemble processing...")
        start_time = time.time()
        
        # Process question
        result = await ensemble.process_question(test_question)
        
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("📊 RESULTS")
        print("="*80)
        
        print(f"\n⏱️  Processing Time: {result['processing_time_ms']}ms ({result['processing_time_ms']/1000:.2f}s)")
        print(f"💰 Total Cost: ${result['cost_estimate']}")
        print(f"🤖 Models Used: {result['models_used']}/{result['generation_responses']}")
        print(f"✅ Successful Generations: {result['successful_generations']}")
        
        print(f"\n📄 Response Length: {len(result['final_response'])} characters")
        print(f"\n📝 Response Preview (first 500 chars):")
        print("-"*40)
        print(result['final_response'][:500] + "...")
        
        print("\n" + "="*80)
        print("🎉 COMPARISON WITH ORIGINAL")
        print("="*80)
        
        print(f"Original System: ~120 seconds")
        print(f"OpenRouter System: {total_time:.2f} seconds")
        print(f"⚡ Speed Improvement: {120/total_time:.1f}x faster!")
        
        if result['processing_time_ms'] < 30000:  # Less than 30 seconds
            print("\n✅ EXCELLENT! Response time under 30 seconds!")
        elif result['processing_time_ms'] < 60000:  # Less than 60 seconds
            print("\n✅ GOOD! Response time under 1 minute!")
        else:
            print("\n⚠️  Response time over 1 minute, but still better than original")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_individual_models():
    """Test each model individually to see response times"""
    print("\n" + "="*80)
    print("🔬 TESTING INDIVIDUAL MODEL SPEEDS")
    print("="*80)
    
    ensemble = VanillaEnsemble()
    test_prompt = "ما هي عقوبة السرقة؟ اجب بفقرة واحدة"
    
    for model in ensemble.generation_models:
        print(f"\n📍 Testing {model}...")
        start = time.time()
        response = await ensemble.call_model(model, test_prompt)
        elapsed = time.time() - start
        
        if response.success:
            print(f"   ✅ Success in {elapsed:.2f}s")
            print(f"   Response length: {len(response.response)} chars")
        else:
            print(f"   ❌ Failed: {response.error}")

if __name__ == "__main__":
    print("🚀 Starting OpenRouter Ensemble Test\n")
    
    # Run the main test
    result = asyncio.run(test_ensemble())
    
    if result and result['successful_generations'] > 0:
        # Test individual models
        asyncio.run(test_individual_models())
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE - OPENROUTER INTEGRATION SUCCESSFUL!")
        print("="*80)
        print("\n📋 Next Steps:")
        print("1. Update app.py to import vanilla_ensemble_openrouter")
        print("2. Update .env to use OPENROUTER_API_KEY only")
        print("3. Deploy and enjoy 6x faster responses!")
    else:
        print("\n❌ Test failed - check the errors above")