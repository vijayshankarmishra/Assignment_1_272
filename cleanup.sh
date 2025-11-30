#!/bin/bash

# Cleanup Script - Remove all resources

set -e

echo "🗑️  Cleaning up Kubernetes resources..."

# Delete application resources
echo "Deleting application resources..."
kubectl delete -f k8s/ --ignore-not-found=true

# Delete Kind cluster
echo "Deleting Kind cluster..."
kind delete cluster --name word-quiz-cluster

# Remove /etc/hosts entry (optional)
read -p "Remove wordquiz.local from /etc/hosts? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo sed -i '' '/wordquiz.local/d' /etc/hosts
    echo "✅ Removed wordquiz.local from /etc/hosts"
fi

echo "✅ Cleanup complete!"
