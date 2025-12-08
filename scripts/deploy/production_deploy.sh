#!/bin/bash
# Production Deployment Script for HishamOS
# Usage: ./production_deploy.sh <version> <environment>

set -e  # Exit on error

VERSION=${1:-latest}
ENVIRONMENT=${2:-production}
REGISTRY=${REGISTRY:-ghcr.io}
IMAGE_NAME=${IMAGE_NAME:-hishamos}

echo "🚀 Starting production deployment..."
echo "Version: $VERSION"
echo "Environment: $ENVIRONMENT"
echo "Registry: $REGISTRY"
echo "Image Name: $IMAGE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker not found. Please install docker.${NC}"
    exit 1
fi

# Verify Kubernetes connection
echo -e "${YELLOW}Verifying Kubernetes connection...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kubernetes connection verified${NC}"

# Build and push Docker images
echo -e "${YELLOW}Building and pushing Docker images...${NC}"

# Backend
echo "Building backend image..."
docker build -f infrastructure/docker/Dockerfile.backend.prod \
  -t $REGISTRY/$IMAGE_NAME-backend:$VERSION \
  -t $REGISTRY/$IMAGE_NAME-backend:latest \
  ./backend

docker push $REGISTRY/$IMAGE_NAME-backend:$VERSION
docker push $REGISTRY/$IMAGE_NAME-backend:latest

# Frontend
echo "Building frontend image..."
docker build -f infrastructure/docker/Dockerfile.frontend.prod \
  -t $REGISTRY/$IMAGE_NAME-frontend:$VERSION \
  -t $REGISTRY/$IMAGE_NAME-frontend:latest \
  ./frontend

docker push $REGISTRY/$IMAGE_NAME-frontend:$VERSION
docker push $REGISTRY/$IMAGE_NAME-frontend:latest

# Celery
echo "Building Celery worker image..."
docker build -f infrastructure/docker/Dockerfile.celery.prod \
  -t $REGISTRY/$IMAGE_NAME-celery:$VERSION \
  -t $REGISTRY/$IMAGE_NAME-celery:latest \
  ./backend

docker push $REGISTRY/$IMAGE_NAME-celery:$VERSION
docker push $REGISTRY/$IMAGE_NAME-celery:latest

echo -e "${GREEN}✓ Docker images built and pushed${NC}"

# Update Kubernetes manifests
echo -e "${YELLOW}Updating Kubernetes manifests...${NC}"

# Create temporary directory for manifests
TEMP_DIR=$(mktemp -d)
cp -r infrastructure/kubernetes/* $TEMP_DIR/

# Update image tags
sed -i.bak "s|hishamos/backend:latest|$REGISTRY/$IMAGE_NAME-backend:$VERSION|g" $TEMP_DIR/backend-deployment.yaml
sed -i.bak "s|hishamos/frontend:latest|$REGISTRY/$IMAGE_NAME-frontend:$VERSION|g" $TEMP_DIR/frontend-deployment.yaml
sed -i.bak "s|hishamos/celery:latest|$REGISTRY/$IMAGE_NAME-celery:$VERSION|g" $TEMP_DIR/celery-deployment.yaml

# Apply Kubernetes manifests
echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"

kubectl apply -f $TEMP_DIR/namespace.yaml
kubectl apply -f $TEMP_DIR/configmap.yaml
kubectl apply -f $TEMP_DIR/secrets.yaml

# Deploy database and Redis
kubectl apply -f $TEMP_DIR/postgres-deployment.yaml
kubectl apply -f $TEMP_DIR/redis-deployment.yaml

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n hishamos --timeout=300s

# Deploy application
kubectl apply -f $TEMP_DIR/backend-deployment.yaml
kubectl apply -f $TEMP_DIR/celery-deployment.yaml
kubectl apply -f $TEMP_DIR/frontend-deployment.yaml
kubectl apply -f $TEMP_DIR/ingress.yaml
kubectl apply -f $TEMP_DIR/hpa.yaml

# Cleanup
rm -rf $TEMP_DIR

echo -e "${GREEN}✓ Kubernetes manifests applied${NC}"

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
kubectl exec -n hishamos deployment/backend -- python manage.py migrate --noinput

echo -e "${GREEN}✓ Database migrations completed${NC}"

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
kubectl exec -n hishamos deployment/backend -- python manage.py collectstatic --noinput

echo -e "${GREEN}✓ Static files collected${NC}"

# Verify deployment
echo -e "${YELLOW}Verifying deployment...${NC}"

kubectl rollout status deployment/backend -n hishamos --timeout=300s
kubectl rollout status deployment/frontend -n hishamos --timeout=300s
kubectl rollout status deployment/celery -n hishamos --timeout=300s

echo -e "${GREEN}✓ Deployment verified${NC}"

# Health check
echo -e "${YELLOW}Running health checks...${NC}"
sleep 10  # Wait for services to be ready

BACKEND_POD=$(kubectl get pods -n hishamos -l app=backend -o jsonpath='{.items[0].metadata.name}')
if kubectl exec -n hishamos $BACKEND_POD -- curl -f http://localhost:8000/api/v1/monitoring/health/ &> /dev/null; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
echo ""
echo "Deployment Summary:"
echo "  Version: $VERSION"
echo "  Environment: $ENVIRONMENT"
echo "  Backend: $REGISTRY/$IMAGE_NAME-backend:$VERSION"
echo "  Frontend: $REGISTRY/$IMAGE_NAME-frontend:$VERSION"
echo "  Celery: $REGISTRY/$IMAGE_NAME-celery:$VERSION"
echo ""
echo "Next steps:"
echo "  1. Monitor deployment: kubectl get pods -n hishamos"
echo "  2. Check logs: kubectl logs -f deployment/backend -n hishamos"
echo "  3. Run smoke tests: ./scripts/deploy/smoke_tests.sh"
echo "  4. Monitor metrics in Grafana"

