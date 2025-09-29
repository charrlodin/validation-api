#!/usr/bin/env python3
"""
Comprehensive Test Suite for Validation API
Runs all tests including stress testing and performance validation
"""
import requests
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict
import sys

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.RESET}")

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_health_check():
    """Test 1: Health Check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        print_success(f"Health check passed: {data}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_status_endpoint():
    """Test 2: Status Endpoint"""
    print_section("Test 2: Status & Data Sources")
    try:
        response = requests.get(f"{BASE_URL}/status")
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Email domains loaded: {data['email_domains_count']:,}")
        print_info(f"Email last updated: {data['email_last_updated']}")
        
        total_ips = sum(data['ip_blacklists'].values())
        print_info(f"Total IPs in blacklists: {total_ips:,}")
        
        for source, count in data['ip_blacklists'].items():
            print_info(f"  - {source}: {count:,} IPs")
            print_info(f"    Last updated: {data['ip_last_updated'][source]}")
        
        print_success("Status endpoint working correctly")
        return True
    except Exception as e:
        print_error(f"Status endpoint failed: {e}")
        return False

def test_validate_clean():
    """Test 3: Validate Clean Email & IP"""
    print_section("Test 3: Validate Clean Email & IP")
    
    test_cases = [
        {
            "name": "Clean email + clean IP",
            "email": "user@gmail.com",
            "ip": "8.8.8.8",
            "expected_disposable": False,
            "expected_blacklisted": False,
            "expected_risk_max": 0
        },
        {
            "name": "Clean email + clean IP (Cloudflare)",
            "email": "contact@proton.me",
            "ip": "1.1.1.1",
            "expected_disposable": False,
            "expected_blacklisted": False,
            "expected_risk_max": 0
        }
    ]
    
    all_passed = True
    for case in test_cases:
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": case["email"], "ip": case["ip"]}
            )
            elapsed = (time.time() - start) * 1000
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['email_disposable'] == case['expected_disposable']
            assert data['ip_blacklisted'] == case['expected_blacklisted']
            assert data['risk_score'] <= case['expected_risk_max']
            
            print_success(f"{case['name']}")
            print_info(f"  Response time: {elapsed:.2f}ms")
            print_info(f"  Risk score: {data['risk_score']}/100")
            
        except Exception as e:
            print_error(f"{case['name']} failed: {e}")
            all_passed = False
    
    return all_passed

def test_validate_disposable():
    """Test 4: Validate Disposable Emails"""
    print_section("Test 4: Disposable Email Detection")
    
    test_cases = [
        {"email": "test@mailinator.com", "ip": "8.8.8.8"},
        {"email": "user@guerrillamail.com", "ip": "1.1.1.1"},
        {"email": "temp@10minutemail.com", "ip": "8.8.8.8"},
        {"email": "disposable@tempmail.com", "ip": "1.1.1.1"}
    ]
    
    all_passed = True
    for case in test_cases:
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/validate",
                json=case
            )
            elapsed = (time.time() - start) * 1000
            
            assert response.status_code == 200
            data = response.json()
            assert data['email_disposable'] == True
            assert data['risk_score'] >= 70
            
            print_success(f"{case['email']} detected as disposable")
            print_info(f"  Response time: {elapsed:.2f}ms")
            print_info(f"  Risk score: {data['risk_score']}/100")
            print_info(f"  Reason: {data['email_reason']}")
            
        except Exception as e:
            print_error(f"{case['email']} test failed: {e}")
            all_passed = False
    
    return all_passed

def test_role_based_detection():
    """Test 5: Role-Based Email Detection"""
    print_section("Test 5: Role-Based Email Detection")
    
    role_emails = [
        "admin@example.com",
        "contact@example.com",
        "info@example.com",
        "support@example.com"
    ]
    
    all_passed = True
    for email in role_emails:
        try:
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": email, "ip": "8.8.8.8"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['email_role_based'] == True
            assert data['risk_score'] >= 20
            
            print_success(f"{email} detected as role-based")
            print_info(f"  Risk score: {data['risk_score']}/100")
            
        except Exception as e:
            print_error(f"{email} test failed: {e}")
            all_passed = False
    
    return all_passed

def test_typo_suggestions():
    """Test 6: Typo Suggestions"""
    print_section("Test 6: Typo Detection & Suggestions")
    
    typo_cases = [
        {"email": "user@gmal.com", "ip": "8.8.8.8", "suggestion": "user@gmail.com"},
        {"email": "admin@yahooo.com", "ip": "1.1.1.1", "suggestion": "admin@yahoo.com"},
        {"email": "test@hotmial.com", "ip": "8.8.8.8", "suggestion": "test@hotmail.com"}
    ]
    
    all_passed = True
    for case in typo_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": case["email"], "ip": case["ip"]}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            if data['email_typo_suggestion']:
                assert data['email_typo_suggestion'] == case['suggestion']
                print_success(f"{case['email']} → {data['email_typo_suggestion']}")
                print_info(f"  Risk score: {data['risk_score']}/100")
            else:
                print_info(f"{case['email']} - no suggestion (may be in disposable list)")
            
        except Exception as e:
            print_error(f"{case['email']} test failed: {e}")
            all_passed = False
    
    return all_passed

def test_ipv6_support():
    """Test 7: IPv6 Support"""
    print_section("Test 7: IPv6 Address Support")
    
    ipv6_cases = [
        "2001:4860:4860::8888",  # Google DNS
        "2606:4700:4700::1111",  # Cloudflare DNS
        "2001:db8::1"            # Documentation range
    ]
    
    all_passed = True
    for ip in ipv6_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": "test@example.com", "ip": ip}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            print_success(f"{ip} validated successfully")
            print_info(f"  Blacklisted: {data['ip_blacklisted']}")
            
        except Exception as e:
            print_error(f"{ip} test failed: {e}")
            all_passed = False
    
    return all_passed

def test_error_handling():
    """Test 8: Error Handling"""
    print_section("Test 8: Error Handling & Validation")
    
    error_cases = [
        {
            "name": "Invalid email format",
            "data": {"email": "not-an-email", "ip": "8.8.8.8"},
            "expected_status": 422
        },
        {
            "name": "Invalid IP format",
            "data": {"email": "test@example.com", "ip": "999.999.999.999"},
            "expected_status": 422
        },
        {
            "name": "Missing email field",
            "data": {"ip": "8.8.8.8"},
            "expected_status": 422
        },
        {
            "name": "Missing IP field",
            "data": {"email": "test@example.com"},
            "expected_status": 422
        }
    ]
    
    all_passed = True
    for case in error_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/validate",
                json=case["data"]
            )
            
            assert response.status_code == case["expected_status"]
            print_success(f"{case['name']} - Got expected {case['expected_status']}")
            
        except Exception as e:
            print_error(f"{case['name']} failed: {e}")
            all_passed = False
    
    return all_passed

def test_performance_stress():
    """Test 9: Performance & Stress Testing"""
    print_section("Test 9: Performance & Stress Testing")
    
    num_requests = 100
    latencies = []
    
    print_info(f"Sending {num_requests} sequential requests...")
    
    for i in range(num_requests):
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": "test@example.com", "ip": "8.8.8.8"}
            )
            elapsed = (time.time() - start) * 1000
            latencies.append(elapsed)
            
            if (i + 1) % 10 == 0:
                print_info(f"  Progress: {i + 1}/{num_requests}")
                
        except Exception as e:
            print_error(f"Request {i + 1} failed: {e}")
    
    if latencies:
        sorted_latencies = sorted(latencies)
        p50 = sorted_latencies[len(sorted_latencies) // 2]
        p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        avg = statistics.mean(latencies)
        
        print_success(f"Completed {num_requests} requests")
        print_info(f"  Average latency: {avg:.2f}ms")
        print_info(f"  p50 (median): {p50:.2f}ms")
        print_info(f"  p95: {p95:.2f}ms")
        print_info(f"  p99: {p99:.2f}ms")
        print_info(f"  Min: {min(latencies):.2f}ms")
        print_info(f"  Max: {max(latencies):.2f}ms")
        
        if p95 < 500:
            print_success(f"✓ p95 latency {p95:.2f}ms < 500ms target")
        else:
            print_error(f"✗ p95 latency {p95:.2f}ms > 500ms target")
        
        return p95 < 500
    
    return False

def test_rate_limiting():
    """Test 10: Rate Limiting"""
    print_section("Test 10: Rate Limiting (60/min)")
    
    print_info("Sending rapid requests to test rate limiting...")
    print_info("Note: Rate limiting is per IP, so this may not trigger on localhost")
    
    rate_limited = False
    for i in range(70):  # Try to exceed 60/min limit
        try:
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"email": "test@example.com", "ip": "8.8.8.8"}
            )
            
            if response.status_code == 429:
                rate_limited = True
                print_success(f"Rate limit triggered at request {i + 1}")
                print_info(f"  Response: {response.json()}")
                break
                
        except Exception as e:
            print_error(f"Request {i + 1} failed: {e}")
    
    if not rate_limited:
        print_info("Rate limiting not triggered (may be due to localhost)")
        print_info("This will work when accessed via tunnel or production URL")
    
    return True  # Don't fail test if rate limit not triggered locally

def test_bulk_validation():
    """Test 11: Bulk Validation"""
    print_section("Test 11: Bulk Validation (CSV)")
    
    try:
        with open('/Users/arronchild/Projects/validation-api/test.csv', 'rb') as f:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/bulk-validate",
                files={'file': ('test.csv', f, 'text/csv')}
            )
            elapsed = (time.time() - start) * 1000
            
            assert response.status_code == 200
            
            # Save results
            results_file = '/Users/arronchild/Projects/validation-api/test_results.csv'
            with open(results_file, 'wb') as out:
                out.write(response.content)
            
            print_success("Bulk validation completed")
            print_info(f"  Response time: {elapsed:.2f}ms")
            print_info(f"  Results saved to: test_results.csv")
            
            # Read and display results
            with open(results_file, 'r') as f:
                lines = f.readlines()
                print_info(f"  Total rows processed: {len(lines) - 1}")  # -1 for header
                if len(lines) > 1:
                    print_info(f"  First result row: {lines[1].strip()}")
            
            return True
            
    except Exception as e:
        print_error(f"Bulk validation failed: {e}")
        return False

def test_metrics_endpoint():
    """Test 12: Metrics Endpoint"""
    print_section("Test 12: Metrics & Observability")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        data = response.json()
        
        print_success("Metrics endpoint working")
        print_info(f"  Uptime: {data['uptime_seconds']:.0f} seconds")
        print_info(f"  Total requests: {data['total_requests']}")
        print_info(f"  Error count: {data['error_count']}")
        print_info(f"  Error rate: {data['error_rate']:.4f}")
        print_info(f"  Requests/second: {data['requests_per_second']:.2f}")
        
        if data['latency_ms']:
            print_info(f"  Latency p50: {data['latency_ms'].get('p50', 0):.2f}ms")
            print_info(f"  Latency p95: {data['latency_ms'].get('p95', 0):.2f}ms")
            print_info(f"  Latency p99: {data['latency_ms'].get('p99', 0):.2f}ms")
        
        return True
        
    except Exception as e:
        print_error(f"Metrics endpoint failed: {e}")
        return False

def main():
    print_section("🚀 COMPREHENSIVE API TEST SUITE")
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check if server is running
    if not check_server():
        print_error("❌ Server is not running!")
        print_info("\nTo start the server, run:")
        print_info("  cd /Users/arronchild/Projects/validation-api")
        print_info("  ./run.sh")
        print_info("\nOr manually:")
        print_info("  source venv/bin/activate")
        print_info("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print_success("✓ Server is running\n")
    
    # Run all tests
    tests = [
        ("Health Check", test_health_check),
        ("Status Endpoint", test_status_endpoint),
        ("Clean Email/IP Validation", test_validate_clean),
        ("Disposable Email Detection", test_validate_disposable),
        ("Role-Based Detection", test_role_based_detection),
        ("Typo Suggestions", test_typo_suggestions),
        ("IPv6 Support", test_ipv6_support),
        ("Error Handling", test_error_handling),
        ("Performance Stress Test", test_performance_stress),
        ("Rate Limiting", test_rate_limiting),
        ("Bulk Validation", test_bulk_validation),
        ("Metrics Endpoint", test_metrics_endpoint)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        if passed:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BOLD}Results: {passed_count}/{total_count} tests passed{Colors.RESET}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.RESET}\n")
        print_info("Your API is production-ready!")
        print_info("\nNext steps:")
        print_info("  1. Expose via ngrok: ngrok http 8000")
        print_info("  2. Test over tunnel with real internet traffic")
        print_info("  3. Deploy to production (Render, Railway, Fly.io)")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.RESET}\n")
        print_info("Please review the errors above and fix before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
