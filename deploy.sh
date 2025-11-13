#!/bin/bash

# Deploy script for hokm-ai infrastructure
echo "🚀 Deploying hokm-ai with Google OAuth fixes..."

# Push to GitHub (you may need to authenticate)
echo "📤 Pushing to GitHub..."
git push origin main

# Check if git push succeeded
if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ GitHub push failed. Please run manually:"
    echo "   git push origin main"
    echo "   or set up GitHub authentication"
fi

echo ""
echo "🏗️ Infrastructure URLs:"
echo "Frontend: https://d3fjlaow1u3j8f.cloudfront.net"
echo "Backend:  https://d3q8vuoyd6a6mx.cloudfront.net"
echo ""
echo "📊 Latest commits:"
git log --oneline -3