#!/bin/bash
# Comprehensive Health Check Script
# Usage: ./health_check.sh [base_url]

set -e

BASE_URL=${1:-https://hishamos.example.com}

echo "🏥 Running comprehensive health checks..."
echo "Target: $BASE_URL"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0
WARNINGS=0

# Function to check endpoint
check_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=$3
    
    local url="$BASE_URL$endpoint"
    local response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $name - Status: $status_code"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $name - Expected: $expected_status, Got: $status_code"
        echo "  Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Function to check response time
check_response_time() {
    local name=$1
    local endpoint=$2
    local max_time=$3  # in seconds
    
    local url="$BASE_URL$endpoint"
    local start_time=$(date +%s.%N)
    curl -s -o /dev/null "$url" || return 1
    local end_time=$(date +%s.%N)
    
    local elapsed=$(echo "$end_time - $start_time" | bc)
    local elapsed_ms=$(echo "$elapsed * 1000" | bc | cut -d. -f1)
    
    if (( $(echo "$elapsed < $max_time" | bc -l) )); then
        echo -e "${GREEN}✓${NC} $name - Response time: ${elapsed_ms}ms (target: < ${max_time}s)"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $name - Response time: ${elapsed_ms}ms (target: < ${max_time}s)"
        ((WARNINGS++))
        return 1
    fi
}

# Health Checks
echo -e "${BLUE}=== Application Health ===${NC}"

# 1. Backend health
check_endpoint "Backend Health" "/api/v1/monitoring/health/" "200"

# 2. Frontend
check_endpoint "Frontend" "/" "200"

# 3. API Schema
check_endpoint "API Schema" "/api/schema/" "200"

# 4. Response times
echo ""
echo -e "${BLUE}=== Performance Checks ===${NC}"

if command -v bc &> /dev/null; then
    check_response_time "Health Endpoint" "/api/v1/monitoring/health/" "0.2"
    check_response_time "Frontend" "/" "0.5"
    check_response_time "API Schema" "/api/schema/" "1.0"
else
    echo -e "${YELLOW}⚠ bc not installed, skipping response time checks${NC}"
fi

# 5. Database connectivity (if authenticated)
echo ""
echo -e "${BLUE}=== Database Connectivity ===${NC}"
echo -e "${YELLOW}Note: Database checks require authentication${NC}"

# 6. SSL/TLS
echo ""
echo -e "${BLUE}=== Security Checks ===${NC}"

SSL_INFO=$(echo | openssl s_client -connect $(echo $BASE_URL | sed 's|https\?://||' | cut -d/ -f1):443 -servername $(echo $BASE_URL | sed 's|https\?://||' | cut -d/ -f1) 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)

if [ -n "$SSL_INFO" ]; then
    echo -e "${GREEN}✓${NC} SSL certificate valid"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} SSL certificate check failed"
    ((FAILED++))
fi

# Summary
echo ""
echo "=========================================="
echo "Health Check Summary:"
echo -e "  ${GREEN}Passed:${NC} $PASSED"
echo -e "  ${RED}Failed:${NC} $FAILED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo "  Total:  $((PASSED + FAILED + WARNINGS))"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some health checks failed${NC}"
    exit 1
fi

