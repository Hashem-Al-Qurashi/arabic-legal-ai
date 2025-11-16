#!/usr/bin/env python3
"""
Quick test script for the Legal AI Vanilla Ensemble System
"""

import requests
import json
import time

def test_ensemble():
    print("🧪 Testing Legal AI Vanilla Ensemble System")
    print("=" * 50)
    
    # Test questions
    questions = [
        "ما هي مدة الإجازة السنوية؟",
        "كيف أحسب مكافأة نهاية الخدمة؟", 
        "ما عقوبات التأخير عن العمل؟"
    ]
    
    base_url = "http://localhost:8003"
    
    # Test health endpoint
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        health = response.json()
        print(f"✅ Health check: {health['status']}")
        print(f"📊 API keys configured: {sum(health['api_keys_configured'].values())}/3")
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test each question
    for i, question in enumerate(questions, 1):
        print(f"📝 Test {i}/3: {question}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/ask",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                elapsed = time.time() - start_time
                
                print(f"✅ Success in {elapsed:.1f}s")
                print(f"   📊 Processing: {result['processing_time_ms']}ms")
                print(f"   💰 Cost: ${result['cost_estimate']:.4f}")
                print(f"   🤖 Models: {result['successful_generations']}/{result['models_used']}")
                print(f"   ⚖️ Judges: {result['successful_evaluations']}")
                print(f"   📝 Response: {len(result['final_response'])} chars")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print()
        
        # Small delay between tests
        if i < len(questions):
            time.sleep(2)
    
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_ensemble()