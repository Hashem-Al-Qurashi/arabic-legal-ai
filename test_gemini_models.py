#!/usr/bin/env python3
"""
Test script to find the correct working Gemini model name
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("🔍 Testing Gemini Models")
print("=" * 50)

# List of model names to try based on official docs
model_names = [
    "gemini-2.5-flash",
    "gemini-2.5-pro", 
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.0-pro"
]

successful_models = []
failed_models = []

for model_name in model_names:
    print(f"\n🧪 Testing: {model_name}")
    
    try:
        # Try to create and use the model
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("What is 2+2?")
        
        print(f"✅ SUCCESS: {model_name}")
        print(f"   Response: {response.text[:100]}...")
        successful_models.append(model_name)
        
    except Exception as e:
        print(f"❌ FAILED: {model_name}")
        print(f"   Error: {str(e)[:100]}...")
        failed_models.append((model_name, str(e)))

print("\n" + "=" * 50)
print("📊 RESULTS SUMMARY")
print("=" * 50)

if successful_models:
    print(f"✅ Working Models ({len(successful_models)}):")
    for model in successful_models:
        print(f"   - {model}")
    print(f"\n🎯 RECOMMENDED: Use '{successful_models[0]}'")
else:
    print("❌ No working models found!")

if failed_models:
    print(f"\n❌ Failed Models ({len(failed_models)}):")
    for model, error in failed_models:
        print(f"   - {model}: {error[:60]}...")

# Try to list available models
print(f"\n🔍 Attempting to list all available models...")
try:
    models = list(genai.list_models())
    print(f"📋 Available models:")
    for m in models[:10]:  # Show first 10
        print(f"   - {m.name}")
        if len(models) > 10:
            print(f"   ... and {len(models) - 10} more")
            break
except Exception as e:
    print(f"❌ Could not list models: {e}")

print("\n🎉 Test complete!")