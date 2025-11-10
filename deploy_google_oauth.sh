#!/bin/bash

# Deploy Google OAuth Changes to AWS
# This script deploys the updated Google OAuth implementation to production

set -e

echo "🚀 DEPLOYING GOOGLE OAUTH TO AWS PRODUCTION"
echo "============================================"

# Configuration
ECR_REPO="940053359036.dkr.ecr.eu-central-1.amazonaws.com/new-moaen-ai"
REGION="eu-central-1"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKEND_TAG="google-oauth-${TIMESTAMP}"
FRONTEND_TAG="google-oauth-frontend-${TIMESTAMP}"

echo "📋 Deployment Configuration:"
echo "   Backend Tag: ${BACKEND_TAG}"
echo "   Frontend Tag: ${FRONTEND_TAG}"
echo "   ECR Repository: ${ECR_REPO}"
echo "   Region: ${REGION}"

# Step 1: Build and push backend Docker image
echo ""
echo "1️⃣ Building Backend Docker Image..."
cd backend

# Create a production Dockerfile that includes Google OAuth environment variables
cat > Dockerfile.google.oauth << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "   Building backend image with Google OAuth support..."
docker build -f Dockerfile.google.oauth -t new-moaen-ai-backend:${BACKEND_TAG} .

echo "   Tagging backend image for ECR..."
docker tag new-moaen-ai-backend:${BACKEND_TAG} ${ECR_REPO}/backend:${BACKEND_TAG}

# Step 2: Build and push frontend Docker image
echo ""
echo "2️⃣ Building Frontend Docker Image..."
cd ../frontend

# Create production Dockerfile for frontend
cat > Dockerfile.google.oauth << 'EOF'
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
EOF

echo "   Building frontend image with Google OAuth support..."
docker build -f Dockerfile.google.oauth -t new-moaen-ai-frontend:${FRONTEND_TAG} .

echo "   Tagging frontend image for ECR..."
docker tag new-moaen-ai-frontend:${FRONTEND_TAG} ${ECR_REPO}/frontend:${FRONTEND_TAG}

cd ..

# Step 3: Update ECS task definition with Google OAuth environment variables
echo ""
echo "3️⃣ Creating Updated ECS Task Definition..."

cat > task-definition-google-oauth.json << EOF
{
  "family": "new-moaen-ai-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::940053359036:role/new-moaen-ai-ecs-task-execution-role",
  "taskRoleArn": "arn:aws:iam::940053359036:role/new-moaen-ai-ecs-task-role",
  "containerDefinitions": [
    {
      "name": "backend-container",
      "image": "${ECR_REPO}/backend:${BACKEND_TAG}",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "False"
        },
        {
          "name": "GOOGLE_CLIENT_ID",
          "value": "1076021198125-6ttfqhm2g42o72v95v29berorj9a85de.apps.googleusercontent.com"
        },
        {
          "name": "GOOGLE_CLIENT_SECRET",
          "value": "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"
        },
        {
          "name": "CORS_ORIGINS",
          "value": "https://hokm.ai,https://app.hokm.ai,https://d10drat4g0606g.cloudfront.net"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:eu-central-1:940053359036:secret:new-moaen-ai/openai-api-key"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:eu-central-1:940053359036:secret:new-moaen-ai/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:eu-central-1:940053359036:secret:new-moaen-ai/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/new-moaen-ai-backend",
          "awslogs-region": "eu-central-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

echo "✅ Created task definition with Google OAuth environment variables"

# Step 4: Instructions for manual deployment (since AWS CLI not configured)
echo ""
echo "4️⃣ DEPLOYMENT INSTRUCTIONS"
echo "=========================="
echo ""
echo "🔧 MANUAL DEPLOYMENT STEPS (AWS CLI not configured):"
echo ""
echo "1. Push Docker images to ECR:"
echo "   aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_REPO}"
echo "   docker push ${ECR_REPO}/backend:${BACKEND_TAG}"
echo "   docker push ${ECR_REPO}/frontend:${FRONTEND_TAG}"
echo ""
echo "2. Update ECS service with new task definition:"
echo "   aws ecs register-task-definition --cli-input-json file://task-definition-google-oauth.json"
echo "   aws ecs update-service --cluster new-moaen-ai-cluster --service new-moaen-ai-backend-service --task-definition new-moaen-ai-backend"
echo ""
echo "3. Update CloudFront with new frontend:"
echo "   (Frontend deployment depends on your specific setup)"
echo ""
echo "🎯 ALTERNATIVE: Use AWS Console"
echo "1. Upload images via AWS Console ECR"
echo "2. Update ECS task definition via AWS Console"
echo "3. Update ECS service to use new task definition"
echo ""
echo "📋 Generated Files:"
echo "   - backend/Dockerfile.google.oauth"
echo "   - frontend/Dockerfile.google.oauth" 
echo "   - task-definition-google-oauth.json"
echo ""
echo "✅ Google OAuth deployment package ready!"
echo "🚀 Images built and ready for AWS deployment"

# Step 5: Test that the local images work
echo ""
echo "5️⃣ LOCAL TESTING"
echo "================"
echo ""
echo "🧪 To test locally before deployment:"
echo "   docker run -p 8000:8000 new-moaen-ai-backend:${BACKEND_TAG}"
echo "   docker run -p 3000:80 new-moaen-ai-frontend:${FRONTEND_TAG}"
echo ""
echo "✅ GOOGLE OAUTH DEPLOYMENT PREPARATION COMPLETE!"