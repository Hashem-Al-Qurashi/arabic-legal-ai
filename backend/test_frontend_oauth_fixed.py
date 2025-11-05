#!/usr/bin/env python3
"""
COMPREHENSIVE FRONTEND GOOGLE OAUTH TESTING SUITE - FIXED VERSION
================================================================

This script tests the Step 2 Frontend Google OAuth implementation thoroughly,
using the correct mock token format and proper testing approach.

Author: Testing Expert (Grumpy & Skeptical - But More Informed)
Date: 2025-10-27
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Test Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
GOOGLE_CLIENT_ID = "test-client-id-12345.apps.googleusercontent.com"

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    critical: bool = False

class FrontendGoogleOAuthTesterFixed:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.mock_tokens = {}
        
    def log_result(self, result: TestResult):
        """Log a test result with appropriate formatting"""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        critical = " [CRITICAL]" if result.critical else ""
        print(f"{status}{critical}: {result.name}")
        print(f"   {result.message}")
        if result.details:
            print(f"   Details: {json.dumps(result.details, indent=2)}")
        print()
        self.results.append(result)
    
    def create_proper_mock_token(self, email: str, name: str) -> str:
        """Create proper mock token in the format expected by backend"""
        # Format: mock_<email>_<name>
        return f"mock_{email}_{name}"
    
    def test_backend_google_auth_proper_mock(self):
        """Test 1: Backend Google Auth with Proper Mock Token"""
        try:
            # Create properly formatted mock token
            test_email = "test@example.com"
            test_name = "Test User"
            mock_token = self.create_proper_mock_token(test_email, test_name)
            
            print(f"🔧 Testing with mock token: {mock_token}")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/google",
                json={"id_token": mock_token},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"🔧 Response status: {response.status_code}")
            print(f"🔧 Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                has_access_token = "access_token" in data
                has_user_data = "user" in data
                
                self.log_result(TestResult(
                    name="Backend Google Auth with Proper Mock",
                    passed=True,
                    message="Backend Google OAuth working with correct mock format",
                    details={
                        "status_code": response.status_code,
                        "has_access_token": has_access_token,
                        "has_user_data": has_user_data,
                        "user_email": data.get("user", {}).get("email") if has_user_data else None
                    }
                ))
                
                # Store tokens for later tests
                if has_access_token:
                    self.mock_tokens["access_token"] = data["access_token"]
                    self.mock_tokens["refresh_token"] = data.get("refresh_token")
                    
            else:
                self.log_result(TestResult(
                    name="Backend Google Auth with Proper Mock",
                    passed=False,
                    message=f"Backend auth failed: HTTP {response.status_code} - {response.text}",
                    critical=True
                ))
                
        except Exception as e:
            self.log_result(TestResult(
                name="Backend Google Auth with Proper Mock",
                passed=False,
                message=f"Backend auth test failed: {e}",
                critical=True
            ))
    
    def test_google_auth_configuration_endpoint(self):
        """Test 2: Google Auth Configuration Endpoints"""
        try:
            endpoints_to_test = [
                ("/api/auth/google/status", "Google Auth Status"),
                ("/api/auth/google/test-info", "Google Test Info")
            ]
            
            results = {}
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                    results[name] = {
                        "status": response.status_code,
                        "accessible": response.status_code == 200,
                        "data": response.json() if response.status_code == 200 else None
                    }
                except Exception as e:
                    results[name] = {
                        "status": "error",
                        "accessible": False,
                        "error": str(e)
                    }
            
            all_accessible = all(r["accessible"] for r in results.values())
            
            self.log_result(TestResult(
                name="Google Auth Configuration Endpoints",
                passed=all_accessible,
                message="Google auth configuration endpoints working" if all_accessible else "Some configuration endpoints not accessible",
                details=results
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Google Auth Configuration Endpoints",
                passed=False,
                message=f"Configuration endpoint test failed: {e}"
            ))
    
    def test_authenticated_endpoints_access(self):
        """Test 3: Authenticated Endpoints Access"""
        try:
            if "access_token" not in self.mock_tokens:
                self.log_result(TestResult(
                    name="Authenticated Endpoints Access",
                    passed=False,
                    message="No access token available from previous tests",
                    critical=True
                ))
                return
            
            access_token = self.mock_tokens["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test various authenticated endpoints
            authenticated_endpoints = [
                ("/api/chat/status", "Chat Status"),
                ("/api/chat/conversations", "Conversations List")
            ]
            
            results = {}
            
            for endpoint, name in authenticated_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                    results[name] = {
                        "status": response.status_code,
                        "accessible": response.status_code in [200, 403],  # 403 might be expected for some endpoints
                        "authenticated": response.status_code != 401,
                        "data": response.json() if response.status_code == 200 else None
                    }
                except Exception as e:
                    results[name] = {
                        "status": "error",
                        "accessible": False,
                        "authenticated": False,
                        "error": str(e)
                    }
            
            authenticated_count = sum(1 for r in results.values() if r["authenticated"])
            all_authenticated = authenticated_count == len(authenticated_endpoints)
            
            self.log_result(TestResult(
                name="Authenticated Endpoints Access",
                passed=all_authenticated,
                message=f"{authenticated_count}/{len(authenticated_endpoints)} endpoints properly authenticated",
                details=results,
                critical=authenticated_count == 0
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Authenticated Endpoints Access",
                passed=False,
                message=f"Authenticated endpoints test failed: {e}",
                critical=True
            ))
    
    def test_frontend_google_button_integration(self):
        """Test 4: Frontend Google Button Integration Analysis"""
        try:
            # Analyze the frontend code for proper integration
            frontend_files = {
                "GoogleSignInButton": "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/components/auth/GoogleSignInButton.tsx",
                "AuthContext": "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/contexts/AuthContext.tsx",
                "LoginForm": "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/components/auth/LoginForm.tsx",
                "API Service": "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/services/api.ts"
            }
            
            integration_checks = {
                "google_script_loading": False,
                "google_signin_button_exists": False,
                "auth_context_google_method": False,
                "api_google_endpoint": False,
                "proper_error_handling": False,
                "token_storage_mechanism": False,
                "login_form_integration": False
            }
            
            for file_name, file_path in frontend_files.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if file_name == "GoogleSignInButton":
                        integration_checks["google_script_loading"] = "https://accounts.google.com/gsi/client" in content
                        integration_checks["google_signin_button_exists"] = "GoogleSignInButton" in content
                        integration_checks["proper_error_handling"] = "catch" in content and "toast.error" in content
                    
                    elif file_name == "AuthContext":
                        integration_checks["auth_context_google_method"] = "loginWithGoogle" in content
                    
                    elif file_name == "LoginForm":
                        integration_checks["login_form_integration"] = "GoogleSignInButton" in content
                    
                    elif file_name == "API Service":
                        integration_checks["api_google_endpoint"] = "/api/auth/google" in content
                        integration_checks["token_storage_mechanism"] = "localStorage" in content and "access_token" in content
                    
                except Exception as e:
                    print(f"Warning: Could not read {file_name}: {e}")
                    continue
            
            integration_score = sum(1 for check in integration_checks.values() if check)
            integration_complete = integration_score >= 6  # At least 6/7 checks should pass
            
            self.log_result(TestResult(
                name="Frontend Google Button Integration",
                passed=integration_complete,
                message=f"Frontend integration analysis: {integration_score}/{len(integration_checks)} requirements met",
                details=integration_checks
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Frontend Google Button Integration",
                passed=False,
                message=f"Frontend integration test failed: {e}"
            ))
    
    def test_environment_variables_configuration(self):
        """Test 5: Environment Variables Configuration"""
        try:
            # Check frontend .env file
            env_checks = {
                "frontend_env_exists": False,
                "google_client_id_set": False,
                "client_id_format_valid": False
            }
            
            try:
                with open("/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/.env", 'r') as f:
                    env_content = f.read()
                
                env_checks["frontend_env_exists"] = True
                env_checks["google_client_id_set"] = "VITE_GOOGLE_CLIENT_ID" in env_content
                env_checks["client_id_format_valid"] = ".apps.googleusercontent.com" in env_content
                
            except Exception:
                pass
            
            # Test backend configuration endpoint
            try:
                response = self.session.get(f"{BACKEND_URL}/api/auth/google/test-info", timeout=5)
                if response.status_code == 200:
                    backend_config = response.json()
                    env_checks["backend_google_configured"] = backend_config.get("google_client_id_configured", False)
                    env_checks["mock_tokens_enabled"] = backend_config.get("mock_tokens_enabled", False)
            except Exception:
                env_checks["backend_google_configured"] = False
                env_checks["mock_tokens_enabled"] = False
            
            config_score = sum(1 for check in env_checks.values() if check)
            config_complete = config_score >= 3  # At least 3/5 should pass
            
            self.log_result(TestResult(
                name="Environment Variables Configuration",
                passed=config_complete,
                message=f"Environment configuration: {config_score}/{len(env_checks)} requirements met",
                details=env_checks
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Environment Variables Configuration",
                passed=False,
                message=f"Environment configuration test failed: {e}"
            ))
    
    def test_error_handling_comprehensive(self):
        """Test 6: Comprehensive Error Handling"""
        try:
            error_scenarios = []
            
            # Test 1: Invalid mock token format
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"id_token": "invalid_mock_format"},
                    timeout=5
                )
                error_scenarios.append({
                    "scenario": "invalid_mock_format",
                    "status": response.status_code,
                    "handled": response.status_code in [400, 422],
                    "response": response.text[:200]
                })
            except Exception as e:
                error_scenarios.append({
                    "scenario": "invalid_mock_format",
                    "status": "error",
                    "handled": False,
                    "error": str(e)
                })
            
            # Test 2: Empty token
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"id_token": ""},
                    timeout=5
                )
                error_scenarios.append({
                    "scenario": "empty_token",
                    "status": response.status_code,
                    "handled": response.status_code in [400, 422],
                    "response": response.text[:200]
                })
            except Exception as e:
                error_scenarios.append({
                    "scenario": "empty_token",
                    "status": "error",
                    "handled": False,
                    "error": str(e)
                })
            
            # Test 3: Missing id_token field
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"wrong_field": "value"},
                    timeout=5
                )
                error_scenarios.append({
                    "scenario": "missing_id_token_field",
                    "status": response.status_code,
                    "handled": response.status_code in [400, 422],
                    "response": response.text[:200]
                })
            except Exception as e:
                error_scenarios.append({
                    "scenario": "missing_id_token_field",
                    "status": "error",
                    "handled": False,
                    "error": str(e)
                })
            
            # Test 4: Invalid email in mock token
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"id_token": "mock_invalid_email_format_test"},
                    timeout=5
                )
                error_scenarios.append({
                    "scenario": "invalid_email_in_mock",
                    "status": response.status_code,
                    "handled": response.status_code in [400, 422],
                    "response": response.text[:200]
                })
            except Exception as e:
                error_scenarios.append({
                    "scenario": "invalid_email_in_mock",
                    "status": "error",
                    "handled": False,
                    "error": str(e)
                })
            
            handled_count = sum(1 for scenario in error_scenarios if scenario["handled"])
            all_handled = handled_count == len(error_scenarios)
            
            self.log_result(TestResult(
                name="Comprehensive Error Handling",
                passed=all_handled,
                message=f"{handled_count}/{len(error_scenarios)} error scenarios handled correctly",
                details={"scenarios": error_scenarios}
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Comprehensive Error Handling",
                passed=False,
                message=f"Error handling test failed: {e}"
            ))
    
    def test_user_creation_and_management(self):
        """Test 7: User Creation and Management"""
        try:
            # Test creating multiple users with different mock tokens
            test_users = [
                ("newuser1@example.com", "New User One"),
                ("newuser2@example.com", "New User Two"),
                ("existing@example.com", "Existing User")  # This one we'll test twice
            ]
            
            user_creation_results = []
            
            for email, name in test_users:
                mock_token = self.create_proper_mock_token(email, name)
                
                try:
                    response = self.session.post(
                        f"{BACKEND_URL}/api/auth/google",
                        json={"id_token": mock_token},
                        timeout=10
                    )
                    
                    user_creation_results.append({
                        "email": email,
                        "status": response.status_code,
                        "success": response.status_code == 200,
                        "data": response.json() if response.status_code == 200 else None
                    })
                    
                except Exception as e:
                    user_creation_results.append({
                        "email": email,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    })
            
            # Test existing user (create the same user again)
            existing_email = test_users[2][0]  # "existing@example.com"
            existing_name = test_users[2][1]
            mock_token = self.create_proper_mock_token(existing_email, existing_name)
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"id_token": mock_token},
                    timeout=10
                )
                
                user_creation_results.append({
                    "email": f"{existing_email} (duplicate)",
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else None
                })
                
            except Exception as e:
                user_creation_results.append({
                    "email": f"{existing_email} (duplicate)",
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
            
            successful_creations = sum(1 for result in user_creation_results if result["success"])
            all_successful = successful_creations == len(user_creation_results)
            
            self.log_result(TestResult(
                name="User Creation and Management",
                passed=all_successful,
                message=f"{successful_creations}/{len(user_creation_results)} user operations successful",
                details={"user_operations": user_creation_results}
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="User Creation and Management",
                passed=False,
                message=f"User creation test failed: {e}"
            ))
    
    def test_complete_authentication_flow(self):
        """Test 8: Complete Authentication Flow End-to-End"""
        try:
            # Step 1: Create a new user via Google OAuth
            test_email = "flowtest@example.com"
            test_name = "Flow Test User"
            mock_token = self.create_proper_mock_token(test_email, test_name)
            
            # Step 2: Authenticate
            auth_response = self.session.post(
                f"{BACKEND_URL}/api/auth/google",
                json={"id_token": mock_token},
                timeout=10
            )
            
            if auth_response.status_code != 200:
                self.log_result(TestResult(
                    name="Complete Authentication Flow",
                    passed=False,
                    message=f"Authentication step failed: HTTP {auth_response.status_code}",
                    critical=True
                ))
                return
            
            auth_data = auth_response.json()
            access_token = auth_data["access_token"]
            
            # Step 3: Test authenticated operations
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get user status
            status_response = self.session.get(f"{BACKEND_URL}/api/chat/status", headers=headers, timeout=5)
            status_ok = status_response.status_code == 200
            
            # Get conversations
            convs_response = self.session.get(f"{BACKEND_URL}/api/chat/conversations", headers=headers, timeout=5)
            convs_ok = convs_response.status_code == 200
            
            # Step 4: Test message sending with FormData
            message_ok = True
            try:
                # Create FormData manually
                boundary = "----formdata-test-boundary"
                form_data = f'--{boundary}\r\nContent-Disposition: form-data; name="message"\r\n\r\nTest authenticated question\r\n--{boundary}--\r\n'
                
                message_headers = {
                    **headers,
                    "Content-Type": f"multipart/form-data; boundary={boundary}"
                }
                
                message_response = self.session.post(
                    f"{BACKEND_URL}/api/chat/message",
                    data=form_data,
                    headers=message_headers,
                    timeout=30
                )
                message_ok = message_response.status_code == 200
            except Exception as e:
                print(f"Message test warning: {e}")
                message_ok = False  # Not critical for this test
            
            flow_working = status_ok and convs_ok
            
            self.log_result(TestResult(
                name="Complete Authentication Flow",
                passed=flow_working,
                message="End-to-end authentication flow working" if flow_working else "Authentication flow has issues",
                details={
                    "authentication": auth_response.status_code == 200,
                    "user_status": status_ok,
                    "conversations": convs_ok,
                    "messaging": message_ok,
                    "user_email": auth_data.get("user", {}).get("email"),
                    "tokens_provided": "access_token" in auth_data and "refresh_token" in auth_data
                },
                critical=not flow_working
            ))
            
        except Exception as e:
            self.log_result(TestResult(
                name="Complete Authentication Flow",
                passed=False,
                message=f"Complete flow test failed: {e}",
                critical=True
            ))
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("=" * 70)
        print("🔍 FRONTEND GOOGLE OAUTH COMPREHENSIVE TESTING - FIXED VERSION")
        print("=" * 70)
        print()
        
        # Run all tests
        test_methods = [
            self.test_backend_google_auth_proper_mock,
            self.test_google_auth_configuration_endpoint,
            self.test_authenticated_endpoints_access,
            self.test_frontend_google_button_integration,
            self.test_environment_variables_configuration,
            self.test_error_handling_comprehensive,
            self.test_user_creation_and_management,
            self.test_complete_authentication_flow
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(TestResult(
                    name=test_method.__name__.replace("test_", "").replace("_", " ").title(),
                    passed=False,
                    message=f"Test execution failed: {e}",
                    critical=True
                ))
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate final test summary report"""
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY REPORT")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r.passed and r.critical)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Critical Failures: {critical_failures} 🚨")
        print()
        
        if critical_failures > 0:
            print("🚨 CRITICAL ISSUES DETECTED:")
            for result in self.results:
                if not result.passed and result.critical:
                    print(f"  - {result.name}: {result.message}")
            print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
            print()
        
        # Detailed analysis
        functionality_score = passed_tests / total_tests
        
        if critical_failures == 0 and functionality_score >= 0.9:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - READY FOR PRODUCTION")
            print("The Google OAuth frontend implementation meets all requirements.")
        elif critical_failures == 0 and functionality_score >= 0.75:
            print("✅ OVERALL ASSESSMENT: GOOD - READY FOR PRODUCTION WITH MINOR IMPROVEMENTS")
            print("The implementation works well with some minor issues to address.")
        elif critical_failures == 0 and functionality_score >= 0.5:
            print("⚠️  OVERALL ASSESSMENT: ACCEPTABLE - NEEDS IMPROVEMENTS BEFORE PRODUCTION")
            print("The implementation works but has several issues that should be addressed.")
        else:
            print("🛑 OVERALL ASSESSMENT: NOT READY FOR PRODUCTION")
            print("Critical issues must be resolved before deployment.")
        
        print()
        print("📋 DETAILED ANALYSIS:")
        print(f"   - Functionality Score: {functionality_score:.1%}")
        print(f"   - Critical Issues: {critical_failures}")
        print(f"   - Overall Reliability: {'High' if critical_failures == 0 else 'Low'}")
        
        print("=" * 70)

def main():
    """Main test execution function"""
    tester = FrontendGoogleOAuthTesterFixed()
    tester.run_all_tests()

if __name__ == "__main__":
    main()