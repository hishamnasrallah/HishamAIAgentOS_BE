#!/bin/bash
# Smoke Tests for Production Deployment
# Usage: ./smoke_tests.sh <base_url>

set -e

BASE_URL=${1:-https://hishamos.example.com}
MAX_RETRIES=5
RETRY_DELAY=10

echo "🧪 Running smoke tests against: $BASE_URL"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local data=$4
    
    local url="$BASE_URL$endpoint"
    local status_code
    
    if [ "$method" == "GET" ]; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    elif [ "$method" == "POST" ]; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url" || echo "000")
    fi
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $method $endpoint - Status: $status_code"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $method $endpoint - Expected: $expected_status, Got: $status_code"
        ((FAILED++))
        return 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    echo -e "${YELLOW}Waiting for service to be ready...${NC}"
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s "$BASE_URL/api/v1/monitoring/health/" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service is ready${NC}"
            return 0
        fi
        
        ((retries++))
        echo "  Retry $retries/$MAX_RETRIES..."
        sleep $RETRY_DELAY
    done
    
    echo -e "${RED}✗ Service not ready after $MAX_RETRIES retries${NC}"
    return 1
}

# Run smoke tests
echo -e "${YELLOW}Starting smoke tests...${NC}"

# Wait for service
if ! wait_for_service; then
    echo -e "${RED}Smoke tests failed: Service not available${NC}"
    exit 1
fi

# Test 1: Health check
echo ""
echo "1. Testing health endpoint..."
test_endpoint "GET" "/api/v1/monitoring/health/" "200"

# Test 2: API schema
echo ""
echo "2. Testing API schema endpoint..."
test_endpoint "GET" "/api/schema/" "200"

# Test 3: Frontend accessibility
echo ""
echo "3. Testing frontend..."
test_endpoint "GET" "/" "200"

# Test 4: Login endpoint (should return 400 without credentials, but endpoint exists)
echo ""
echo "4. Testing login endpoint..."
test_endpoint "POST" "/api/v1/auth/login/" "400" '{}'

# Test 5: Registration endpoint
echo ""
echo "5. Testing registration endpoint..."
test_endpoint "POST" "/api/v1/auth/register/" "400" '{}'

# Test 6: GDPR retention policy (public endpoint)
echo ""
echo "6. Testing GDPR retention policy endpoint..."
test_endpoint "GET" "/api/v1/auth/gdpr/retention-policy/" "401"  # Requires auth

# Summary
echo ""
echo "=========================================="
echo "Smoke Test Summary:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "  Total:  $((PASSED + FAILED))"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some smoke tests failed${NC}"
    exit 1
fi

