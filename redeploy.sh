#!/bin/bash

# Quick Build and Deploy Script (for updates after initial deployment)

set -e

echo "🔄 Rebuilding and redeploying services..."

# Build images
echo "📦 Building Docker images..."
docker build -t wordquiz-frontend:latest ./frontend
docker build -t wordquiz-api-gateway:latest ./api-gateway
docker build -t wordquiz-quiz-service:latest ./quiz-service
docker build -t wordquiz-metrics-service:latest ./metrics-service

# Load images to Kind
echo "📥 Loading images to Kind cluster..."
kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster
kind load docker-image wordquiz-api-gateway:latest --name word-quiz-cluster
kind load docker-image wordquiz-quiz-service:latest --name word-quiz-cluster
kind load docker-image wordquiz-metrics-service:latest --name word-quiz-cluster

# Restart deployments
echo "🔄 Restarting deployments..."
kubectl rollout restart deployment/frontend-deployment -n word-quiz-app
kubectl rollout restart deployment/api-gateway-deployment -n word-quiz-app
kubectl rollout restart deployment/quiz-service-deployment -n word-quiz-app
kubectl rollout restart deployment/metrics-service-deployment -n word-quiz-app

# Wait for rollout
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/frontend-deployment -n word-quiz-app
kubectl rollout status deployment/api-gateway-deployment -n word-quiz-app
kubectl rollout status deployment/quiz-service-deployment -n word-quiz-app
kubectl rollout status deployment/metrics-service-deployment -n word-quiz-app

echo "✅ Deployment complete!"
echo "🌐 Access at: http://wordquiz.local"
