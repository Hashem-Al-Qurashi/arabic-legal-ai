#!/usr/bin/env python3
"""
Test script for Google OAuth Step 1 - Backend Functionality
This script tests the Google OAuth endpoint with mock tokens in development mode.
"""

import requests
import json
import sqlite3
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/auth/google"
STATUS_URL = f"{BASE_URL}/api/auth/google/status"
TEST_INFO_URL = f"{BASE_URL}/api/auth/google/test-info"

# Test cases
TEST_CASES = [
    {
        "name": "New user with mock token",
        "token": "mock_newuser@test.com_New User",
        "expected_email": "newuser@test.com",
        "expected_name": "New User"
    },
    {
        "name": "Existing user with mock token",
        "token": "mock_existing@test.com_Existing User",
        "expected_email": "existing@test.com",
        "expected_name": "Existing User"
    },
    {
        "name": "User without name in token",
        "token": "mock_noname@test.com",
        "expected_email": "noname@test.com",
        "expected_name": "noname"
    }
]

def check_server_running():
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_google_status():
    """Test the Google OAuth status endpoint"""
    print("\n📊 Testing Google OAuth Status Endpoint...")
    try:
        response = requests.get(STATUS_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status endpoint working")
            print(f"   - Library installed: {data.get('library_installed')}")
            print(f"   - Client ID configured: {data.get('configured')}")
            print(f"   - Environment: {data.get('environment')}")
            print(f"   - Mock mode available: {data.get('mock_mode_available')}")
            return True
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {str(e)}")
        return False

def test_google_test_info():
    """Test the Google OAuth test info endpoint"""
    print("\n📋 Testing Google OAuth Test Info Endpoint...")
    try:
        response = requests.get(TEST_INFO_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test info endpoint working")
            if data.get('test_mode') == 'enabled':
                print(f"   - Mock token format: {data.get('mock_token_format')}")
                print(f"   - Example tokens available: {len(data.get('example_tokens', []))}")
            return True
        else:
            print(f"❌ Test info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting test info: {str(e)}")
        return False

def test_google_signin(test_case):
    """Test Google sign-in with a mock token"""
    print(f"\n🔐 Testing: {test_case['name']}")
    print(f"   Token: {test_case['token']}")
    
    try:
        # Make the sign-in request
        response = requests.post(
            API_URL,
            json={"id_token": test_case["token"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sign-in successful!")
            
            # Check response structure
            if "access_token" in data:
                print(f"   - Access token received: {data['access_token'][:20]}...")
            else:
                print(f"   ⚠️ No access token in response")
            
            if "user" in data:
                user = data["user"]
                print(f"   - User ID: {user.get('id')}")
                print(f"   - Email: {user.get('email')}")
                print(f"   - Name: {user.get('full_name')}")
                print(f"   - Verified: {user.get('is_verified')}")
                print(f"   - Active: {user.get('is_active')}")
                
                # Verify expected values
                if user.get('email') == test_case['expected_email']:
                    print(f"   ✅ Email matches expected")
                else:
                    print(f"   ❌ Email mismatch: expected {test_case['expected_email']}, got {user.get('email')}")
                
                if user.get('full_name') == test_case['expected_name']:
                    print(f"   ✅ Name matches expected")
                else:
                    print(f"   ❌ Name mismatch: expected {test_case['expected_name']}, got {user.get('full_name')}")
            
            return True, data
        else:
            print(f"❌ Sign-in failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during sign-in: {str(e)}")
        return False, None

def verify_database_entries():
    """Verify that users were created in the database with Google fields"""
    print("\n🗄️ Verifying Database Entries...")
    
    try:
        conn = sqlite3.connect('data/arabic_legal.db')
        cursor = conn.cursor()
        
        # Check for users with Google auth
        cursor.execute("""
            SELECT email, full_name, google_id, auth_provider, is_verified 
            FROM users 
            WHERE auth_provider = 'google' OR google_id IS NOT NULL
        """)
        
        users = cursor.fetchall()
        
        if users:
            print(f"✅ Found {len(users)} Google OAuth users in database:")
            for user in users:
                print(f"   - Email: {user[0]}")
                print(f"     Name: {user[1]}")
                print(f"     Google ID: {user[2]}")
                print(f"     Auth Provider: {user[3]}")
                print(f"     Verified: {user[4]}")
                print()
        else:
            print("⚠️ No Google OAuth users found in database")
        
        conn.close()
        return len(users) > 0
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

def test_duplicate_signin(email):
    """Test signing in again with the same email"""
    print(f"\n🔄 Testing duplicate sign-in for {email}...")
    
    token = f"mock_{email}_Updated Name"
    response = requests.post(
        API_URL,
        json={"id_token": token},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✅ Duplicate sign-in successful (existing user handled)")
        data = response.json()
        if "user" in data:
            print(f"   - User ID: {data['user'].get('id')}")
            print(f"   - Email: {data['user'].get('email')}")
        return True
    else:
        print(f"❌ Duplicate sign-in failed: {response.status_code}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 Google OAuth Backend Functionality Test - Step 1")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("\n⚠️ FastAPI server is not running!")
        print("Please start the server with: uvicorn app.main:app --reload")
        print("Then run this test script again.")
        return False
    
    print("✅ Server is running")
    
    # Track test results
    all_passed = True
    
    # Test 1: Check status endpoint
    if not test_google_status():
        all_passed = False
    
    # Test 2: Check test info endpoint
    if not test_google_test_info():
        all_passed = False
    
    # Test 3: Test sign-in with mock tokens
    successful_signins = []
    for test_case in TEST_CASES:
        success, data = test_google_signin(test_case)
        if success:
            successful_signins.append(test_case['expected_email'])
        else:
            all_passed = False
    
    # Test 4: Test duplicate sign-in
    if successful_signins:
        if not test_duplicate_signin(successful_signins[0]):
            all_passed = False
    
    # Test 5: Verify database entries
    if not verify_database_entries():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n✨ Step 1 Complete: Backend Google OAuth is functional!")
        print("\n📝 Next Steps:")
        print("1. The backend endpoint is working with mock tokens")
        print("2. Database schema has been updated with Google fields")
        print("3. Users can be created and authenticated via Google OAuth")
        print("\n🔧 For production:")
        print("1. Set real GOOGLE_CLIENT_ID in .env file")
        print("2. Set ENVIRONMENT to 'production' to disable mock tokens")
        print("3. Configure real Google OAuth credentials from Google Console")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the errors above and fix any issues.")
        print("Common issues:")
        print("1. Server not running - start with: uvicorn app.main:app --reload")
        print("2. Database migration not applied - run: python add_google_fields.py")
        print("3. Environment variables not loaded - check .env file")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)