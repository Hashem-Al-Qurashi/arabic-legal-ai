"""
Quick test for vanilla ensemble system
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def quick_vanilla_test():
    """Quick test to validate vanilla ensemble"""
    
    print("🧪 Quick Vanilla Ensemble Test")
    print("=" * 40)
    
    # Test API key availability
    print("🔑 Checking API keys...")
    
    keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "DeepSeek": os.getenv("DEEPSEEK_API_KEY"),
        "Grok": os.getenv("GROK_API_KEY"),
        "Gemini": os.getenv("GEMINI_API_KEY")
    }
    
    available_models = []
    for name, key in keys.items():
        if key and len(key.strip()) > 10:
            available_models.append(name)
            print(f"  ✅ {name}: Available")
        else:
            print(f"  ❌ {name}: Missing")
    
    print(f"\n📊 Available models: {len(available_models)}")
    
    if len(available_models) < 2:
        print("❌ Need at least 2 models for vanilla ensemble")
        return False
    
    # Test vanilla ensemble import
    print("\n🔧 Testing imports...")
    try:
        from vanilla_ensemble import (
            VanillaModelClients, VanillaMultiModelGenerator,
            get_vanilla_ensemble_stats
        )
        print("  ✅ Vanilla ensemble imports successful")
        
        # Test client initialization
        clients = VanillaModelClients()
        generators = clients.get_available_generators()
        judges = clients.get_available_judges()
        
        print(f"  ✅ Clients initialized: {len(generators)} generators, {len(judges)} judges")
        
        # Test stats
        stats = get_vanilla_ensemble_stats()
        print(f"  ✅ Stats accessible: {stats['system_type']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import/initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_vanilla_test())
    
    if success:
        print("\n✅ VANILLA ENSEMBLE READY!")
        print("🚀 Next: Test via API endpoint /api/chat/message/vanilla-ensemble")
    else:
        print("\n❌ VANILLA ENSEMBLE NOT READY")
        print("🔧 Check API keys and dependencies")