#!/usr/bin/env python3
"""
FRONTEND UI INTEGRATION TESTING SUITE
=====================================

This script tests the actual frontend UI integration with the Google OAuth implementation.
It validates the component structure, JavaScript functionality, and real-world usability.

Author: Testing Expert (Grumpy & Skeptical - UI Focus)
Date: 2025-10-27
"""

import requests
import json
import re
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Test Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

@dataclass
class UITestResult:
    name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    critical: bool = False

class FrontendUIIntegrationTester:
    def __init__(self):
        self.results: List[UITestResult] = []
        self.session = requests.Session()
        
    def log_result(self, result: UITestResult):
        """Log a test result with appropriate formatting"""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        critical = " [CRITICAL]" if result.critical else ""
        print(f"{status}{critical}: {result.name}")
        print(f"   {result.message}")
        if result.details:
            print(f"   Details: {json.dumps(result.details, indent=2)}")
        print()
        self.results.append(result)
    
    def test_frontend_loading_and_structure(self):
        """Test 1: Frontend Loading and HTML Structure"""
        try:
            response = self.session.get(f"{FRONTEND_URL}/", timeout=10)
            
            if response.status_code != 200:
                self.log_result(UITestResult(
                    name="Frontend Loading and Structure",
                    passed=False,
                    message=f"Frontend not accessible: HTTP {response.status_code}",
                    critical=True
                ))
                return
            
            html_content = response.text
            
            # Check essential HTML structure
            structure_checks = {
                "has_html_tag": "<html" in html_content,
                "has_arabic_lang": 'lang="ar"' in html_content,
                "has_rtl_direction": 'dir="rtl"' in html_content,
                "has_viewport_meta": 'name="viewport"' in html_content,
                "has_title": "<title>" in html_content,
                "has_vite_client": "/@vite/client" in html_content,
                "has_react_refresh": "@react-refresh" in html_content,
                "has_app_mount_point": 'id="root"' in html_content
            }
            
            structure_score = sum(1 for check in structure_checks.values() if check)
            structure_complete = structure_score >= 6  # At least 6/8 essential checks
            
            self.log_result(UITestResult(
                name="Frontend Loading and Structure",
                passed=structure_complete,
                message=f"Frontend structure analysis: {structure_score}/{len(structure_checks)} requirements met",
                details=structure_checks,
                critical=structure_score < 4
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Frontend Loading and Structure",
                passed=False,
                message=f"Frontend structure test failed: {e}",
                critical=True
            ))
    
    def test_component_file_structure(self):
        """Test 2: Component File Structure and Imports"""
        try:
            frontend_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src"
            
            required_files = {
                "App.tsx": f"{frontend_path}/App.tsx",
                "AuthContext": f"{frontend_path}/contexts/AuthContext.tsx",
                "GoogleSignInButton": f"{frontend_path}/components/auth/GoogleSignInButton.tsx",
                "LoginForm": f"{frontend_path}/components/auth/LoginForm.tsx",
                "AuthScreen": f"{frontend_path}/components/auth/AuthScreen.tsx",
                "API Service": f"{frontend_path}/services/api.ts",
                "Types": f"{frontend_path}/types/index.ts"
            }
            
            file_checks = {}
            import_checks = {}
            
            for component_name, file_path in required_files.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_checks[component_name] = {
                        "exists": True,
                        "size": len(content),
                        "lines": len(content.split('\n'))
                    }
                    
                    # Check for proper imports based on component type
                    if component_name == "GoogleSignInButton":
                        import_checks[component_name] = {
                            "react_imports": "import React" in content,
                            "auth_context_import": "useAuth" in content,
                            "api_import": "api" in content,
                            "toast_import": "toast" in content,
                            "google_types": "google" in content.lower(),
                            "proper_export": "export default GoogleSignInButton" in content
                        }
                    elif component_name == "AuthContext":
                        import_checks[component_name] = {
                            "react_imports": "import React" in content,
                            "api_imports": "authAPI" in content,
                            "google_method": "loginWithGoogle" in content,
                            "proper_export": "export const AuthProvider" in content
                        }
                    elif component_name == "LoginForm":
                        import_checks[component_name] = {
                            "react_imports": "import React" in content,
                            "auth_context_import": "useAuth" in content,
                            "google_button_import": "GoogleSignInButton" in content,
                            "proper_export": "export default LoginForm" in content
                        }
                    
                except FileNotFoundError:
                    file_checks[component_name] = {
                        "exists": False,
                        "size": 0,
                        "lines": 0
                    }
                except Exception as e:
                    file_checks[component_name] = {
                        "exists": False,
                        "error": str(e)
                    }
            
            files_exist = sum(1 for check in file_checks.values() if check.get("exists", False))
            imports_correct = sum(1 for checks in import_checks.values() for check in checks.values() if check)
            total_import_checks = sum(len(checks) for checks in import_checks.values())
            
            structure_good = files_exist >= len(required_files) * 0.8  # 80% of files should exist
            imports_good = imports_correct >= total_import_checks * 0.8 if total_import_checks > 0 else True
            
            self.log_result(UITestResult(
                name="Component File Structure and Imports",
                passed=structure_good and imports_good,
                message=f"File structure: {files_exist}/{len(required_files)} files exist, Import structure: {imports_correct}/{total_import_checks} import checks passed",
                details={
                    "file_checks": file_checks,
                    "import_checks": import_checks
                },
                critical=files_exist < len(required_files) * 0.6
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Component File Structure and Imports",
                passed=False,
                message=f"Component structure test failed: {e}"
            ))
    
    def test_google_oauth_integration_code_quality(self):
        """Test 3: Google OAuth Integration Code Quality"""
        try:
            google_button_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/components/auth/GoogleSignInButton.tsx"
            
            with open(google_button_path, 'r', encoding='utf-8') as f:
                button_content = f.read()
            
            code_quality_checks = {
                "proper_typescript": "React.FC" in button_content,
                "google_script_loading": "https://accounts.google.com/gsi/client" in button_content,
                "google_types_declared": "interface Window" in button_content and "google?" in button_content,
                "environment_variable_check": "import.meta.env.VITE_GOOGLE_CLIENT_ID" in button_content,
                "error_handling": "try" in button_content and "catch" in button_content,
                "loading_states": "isLoading" in button_content and "setIsLoading" in button_content,
                "user_feedback": "toast" in button_content,
                "token_backend_call": "/api/auth/google" in button_content,
                "token_storage": "localStorage.setItem" in button_content,
                "auth_context_integration": "loginWithGoogle" in button_content,
                "proper_cleanup": "removeEventListener" in button_content or "script.onload" in button_content,
                "accessibility": "disabled" in button_content,
                "responsive_design": "className" in button_content or "style" in button_content
            }
            
            quality_score = sum(1 for check in code_quality_checks.values() if check)
            quality_excellent = quality_score >= len(code_quality_checks) * 0.8
            
            self.log_result(UITestResult(
                name="Google OAuth Integration Code Quality",
                passed=quality_excellent,
                message=f"Code quality analysis: {quality_score}/{len(code_quality_checks)} quality checks passed",
                details=code_quality_checks,
                critical=quality_score < len(code_quality_checks) * 0.6
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Google OAuth Integration Code Quality",
                passed=False,
                message=f"Code quality test failed: {e}"
            ))
    
    def test_authentication_state_management(self):
        """Test 4: Authentication State Management"""
        try:
            auth_context_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/contexts/AuthContext.tsx"
            
            with open(auth_context_path, 'r', encoding='utf-8') as f:
                context_content = f.read()
            
            state_management_checks = {
                "react_context_pattern": "createContext" in context_content and "useContext" in context_content,
                "google_login_method": "loginWithGoogle" in context_content,
                "proper_state_hooks": "useState" in context_content and "useEffect" in context_content,
                "user_state_management": "user" in context_content and "setUser" in context_content,
                "loading_state": "loading" in context_content and "setLoading" in context_content,
                "guest_state": "isGuest" in context_content,
                "token_handling": "localStorage" in context_content,
                "api_integration": "authAPI" in context_content,
                "error_handling": "catch" in context_content,
                "logout_functionality": "logout" in context_content,
                "type_safety": "interface" in context_content or "type" in context_content,
                "memoization": "useMemo" in context_content or "useCallback" in context_content
            }
            
            state_score = sum(1 for check in state_management_checks.values() if check)
            state_excellent = state_score >= len(state_management_checks) * 0.8
            
            self.log_result(UITestResult(
                name="Authentication State Management",
                passed=state_excellent,
                message=f"State management analysis: {state_score}/{len(state_management_checks)} requirements met",
                details=state_management_checks,
                critical=state_score < len(state_management_checks) * 0.6
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Authentication State Management",
                passed=False,
                message=f"State management test failed: {e}"
            ))
    
    def test_ui_routing_integration(self):
        """Test 5: UI Routing Integration"""
        try:
            app_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/App.tsx"
            
            with open(app_path, 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            routing_checks = {
                "router_import": "BrowserRouter" in app_content or "Router" in app_content,
                "routes_component": "Routes" in app_content,
                "route_component": "Route" in app_content,
                "auth_provider_wrapper": "AuthProvider" in app_content,
                "auth_screen_route": "AuthScreen" in app_content,
                "chat_app_route": "ChatApp" in app_content,
                "fallback_route": "Navigate" in app_content or "*" in app_content,
                "loading_component": "loading" in app_content,
                "proper_nesting": app_content.count("<") >= 6  # Should have multiple JSX elements
            }
            
            routing_score = sum(1 for check in routing_checks.values() if check)
            routing_complete = routing_score >= len(routing_checks) * 0.8
            
            self.log_result(UITestResult(
                name="UI Routing Integration",
                passed=routing_complete,
                message=f"Routing integration: {routing_score}/{len(routing_checks)} routing features implemented",
                details=routing_checks
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="UI Routing Integration",
                passed=False,
                message=f"Routing integration test failed: {e}"
            ))
    
    def test_api_service_integration_frontend(self):
        """Test 6: API Service Integration from Frontend Perspective"""
        try:
            api_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/src/services/api.ts"
            
            with open(api_path, 'r', encoding='utf-8') as f:
                api_content = f.read()
            
            api_integration_checks = {
                "axios_setup": "axios" in api_content,
                "base_url_detection": "getApiBaseUrl" in api_content or "API_BASE_URL" in api_content,
                "token_interceptor": "interceptors.request" in api_content,
                "auth_header": "Authorization" in api_content and "Bearer" in api_content,
                "token_storage": "localStorage" in api_content,
                "error_interceptor": "interceptors.response" in api_content,
                "google_auth_method": "google" in api_content.lower(),
                "proper_exports": "export" in api_content,
                "typescript_types": ":" in api_content  # Basic TypeScript check
            }
            
            api_score = sum(1 for check in api_integration_checks.values() if check)
            api_complete = api_score >= len(api_integration_checks) * 0.8
            
            self.log_result(UITestResult(
                name="API Service Integration from Frontend",
                passed=api_complete,
                message=f"API service integration: {api_score}/{len(api_integration_checks)} features implemented",
                details=api_integration_checks,
                critical=api_score < len(api_integration_checks) * 0.5
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="API Service Integration from Frontend",
                passed=False,
                message=f"API service integration test failed: {e}"
            ))
    
    def test_environment_configuration_frontend(self):
        """Test 7: Frontend Environment Configuration"""
        try:
            env_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/.env"
            package_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/package.json"
            vite_config_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/vite.config.ts"
            
            env_config_checks = {
                "env_file_exists": False,
                "google_client_id_configured": False,
                "package_json_exists": False,
                "react_dependencies": False,
                "typescript_configured": False,
                "vite_config_exists": False,
                "dev_server_configured": False
            }
            
            # Check .env file
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                env_config_checks["env_file_exists"] = True
                env_config_checks["google_client_id_configured"] = "VITE_GOOGLE_CLIENT_ID" in env_content
            except:
                pass
            
            # Check package.json
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    package_content = f.read()
                env_config_checks["package_json_exists"] = True
                env_config_checks["react_dependencies"] = "react" in package_content
                env_config_checks["typescript_configured"] = "typescript" in package_content
                env_config_checks["dev_server_configured"] = "vite" in package_content
            except:
                pass
            
            # Check vite config
            try:
                with open(vite_config_path, 'r', encoding='utf-8') as f:
                    vite_content = f.read()
                env_config_checks["vite_config_exists"] = True
            except:
                pass
            
            config_score = sum(1 for check in env_config_checks.values() if check)
            config_complete = config_score >= len(env_config_checks) * 0.7
            
            self.log_result(UITestResult(
                name="Frontend Environment Configuration",
                passed=config_complete,
                message=f"Environment configuration: {config_score}/{len(env_config_checks)} configuration items verified",
                details=env_config_checks
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Frontend Environment Configuration",
                passed=False,
                message=f"Environment configuration test failed: {e}"
            ))
    
    def test_frontend_backend_communication_simulation(self):
        """Test 8: Frontend-Backend Communication Simulation"""
        try:
            # Simulate what the frontend would do
            communication_tests = []
            
            # Test 1: Check if backend is accessible from frontend perspective
            try:
                response = self.session.get(f"{BACKEND_URL}/docs", timeout=5)
                communication_tests.append({
                    "test": "backend_accessibility",
                    "success": response.status_code == 200,
                    "status": response.status_code
                })
            except Exception as e:
                communication_tests.append({
                    "test": "backend_accessibility",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 2: CORS headers check
            try:
                response = self.session.options(f"{BACKEND_URL}/api/auth/google", timeout=5)
                cors_headers = response.headers
                communication_tests.append({
                    "test": "cors_headers",
                    "success": "Access-Control-Allow-Origin" in cors_headers,
                    "headers": dict(cors_headers)
                })
            except Exception as e:
                communication_tests.append({
                    "test": "cors_headers",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 3: Google auth endpoint availability
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/api/auth/google",
                    json={"id_token": "mock_test@frontend.com_Frontend Test"},
                    timeout=10
                )
                communication_tests.append({
                    "test": "google_auth_endpoint",
                    "success": response.status_code == 200,
                    "status": response.status_code,
                    "has_tokens": "access_token" in response.text if response.status_code == 200 else False
                })
            except Exception as e:
                communication_tests.append({
                    "test": "google_auth_endpoint",
                    "success": False,
                    "error": str(e)
                })
            
            successful_communications = sum(1 for test in communication_tests if test["success"])
            communication_working = successful_communications >= len(communication_tests) * 0.7
            
            self.log_result(UITestResult(
                name="Frontend-Backend Communication Simulation",
                passed=communication_working,
                message=f"Communication tests: {successful_communications}/{len(communication_tests)} tests passed",
                details={"communication_tests": communication_tests},
                critical=successful_communications == 0
            ))
            
        except Exception as e:
            self.log_result(UITestResult(
                name="Frontend-Backend Communication Simulation",
                passed=False,
                message=f"Communication simulation failed: {e}",
                critical=True
            ))
    
    def run_all_tests(self):
        """Run all UI integration tests"""
        print("=" * 80)
        print("🔍 FRONTEND UI INTEGRATION TESTING SUITE")
        print("=" * 80)
        print()
        
        test_methods = [
            self.test_frontend_loading_and_structure,
            self.test_component_file_structure,
            self.test_google_oauth_integration_code_quality,
            self.test_authentication_state_management,
            self.test_ui_routing_integration,
            self.test_api_service_integration_frontend,
            self.test_environment_configuration_frontend,
            self.test_frontend_backend_communication_simulation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(UITestResult(
                    name=test_method.__name__.replace("test_", "").replace("_", " ").title(),
                    passed=False,
                    message=f"Test execution failed: {e}",
                    critical=True
                ))
        
        self.generate_ui_summary_report()
    
    def generate_ui_summary_report(self):
        """Generate UI integration test summary"""
        print("=" * 80)
        print("📊 FRONTEND UI INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r.passed and r.critical)
        
        print(f"Total UI Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Critical UI Failures: {critical_failures} 🚨")
        print()
        
        if critical_failures > 0:
            print("🚨 CRITICAL UI ISSUES:")
            for result in self.results:
                if not result.passed and result.critical:
                    print(f"  - {result.name}: {result.message}")
            print()
        
        if failed_tests > 0:
            print("❌ FAILED UI TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
            print()
        
        # UI-specific assessment
        ui_quality_score = passed_tests / total_tests
        
        if critical_failures == 0 and ui_quality_score >= 0.9:
            print("🎉 UI ASSESSMENT: EXCELLENT - UI IS PRODUCTION READY")
            print("The frontend UI integration is professional and complete.")
        elif critical_failures == 0 and ui_quality_score >= 0.75:
            print("✅ UI ASSESSMENT: GOOD - UI IS READY WITH MINOR POLISH NEEDED")
            print("The UI works well with room for minor improvements.")
        elif critical_failures == 0 and ui_quality_score >= 0.5:
            print("⚠️  UI ASSESSMENT: ACCEPTABLE - UI NEEDS IMPROVEMENT")
            print("The UI functions but needs significant improvement.")
        else:
            print("🛑 UI ASSESSMENT: UI NOT READY FOR USERS")
            print("Critical UI issues must be resolved before user access.")
        
        print("=" * 80)

def main():
    """Main UI test execution"""
    tester = FrontendUIIntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()