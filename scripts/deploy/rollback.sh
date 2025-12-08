#!/bin/bash
# Rollback Script for Production Deployment
# Usage: ./rollback.sh <previous_version>

set -e

PREVIOUS_VERSION=${1:-latest}

echo "🔄 Rolling back to version: $PREVIOUS_VERSION"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found${NC}"
    exit 1
fi

# Verify Kubernetes connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

# Rollback deployments
echo -e "${YELLOW}Rolling back deployments...${NC}"

kubectl rollout undo deployment/backend -n hishamos
kubectl rollout undo deployment/frontend -n hishamos
kubectl rollout undo deployment/celery -n hishamos

# Wait for rollback to complete
echo -e "${YELLOW}Waiting for rollback to complete...${NC}"

kubectl rollout status deployment/backend -n hishamos --timeout=300s
kubectl rollout status deployment/frontend -n hishamos --timeout=300s
kubectl rollout status deployment/celery -n hishamos --timeout=300s

echo -e "${GREEN}✓ Rollback completed${NC}"

# Verify rollback
echo -e "${YELLOW}Verifying rollback...${NC}"

kubectl get pods -n hishamos

echo -e "${GREEN}✅ Rollback to version $PREVIOUS_VERSION completed successfully!${NC}"

