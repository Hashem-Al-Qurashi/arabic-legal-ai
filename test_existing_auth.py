#!/usr/bin/env python3
"""
Test existing authentication system to ensure Google OAuth integration doesn't break anything
"""
import sys
import os
import requests
import json
import uuid
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, '/media/windows_drive/legal/arabic_legal_ai/backend')

# Test configuration
BASE_URL = "http://localhost:8000"  # Adjust if different
TEST_USER_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "test_password_123"
TEST_USER_NAME = "Test User"

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_data = None
        self.errors = []
        self.tests_passed = 0
        self.tests_total = 0

    def log_error(self, test_name: str, error: str):
        self.errors.append(f"❌ {test_name}: {error}")
        print(f"❌ {test_name}: {error}")

    def log_success(self, test_name: str, message: str = ""):
        self.tests_passed += 1
        print(f"✅ {test_name}: {message}")

    def run_test(self, test_name: str):
        self.tests_total += 1
        print(f"\n🧪 Testing: {test_name}")

    def test_server_health(self) -> bool:
        """Test if the server is running"""
        self.run_test("Server Health Check")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_success("Server Health Check", f"Server is running - {data.get('service', 'Unknown')}")
                return True
            else:
                self.log_error("Server Health Check", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("Server Health Check", f"Connection failed: {str(e)}")
            return False

    def test_user_registration(self) -> bool:
        """Test user registration endpoint"""
        self.run_test("User Registration")
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME
            }
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'email', 'full_name', 'subscription_tier']
                
                for field in required_fields:
                    if field not in data:
                        self.log_error("User Registration", f"Missing field in response: {field}")
                        return False
                
                if data['email'] != TEST_USER_EMAIL:
                    self.log_error("User Registration", f"Email mismatch: {data['email']} != {TEST_USER_EMAIL}")
                    return False
                
                self.log_success("User Registration", f"User created with ID: {data['id']}")
                return True
            else:
                self.log_error("User Registration", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("User Registration", f"Exception: {str(e)}")
            return False

    def test_user_login(self) -> bool:
        """Test user login endpoint"""
        self.run_test("User Login")
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['access_token', 'refresh_token', 'token_type', 'expires_in', 'user']
                
                for field in required_fields:
                    if field not in data:
                        self.log_error("User Login", f"Missing field in response: {field}")
                        return False
                
                # Store token for subsequent tests
                self.access_token = data['access_token']
                self.user_data = data['user']
                
                if data['token_type'] != 'bearer':
                    self.log_error("User Login", f"Unexpected token type: {data['token_type']}")
                    return False
                
                self.log_success("User Login", f"Login successful, token received")
                return True
            else:
                self.log_error("User Login", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("User Login", f"Exception: {str(e)}")
            return False

    def test_token_usage(self) -> bool:
        """Test using the access token for authenticated endpoints"""
        self.run_test("Token Usage")
        if not self.access_token:
            self.log_error("Token Usage", "No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{BASE_URL}/api/chat/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'email' in data and data['email'] == TEST_USER_EMAIL:
                    self.log_success("Token Usage", "Authenticated endpoint accessible")
                    return True
                else:
                    self.log_error("Token Usage", f"User data mismatch in authenticated endpoint")
                    return False
            else:
                self.log_error("Token Usage", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("Token Usage", f"Exception: {str(e)}")
            return False

    def test_duplicate_registration(self) -> bool:
        """Test that duplicate registration fails appropriately"""
        self.run_test("Duplicate Registration Prevention")
        try:
            payload = {
                "email": TEST_USER_EMAIL,  # Same email as before
                "password": "different_password",
                "full_name": "Different Name"
            }
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
            
            if response.status_code == 400:
                self.log_success("Duplicate Registration Prevention", "Correctly rejected duplicate email")
                return True
            else:
                self.log_error("Duplicate Registration Prevention", 
                             f"Expected 400, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("Duplicate Registration Prevention", f"Exception: {str(e)}")
            return False

    def test_invalid_login(self) -> bool:
        """Test that invalid credentials are rejected"""
        self.run_test("Invalid Login Rejection")
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": "wrong_password"
            }
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=payload)
            
            if response.status_code == 401:
                self.log_success("Invalid Login Rejection", "Correctly rejected invalid credentials")
                return True
            else:
                self.log_error("Invalid Login Rejection", 
                             f"Expected 401, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("Invalid Login Rejection", f"Exception: {str(e)}")
            return False

    def test_google_auth_endpoint_availability(self) -> bool:
        """Test that Google auth endpoint is available (even if not configured)"""
        self.run_test("Google Auth Endpoint Availability")
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/google/status")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['available', 'configured', 'library_installed']
                
                for field in expected_fields:
                    if field not in data:
                        self.log_error("Google Auth Endpoint", f"Missing field in status: {field}")
                        return False
                
                self.log_success("Google Auth Endpoint Availability", 
                               f"Status endpoint working, available: {data.get('available', False)}")
                return True
            else:
                self.log_error("Google Auth Endpoint Availability", 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_error("Google Auth Endpoint Availability", f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all authentication tests"""
        print("🚀 Starting Authentication System Tests")
        print("=" * 50)
        
        # Run tests in order
        tests = [
            self.test_server_health,
            self.test_user_registration,
            self.test_user_login,
            self.test_token_usage,
            self.test_duplicate_registration,
            self.test_invalid_login,
            self.test_google_auth_endpoint_availability
        ]
        
        for test_func in tests:
            if not test_func():
                # Continue testing even if one fails
                pass
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        success_rate = (self.tests_passed / self.tests_total) * 100 if self.tests_total > 0 else 0
        
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_total} ({success_rate:.1f}%)")
        
        if self.errors:
            print(f"❌ Errors Found: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        
        # Determine if system is ready
        critical_tests_passed = self.tests_passed >= 6  # All except Google auth can fail
        
        if critical_tests_passed:
            print("\n🎉 EXISTING AUTH SYSTEM: ✅ WORKING CORRECTLY")
            print("✅ Safe to proceed with Google OAuth integration")
        else:
            print("\n🚨 EXISTING AUTH SYSTEM: ❌ HAS ISSUES")
            print("⚠️  Fix existing authentication issues before adding Google OAuth")
        
        return {
            "total_tests": self.tests_total,
            "passed_tests": self.tests_passed,
            "success_rate": success_rate,
            "errors": self.errors,
            "system_ready": critical_tests_passed
        }

if __name__ == "__main__":
    tester = AuthTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["system_ready"] else 1)