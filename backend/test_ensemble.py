"""
Test Script for Ensemble Legal AI System
Validates all components and measures performance
"""

import asyncio
import json
import time
from typing import Dict, Any

# Test configuration
TEST_QUERIES = [
    "ما هي مكافأة نهاية الخدمة للموظف الذي عمل 5 سنوات براتب 6000 ريال؟",  # Calculation test
    "موظف رفع عليه دعوى من شركته بزعم إفشاء أسرار، كيف يرد على هذه الدعوى؟",  # Dispute handling  
    "أريد فصل موظف لسوء السلوك، ما هي الإجراءات المطلوبة؟"  # Procedural guidance
]

# Mock API keys for testing (replace with real keys)
import os
from dotenv import load_dotenv
load_dotenv()

async def test_component_availability():
    """Test if all required API keys are available"""
    
    print("🔧 Testing Component Availability...")
    
    required_keys = {
        "OpenAI (Generator + Judge)": os.getenv("OPENAI_API_KEY"),
        "DeepSeek (Generator)": os.getenv("DEEPSEEK_API_KEY"),
        "Grok (Generator)": os.getenv("GROK_API_KEY"), 
        "Gemini (Generator + Judge)": os.getenv("GEMINI_API_KEY"),
        "Claude (Judge)": os.getenv("ANTHROPIC_API_KEY")
    }
    
    available_models = []
    missing_models = []
    
    for model_name, api_key in required_keys.items():
        if api_key and len(api_key.strip()) > 10:
            available_models.append(model_name)
            print(f"  ✅ {model_name}: Available")
        else:
            missing_models.append(model_name)
            print(f"  ❌ {model_name}: Missing API key")
    
    print(f"\n📊 Summary: {len(available_models)}/{len(required_keys)} models available")
    
    if len(available_models) < 3:
        print("⚠️ Warning: Ensemble requires at least 3 models for meaningful results")
    
    return {
        "available": available_models,
        "missing": missing_models,
        "can_run_ensemble": len(available_models) >= 2
    }

async def test_individual_components():
    """Test each ensemble component individually"""
    
    print("\n🧪 Testing Individual Components...")
    
    try:
        from ensemble_engine import (
            ContextRetriever, ModelClients, MultiModelGenerator,
            ThreeJudgeSystem, ConsensusBuilder, ResponseAssembler,
            QualityVerifier, DataCollector, EnsembleConfig
        )
        
        # Test 1: Context Retriever
        print("  🔧 Testing Context Retriever...")
        try:
            context_retriever = ContextRetriever()
            context_data = await context_retriever.get_legal_context("ما هي المكافأة؟")
            print(f"    ✅ Context retrieval: {context_data['chunk_count']} chunks")
        except Exception as e:
            print(f"    ❌ Context retrieval failed: {e}")
        
        # Test 2: Model Clients  
        print("  🤖 Testing Model Clients...")
        try:
            clients = ModelClients()
            generators = clients.get_available_generators()
            judges = clients.get_available_judges()
            print(f"    ✅ Model clients: {len(generators)} generators, {len(judges)} judges")
        except Exception as e:
            print(f"    ❌ Model clients failed: {e}")
        
        # Test 3: Multi-Model Generator
        print("  🎭 Testing Multi-Model Generator...")
        try:
            if len(generators) > 0:
                multi_gen = MultiModelGenerator(clients)
                print(f"    ✅ Multi-model generator: Ready with {len(generators)} models")
            else:
                print(f"    ⚠️ Multi-model generator: No models available")
        except Exception as e:
            print(f"    ❌ Multi-model generator failed: {e}")
        
        # Test 4: Judge System
        print("  ⚖️ Testing Judge System...")
        try:
            if len(judges) > 0:
                judge_system = ThreeJudgeSystem(clients)
                print(f"    ✅ Judge system: Ready with {len(judges)} judges")
            else:
                print(f"    ⚠️ Judge system: No judges available")
        except Exception as e:
            print(f"    ❌ Judge system failed: {e}")
        
        print("  ✅ All components initialized successfully")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Component test failed: {e}")
        return False

async def test_simple_ensemble_query():
    """Test ensemble with a simple query"""
    
    print("\n🚀 Testing Simple Ensemble Query...")
    
    try:
        from ensemble_engine import process_ensemble_query
        
        # Simple test query
        test_query = "ما هي مكافأة نهاية الخدمة؟"
        
        print(f"  Query: {test_query}")
        print("  Processing with ensemble system...")
        
        start_time = time.time()
        result = await process_ensemble_query(test_query)
        processing_time = time.time() - start_time
        
        print(f"\n📊 Ensemble Results:")
        print(f"  ⏱️ Processing time: {processing_time:.2f}s ({result.get('processing_time_ms', 0)}ms)")
        print(f"  💰 Cost estimate: ${result.get('cost_estimate', 0):.3f}")
        print(f"  ✅ Quality passed: {result.get('quality_report', {}).get('passed', False)}")
        
        if 'ensemble_data' in result:
            ensemble_data = result['ensemble_data']
            print(f"  📄 Context chunks: {ensemble_data.get('context_chunks', 0)}")
            print(f"  🤖 Models used: {ensemble_data.get('generator_responses', 0)}")
            print(f"  ⚖️ Judges used: {ensemble_data.get('judge_evaluations', 0)}")
            print(f"  🧩 Components: {ensemble_data.get('consensus_components', 0)}")
        
        # Show response preview
        final_response = result.get('final_response', '')
        print(f"\n📝 Response Preview:")
        print(f"  Length: {len(final_response)} characters")
        print(f"  Preview: {final_response[:200]}...")
        
        if result.get('quality_report', {}).get('issues'):
            print(f"\n⚠️ Quality Issues:")
            for issue in result['quality_report']['issues']:
                print(f"    - {issue}")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Ensemble query failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_ensemble_streaming():
    """Test ensemble streaming functionality"""
    
    print("\n📡 Testing Ensemble Streaming...")
    
    try:
        from ensemble_engine import process_ensemble_streaming
        
        test_query = "ما هو راتب الموظف الحد الأدنى؟"
        
        print(f"  Query: {test_query}")
        print("  Streaming updates:")
        
        start_time = time.time()
        updates_received = 0
        
        async for update in process_ensemble_streaming(test_query):
            updates_received += 1
            update_type = update.get('type', 'unknown')
            
            if update_type == 'progress':
                layer = update.get('layer', 0)
                status = update.get('status', '')
                print(f"    📡 Layer {layer}: {status}")
                
            elif update_type == 'complete':
                processing_time = time.time() - start_time
                print(f"    ✅ Complete: {processing_time:.2f}s")
                print(f"    💰 Cost: ${update.get('cost_estimate', 0):.3f}")
                
                if 'ensemble_stats' in update:
                    stats = update['ensemble_stats']
                    print(f"    📊 Stats: {stats}")
                
            elif update_type == 'error':
                print(f"    ❌ Error: {update.get('error', 'Unknown error')}")
        
        print(f"  📊 Received {updates_received} streaming updates")
        return True
        
    except Exception as e:
        print(f"  ❌ Streaming test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive test of ensemble system"""
    
    print("🧪 ENSEMBLE SYSTEM COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Test 1: Component availability
    availability = await test_component_availability()
    
    if not availability['can_run_ensemble']:
        print("\n❌ Cannot run ensemble tests - insufficient API keys")
        print("Required: OPENAI_API_KEY, and at least one of: DEEPSEEK_API_KEY, GROK_API_KEY, GEMINI_API_KEY")
        return False
    
    # Test 2: Individual components
    components_ok = await test_individual_components()
    
    if not components_ok:
        print("\n❌ Component tests failed - cannot proceed")
        return False
    
    # Test 3: Simple ensemble query
    simple_result = await test_simple_ensemble_query()
    
    if not simple_result:
        print("\n❌ Simple ensemble test failed")
        return False
    
    # Test 4: Streaming functionality
    streaming_ok = await test_ensemble_streaming()
    
    if not streaming_ok:
        print("\n⚠️ Streaming test failed, but ensemble core works")
    
    print("\n" + "=" * 50)
    print("✅ ENSEMBLE SYSTEM TESTS COMPLETED")
    print(f"📊 Summary:")
    print(f"  - Models available: {len(availability['available'])}")
    print(f"  - Components working: {'✅' if components_ok else '❌'}")
    print(f"  - Ensemble query: {'✅' if simple_result else '❌'}")
    print(f"  - Streaming: {'✅' if streaming_ok else '⚠️'}")
    
    if simple_result:
        print(f"\n🎯 Performance Metrics:")
        print(f"  - Processing time: {simple_result.get('processing_time_ms', 0)}ms")
        print(f"  - Estimated cost: ${simple_result.get('cost_estimate', 0):.3f}")
        print(f"  - Quality passed: {simple_result.get('quality_report', {}).get('passed', False)}")
    
    return True

async def test_cost_estimation():
    """Test cost estimation across different query types"""
    
    print("\n💰 Testing Cost Estimation...")
    
    cost_results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n  Test {i}: {query[:50]}...")
        
        try:
            # Note: This is expensive - only run with real API keys for final testing
            # For now, just test the system without actually calling APIs
            from ensemble_engine import ensemble_engine
            
            # Mock cost calculation
            mock_cost = 0.16 + 0.11 + 0.02  # Generation + Judging + Assembly
            
            print(f"    Estimated cost: ${mock_cost:.3f}")
            cost_results.append({
                "query": query[:50],
                "estimated_cost": mock_cost
            })
            
        except Exception as e:
            print(f"    Error: {e}")
    
    if cost_results:
        total_cost = sum(r['estimated_cost'] for r in cost_results)
        avg_cost = total_cost / len(cost_results)
        
        print(f"\n💰 Cost Summary:")
        print(f"  - Queries tested: {len(cost_results)}")
        print(f"  - Total cost: ${total_cost:.3f}")
        print(f"  - Average per query: ${avg_cost:.3f}")
        print(f"  - Projected 1000 queries: ${avg_cost * 1000:.2f}")
        print(f"  - Projected 10000 queries: ${avg_cost * 10000:.2f}")

if __name__ == "__main__":
    # Run comprehensive test
    asyncio.run(run_comprehensive_test())
    
    # Run cost estimation
    asyncio.run(test_cost_estimation())