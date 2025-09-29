#!/usr/bin/env python3
"""
Test script for the validation API
Run this after starting the API server
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_status():
    print("Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Email domains: {data['email_domains_count']}")
    print(f"IP blacklists: {data['ip_blacklists']}\n")

def test_validate():
    print("Testing /validate endpoint...")
    
    test_cases = [
        {
            "name": "Disposable email + clean IP",
            "data": {"email": "test@mailinator.com", "ip": "8.8.8.8"}
        },
        {
            "name": "Clean email + clean IP",
            "data": {"email": "user@gmail.com", "ip": "1.1.1.1"}
        },
        {
            "name": "Disposable email from list",
            "data": {"email": "admin@guerrillamail.com", "ip": "93.184.216.34"}
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/validate",
            json=test['data']
        )
        elapsed = (time.time() - start) * 1000
        
        print(f"  Response time: {elapsed:.2f}ms")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Email disposable: {data['email_disposable']}")
            print(f"  Email reason: {data['email_reason']}")
            print(f"  IP blacklisted: {data['ip_blacklisted']}")
            print(f"  IP hits: {data['ip_blacklist_hits']}")
            print(f"  IP sources: {data['ip_blacklist_sources']}")

def test_invalid_input():
    print("\n\nTesting invalid input...")
    
    print("\nInvalid email:")
    response = requests.post(
        f"{BASE_URL}/validate",
        json={"email": "not-an-email", "ip": "8.8.8.8"}
    )
    print(f"Status: {response.status_code} (expected 422)")
    
    print("\nInvalid IP:")
    response = requests.post(
        f"{BASE_URL}/validate",
        json={"email": "test@example.com", "ip": "999.999.999.999"}
    )
    print(f"Status: {response.status_code} (expected 422)")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Email & IP Validation API Test Suite")
        print("=" * 60)
        print()
        
        test_health()
        test_status()
        test_validate()
        test_invalid_input()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Make sure the server is running: uvicorn main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
