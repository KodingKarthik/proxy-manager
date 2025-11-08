#!/usr/bin/env python3
"""
Proxy Manager Demonstration Script
Shows how to connect to a proxy and perform web scraping
"""

import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
TARGET_URL = "https://httpbin.org/ip"  # Test URL

def print_header(title):
    """Print formatted header."""
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()

def get_access_token():
    """Get access token from user or environment."""
    token = input("Enter your access token (from /auth/login): ").strip()
    if not token:
        print("❌ Error: Access token is required")
        print("   Get token by logging in at: http://localhost:8000/docs")
        sys.exit(1)
    return token

def get_best_proxy(access_token):
    """Get best proxy based on health score."""
    print("📡 Step 1: Getting best proxy (health score strategy)...")
    try:
        response = requests.get(
            f"{API_URL}/proxy?strategy=health_score",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print("❌ Error: No working proxies available")
            print("   Please add at least one proxy first")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"   Make sure server is running at {API_URL}")
        sys.exit(1)

def display_proxy_info(proxy_data):
    """Display proxy information."""
    print("✅ Proxy Selected:")
    print(f"   ID: {proxy_data['id']}")
    print(f"   Address: {proxy_data['address']}")
    print(f"   Protocol: {proxy_data['protocol']}")
    print(f"   Health Score: {proxy_data.get('health_score', 0):.2f}/100")
    print(f"   Latency: {proxy_data.get('latency', 'N/A')}ms")
    print(f"   Status: {'✅ Working' if proxy_data['is_working'] else '❌ Not Working'}")
    print(f"   Fail Count: {proxy_data.get('fail_count', 0)}")
    print()

def build_proxy_url(proxy_data):
    """Build proxy URL for requests library."""
    if proxy_data.get('username') and proxy_data.get('password'):
        proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
    else:
        proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
    
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def make_request_through_proxy(target_url, proxies):
    """Make HTTP request through proxy."""
    print("🔗 Step 2: Connecting through proxy...")
    print(f"   Proxy URL: {proxies['http']}")
    print()
    
    print("🌐 Step 3: Making request through proxy...")
    print(f"   Target URL: {target_url}")
    print()
    
    try:
        response = requests.get(
            target_url,
            proxies=proxies,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        response.raise_for_status()
        return response
    except requests.exceptions.ProxyError as e:
        print(f"❌ Proxy Error: {e}")
        print("   The proxy might not be working. Try adding a different proxy.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Request Timeout")
        print("   The proxy might be slow or unreachable.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def display_results(response):
    """Display request results."""
    print("✅ SUCCESS! Request completed through proxy")
    print()
    print("📊 Response Details:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response Time: {response.elapsed.total_seconds():.2f} seconds")
    print(f"   Content Length: {len(response.content)} bytes")
    print()
    
    print("📄 Response Content:")
    try:
        # Try to parse as JSON
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        # If not JSON, show first 500 characters
        content = response.text[:500]
        print(content)
        if len(response.text) > 500:
            print("... (truncated)")
    print()

def main():
    """Main demonstration function."""
    print_header("PROXY MANAGER DEMONSTRATION")
    
    # Get access token
    access_token = get_access_token()
    print()
    
    # Get best proxy
    proxy_data = get_best_proxy(access_token)
    display_proxy_info(proxy_data)
    
    # Build proxy URL
    proxies = build_proxy_url(proxy_data)
    
    # Make request through proxy
    response = make_request_through_proxy(TARGET_URL, proxies)
    
    # Display results
    display_results(response)
    
    print_header("✅ DEMONSTRATION COMPLETE!")
    print("📦 Repository: https://github.com/KodingKarthik/proxy-manager")
    print("📚 API Docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()

