# Quick Reference Guide

## 🚀 Essential Commands

### Deployment
```bash
./deploy.sh              # Full deployment
./redeploy.sh            # Update after code changes
./status.sh              # Check deployment status
./cleanup.sh             # Remove everything
```

### Kubectl Commands
```bash
# View resources
kubectl get all -n word-quiz-app
kubectl get pods -n word-quiz-app
kubectl get services -n word-quiz-app
kubectl get ingress -n word-quiz-app

# Logs
kubectl logs -f deployment/frontend-deployment -n word-quiz-app
kubectl logs -f deployment/api-gateway-deployment -n word-quiz-app
kubectl logs -f deployment/quiz-service-deployment -n word-quiz-app
kubectl logs -f deployment/metrics-service-deployment -n word-quiz-app

# Describe resources
kubectl describe pod <pod-name> -n word-quiz-app
kubectl describe service <service-name> -n word-quiz-app

# Execute commands in pods
kubectl exec -it <pod-name> -n word-quiz-app -- /bin/bash
kubectl exec -it <pod-name> -n word-quiz-app -- /bin/sh

# Port forwarding (for testing)
kubectl port-forward svc/frontend-service 8080:80 -n word-quiz-app
kubectl port-forward svc/api-gateway-service 8081:8080 -n word-quiz-app
```

### Scaling
```bash
# Scale deployments
kubectl scale deployment/quiz-service-deployment --replicas=5 -n word-quiz-app
kubectl scale deployment/metrics-service-deployment --replicas=3 -n word-quiz-app

# Auto-scaling (requires metrics-server)
kubectl autoscale deployment/quiz-service-deployment --cpu-percent=70 --min=2 --max=10 -n word-quiz-app
```

### Docker Commands
```bash
# Build images
docker build -t wordquiz-frontend:latest ./frontend
docker build -t wordquiz-api-gateway:latest ./api-gateway
docker build -t wordquiz-quiz-service:latest ./quiz-service
docker build -t wordquiz-metrics-service:latest ./metrics-service

# Load to Kind
kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster
kind load docker-image wordquiz-api-gateway:latest --name word-quiz-cluster
kind load docker-image wordquiz-quiz-service:latest --name word-quiz-cluster
kind load docker-image wordquiz-metrics-service:latest --name word-quiz-cluster

# View images
docker images | grep wordquiz

# Remove images
docker rmi wordquiz-frontend:latest
```

### Kind Commands
```bash
# Create cluster
kind create cluster --config kind-config.yaml

# List clusters
kind get clusters

# Delete cluster
kind delete cluster --name word-quiz-cluster

# Load image
kind load docker-image <image-name>:latest --name word-quiz-cluster

# Get nodes
kubectl get nodes
```

### Debugging
```bash
# Check pod status
kubectl get pods -n word-quiz-app -o wide

# Check events
kubectl get events -n word-quiz-app --sort-by='.lastTimestamp'

# Check logs with previous container
kubectl logs <pod-name> -n word-quiz-app --previous

# Describe failing pod
kubectl describe pod <pod-name> -n word-quiz-app

# Interactive shell in pod
kubectl exec -it <pod-name> -n word-quiz-app -- /bin/sh

# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -n word-quiz-app -- sh
# Then inside pod: wget -O- http://quiz-service:5000/quiz/health
```

## 📝 Service URLs

### External
- Application: http://wordquiz.local

### Internal (within cluster)
- Frontend: http://frontend-service.word-quiz-app.svc.cluster.local:80
- API Gateway: http://api-gateway-service.word-quiz-app.svc.cluster.local:8080
- Quiz Service: http://quiz-service.word-quiz-app.svc.cluster.local:5000
- Metrics Service: http://metrics-service.word-quiz-app.svc.cluster.local:5001

### Health Endpoints
- Frontend: http://wordquiz.local/health
- API Gateway: http://wordquiz.local/api/health
- Quiz Service: http://quiz-service:5000/quiz/health (internal)
- Metrics Service: http://metrics-service:5001/metrics/health (internal)

## 🎯 API Endpoints

### Quiz Service
```bash
GET  /quiz/health          # Health check
GET  /quiz/generate        # Generate question
POST /quiz/validate        # Validate answer
GET  /quiz/words           # Word bank info
```

### Metrics Service
```bash
GET  /metrics/health              # Health check
POST /metrics/record              # Record attempt
GET  /metrics/stats               # Get statistics
GET  /metrics/session/<id>        # Session stats
GET  /metrics/leaderboard         # Top scores
POST /metrics/reset               # Reset all metrics
```

### API Gateway
```bash
GET  /api/health               # Health check
GET  /api/quiz/question        # Get question (proxies to quiz-service)
POST /api/quiz/answer          # Submit answer (proxies to quiz-service)
GET  /api/metrics/stats        # Get stats (proxies to metrics-service)
POST /api/metrics/record       # Record metric (proxies to metrics-service)
```

## 🔍 Testing Commands

### Test APIs
```bash
# Port forward API Gateway
kubectl port-forward svc/api-gateway-service 8080:8080 -n word-quiz-app

# Test health
curl http://localhost:8080/api/health

# Get question
curl http://localhost:8080/api/quiz/question

# Submit answer
curl -X POST http://localhost:8080/api/quiz/answer \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session",
    "question": "p_th_n",
    "answer": "python",
    "selectedOption": "python",
    "correct": true,
    "round": 1,
    "timestamp": "2024-01-01T00:00:00Z"
  }'

# Get statistics
curl http://localhost:8080/api/metrics/stats
```

### Load Testing
```bash
# Install Apache Bench (if not installed)
brew install httpd

# Run load test
ab -n 1000 -c 10 http://wordquiz.local/

# Test API endpoint
ab -n 100 -c 5 http://wordquiz.local/api/quiz/question
```

## 📊 Monitoring

### Resource Usage
```bash
# Install metrics-server (if not installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View resource usage
kubectl top nodes
kubectl top pods -n word-quiz-app

# Watch resources
watch kubectl top pods -n word-quiz-app
```

### Logs
```bash
# Stream logs from all pods
kubectl logs -f -l app=frontend -n word-quiz-app
kubectl logs -f -l app=api-gateway -n word-quiz-app
kubectl logs -f -l app=quiz-service -n word-quiz-app
kubectl logs -f -l app=metrics-service -n word-quiz-app

# Save logs to file
kubectl logs deployment/api-gateway-deployment -n word-quiz-app > gateway.log
```

## 🛠️ Common Tasks

### Update Code
```bash
# 1. Make code changes
# 2. Rebuild image
docker build -t wordquiz-frontend:latest ./frontend

# 3. Load to Kind
kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster

# 4. Restart deployment
kubectl rollout restart deployment/frontend-deployment -n word-quiz-app

# 5. Watch rollout
kubectl rollout status deployment/frontend-deployment -n word-quiz-app
```

### Reset Application State
```bash
# Delete and recreate all pods
kubectl delete pods --all -n word-quiz-app

# Reset metrics
kubectl port-forward svc/api-gateway-service 8080:8080 -n word-quiz-app
curl -X POST http://localhost:8080/api/metrics/reset
```

### Backup/Export
```bash
# Export all resources
kubectl get all -n word-quiz-app -o yaml > backup.yaml

# Export specific resource
kubectl get deployment/frontend-deployment -n word-quiz-app -o yaml > frontend-deployment.yaml
```

## 🚨 Troubleshooting

### Pods Stuck in Pending
```bash
# Check events
kubectl describe pod <pod-name> -n word-quiz-app

# Common causes:
# - Insufficient resources
# - Image pull errors
# - Volume mount issues
```

### Pods CrashLoopBackOff
```bash
# Check logs
kubectl logs <pod-name> -n word-quiz-app

# Check previous logs
kubectl logs <pod-name> -n word-quiz-app --previous

# Common causes:
# - Application errors
# - Missing environment variables
# - Port conflicts
```

### Cannot Access Application
```bash
# Verify ingress
kubectl get ingress -n word-quiz-app

# Check /etc/hosts
cat /etc/hosts | grep wordquiz

# Test with port-forward
kubectl port-forward svc/frontend-service 8080:80 -n word-quiz-app
# Access: http://localhost:8080
```

## 📦 Resource Limits

Current configuration per pod:

| Service | Replicas | Requests (RAM/CPU) | Limits (RAM/CPU) |
|---------|----------|-------------------|------------------|
| Frontend | 2 | 64Mi / 100m | 128Mi / 200m |
| API Gateway | 2 | 128Mi / 200m | 256Mi / 500m |
| Quiz Service | 3 | 128Mi / 200m | 256Mi / 500m |
| Metrics Service | 2 | 128Mi / 200m | 256Mi / 500m |

**Total Resources:**
- Memory Requests: ~1.2GB
- Memory Limits: ~2.4GB
- CPU Requests: ~1.6 cores
- CPU Limits: ~3.6 cores

## 🔐 Security Best Practices

### Production Considerations
```bash
# Use secrets for sensitive data
kubectl create secret generic app-secrets \
  --from-literal=api-key=your-api-key \
  -n word-quiz-app

# Use network policies
kubectl apply -f network-policy.yaml

# Run as non-root user (already configured in Dockerfiles)

# Use resource quotas
kubectl create quota app-quota \
  --hard=pods=20,requests.cpu=4,requests.memory=8Gi \
  -n word-quiz-app
```

## 📚 Additional Resources

- [Kubernetes Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)
