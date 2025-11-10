#!/usr/bin/env python3
"""
Test script for REAL Google OAuth integration
This script verifies the configuration is ready for real Google authentication
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_configuration():
    """Test that Google OAuth is properly configured"""
    print("🔐 Testing Real Google OAuth Configuration\n")
    
    # Check environment variables
    print("1. Environment Variables:")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not google_client_id or google_client_id.startswith("your-google-client-id"):
        print("❌ GOOGLE_CLIENT_ID not configured in .env")
        print("   Please follow GOOGLE_OAUTH_SETUP.md to get your credentials")
        return False
    else:
        print(f"✅ GOOGLE_CLIENT_ID configured: {google_client_id[:20]}...")
    
    if not google_client_secret or google_client_secret.startswith("your-google-client-secret"):
        print("❌ GOOGLE_CLIENT_SECRET not configured in .env")
        print("   Please follow GOOGLE_OAUTH_SETUP.md to get your credentials")
        return False
    else:
        print(f"✅ GOOGLE_CLIENT_SECRET configured: {google_client_secret[:10]}...")
    
    # Check backend configuration
    print("\n2. Backend Configuration:")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/status")
        if response.status_code == 200:
            data = response.json()
            if data.get("available") and data.get("configured"):
                print("✅ Backend Google OAuth properly configured")
            else:
                print("❌ Backend configuration issues:")
                print(f"   Available: {data.get('available')}")
                print(f"   Configured: {data.get('configured')}")
                return False
        else:
            print(f"❌ Backend status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Check test info endpoint
    print("\n3. Test Configuration Endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/test-info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Environment: {data.get('environment')}")
            print(f"✅ Client ID configured: {data.get('google_client_id_configured')}")
            print(f"✅ Google Auth available: {data.get('google_auth_available')}")
            print(f"✅ Requires real tokens: {data.get('requires_real_google_token')}")
            
            if not data.get('requires_real_google_token'):
                print("⚠️ Warning: System still accepting mock tokens")
        else:
            print(f"❌ Test info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test info request failed: {e}")
        return False
    
    # Test with invalid token (should fail)
    print("\n4. Invalid Token Rejection Test:")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/google", json={
            "id_token": "invalid-token-should-fail"
        })
        if response.status_code in [400, 401, 500]:
            print("✅ Invalid tokens properly rejected")
        else:
            print(f"❌ Invalid token not rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid token test failed: {e}")
        return False
    
    return True

def test_frontend_config():
    """Check if frontend is configured"""
    print("\n5. Frontend Configuration:")
    
    frontend_env_path = "/home/sakr_quraish/Projects/legal/arabic_legal_ai/frontend/.env"
    
    try:
        with open(frontend_env_path, 'r') as f:
            content = f.read()
            
        if "your-google-client-id-from-console" in content:
            print("❌ Frontend VITE_GOOGLE_CLIENT_ID not configured")
            print("   Please update frontend/.env with your Google Client ID")
            return False
        else:
            print("✅ Frontend Google Client ID configured")
            return True
    except FileNotFoundError:
        print("❌ Frontend .env file not found")
        return False

def show_next_steps():
    """Show what user needs to do next"""
    print("\n" + "="*60)
    print("🚀 NEXT STEPS TO COMPLETE REAL GOOGLE OAUTH SETUP:")
    print("="*60)
    print()
    print("1. 📖 READ the setup guide:")
    print("   cat GOOGLE_OAUTH_SETUP.md")
    print()
    print("2. 🌐 Create Google Cloud project and OAuth credentials:")
    print("   https://console.cloud.google.com/")
    print()
    print("3. ⚙️ Update your .env files with REAL credentials:")
    print("   backend/.env  -> GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    print("   frontend/.env -> VITE_GOOGLE_CLIENT_ID")
    print()
    print("4. 🔄 Restart both services:")
    print("   Backend: python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("   Frontend: npm run dev")
    print()
    print("5. 🧪 Test with your real Google account:")
    print("   Visit http://localhost:3000 and click 'Sign in with Google'")
    print()

def main():
    """Run all configuration tests"""
    print("🔐 REAL GOOGLE OAUTH CONFIGURATION TEST")
    print("=" * 60)
    
    config_ok = test_configuration()
    frontend_ok = test_frontend_config()
    
    print("\n" + "="*60)
    if config_ok and frontend_ok:
        print("🎉 CONFIGURATION COMPLETE!")
        print("✅ Your Google OAuth is ready for REAL authentication")
        print("🚀 Users can now sign in with their Google accounts")
        print()
        print("Visit: http://localhost:3000")
        print("Click: 'Sign in with Google'")
        print("Test: Real Google authentication flow")
    else:
        print("❌ CONFIGURATION INCOMPLETE")
        print("⚠️ You need to complete the setup before real Google OAuth will work")
        show_next_steps()
    
    return config_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)