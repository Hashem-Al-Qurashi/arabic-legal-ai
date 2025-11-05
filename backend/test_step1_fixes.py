#!/usr/bin/env python3
"""
Comprehensive test for Step 1 Google OAuth fixes
Tests JWT tokens, validation, and functionality
"""

import requests
import json
import sys
import sqlite3
from jose import jwt

BASE_URL = "http://localhost:8000"

def test_proper_jwt_tokens():
    """Test that proper JWT tokens are generated"""
    print("🔑 Testing JWT Token Generation...")
    
    # Test with valid mock token
    response = requests.post(f"{BASE_URL}/api/auth/google", json={
        "id_token": "mock_test@example.com_Test User"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    access_token = data.get("access_token")
    
    # Verify it's a real JWT token (has 3 parts separated by dots)
    jwt_parts = access_token.split('.')
    if len(jwt_parts) != 3:
        print(f"❌ Not a valid JWT: {access_token}")
        return False
    
    print(f"✅ Valid JWT token generated: {access_token[:50]}...")
    return True

def test_input_validation():
    """Test input validation for emails and names"""
    print("🛡️ Testing Input Validation...")
    
    test_cases = [
        # Invalid emails
        ("mock_invalid-email_Test", 400),
        ("mock__Test", 400),  # Empty email
        ("mock_@test.com_Test", 400),  # Invalid email format
        
        # Valid cases
        ("mock_valid@test.com_Valid User", 200),
        ("mock_test.user+123@example.org_", 200),  # Empty name should get default
    ]
    
    for token, expected_status in test_cases:
        response = requests.post(f"{BASE_URL}/api/auth/google", json={
            "id_token": token
        })
        
        if response.status_code != expected_status:
            print(f"❌ Token '{token}' - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        if expected_status == 200:
            data = response.json()
            user = data.get("user", {})
            email = user.get("email")
            name = user.get("full_name")
            
            # Check email is properly formatted
            if not email or "@" not in email:
                print(f"❌ Invalid email in response: {email}")
                return False
            
            # Check name is sanitized
            if not name or len(name) > 100:
                print(f"❌ Invalid name in response: {name}")
                return False
    
    print("✅ Input validation working correctly")
    return True

def test_mock_token_parsing():
    """Test mock token parsing edge cases"""
    print("🎭 Testing Mock Token Parsing...")
    
    test_cases = [
        # Valid formats
        ("mock_user@test.com_John Doe", 200),
        ("mock_simple@test.com_", 200),  # Empty name
        ("mock_user@test.com", 200),  # No name part
        
        # Invalid formats  
        ("mock_", 400),  # Just mock prefix
        ("mock", 400),   # No underscore
        ("not_mock_token", 400),  # Not a mock token, invalid format
    ]
    
    for token, expected_status in test_cases:
        response = requests.post(f"{BASE_URL}/api/auth/google", json={
            "id_token": token
        })
        
        if response.status_code != expected_status:
            print(f"❌ Token '{token}' - Expected {expected_status}, got {response.status_code}")
            return False
    
    print("✅ Mock token parsing working correctly")
    return True

def test_database_integration():
    """Test database is properly updated"""
    print("🗄️ Testing Database Integration...")
    
    # Create a new user
    email = "newuser@test.com"
    response = requests.post(f"{BASE_URL}/api/auth/google", json={
        "id_token": f"mock_{email}_New User"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.text}")
        return False
    
    data = response.json()
    user_id = data["user"]["id"]
    
    # Check database directly
    try:
        conn = sqlite3.connect("data/arabic_legal.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, full_name, google_id, auth_provider 
            FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print(f"❌ User not found in database: {user_id}")
            return False
        
        db_email, db_name, db_google_id, db_auth_provider = result
        
        if db_email != email:
            print(f"❌ Email mismatch: {db_email} != {email}")
            return False
        
        if db_auth_provider != "google":
            print(f"❌ Auth provider wrong: {db_auth_provider}")
            return False
        
        if not db_google_id.startswith("mock_google_"):
            print(f"❌ Google ID wrong format: {db_google_id}")
            return False
        
        print("✅ Database integration working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_endpoints_working():
    """Test all endpoints are accessible"""
    print("🌐 Testing Endpoints...")
    
    endpoints = [
        ("/api/auth/google/status", 200),
        ("/api/auth/google/test-info", 200),
    ]
    
    for endpoint, expected_status in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code != expected_status:
            print(f"❌ Endpoint {endpoint} failed: {response.status_code}")
            return False
    
    print("✅ All endpoints accessible")
    return True

def main():
    """Run all tests"""
    print("🚀 Running Comprehensive Step 1 Fixes Test\n")
    
    tests = [
        test_endpoints_working,
        test_proper_jwt_tokens,
        test_input_validation,
        test_mock_token_parsing,
        test_database_integration,
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
        print("🎉 ALL TESTS PASSED! Step 1 fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Step 1 needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)