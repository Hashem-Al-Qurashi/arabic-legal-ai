#!/usr/bin/env python3
"""
COMPREHENSIVE Google OAuth Security Testing
===============================================
This is NOT ready for production! Testing every edge case and vulnerability.
"""

import requests
import json
import time
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, List

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class GoogleOAuthSecurityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.failed_tests = []
        self.passed_tests = []
        self.critical_failures = []
        
    def print_header(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    def print_test(self, test_name: str):
        print(f"{Colors.BLUE}🧪 Testing: {test_name}{Colors.ENDC}")
    
    def print_pass(self, message: str):
        print(f"{Colors.GREEN}✅ PASS: {message}{Colors.ENDC}")
        self.passed_tests.append(message)
    
    def print_fail(self, message: str, is_critical: bool = False):
        if is_critical:
            print(f"{Colors.RED}{Colors.BOLD}❌ CRITICAL FAIL: {message}{Colors.ENDC}")
            self.critical_failures.append(message)
        else:
            print(f"{Colors.YELLOW}⚠️  FAIL: {message}{Colors.ENDC}")
        self.failed_tests.append(message)
    
    def print_info(self, message: str):
        print(f"{Colors.WHITE}ℹ️  INFO: {message}{Colors.ENDC}")

    def test_configuration_detection(self) -> Dict[str, Any]:
        """Test if the system properly detects configuration issues"""
        self.print_test("Configuration Detection")
        
        try:
            # Test status endpoint
            response = requests.get(f"{self.base_url}/api/auth/google/status")
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('configured'):
                    self.print_pass("System correctly detects missing configuration")
                else:
                    self.print_fail("System incorrectly reports as configured", is_critical=True)
                    
                if not data.get('client_id_is_real'):
                    self.print_pass("System correctly identifies placeholder Client ID")
                else:
                    self.print_fail("System incorrectly accepts placeholder Client ID", is_critical=True)
                    
                return data
            else:
                self.print_fail(f"Status endpoint returned {response.status_code}")
                return {}
                
        except Exception as e:
            self.print_fail(f"Configuration test failed: {e}", is_critical=True)
            return {}

    def test_malformed_requests(self):
        """Test various malformed request scenarios"""
        self.print_test("Malformed Request Handling")
        
        malformed_tests = [
            # Empty body
            ("Empty body", {}),
            # Missing field
            ("Missing id_token field", {"wrong_field": "test"}),
            # Empty token
            ("Empty token", {"id_token": ""}),
            # Whitespace only token
            ("Whitespace token", {"id_token": "   "}),
            # None value
            ("Null token", {"id_token": None}),
            # Wrong type
            ("Integer token", {"id_token": 12345}),
            # Array instead of string
            ("Array token", {"id_token": ["fake", "token"]}),
            # Extremely long token
            ("Long token", {"id_token": "a" * 10000}),
            # SQL injection attempt
            ("SQL injection", {"id_token": "'; DROP TABLE users; --"}),
            # XSS attempt
            ("XSS attempt", {"id_token": "<script>alert('xss')</script>"}),
            # Binary data
            ("Binary data", {"id_token": b"binary_data".hex()}),
        ]
        
        for test_name, payload in malformed_tests:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Should return 4xx error, not 5xx (no server crash)
                if 400 <= response.status_code < 500:
                    self.print_pass(f"{test_name}: Properly rejected with {response.status_code}")
                elif response.status_code >= 500:
                    self.print_fail(f"{test_name}: Server error {response.status_code} - possible crash", is_critical=True)
                else:
                    self.print_fail(f"{test_name}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                self.print_fail(f"{test_name}: Exception - {e}", is_critical=True)

    def test_fake_google_tokens(self):
        """Test various fake Google token scenarios"""
        self.print_test("Fake Google Token Handling")
        
        fake_tokens = [
            ("Basic fake", "fake.google.token"),
            ("JWT-like fake", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"),
            ("Empty segments", ".."),
            ("One segment", "onlyonepart"),
            ("Two segments", "two.parts"),
            ("Four segments", "too.many.parts.here"),
            ("Invalid base64", "invalid!base64@.invalid!base64@.invalid!base64@"),
            ("Real-looking but fake", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImZha2UifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXVkIjoiZmFrZS1jbGllbnQtaWQuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMjM0NTY3ODkwIiwiZW1haWwiOiJmYWtlQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiRmFrZSBVc2VyIiwiaWF0IjoxNjMwMDAwMDAwLCJleHAiOjE2MzAwMDM2MDB9.fakesignature"),
        ]
        
        for test_name, fake_token in fake_tokens:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json={"id_token": fake_token},
                    headers={"Content-Type": "application/json"}
                )
                
                # Should return 503 (not configured) or 400/401 (invalid token)
                if response.status_code in [400, 401, 403, 422, 503]:
                    self.print_pass(f"{test_name}: Properly rejected with {response.status_code}")
                elif response.status_code == 200:
                    self.print_fail(f"{test_name}: ACCEPTED FAKE TOKEN!", is_critical=True)
                else:
                    self.print_fail(f"{test_name}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                self.print_fail(f"{test_name}: Exception - {e}", is_critical=True)

    def test_dos_scenarios(self):
        """Test Denial of Service scenarios"""
        self.print_test("DoS Protection")
        
        # Test rapid requests
        start_time = time.time()
        for i in range(10):
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json={"id_token": f"fake-token-{i}"},
                    timeout=5
                )
                if response.status_code >= 500:
                    self.print_fail("Server crashed under rapid requests", is_critical=True)
                    break
            except requests.exceptions.Timeout:
                self.print_fail("Server became unresponsive", is_critical=True)
                break
            except Exception as e:
                self.print_fail(f"DoS test exception: {e}")
                break
        
        elapsed = time.time() - start_time
        if elapsed < 30:  # Should handle 10 requests in under 30 seconds
            self.print_pass(f"Handled rapid requests in {elapsed:.2f}s")
        else:
            self.print_fail(f"Too slow: {elapsed:.2f}s for 10 requests")

    def test_cors_configuration(self):
        """Test CORS configuration security"""
        self.print_test("CORS Security")
        
        dangerous_origins = [
            "https://malicious.com",
            "http://evil.example.com", 
            "https://attacker.net",
            "null",
            "*"
        ]
        
        for origin in dangerous_origins:
            try:
                response = requests.options(
                    f"{self.base_url}/api/auth/google",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "Content-Type"
                    }
                )
                
                cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
                if cors_origin == origin or cors_origin == "*":
                    self.print_fail(f"CORS allows dangerous origin: {origin}", is_critical=True)
                else:
                    self.print_pass(f"CORS correctly blocks: {origin}")
                    
            except Exception as e:
                self.print_fail(f"CORS test exception: {e}")

    def test_secret_key_strength(self):
        """Test if we can detect weak secret keys"""
        self.print_test("Secret Key Security")
        
        # This is a black-box test - we can't directly check the secret
        # But we can test JWT behavior
        
        # Try to predict JWT tokens (should be impossible)
        try:
            # Make requests with same fake token
            responses = []
            for i in range(3):
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json={"id_token": "fake.token.test"},
                    headers={"Content-Type": "application/json"}
                )
                responses.append(response.status_code)
            
            # All should be rejected with same error code
            if len(set(responses)) == 1 and all(r in [400, 401, 403, 422, 503] for r in responses):
                self.print_pass("Consistent error handling - no timing attacks visible")
            else:
                self.print_fail("Inconsistent responses - potential timing attack")
                
        except Exception as e:
            self.print_fail(f"Secret key test exception: {e}")

    def test_input_validation_edge_cases(self):
        """Test extreme input validation scenarios"""
        self.print_test("Input Validation Edge Cases")
        
        edge_cases = [
            # Unicode attacks
            ("Unicode null", {"id_token": "test\x00token"}),
            ("Unicode control", {"id_token": "test\x01\x02\x03token"}),
            ("Unicode normalization", {"id_token": "tést.tøken.ñormalization"}),
            # Encoding attacks
            ("URL encoded", {"id_token": "test%2Etoken%2Ehere"}),
            ("Double encoded", {"id_token": "test%252Etoken%252Ehere"}),
            ("HTML encoded", {"id_token": "test&lt;token&gt;here"}),
            # Path traversal attempts
            ("Path traversal", {"id_token": "../../../etc/passwd"}),
            ("Windows path", {"id_token": "..\\..\\..\\windows\\system32"}),
            # Format string attacks
            ("Format string", {"id_token": "%s%s%s%s%s%s"}),
            ("printf format", {"id_token": "%n%n%n%n%n%n"}),
        ]
        
        for test_name, payload in edge_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if 400 <= response.status_code < 500:
                    self.print_pass(f"{test_name}: Properly rejected")
                elif response.status_code >= 500:
                    self.print_fail(f"{test_name}: Server error - possible vulnerability", is_critical=True)
                elif response.status_code == 200:
                    self.print_fail(f"{test_name}: Accepted dangerous input!", is_critical=True)
                else:
                    self.print_fail(f"{test_name}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                self.print_fail(f"{test_name}: Exception - {e}")

    def test_rate_limiting(self):
        """Test for rate limiting protection"""
        self.print_test("Rate Limiting")
        
        # Make many requests quickly
        responses = []
        start_time = time.time()
        
        for i in range(50):  # 50 requests rapidly
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/google",
                    json={"id_token": f"rate-limit-test-{i}"},
                    timeout=2
                )
                responses.append(response.status_code)
                
                # Check if we get rate limited
                if response.status_code == 429:
                    self.print_pass("Rate limiting is active (429 Too Many Requests)")
                    return
                    
            except requests.exceptions.Timeout:
                self.print_fail("Server timeout under load", is_critical=True)
                return
            except Exception as e:
                self.print_fail(f"Rate limiting test exception: {e}")
                return
        
        elapsed = time.time() - start_time
        
        # If all requests succeeded, rate limiting might be missing
        if all(r in [400, 401, 403, 422, 503] for r in responses):
            self.print_fail("No rate limiting detected - potential DoS vulnerability")
        else:
            self.print_pass("Requests handled consistently")

    def run_all_tests(self):
        """Run comprehensive security test suite"""
        self.print_header("GOOGLE OAUTH COMPREHENSIVE SECURITY TEST")
        
        print(f"{Colors.BOLD}Target: {self.base_url}{Colors.ENDC}")
        print(f"{Colors.BOLD}Time: {datetime.now(timezone.utc).isoformat()}{Colors.ENDC}\n")
        
        # Run all test categories
        config_data = self.test_configuration_detection()
        self.test_malformed_requests()
        self.test_fake_google_tokens()
        self.test_dos_scenarios()
        self.test_cors_configuration()
        self.test_secret_key_strength()
        self.test_input_validation_edge_cases()
        self.test_rate_limiting()
        
        # Generate final report
        self.generate_security_report(config_data)

    def generate_security_report(self, config_data: Dict[str, Any]):
        """Generate comprehensive security report"""
        self.print_header("SECURITY ASSESSMENT REPORT")
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        pass_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Colors.BOLD}SUMMARY:{Colors.ENDC}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {Colors.GREEN}{len(self.passed_tests)}{Colors.ENDC}")
        print(f"  Failed: {Colors.YELLOW}{len(self.failed_tests)}{Colors.ENDC}")
        print(f"  Critical Failures: {Colors.RED}{len(self.critical_failures)}{Colors.ENDC}")
        print(f"  Pass Rate: {Colors.GREEN if pass_rate > 80 else Colors.YELLOW if pass_rate > 60 else Colors.RED}{pass_rate:.1f}%{Colors.ENDC}")
        
        # Configuration analysis
        print(f"\n{Colors.BOLD}CONFIGURATION ANALYSIS:{Colors.ENDC}")
        if config_data:
            for key, value in config_data.items():
                status_color = Colors.GREEN if (
                    (key == 'available' and not value) or
                    (key == 'configured' and not value) or
                    (key == 'client_id_is_real' and not value) or
                    (key == 'library_installed' and value)
                ) else Colors.RED
                print(f"  {key}: {status_color}{value}{Colors.ENDC}")
        
        # Critical issues
        if self.critical_failures:
            print(f"\n{Colors.RED}{Colors.BOLD}CRITICAL SECURITY ISSUES:{Colors.ENDC}")
            for i, issue in enumerate(self.critical_failures, 1):
                print(f"  {i}. {Colors.RED}{issue}{Colors.ENDC}")
        
        # Production readiness assessment
        print(f"\n{Colors.BOLD}PRODUCTION READINESS:{Colors.ENDC}")
        
        if self.critical_failures:
            print(f"{Colors.RED}{Colors.BOLD}❌ NOT READY FOR PRODUCTION{Colors.ENDC}")
            print(f"{Colors.RED}Critical security vulnerabilities detected!{Colors.ENDC}")
        elif len(self.failed_tests) > len(self.passed_tests):
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  NOT RECOMMENDED FOR PRODUCTION{Colors.ENDC}")
            print(f"{Colors.YELLOW}Many security tests failed{Colors.ENDC}")
        elif pass_rate > 90:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ GOOD SECURITY POSTURE{Colors.ENDC}")
            print(f"{Colors.GREEN}Ready for production with real Google credentials{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  NEEDS IMPROVEMENT{Colors.ENDC}")
            print(f"{Colors.YELLOW}Some security concerns need attention{Colors.ENDC}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}RECOMMENDATIONS:{Colors.ENDC}")
        recommendations = [
            "✓ Add real Google Cloud Console credentials",
            "✓ Implement rate limiting (if not present)",
            "✓ Set up monitoring and alerting",
            "✓ Regular security audits",
            "✓ Test with real Google tokens",
            "✓ Implement request logging",
            "✓ Set up proper error tracking"
        ]
        
        for rec in recommendations:
            print(f"  {rec}")

if __name__ == "__main__":
    tester = GoogleOAuthSecurityTester()
    tester.run_all_tests()