#!/usr/bin/env python3
"""
Load Testing Script for Datadog APM Logging Demo API

This script generates continuous traffic to the API to demonstrate:
- Log generation across different endpoints
- APM trace correlation
- Error tracking and monitoring
- Business transaction logging

Usage:
    python load_test.py [--host HOST] [--port PORT] [--rate RATE]
"""

import argparse
import time
import random
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class LoadTester:
    def __init__(self, base_url, requests_per_second=1):
        self.base_url = base_url
        self.requests_per_second = requests_per_second
        self.session = requests.Session()
        self.stats = {
            'total': 0,
            'success': 0,
            'errors': 0,
            'by_endpoint': {}
        }
        
    def log(self, message, color=Colors.RESET):
        """Print colored log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Colors.CYAN}[{timestamp}]{Colors.RESET} {color}{message}{Colors.RESET}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request and track statistics"""
        url = f"{self.base_url}{endpoint}"
        endpoint_key = f"{method} {endpoint}"
        
        if endpoint_key not in self.stats['by_endpoint']:
            self.stats['by_endpoint'][endpoint_key] = {'success': 0, 'errors': 0}
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            self.stats['total'] += 1
            
            if 200 <= response.status_code < 300:
                self.stats['success'] += 1
                self.stats['by_endpoint'][endpoint_key]['success'] += 1
                self.log(
                    f"{Colors.GREEN}✓{Colors.RESET} {method:4s} {endpoint:40s} "
                    f"[{response.status_code}] {response.elapsed.total_seconds():.3f}s",
                    Colors.GREEN
                )
                return response
            else:
                self.stats['errors'] += 1
                self.stats['by_endpoint'][endpoint_key]['errors'] += 1
                self.log(
                    f"{Colors.YELLOW}⚠{Colors.RESET} {method:4s} {endpoint:40s} "
                    f"[{response.status_code}] {response.text[:50]}",
                    Colors.YELLOW
                )
                return response
                
        except Exception as e:
            self.stats['total'] += 1
            self.stats['errors'] += 1
            self.stats['by_endpoint'][endpoint_key]['errors'] += 1
            self.log(
                f"{Colors.RED}✗{Colors.RESET} {method:4s} {endpoint:40s} "
                f"Error: {str(e)[:50]}",
                Colors.RED
            )
            return None
    
    def test_health_check(self):
        """Test health check endpoint"""
        self.make_request('GET', '/health')
    
    def test_get_user(self):
        """Test get user endpoint with random user"""
        user_ids = ['user_001', 'user_002', 'user_003', 'user_999']  # user_999 doesn't exist
        user_id = random.choice(user_ids)
        self.make_request('GET', f'/api/user/{user_id}')
    
    def test_list_products(self):
        """Test list products endpoint"""
        self.make_request('GET', '/api/products')
    
    def test_create_transaction(self):
        """Test create transaction endpoint"""
        users = ['user_001', 'user_002', 'user_003']
        products = ['prod_001', 'prod_002', 'prod_003']
        
        data = {
            'user_id': random.choice(users),
            'product_id': random.choice(products),
            'quantity': random.randint(1, 3)
        }
        
        self.make_request('POST', '/api/transaction', 
                         json=data,
                         headers={'Content-Type': 'application/json'})
    
    def test_analytics(self):
        """Test analytics endpoint"""
        self.make_request('GET', '/api/analytics/transactions')
    
    def test_error_simulation(self):
        """Test error simulation endpoint"""
        error_types = ['division', 'validation', 'generic']
        error_type = random.choice(error_types)
        self.make_request('GET', f'/api/error/simulate?type={error_type}')
    
    def test_invalid_transaction(self):
        """Test transaction with invalid data to generate validation errors"""
        # Missing required fields
        invalid_payloads = [
            {},  # Missing all fields
            {'user_id': 'user_001'},  # Missing product_id
            {'product_id': 'prod_001'},  # Missing user_id
            {'user_id': 'user_999', 'product_id': 'prod_001', 'quantity': 1},  # Invalid user
            {'user_id': 'user_001', 'product_id': 'prod_999', 'quantity': 1},  # Invalid product
        ]
        
        data = random.choice(invalid_payloads)
        self.make_request('POST', '/api/transaction',
                         json=data,
                         headers={'Content-Type': 'application/json'})
    
    def run_random_scenario(self):
        """Execute a random test scenario with weighted probabilities"""
        scenarios = [
            (self.test_health_check, 5),       # 5% - Health checks
            (self.test_get_user, 20),          # 20% - Get user
            (self.test_list_products, 15),     # 15% - List products
            (self.test_create_transaction, 35), # 35% - Create transaction (most common)
            (self.test_analytics, 10),         # 10% - Analytics
            (self.test_error_simulation, 5),   # 5% - Error simulation
            (self.test_invalid_transaction, 10) # 10% - Invalid transactions
        ]
        
        # Weighted random selection
        total_weight = sum(weight for _, weight in scenarios)
        rand = random.randint(1, total_weight)
        cumulative = 0
        
        for scenario, weight in scenarios:
            cumulative += weight
            if rand <= cumulative:
                scenario()
                break
    
    def print_stats(self):
        """Print statistics summary"""
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Load Test Statistics{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"Total Requests:    {Colors.CYAN}{self.stats['total']}{Colors.RESET}")
        print(f"Successful:        {Colors.GREEN}{self.stats['success']}{Colors.RESET}")
        print(f"Errors:            {Colors.RED}{self.stats['errors']}{Colors.RESET}")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / self.stats['total']) * 100
            print(f"Success Rate:      {Colors.GREEN}{success_rate:.2f}%{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}By Endpoint:{Colors.RESET}")
        for endpoint, stats in sorted(self.stats['by_endpoint'].items()):
            total = stats['success'] + stats['errors']
            print(f"  {endpoint:45s} - Success: {Colors.GREEN}{stats['success']:4d}{Colors.RESET} "
                  f"Errors: {Colors.RED}{stats['errors']:4d}{Colors.RESET} "
                  f"Total: {total:4d}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    def run(self, duration_seconds=None):
        """
        Run load test
        
        Args:
            duration_seconds: How long to run the test (None = run indefinitely)
        """
        self.log(f"Starting load test against {self.base_url}", Colors.BOLD)
        self.log(f"Rate: {self.requests_per_second} requests/second", Colors.BOLD)
        
        if duration_seconds:
            self.log(f"Duration: {duration_seconds} seconds", Colors.BOLD)
        else:
            self.log("Duration: Indefinite (Ctrl+C to stop)", Colors.BOLD)
        
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
        
        start_time = time.time()
        request_interval = 1.0 / self.requests_per_second
        
        try:
            while True:
                iteration_start = time.time()
                
                # Run test scenario
                self.run_random_scenario()
                
                # Check duration
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                
                # Sleep to maintain request rate
                elapsed = time.time() - iteration_start
                sleep_time = max(0, request_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.log("\n\nLoad test interrupted by user", Colors.YELLOW)
        
        finally:
            self.print_stats()

def main():
    parser = argparse.ArgumentParser(
        description='Load testing script for Datadog APM Logging Demo API'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='API host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='API port (default: 8080)'
    )
    parser.add_argument(
        '--rate',
        type=float,
        default=1.0,
        help='Requests per second (default: 1.0)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Test duration in seconds (default: run indefinitely)'
    )
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    # Test connectivity first
    print(f"{Colors.CYAN}Testing connectivity to {base_url}...{Colors.RESET}")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"{Colors.GREEN}✓ API is reachable{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Cannot connect to API: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}Make sure the API is running and accessible at {base_url}{Colors.RESET}")
        return
    
    # Run load test
    tester = LoadTester(base_url, requests_per_second=args.rate)
    tester.run(duration_seconds=args.duration)

if __name__ == '__main__':
    main()

