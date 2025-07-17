#!/bin/bash

# Deployment script for Liberation System Mesh Network
# This script builds the Docker image and deploys to Kubernetes

set -e

echo "🚀 Starting deployment process..."

# Configuration
IMAGE_NAME="mesh-network"
IMAGE_TAG="latest"
REGISTRY="your-registry.com"  # Replace with your container registry
NAMESPACE="liberation-system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Build Docker image
print_status "Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Tag image for registry (if using external registry)
if [ "$REGISTRY" != "your-registry.com" ]; then
    print_status "Tagging image for registry..."
    docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    
    # Push to registry
    print_status "Pushing image to registry..."
    docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    
    if [ $? -eq 0 ]; then
        print_success "Image pushed to registry successfully"
    else
        print_error "Failed to push image to registry"
        exit 1
    fi
fi

# Create namespace if it doesn't exist
print_status "Creating namespace $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply ConfigMap
print_status "Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE

# Apply Deployment
print_status "Applying Deployment..."
kubectl apply -f k8s/deployment.yaml -n $NAMESPACE

# Apply Service
print_status "Applying Service..."
kubectl apply -f k8s/service.yaml -n $NAMESPACE

# Wait for deployment to be ready
print_status "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mesh-network -n $NAMESPACE

if [ $? -eq 0 ]; then
    print_success "Deployment is ready"
else
    print_error "Deployment failed to become ready"
    exit 1
fi

# Get service information
print_status "Getting service information..."
kubectl get service mesh-network-service -n $NAMESPACE

# Get pod information
print_status "Getting pod information..."
kubectl get pods -n $NAMESPACE -l app=mesh-network

# Show deployment status
print_status "Deployment status:"
kubectl get deployment mesh-network -n $NAMESPACE

print_success "🎉 Deployment completed successfully!"

# Show access instructions
echo ""
echo "📋 Access Information:"
echo "====================="
echo "• Namespace: $NAMESPACE"
echo "• Service: mesh-network-service"
echo "• Dashboard: Access via LoadBalancer IP on port 80"
echo ""
echo "To get the external IP:"
echo "kubectl get service mesh-network-service -n $NAMESPACE"
echo ""
echo "To view logs:"
echo "kubectl logs -f deployment/mesh-network -n $NAMESPACE"
echo ""
echo "To scale the deployment:"
echo "kubectl scale deployment mesh-network --replicas=5 -n $NAMESPACE"
