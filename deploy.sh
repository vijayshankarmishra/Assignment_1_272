#!/bin/bash

# Word Quiz Kubernetes Deployment Script
# This script sets up a complete Kubernetes cluster using Kind and deploys the microservices

set -e  # Exit on any error

echo "=========================================="
echo "  Word Quiz - Kubernetes Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Kind
    if ! command -v kind &> /dev/null; then
        print_error "Kind is not installed. Please install Kind first."
        echo "Install with: brew install kind"
        exit 1
    fi
    print_success "Kind is installed"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        echo "Install with: brew install kubectl"
        exit 1
    fi
    print_success "kubectl is installed"
    
    echo ""
}

# Create Kind cluster
create_cluster() {
    print_info "Creating Kind cluster..."
    
    # Check if cluster already exists
    if kind get clusters | grep -q "word-quiz-cluster"; then
        print_warning "Cluster 'word-quiz-cluster' already exists"
        read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Deleting existing cluster..."
            kind delete cluster --name word-quiz-cluster
        else
            print_info "Using existing cluster"
            return
        fi
    fi
    
    # Create cluster with config
    kind create cluster --config kind-config.yaml
    print_success "Kind cluster created successfully"
    
    # Wait for cluster to be ready
    print_info "Waiting for cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=120s
    print_success "Cluster is ready"
    
    echo ""
}

# Install Nginx Ingress Controller
install_ingress() {
    print_info "Installing Nginx Ingress Controller..."
    
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    print_info "Waiting for Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
    
    print_success "Nginx Ingress Controller installed"
    echo ""
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    
    # Frontend
    print_info "Building frontend image..."
    docker build -t wordquiz-frontend:latest ./frontend
    kind load docker-image wordquiz-frontend:latest --name word-quiz-cluster
    print_success "Frontend image built and loaded"
    
    # API Gateway
    print_info "Building API Gateway image..."
    docker build -t wordquiz-api-gateway:latest ./api-gateway
    kind load docker-image wordquiz-api-gateway:latest --name word-quiz-cluster
    print_success "API Gateway image built and loaded"
    
    # Quiz Service
    print_info "Building Quiz Service image..."
    docker build -t wordquiz-quiz-service:latest ./quiz-service
    kind load docker-image wordquiz-quiz-service:latest --name word-quiz-cluster
    print_success "Quiz Service image built and loaded"
    
    # Metrics Service
    print_info "Building Metrics Service image..."
    docker build -t wordquiz-metrics-service:latest ./metrics-service
    kind load docker-image wordquiz-metrics-service:latest --name word-quiz-cluster
    print_success "Metrics Service image built and loaded"
    
    echo ""
}

# Deploy application
deploy_application() {
    print_info "Deploying application to Kubernetes..."
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/
    
    print_success "Application manifests applied"
    
    # Wait for deployments to be ready
    print_info "Waiting for deployments to be ready..."
    
    kubectl wait --for=condition=available --timeout=180s \
        deployment/frontend-deployment -n word-quiz-app
    
    kubectl wait --for=condition=available --timeout=180s \
        deployment/api-gateway-deployment -n word-quiz-app
    
    kubectl wait --for=condition=available --timeout=180s \
        deployment/quiz-service-deployment -n word-quiz-app
    
    kubectl wait --for=condition=available --timeout=180s \
        deployment/metrics-service-deployment -n word-quiz-app
    
    print_success "All deployments are ready"
    echo ""
}

# Configure /etc/hosts
configure_hosts() {
    print_info "Configuring /etc/hosts..."
    
    if grep -q "wordquiz.local" /etc/hosts; then
        print_warning "Entry for wordquiz.local already exists in /etc/hosts"
    else
        echo "127.0.0.1 wordquiz.local" | sudo tee -a /etc/hosts > /dev/null
        print_success "Added wordquiz.local to /etc/hosts"
    fi
    
    echo ""
}

# Display status
display_status() {
    print_info "Deployment Status"
    echo "=========================================="
    
    echo ""
    print_info "Namespaces:"
    kubectl get namespaces | grep word-quiz-app
    
    echo ""
    print_info "Pods:"
    kubectl get pods -n word-quiz-app
    
    echo ""
    print_info "Services:"
    kubectl get services -n word-quiz-app
    
    echo ""
    print_info "Ingress:"
    kubectl get ingress -n word-quiz-app
    
    echo ""
    echo "=========================================="
    print_success "Deployment Complete!"
    echo "=========================================="
    echo ""
    print_info "Access your application at: ${GREEN}http://wordquiz.local${NC}"
    echo ""
    print_info "Useful commands:"
    echo "  - View pods:         kubectl get pods -n word-quiz-app"
    echo "  - View logs:         kubectl logs -f <pod-name> -n word-quiz-app"
    echo "  - Describe pod:      kubectl describe pod <pod-name> -n word-quiz-app"
    echo "  - Port forward:      kubectl port-forward svc/frontend-service 8080:80 -n word-quiz-app"
    echo "  - Delete deployment: kubectl delete -f k8s/"
    echo "  - Delete cluster:    kind delete cluster --name word-quiz-cluster"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    create_cluster
    install_ingress
    build_images
    deploy_application
    configure_hosts
    display_status
}

# Run main function
main
