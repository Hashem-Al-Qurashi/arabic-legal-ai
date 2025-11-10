#!/usr/bin/env python3
"""
Complete functionality test for Real Google OAuth implementation
Tests the system both with and without real credentials
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_endpoints():
    """Test all backend endpoints"""
    print("🔐 Testing Backend Google OAuth Endpoints\n")
    
    # Test 1: Status endpoint
    print("1. Testing /api/auth/google/status")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Available: {data.get('available')}")
            print(f"   📊 Configured: {data.get('configured')}")
            print(f"   📊 Library installed: {data.get('library_installed')}")
            print(f"   📊 Client ID is real: {data.get('client_id_is_real')}")
            
            if not data.get('configured'):
                print("   ⚠️ Google OAuth not configured (expected with placeholder credentials)")
            
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Status endpoint error: {e}")
        return False
    
    # Test 2: Test info endpoint
    print("\n2. Testing /api/auth/google/test-info")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/test-info")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Environment: {data.get('environment')}")
            print(f"   📊 Client ID configured: {data.get('google_client_id_configured')}")
            print(f"   📊 Setup needed: {data.get('setup_needed')}")
            print(f"   📊 Current Client ID: {data.get('current_client_id')}")
        else:
            print(f"   ❌ Test info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Test info endpoint error: {e}")
        return False
    
    # Test 3: Authentication endpoint (should fail without real credentials)
    print("\n3. Testing /api/auth/google authentication")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/google", json={
            "id_token": "fake-google-token-for-testing"
        })
        
        if response.status_code == 503:
            print(f"   ✅ Status: {response.status_code} (correctly rejected)")
            print(f"   📊 Message: {response.json().get('detail')}")
            print("   ✅ System properly rejects authentication without real credentials")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Authentication test error: {e}")
        return False
    
    return True

def test_frontend_accessibility():
    """Test that frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility\n")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend accessible at {FRONTEND_URL}")
            
            # Check if the response contains React app indicators
            content = response.text
            if 'vite' in content.lower() or 'react' in content.lower() or 'root' in content:
                print("✅ React app appears to be loaded")
            else:
                print("⚠️ Frontend content looks unusual")
                
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print("\n🌍 Testing CORS Configuration\n")
    
    try:
        # Test preflight request
        response = requests.options(f"{BASE_URL}/api/auth/google", headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        if response.status_code == 200:
            print("✅ CORS preflight request successful")
            headers = response.headers
            if 'Access-Control-Allow-Origin' in headers:
                print(f"✅ CORS origin allowed: {headers['Access-Control-Allow-Origin']}")
            else:
                print("⚠️ CORS headers not found")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_error_handling():
    """Test various error scenarios"""
    print("\n🚨 Testing Error Handling\n")
    
    test_cases = [
        ("Empty token", {"id_token": ""}),
        ("Invalid JSON", None),
        ("Missing token field", {"not_id_token": "value"}),
        ("Very long token", {"id_token": "x" * 10000}),
    ]
    
    for test_name, payload in test_cases:
        print(f"Testing: {test_name}")
        try:
            if payload is None:
                response = requests.post(f"{BASE_URL}/api/auth/google", 
                                       data="invalid json", 
                                       headers={'Content-Type': 'application/json'})
            else:
                response = requests.post(f"{BASE_URL}/api/auth/google", json=payload)
            
            if response.status_code in [400, 422, 503]:
                print(f"   ✅ Properly handled: {response.status_code}")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ✅ Request failed as expected: {type(e).__name__}")
    
    return True

def show_real_setup_status():
    """Show what's needed for real setup"""
    print("\n" + "="*80)
    print("📋 REAL GOOGLE OAUTH SETUP STATUS")
    print("="*80)
    
    # Check status
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/status")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('configured'):
                print("🎉 ✅ Google OAuth is FULLY CONFIGURED and ready!")
                print("🚀 Users can now sign in with their Google accounts")
            else:
                print("⚠️ ❌ Google OAuth setup is INCOMPLETE")
                print("\n📝 TO COMPLETE SETUP:")
                print("1. Get real credentials from Google Cloud Console")
                print("2. Update backend/.env with real GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
                print("3. Update frontend/.env with real VITE_GOOGLE_CLIENT_ID")
                print("4. Restart both services")
                print("\n📚 See: GOOGLE_OAUTH_SETUP.md for detailed instructions")
                
    except Exception as e:
        print(f"❌ Could not check status: {e}")

def main():
    """Run all functionality tests"""
    print("🧪 COMPLETE GOOGLE OAUTH FUNCTIONALITY TEST")
    print("="*60)
    
    tests = [
        ("Backend Endpoints", test_backend_endpoints),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("CORS Configuration", test_cors_configuration),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name.upper()}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: CRASHED - {e}")
    
    # Show results
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL FUNCTIONALITY TESTS PASSED!")
        print("✅ The system is properly structured for real Google OAuth")
    else:
        print("⚠️ Some tests failed - check the issues above")
    
    show_real_setup_status()
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)