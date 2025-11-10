#!/bin/bash

# Quick certificate status checker
export AWS_PROFILE=newaccount

echo "🔍 Checking certificate validation status..."
STATUS=$(aws acm describe-certificate \
    --region us-east-1 \
    --certificate-arn arn:aws:acm:us-east-1:940053359036:certificate/62ae47d6-af9d-4c6d-843e-7c52811034cc \
    --query "Certificate.Status" \
    --output text)

echo "Certificate Status: $STATUS"

if [ "$STATUS" = "ISSUED" ]; then
    echo "✅ Certificate is validated! Ready to enable custom domains."
    echo "Run: ./enable_custom_domains.sh"
else
    echo "⏳ Certificate still pending validation."
    echo "Current working URLs:"
    echo "  Frontend: https://d2a614vyz9m2g5.cloudfront.net"
    echo "  API: https://dw9g4qpwv2fx5.cloudfront.net"
    echo ""
    echo "Try again in 30 minutes. Certificate validation can take up to 24 hours."
fi