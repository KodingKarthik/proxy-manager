#!/usr/bin/env python3
"""
Simple script to test proxy connection using health score selection.

This is a minimal example showing how to:
1. Get a token
2. Get the best proxy by health score
3. Test the connection
"""

import requests
import sys


def main():
    """Simple proxy test."""
    
    API_URL = "http://localhost:8000"
    USERNAME = "demo_user"
    PASSWORD = "demo123456"
    
    print("🔐 Step 1: Logging in...")
    
    # Login
    login_url = f"{API_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(login_url, data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print(f"✅ Logged in! Token: {token[:20]}...")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Login failed. Please register first:")
            print(f"   curl -X POST '{API_URL}/auth/register' \\")
            print(f"     -H 'Content-Type: application/json' \\")
            print(f"     -d '{{\"username\": \"{USERNAME}\", \"email\": \"demo@example.com\", \"password\": \"{PASSWORD}\"}}'")
            sys.exit(1)
        else:
            raise
    
    print()
    print("📊 Step 2: Getting best proxy by health score...")
    
    # Get best proxy
    proxy_url = f"{API_URL}/proxy"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    params = {"strategy": "health_score"}
    
    try:
        response = requests.get(proxy_url, headers=headers, params=params)
        response.raise_for_status()
        proxy = response.json()
        
        print(f"✅ Got proxy:")
        print(f"   Address: {proxy['address']}")
        print(f"   Health Score: {proxy.get('health_score', 'N/A')}")
        print(f"   Latency: {proxy.get('latency', 'N/A')}ms")
        print(f"   Protocol: {proxy.get('protocol', 'http')}")
        print()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("❌ No working proxies available!")
            print("   Please add some proxies first using POST /proxies")
            sys.exit(1)
        else:
            raise
    
    print("🧪 Step 3: Testing proxy connection...")
    
    # Test proxy
    test_url = "http://httpbin.org/ip"
    proxy_url_formatted = f"http://{proxy['address']}"
    
    proxies = {
        "http": proxy_url_formatted,
        "https": proxy_url_formatted
    }
    
    try:
        response = requests.get(test_url, proxies=proxies, timeout=10, verify=False)
        response.raise_for_status()
        print(f"✅ Proxy connection successful!")
        print(f"   Response: {response.text}")
        print()
        print("🎉 Proxy is working! You can now use it for web scraping.")
    except Exception as e:
        print(f"❌ Proxy connection failed: {e}")
        print("   The proxy might be down or unreachable.")
        sys.exit(1)


if __name__ == "__main__":
    main()


