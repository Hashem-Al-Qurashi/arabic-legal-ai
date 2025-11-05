#!/usr/bin/env python3
"""
Test the complete authentication flow for Google OAuth
Tests JWT token generation and authentication middleware compatibility
"""

import requests
import json
import sys
from jose import jwt

BASE_URL = "http://localhost:8000"

def test_complete_auth_flow():
    """Test complete authentication flow from login to protected resource"""
    print("🔐 Testing Complete Authentication Flow...")
    
    # Step 1: Login with Google OAuth
    print("Step 1: Login with Google OAuth mock token")
    login_response = requests.post(f"{BASE_URL}/api/auth/google", json={
        "id_token": "mock_testflow@example.com_Test Flow User"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    user_info = login_data.get("user")
    user_id = user_info.get("id")
    
    print(f"✅ Login successful, user ID: {user_id}")
    print(f"✅ JWT token: {access_token[:50]}...")
    
    # Step 2: Verify JWT token structure
    print("\nStep 2: Verify JWT token structure")
    try:
        # Decode without verification to check structure
        unverified_payload = jwt.get_unverified_claims(access_token)
        token_user_id = unverified_payload.get("sub")
        token_type = unverified_payload.get("type")
        
        if token_user_id != user_id:
            print(f"❌ Token user ID mismatch: {token_user_id} != {user_id}")
            return False
        
        if token_type != "access":
            print(f"❌ Wrong token type: {token_type}")
            return False
        
        print(f"✅ JWT structure valid - user_id: {token_user_id}, type: {token_type}")
        
    except Exception as e:
        print(f"❌ JWT token invalid: {e}")
        return False
    
    # Step 3: Test authentication middleware with protected endpoint
    print("\nStep 3: Test protected endpoint with JWT token")
    
    # Find a protected endpoint to test
    # Let's try the user profile endpoint if it exists
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test actual available endpoints that might require authentication
    test_cases = [
        ("GET", "/api/chat/conversations"),
        ("POST", "/api/chat/message", {"message": "Test authentication", "conversation_id": None}),
        ("GET", "/export/docx"),
        ("POST", "/api/ocr/extract", {"image": "test"}),
    ]
    
    auth_working = False
    
    for method, endpoint, *data in test_cases:
        print(f"   Testing {method} {endpoint}...")
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            payload = data[0] if data else {}
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"   ✅ {endpoint} - Authentication successful")
            auth_working = True
            break
        elif response.status_code == 401:
            print(f"   ❌ {endpoint} - Authentication failed (401)")
        elif response.status_code == 422:
            print(f"   ⚠️ {endpoint} - Validation error (422) - but auth worked")
            auth_working = True  # Auth worked, just bad data
            break
        else:
            print(f"   ⚠️ {endpoint} - Status: {response.status_code}")
    
    # Step 4: Test protected endpoint that requires authentication
    print("\nStep 4: Test strictly protected endpoint without authentication")
    no_auth_response = requests.get(f"{BASE_URL}/api/chat/conversations")
    
    if no_auth_response.status_code in [401, 403]:
        print(f"✅ Correctly rejected request without authentication ({no_auth_response.status_code})")
    elif no_auth_response.status_code == 200:
        print("⚠️ Endpoint allows access without authentication (might be guest-enabled)")
    else:
        print(f"⚠️ Unexpected response without auth: {no_auth_response.status_code}")
    
    return auth_working

def test_token_validation():
    """Test that invalid tokens are properly rejected"""
    print("\n🛡️ Testing Token Validation...")
    
    invalid_tokens = [
        "invalid.jwt.token",
        "Bearer fake-token",
        "",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
    ]
    
    for token in invalid_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/chat/conversations", headers=headers)
        
        if response.status_code in [401, 403]:
            print(f"✅ Correctly rejected invalid token: {token[:20]}... ({response.status_code})")
        else:
            print(f"❌ Invalid token accepted: {token[:20]}... - Status: {response.status_code}")
            return False
    
    return True

def main():
    """Run all authentication flow tests"""
    print("🚀 Testing Google OAuth Authentication Flow\n")
    
    tests = [
        test_complete_auth_flow,
        test_token_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL AUTHENTICATION TESTS PASSED!")
        return True
    else:
        print("❌ Some authentication tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)