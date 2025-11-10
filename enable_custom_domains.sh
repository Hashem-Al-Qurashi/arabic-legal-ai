#!/bin/bash

# Script to enable custom domains after certificate validation
# Run this when DNS has propagated and certificate is validated

set -e

echo "🔍 Checking certificate validation status..."

# Check certificate status
CERT_STATUS=$(aws acm describe-certificate \
    --region us-east-1 \
    --certificate-arn arn:aws:acm:us-east-1:940053359036:certificate/62ae47d6-af9d-4c6d-843e-7c52811034cc \
    --query "Certificate.Status" \
    --output text)

echo "Certificate status: $CERT_STATUS"

if [ "$CERT_STATUS" != "ISSUED" ]; then
    echo "❌ Certificate not yet validated. Current status: $CERT_STATUS"
    echo "Please wait for DNS propagation and certificate validation before running this script."
    echo ""
    echo "You can check status with:"
    echo "aws acm describe-certificate --region us-east-1 --certificate-arn arn:aws:acm:us-east-1:940053359036:certificate/62ae47d6-af9d-4c6d-843e-7c52811034cc"
    exit 1
fi

echo "✅ Certificate is validated! Enabling custom domains..."

# Apply terraform with custom domains
cd infrastructure
terraform apply -auto-approve

echo ""
echo "🎉 Custom domains enabled successfully!"
echo ""
echo "Your sites are now available at:"
echo "  Frontend: https://hokm.ai"
echo "  API: https://api.hokm.ai"
echo ""
echo "Note: CloudFront distribution updates can take 10-15 minutes to propagate globally."