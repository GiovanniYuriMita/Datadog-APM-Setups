#!/bin/bash

# Laravel Datadog APM Test Script
# This script generates various HTTP requests to test Datadog APM tracing and payload capture

BASE_URL="http://localhost:8080"
API_URL="${BASE_URL}/api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Laravel Datadog APM Test Script${NC}"
echo "==================================="
echo ""

# Function to make HTTP requests and display results
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo -e "${BLUE}${method} ${url}${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d "$data" \
            "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Accept: application/json" \
            "$url")
    fi
    
    # Split response and status code
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Success (HTTP $http_code)${NC}"
        echo "Response: $body" | head -c 200
        if [ ${#body} -gt 200 ]; then
            echo "..."
        fi
    else
        echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# Test 1: Health Check
make_request "GET" "$API_URL/health" "" "Health Check"

# Test 2: Echo endpoint with JSON payload
make_request "POST" "$API_URL/echo" '{"id": "test-001", "content": "Testing Laravel middleware payload capture", "user": {"name": "John Doe", "email": "john@example.com"}}' "Echo with JSON Payload"

# Test 3: Process data endpoint
make_request "POST" "$API_URL/process" '{"id": "process-001", "data": {"type": "user_registration", "fields": ["name", "email", "password"], "metadata": {"source": "web", "version": "1.0"}}}' "Process Data with Complex Payload"

# Test 4: Custom function endpoint
make_request "POST" "$API_URL/custom-function" '{"id": "custom-001", "content": "Testing custom function tracing"}' "Custom Function with Tracing"

# Test 5: Database simulation
make_request "GET" "$API_URL/database" "" "Database Query Simulation"

# Test 6: External API simulation
make_request "GET" "$API_URL/external" "" "External API Call Simulation"

# Test 7: Error generation
make_request "GET" "$API_URL/error" "" "Error Generation Test"

# Test 8: Form data (URL-encoded)
echo -e "${YELLOW}Testing: Form Data (URL-encoded)${NC}"
echo -e "${BLUE}POST $API_URL/echo${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Accept: application/json" \
    -d "id=form-001&content=Testing+form+data&user[name]=Jane+Doe&user[email]=jane@example.com" \
    "$API_URL/echo")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✅ Success (HTTP $http_code)${NC}"
    echo "Response: $body" | head -c 200
    if [ ${#body} -gt 200 ]; then
        echo "..."
    fi
else
    echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 9: Rapid requests to test trace batching
echo -e "${YELLOW}Testing: Rapid Requests (Trace Batching)${NC}"
for i in {1..5}; do
    make_request "POST" "$API_URL/echo" "{\"id\": \"rapid-$i\", \"content\": \"Rapid request $i\"}" "Rapid Request $i"
    sleep 0.1
done

echo -e "${GREEN}🎉 All tests completed!${NC}"
echo ""
echo -e "${BLUE}Check the container logs to see Datadog traces:${NC}"
echo "docker-compose logs laravel-app | grep -A 5 -B 5 'http.request.body_raw\\|http.payload'"
echo ""
echo -e "${BLUE}Check Datadog agent logs:${NC}"
echo "docker-compose logs datadog-agent | tail -20"