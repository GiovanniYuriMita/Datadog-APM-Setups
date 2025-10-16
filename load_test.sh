#!/bin/bash

##############################################################################
# Load Testing Script for Datadog APM Logging Demo API (Bash Version)
#
# This script generates continuous traffic to the API using curl
# Demonstrates logging best practices across different endpoints
#
# Usage:
#   ./load_test.sh [HOST] [PORT] [RATE_PER_SECOND]
#
# Examples:
#   ./load_test.sh                          # localhost:8080, 1 req/sec
#   ./load_test.sh localhost 8080 2         # localhost:8080, 2 req/sec
##############################################################################

# Configuration
HOST="${1:-localhost}"
PORT="${2:-8080}"
RATE="${3:-1}"  # Requests per second
BASE_URL="http://${HOST}:${PORT}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Statistics
TOTAL_REQUESTS=0
SUCCESSFUL_REQUESTS=0
FAILED_REQUESTS=0

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to log with timestamp
log() {
    local color=$1
    shift
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${CYAN}[${timestamp}]${NC} ${color}$@${NC}"
}

# Function to make HTTP request
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local url="${BASE_URL}${endpoint}"
    
    ((TOTAL_REQUESTS++))
    
    local start_time=$(date +%s.%N)
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # Extract status code (last line)
    local status_code=$(echo "$response" | tail -n 1)
    local body=$(echo "$response" | head -n -1)
    
    # Check if status code is numeric
    if [[ ! "$status_code" =~ ^[0-9]+$ ]]; then
        ((FAILED_REQUESTS++))
        log "${RED}" "✗ ${method} ${endpoint} - Connection Error"
        return 1
    fi
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        ((SUCCESSFUL_REQUESTS++))
        log "${GREEN}" "✓ ${method} ${endpoint} [${status_code}] ${duration}s"
    else
        ((FAILED_REQUESTS++))
        local error_msg=$(echo "$body" | head -c 50)
        log "${YELLOW}" "⚠ ${method} ${endpoint} [${status_code}] ${error_msg}"
    fi
}

# Test scenarios
test_health_check() {
    make_request "GET" "/health"
}

test_get_user() {
    local users=("user_001" "user_002" "user_003" "user_999")
    local user_id=${users[$RANDOM % ${#users[@]}]}
    make_request "GET" "/api/user/${user_id}"
}

test_list_products() {
    make_request "GET" "/api/products"
}

test_create_transaction() {
    local users=("user_001" "user_002" "user_003")
    local products=("prod_001" "prod_002" "prod_003")
    local user_id=${users[$RANDOM % ${#users[@]}]}
    local product_id=${products[$RANDOM % ${#products[@]}]}
    local quantity=$((RANDOM % 3 + 1))
    
    local data="{\"user_id\":\"${user_id}\",\"product_id\":\"${product_id}\",\"quantity\":${quantity}}"
    make_request "POST" "/api/transaction" "$data"
}

test_analytics() {
    make_request "GET" "/api/analytics/transactions"
}

test_error_simulation() {
    local error_types=("division" "validation" "generic")
    local error_type=${error_types[$RANDOM % ${#error_types[@]}]}
    make_request "GET" "/api/error/simulate?type=${error_type}"
}

test_invalid_transaction() {
    local invalid_payloads=(
        '{}'
        '{"user_id":"user_001"}'
        '{"product_id":"prod_001"}'
        '{"user_id":"user_999","product_id":"prod_001","quantity":1}'
        '{"user_id":"user_001","product_id":"prod_999","quantity":1}'
    )
    local data=${invalid_payloads[$RANDOM % ${#invalid_payloads[@]}]}
    make_request "POST" "/api/transaction" "$data"
}

# Run random scenario with weighted probabilities
run_random_scenario() {
    local rand=$((RANDOM % 100))
    
    if [ $rand -lt 5 ]; then
        test_health_check          # 5%
    elif [ $rand -lt 25 ]; then
        test_get_user             # 20%
    elif [ $rand -lt 40 ]; then
        test_list_products        # 15%
    elif [ $rand -lt 75 ]; then
        test_create_transaction   # 35%
    elif [ $rand -lt 85 ]; then
        test_analytics            # 10%
    elif [ $rand -lt 90 ]; then
        test_error_simulation     # 5%
    else
        test_invalid_transaction  # 10%
    fi
}

# Print statistics
print_stats() {
    echo ""
    print_color "${BOLD}" "================================================================================"
    print_color "${BOLD}" "Load Test Statistics"
    print_color "${BOLD}" "================================================================================"
    print_color "${CYAN}" "Total Requests:    ${TOTAL_REQUESTS}"
    print_color "${GREEN}" "Successful:        ${SUCCESSFUL_REQUESTS}"
    print_color "${RED}" "Errors:            ${FAILED_REQUESTS}"
    
    if [ $TOTAL_REQUESTS -gt 0 ]; then
        local success_rate=$(echo "scale=2; ($SUCCESSFUL_REQUESTS * 100) / $TOTAL_REQUESTS" | bc)
        print_color "${GREEN}" "Success Rate:      ${success_rate}%"
    fi
    
    print_color "${BOLD}" "================================================================================"
    echo ""
}

# Cleanup on exit
cleanup() {
    echo ""
    log "${YELLOW}" "Load test interrupted by user"
    print_stats
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_color "${BOLD}" "================================================================================"
    print_color "${BOLD}" "Datadog APM Logging Demo - Load Test (Bash)"
    print_color "${BOLD}" "================================================================================"
    log "${BOLD}" "Starting load test against ${BASE_URL}"
    log "${BOLD}" "Rate: ${RATE} requests/second"
    log "${BOLD}" "Duration: Indefinite (Ctrl+C to stop)"
    print_color "${BOLD}" "================================================================================"
    echo ""
    
    # Test connectivity
    print_color "${CYAN}" "Testing connectivity to ${BASE_URL}..."
    if curl -s -f "${BASE_URL}/health" > /dev/null 2>&1; then
        print_color "${GREEN}" "✓ API is reachable"
        echo ""
    else
        print_color "${RED}" "✗ Cannot connect to API at ${BASE_URL}"
        print_color "${YELLOW}" "Make sure the API is running and accessible"
        exit 1
    fi
    
    # Calculate sleep interval
    local sleep_interval=$(echo "scale=3; 1 / $RATE" | bc)
    
    # Run load test
    while true; do
        run_random_scenario
        sleep "$sleep_interval"
    done
}

# Run main
main

