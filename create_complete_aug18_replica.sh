#!/bin/bash

echo "🎯 Creating COMPLETE replica of August 18th version (frontend + backend)"
echo "This will be EXACTLY what was working on August 18th"

# Create replica directory
mkdir -p complete_aug18_replica
cd complete_aug18_replica

echo "📦 Step 1: Extract ENTIRE codebase from August 18th image..."

# Run the August 18th container to extract everything
docker run -d --name aug18-full-extract 683342011909.dkr.ecr.eu-central-1.amazonaws.com/hokm-ai/backend:v20250818-123617 sleep 3600

# Copy the entire /app directory (backend)
echo "📁 Extracting backend from /app..."
docker cp aug18-full-extract:/app ./backend

# Also check if there's a frontend build in the image
echo "🔍 Checking for frontend files..."
docker exec aug18-full-extract find / -name "frontend" -type d 2>/dev/null || echo "No frontend directory found in image"
docker exec aug18-full-extract find / -name "dist" -type d 2>/dev/null || echo "No dist directory found in image"
docker exec aug18-full-extract find / -name "*.html" 2>/dev/null | head -5

# Copy any static files or frontend if they exist
docker exec aug18-full-extract ls -la / > container_root_listing.txt
docker exec aug18-full-extract ls -la /usr/share/nginx/html/ 2>/dev/null > nginx_html.txt || echo "No nginx html found"

# Stop container
docker stop aug18-full-extract
docker rm aug18-full-extract

echo "📋 Step 2: Copy current frontend (as of August 18th state)..."
# We need to get frontend from the original repo as it was on Aug 18th
# Check git log for commits around Aug 18th
cd ..
git log --oneline --since="2025-08-17" --until="2025-08-19" > complete_aug18_replica/aug18_git_commits.txt

# Copy current frontend but we'll need to revert it to Aug 18th state
cp -r frontend complete_aug18_replica/

cd complete_aug18_replica

echo "✅ Complete August 18th replica created!"
echo ""
echo "📁 Structure:"
echo "- backend/ (extracted from working Aug 18th image)"
echo "- frontend/ (current state - needs to be reverted to Aug 18th)"
echo "- aug18_git_commits.txt (commits around Aug 18th)"
echo "- container_root_listing.txt (what was in the Aug 18th container)"
echo ""
echo "📝 Next: Remove OCR dependencies from backend and revert frontend to Aug 18th state"
echo ""
ls -la