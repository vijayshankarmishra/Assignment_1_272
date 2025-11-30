#!/bin/bash

# Status Check Script - View deployment status

echo "=========================================="
echo "  Kubernetes Cluster Status"
echo "=========================================="

# Check if cluster exists
if ! kind get clusters | grep -q "word-quiz-cluster"; then
    echo "❌ Cluster 'word-quiz-cluster' does not exist"
    echo "Run ./deploy.sh to create and deploy"
    exit 1
fi

# Cluster info
echo ""
echo "📊 Cluster Information:"
kubectl cluster-info --context kind-word-quiz-cluster

# Nodes
echo ""
echo "🖥️  Nodes:"
kubectl get nodes

# Namespace
echo ""
echo "📦 Namespace:"
kubectl get namespace word-quiz-app

# Pods
echo ""
echo "🚀 Pods:"
kubectl get pods -n word-quiz-app -o wide

# Deployments
echo ""
echo "📋 Deployments:"
kubectl get deployments -n word-quiz-app

# Services
echo ""
echo "🌐 Services:"
kubectl get services -n word-quiz-app

# Ingress
echo ""
echo "🔗 Ingress:"
kubectl get ingress -n word-quiz-app

# ConfigMaps
echo ""
echo "⚙️  ConfigMaps:"
kubectl get configmaps -n word-quiz-app

# Resource Usage
echo ""
echo "📈 Resource Usage:"
kubectl top pods -n word-quiz-app 2>/dev/null || echo "Metrics server not available"

# Events (last 10)
echo ""
echo "📝 Recent Events:"
kubectl get events -n word-quiz-app --sort-by='.lastTimestamp' | tail -10

echo ""
echo "=========================================="
echo "✅ Application URL: http://wordquiz.local"
echo "=========================================="
