#!/bin/bash

echo "🔍 Extracting code from original August 18th image..."

# Create extraction directory
mkdir -p extracted_aug18_code
cd extracted_aug18_code

# Run container and copy the entire /app directory
echo "📁 Extracting /app directory from August 18th image..."
docker run -d --name temp-aug18-extract 683342011909.dkr.ecr.eu-central-1.amazonaws.com/hokm-ai/backend:v20250818-123617 sleep 3600

# Copy the entire application code
docker cp temp-aug18-extract:/app ./aug18_app

# Stop and remove container
docker stop temp-aug18-extract
docker rm temp-aug18-extract

echo "✅ Code extracted to: extracted_aug18_code/aug18_app/"
echo ""
echo "📋 Contents:"
ls -la aug18_app/
echo ""
echo "🎯 This is the EXACT code from the working August 18th version!"
echo "Now creating replica with no OCR dependencies..."

cd ../