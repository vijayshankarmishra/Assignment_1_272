# 🎯 Word Quiz - Kubernetes Microservices Deployment

[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kind](https://img.shields.io/badge/Kind-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kind.sigs.k8s.io/)

A production-grade **Word Quiz application** demonstrating **microservices architecture** deployed on **Kubernetes**. This project showcases enterprise-level software engineering practices including service decomposition, containerization, orchestration, and scalability.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Guide](#detailed-deployment-guide)
- [Microservices Breakdown](#microservices-breakdown)
- [Kubernetes Resources](#kubernetes-resources)
- [Testing & Verification](#testing--verification)
- [Screenshots](#screenshots)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

---

## 🎯 Overview

This project transforms a monolithic web application into a **microservices-based architecture** deployed on Kubernetes, demonstrating:

- ✅ **Service Decomposition**: Breaking down a monolith into 4 independent microservices
- ✅ **Containerization**: Docker containers for each service
- ✅ **Orchestration**: Kubernetes for container management and scaling
- ✅ **High Availability**: Multiple replicas with load balancing
- ✅ **Service Discovery**: Internal DNS for inter-service communication
- ✅ **API Gateway Pattern**: Centralized routing and request handling
- ✅ **Health Checks**: Liveness and readiness probes
- ✅ **Resource Management**: CPU and memory limits/requests
- ✅ **Ingress Controller**: External access via Nginx Ingress

### Application Features

- 📝 Interactive word quiz with missing letters
- 🎲 Multiple choice questions with real-time validation
- 📊 Statistics tracking and leaderboard
- 🏗️ Production-ready microservices architecture
- 📈 Horizontal scaling capability

---

## 🏗️ Architecture

### Before: Monolithic Architecture

```
┌─────────────────────────────────┐
│     Single Docker Container     │
│                                 │
│  ┌───────────────────────────┐ │
│  │    Nginx Web Server       │ │
│  │  - Static HTML/CSS/JS     │ │
│  │  - No backend API         │ │
│  │  - Client-side only       │ │
│  └───────────────────────────┘ │
└─────────────────────────────────┘
```

**Limitations:**
- ❌ Single point of failure
- ❌ Cannot scale components independently
- ❌ No API for integrations
- ❌ Tight coupling of all components

### After: Microservices Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Kind)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Ingress Controller (Nginx)                │ │
│  │                    Port 80/443                         │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│         ┌─────────────▼──────────────┐                      │
│         │   Frontend Service         │                      │
│         │   (Nginx - 2 replicas)     │                      │
│         │   Serves SPA               │                      │
│         └─────────────┬──────────────┘                      │
│                       │                                      │
│         ┌─────────────▼──────────────┐                      │
│         │   API Gateway Service      │                      │
│         │   (Node.js - 2 replicas)   │                      │
│         │   Routes & Load Balancing  │                      │
│         └─────────────┬──────────────┘                      │
│                       │                                      │
│            ┌──────────┴──────────┐                          │
│            │                     │                          │
│    ┌───────▼────────┐   ┌───────▼────────┐                │
│    │ Quiz Service   │   │ Metrics Service │                │
│    │ (Python Flask) │   │ (Python Flask)  │                │
│    │ 3 replicas     │   │ 2 replicas      │                │
│    │ Question Gen   │   │ Analytics       │                │
│    └────────────────┘   └─────────────────┘                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ **Scalability**: Each service scales independently
- ✅ **Resilience**: Service isolation and multiple replicas
- ✅ **Technology Diversity**: Best tool for each job
- ✅ **Deployment Flexibility**: Update services independently
- ✅ **Load Distribution**: 9 total pods across 4 services

---

## 📦 Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| **Docker** | 20.x+ | [Install Docker](https://docs.docker.com/get-docker/) |
| **Kind** | 0.20.x+ | `brew install kind` |
| **kubectl** | 1.27.x+ | `brew install kubectl` |
| **Git** | 2.x+ | Pre-installed on macOS |

### Verify Installation

```bash
# Check Docker
docker --version
docker ps

# Check Kind
kind version

# Check kubectl
kubectl version --client

# Check available resources
docker info | grep -i "CPUs\|Memory"
```

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **RAM**: Minimum 8GB (16GB recommended)
- **CPU**: 4+ cores recommended
- **Disk**: 10GB free space

---

## 🚀 Quick Start

### One-Command Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd k8s-microservices

# Deploy everything
./deploy.sh
```

This script will:
1. ✅ Verify prerequisites
2. ✅ Create Kind cluster with 3 nodes
3. ✅ Install Nginx Ingress Controller
4. ✅ Build all Docker images
5. ✅ Load images into Kind
6. ✅ Deploy all Kubernetes resources
7. ✅ Configure /etc/hosts
8. ✅ Wait for all pods to be ready

### Access the Application

Once deployed, open your browser:

```
http://wordquiz.local
```

---

## 📖 Detailed Deployment Guide

### Step 1: Create Kind Cluster

```bash
# Create cluster with custom configuration
kind create cluster --config kind-config.yaml

# Verify cluster
kubectl cluster-info --context kind-word-quiz-cluster
kubectl get nodes
```

**Cluster Configuration:**
- 1 Control plane node
- 2 Worker nodes
- Ingress ports exposed (80, 443)

### Step 2: Install Ingress Controller

```bash
# Apply Nginx Ingress for Kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### Step 3: Build Docker Images

```bash
# Frontend
docker build -t wordquiz-frontend:latest ./frontend

# API Gateway
docker build -t wordquiz-api-gateway:latest ./api-gateway

# Quiz Service
docker build -t wordquiz-quiz-service:latest ./quiz-service

# Metrics Service
docker build -t wordquiz-metrics-service:latest ./metrics-service

# Verify images
docker images | grep wordquiz
```

### Step 4: Load Images to Kind

```bash
# Load all images to Kind cluster
kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster
kind load docker-image wordquiz-api-gateway:latest --name word-quiz-cluster
kind load docker-image wordquiz-quiz-service:latest --name word-quiz-cluster
kind load docker-image wordquiz-metrics-service:latest --name word-quiz-cluster
```

### Step 5: Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Watch deployment progress
kubectl get pods -n word-quiz-app -w
```

### Step 6: Verify Deployment

```bash
# Check all resources
./status.sh

# Or manually:
kubectl get all -n word-quiz-app
```

### Step 7: Configure Local DNS

```bash
# Add to /etc/hosts (requires sudo)
echo "127.0.0.1 wordquiz.local" | sudo tee -a /etc/hosts
```

---

## 🔧 Microservices Breakdown

### 1. Frontend Service (Nginx)

**Purpose**: Serve the Single Page Application

- **Technology**: Nginx Alpine
- **Replicas**: 2
- **Port**: 80
- **Resources**: 64Mi RAM, 100m CPU

**Files:**
```
frontend/
├── Dockerfile
├── nginx.conf      # Proxy config for API Gateway
├── index.html      # Main HTML
├── app.js          # JavaScript logic
└── styles.css      # Styling
```

**Key Features:**
- Serves static files
- Proxies `/api/*` to API Gateway
- Health check endpoint at `/health`

### 2. API Gateway Service (Node.js/Express)

**Purpose**: Central routing and request orchestration

- **Technology**: Node.js 18 with Express
- **Replicas**: 2
- **Port**: 8080
- **Resources**: 128Mi RAM, 200m CPU

**Files:**
```
api-gateway/
├── Dockerfile
├── package.json
└── server.js       # Express server with routes
```

**Endpoints:**
- `GET /api/health` - Health check
- `GET /api/quiz/question` - Fetch question from Quiz Service
- `POST /api/quiz/answer` - Validate answer
- `GET /api/metrics/stats` - Get statistics from Metrics Service

**Key Features:**
- Request routing and load balancing
- Service discovery via Kubernetes DNS
- Error handling and retry logic
- Background metrics recording

### 3. Quiz Service (Python/Flask)

**Purpose**: Core quiz logic and question generation

- **Technology**: Python 3.11 with Flask
- **Replicas**: 3 (handles computation load)
- **Port**: 5000
- **Resources**: 128Mi RAM, 200m CPU

**Files:**
```
quiz-service/
├── Dockerfile
├── requirements.txt
└── app.py          # Flask app with quiz logic
```

**Endpoints:**
- `GET /quiz/health` - Health check
- `GET /quiz/generate` - Generate new question
- `POST /quiz/validate` - Validate answer
- `GET /quiz/words` - Word bank info

**Key Features:**
- 50+ word vocabulary
- Smart masking algorithm
- Multiple choice generation
- Same-length distractor words

### 4. Metrics Service (Python/Flask)

**Purpose**: Track and analyze quiz performance

- **Technology**: Python 3.11 with Flask
- **Replicas**: 2
- **Port**: 5001
- **Resources**: 128Mi RAM, 200m CPU

**Files:**
```
metrics-service/
├── Dockerfile
├── requirements.txt
└── app.py          # Flask app with metrics storage
```

**Endpoints:**
- `GET /metrics/health` - Health check
- `POST /metrics/record` - Record quiz attempt
- `GET /metrics/stats` - Aggregate statistics
- `GET /metrics/session/<id>` - Session stats
- `GET /metrics/leaderboard` - Top scores

**Key Features:**
- In-memory storage (use DB in production)
- Session tracking
- Aggregate statistics
- Leaderboard generation

---

## ☸️ Kubernetes Resources

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: word-quiz-app
```

Isolates all resources logically.

### ConfigMap

Stores environment configuration:
- Service URLs
- Environment variables
- Feature flags

### Deployments (4)

| Deployment | Replicas | Image | Port |
|------------|----------|-------|------|
| frontend-deployment | 2 | wordquiz-frontend:latest | 80 |
| api-gateway-deployment | 2 | wordquiz-api-gateway:latest | 8080 |
| quiz-service-deployment | 3 | wordquiz-quiz-service:latest | 5000 |
| metrics-service-deployment | 2 | wordquiz-metrics-service:latest | 5001 |

**Total Pods**: 9

### Services (4)

All use `ClusterIP` for internal communication:
- `frontend-service:80`
- `api-gateway-service:8080`
- `quiz-service:5000`
- `metrics-service:5001`

### Ingress

Routes external traffic to Frontend Service:
- Host: `wordquiz.local`
- Backend: `frontend-service:80`

### Health Checks

**Liveness Probes**: Restart unhealthy containers
**Readiness Probes**: Route traffic only to ready containers

---

## ✅ Testing & Verification

### Check Cluster Status

```bash
# View all resources
kubectl get all -n word-quiz-app

# Check pod logs
kubectl logs -f deployment/api-gateway-deployment -n word-quiz-app

# Describe a pod
kubectl describe pod <pod-name> -n word-quiz-app

# Execute command in pod
kubectl exec -it <pod-name> -n word-quiz-app -- /bin/sh
```

### Test Service Endpoints

```bash
# Port forward to test services individually
kubectl port-forward svc/frontend-service 8080:80 -n word-quiz-app
kubectl port-forward svc/api-gateway-service 8081:8080 -n word-quiz-app
kubectl port-forward svc/quiz-service 8082:5000 -n word-quiz-app
kubectl port-forward svc/metrics-service 8083:5001 -n word-quiz-app

# Test endpoints
curl http://localhost:8081/api/health
curl http://localhost:8082/quiz/health
curl http://localhost:8083/metrics/health
```

### Test Application Functionality

1. **Open Browser**: Navigate to `http://wordquiz.local`
2. **Play Quiz**: Answer 10 questions
3. **Check Stats**: Click "View Stats" button
4. **Verify Logs**: Check that metrics are being recorded

```bash
# Watch metrics being recorded
kubectl logs -f deployment/metrics-service-deployment -n word-quiz-app | grep "Recorded metric"
```

### Performance Testing

```bash
# Scale up replicas
kubectl scale deployment/quiz-service-deployment --replicas=5 -n word-quiz-app

# Monitor resource usage (if metrics-server installed)
kubectl top pods -n word-quiz-app

# Load testing with Apache Bench (install: brew install httpd)
ab -n 1000 -c 10 http://wordquiz.local/api/quiz/question
```

---

## 📸 Screenshots

### Required Screenshots for Assignment

Capture these screenshots for your deliverables:

#### 1. Kubernetes Cluster Status

```bash
./status.sh
```

**Screenshot should show:**
- ✅ All nodes in Ready state
- ✅ All pods running (9 total)
- ✅ All services listed
- ✅ Ingress configuration

#### 2. Running Pods

```bash
kubectl get pods -n word-quiz-app -o wide
```

**Screenshot should show:**
- ✅ Pod names
- ✅ Ready status (2/2, 1/1)
- ✅ Running state
- ✅ Age
- ✅ Node assignments

#### 3. Services

```bash
kubectl get services -n word-quiz-app
```

**Screenshot should show:**
- ✅ Service names
- ✅ ClusterIP addresses
- ✅ Ports
- ✅ Age

#### 4. Application Interface

Open browser to `http://wordquiz.local`

**Screenshot should show:**
- ✅ Quiz question with masked word
- ✅ Multiple choice options
- ✅ Score and round counter
- ✅ Architecture info panel

#### 5. Statistics Dashboard

Click "View Stats" button

**Screenshot should show:**
- ✅ Total questions answered
- ✅ Correct answers
- ✅ Overall accuracy
- ✅ Total sessions
- ✅ Average score

#### 6. Architecture Diagram

Include the ASCII diagram from `ARCHITECTURE.md` showing:
- ✅ Before (monolith)
- ✅ After (microservices)
- ✅ Service relationships

---

## 🔧 Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n word-quiz-app

# Check logs
kubectl logs <pod-name> -n word-quiz-app

# Common issues:
# - Image pull errors: Ensure images are loaded to Kind
# - Resource limits: Increase Docker resources
# - Port conflicts: Check nothing is using port 80
```

### Cannot Access wordquiz.local

```bash
# Verify /etc/hosts
cat /etc/hosts | grep wordquiz

# Verify ingress
kubectl get ingress -n word-quiz-app

# Check ingress controller
kubectl get pods -n ingress-nginx

# Test with port-forward instead
kubectl port-forward svc/frontend-service 8080:80 -n word-quiz-app
# Then access: http://localhost:8080
```

### Services Not Communicating

```bash
# Check service endpoints
kubectl get endpoints -n word-quiz-app

# Test DNS resolution from a pod
kubectl run -it --rm debug --image=busybox --restart=Never -n word-quiz-app -- nslookup quiz-service

# Check logs for connection errors
kubectl logs deployment/api-gateway-deployment -n word-quiz-app | grep -i error
```

### Rebuild and Redeploy

```bash
# Quick rebuild script
./redeploy.sh

# Or manually:
docker build -t wordquiz-frontend:latest ./frontend
kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster
kubectl rollout restart deployment/frontend-deployment -n word-quiz-app
```

---

## 🧹 Cleanup

### Remove Application Only

```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# Verify deletion
kubectl get all -n word-quiz-app
```

### Complete Cleanup

```bash
# Run cleanup script
./cleanup.sh

# This will:
# 1. Delete all K8s resources
# 2. Delete Kind cluster
# 3. Optionally remove /etc/hosts entry
```

### Manual Cleanup

```bash
# Delete namespace (cascades to all resources)
kubectl delete namespace word-quiz-app

# Delete Kind cluster
kind delete cluster --name word-quiz-cluster

# Remove /etc/hosts entry
sudo sed -i '' '/wordquiz.local/d' /etc/hosts

# Remove Docker images (optional)
docker rmi wordquiz-frontend:latest
docker rmi wordquiz-api-gateway:latest
docker rmi wordquiz-quiz-service:latest
docker rmi wordquiz-metrics-service:latest
```

---

## 📚 Additional Resources

### Documentation

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

### Architecture Patterns

- [Microservices Pattern](https://microservices.io/)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [Health Check Pattern](https://microservices.io/patterns/observability/health-check-api.html)

### Project Files

```
k8s-microservices/
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed architecture doc
├── kind-config.yaml             # Kind cluster configuration
├── deploy.sh                    # Main deployment script
├── redeploy.sh                  # Quick update script
├── cleanup.sh                   # Cleanup script
├── status.sh                    # Status check script
├── frontend/                    # Frontend service
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── api-gateway/                 # API Gateway service
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
├── quiz-service/                # Quiz service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── metrics-service/             # Metrics service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── k8s/                         # Kubernetes manifests
    ├── 00-namespace.yaml
    ├── 01-configmap.yaml
    ├── 02-frontend.yaml
    ├── 03-api-gateway.yaml
    ├── 04-quiz-service.yaml
    ├── 05-metrics-service.yaml
    └── 06-ingress.yaml
```

---

## 👥 Assignment Deliverables Checklist

For your assignment submission, ensure you have:

### 1. Architecture Documentation ✅
- [x] `ARCHITECTURE.md` with before/after diagrams
- [x] Component descriptions
- [x] Technology stack explanation
- [x] Benefits of microservices approach

### 2. Code Repository ✅
- [x] All source code in GitHub repository
- [x] Organized directory structure
- [x] Dockerfiles for each service
- [x] Kubernetes YAML manifests
- [x] Deployment scripts

### 3. Kubernetes Manifests ✅
- [x] Namespace configuration
- [x] ConfigMaps
- [x] Deployments (4 services)
- [x] Services (4 services)
- [x] Ingress configuration

### 4. Screenshots 📸
Required screenshots:
- [ ] Kubernetes cluster running (`kubectl get nodes`)
- [ ] All pods running (`kubectl get pods -n word-quiz-app`)
- [ ] All services (`kubectl get services -n word-quiz-app`)
- [ ] Ingress configuration (`kubectl get ingress -n word-quiz-app`)
- [ ] Application homepage (browser)
- [ ] Quiz in progress (browser)
- [ ] Statistics page (browser)
- [ ] Full status output (`./status.sh`)

### 5. Documentation ✅
- [x] Comprehensive README with deployment instructions
- [x] Architecture explanation
- [x] Technology justification
- [x] Troubleshooting guide

---

## 🎓 Learning Outcomes

This project demonstrates proficiency in:

1. **Microservices Architecture**
   - Service decomposition strategies
   - Inter-service communication
   - API Gateway pattern

2. **Containerization**
   - Docker best practices
   - Multi-stage builds
   - Image optimization

3. **Kubernetes**
   - Pod orchestration
   - Service discovery
   - Resource management
   - Health checks
   - Horizontal scaling

4. **DevOps Practices**
   - Infrastructure as Code
   - Automated deployment
   - Monitoring and observability

5. **Software Engineering**
   - Clean code architecture
   - Separation of concerns
   - Production-ready practices

---

## 📧 Support

For questions or issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Kubernetes logs: `kubectl logs <pod-name> -n word-quiz-app`
3. Run status check: `./status.sh`
4. Consult official documentation

---

## 📄 License

This project is created for educational purposes as part of SJSU CMPE 272 - Enterprise Software Platforms.

---

## 🌟 Acknowledgments

- **Kubernetes** for container orchestration
- **Kind** for local Kubernetes clusters
- **Docker** for containerization
- **Nginx** for web serving and ingress
- **Flask** and **Express** for microservice frameworks

---

**Built with ❤️ by Enterprise Software Engineering Team**

**November 2025**
