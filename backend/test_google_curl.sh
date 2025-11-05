#!/bin/bash

# Google OAuth Backend Testing Script - Manual curl commands
# Usage: bash test_google_curl.sh

echo "========================================="
echo "Google OAuth Backend Testing with curl"
echo "========================================="

BASE_URL="http://localhost:8000"

echo -e "\n1️⃣ Testing Google OAuth Status:"
echo "--------------------------------"
curl -X GET "$BASE_URL/api/auth/google/status" -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n\n2️⃣ Testing Google OAuth Test Info:"
echo "------------------------------------"
curl -X GET "$BASE_URL/api/auth/google/test-info" -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n\n3️⃣ Testing Google Sign-in with Mock Token:"
echo "--------------------------------------------"
echo "Creating new user: testuser@example.com"
curl -X POST "$BASE_URL/api/auth/google" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "mock_testuser@example.com_Test User"}' | python3 -m json.tool

echo -e "\n\n4️⃣ Testing Duplicate Sign-in (existing user):"
echo "-----------------------------------------------"
echo "Signing in again with same email:"
curl -X POST "$BASE_URL/api/auth/google" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "mock_testuser@example.com_Test User Updated"}' | python3 -m json.tool

echo -e "\n\n5️⃣ Testing Invalid Token (should fail):"
echo "-----------------------------------------"
curl -X POST "$BASE_URL/api/auth/google" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "invalid_token_format"}' | python3 -m json.tool

echo -e "\n\n✅ Manual testing complete!"
echo "Check the responses above to verify:"
echo "- Status endpoint returns configuration info"
echo "- Test info shows mock token examples"
echo "- Sign-in creates user and returns token"
echo "- Duplicate sign-in works with existing user"
echo "- Invalid tokens are rejected properly"