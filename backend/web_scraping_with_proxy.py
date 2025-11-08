#!/usr/bin/env python3
"""
Web Scraping Script using Proxy Manager with Health Score Selection

This script demonstrates how to:
1. Connect to the Proxy Manager API
2. Get the best proxy based on health score
3. Use the proxy for web scraping
"""

import httpx
import requests
from typing import Optional, Dict, Any
import json
import time
from urllib.parse import urlparse


class ProxyManagerClient:
    """Client for interacting with the Proxy Manager API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the Proxy Manager client.
        
        Args:
            base_url: Base URL of the Proxy Manager API
        """
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            
        Returns:
            User data
        """
        url = f"{self.base_url}/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> str:
        """
        Login and get access token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Access token
        """
        url = f"{self.base_url}/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, data=data)  # Form data, not JSON
        response.raise_for_status()
        
        result = response.json()
        self.token = result["access_token"]
        self.username = username
        self.password = password
        
        return self.token
    
    def get_best_proxy(self, strategy: str = "health_score", target_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the best proxy based on health score.
        
        Args:
            strategy: Rotation strategy (default: "health_score")
            target_url: Optional target URL for blacklist checking
            
        Returns:
            Proxy data with health score
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")
        
        url = f"{self.base_url}/proxy"
        params = {"strategy": strategy}
        if target_url:
            params["target_url"] = target_url
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_proxies_list(self, working_only: bool = True, limit: int = 100) -> list:
        """
        Get list of all proxies.
        
        Args:
            working_only: Only return working proxies
            limit: Maximum number of proxies to return
            
        Returns:
            List of proxies
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")
        
        url = f"{self.base_url}/proxies"
        params = {
            "working_only": working_only,
            "limit": limit
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def add_proxy(self, ip: str, port: int, protocol: str = "http", 
                  username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new proxy.
        
        Args:
            ip: Proxy IP address
            port: Proxy port
            protocol: Proxy protocol (http, https, socks5)
            username: Optional proxy username
            password: Optional proxy password
            
        Returns:
            Created proxy data
        """
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")
        
        url = f"{self.base_url}/proxies"
        data = {
            "ip": ip,
            "port": port,
            "protocol": protocol
        }
        
        if username:
            data["username"] = username
        if password:
            data["password"] = password
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()


def build_proxy_dict(proxy_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Build proxy dictionary for requests/httpx.
    
    Args:
        proxy_data: Proxy data from API
        
    Returns:
        Proxy dictionary in format: {"http": "http://ip:port", "https": "http://ip:port"}
    """
    protocol = proxy_data.get("protocol", "http").lower()
    ip = proxy_data["ip"]
    port = proxy_data["port"]
    username = proxy_data.get("username")
    password = proxy_data.get("password")
    
    # Build proxy URL
    if username and password:
        proxy_url = f"{protocol}://{username}:{password}@{ip}:{port}"
    else:
        proxy_url = f"{protocol}://{ip}:{port}"
    
    # For requests library, use same proxy for both http and https
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def scrape_with_proxy(url: str, proxy_data: Dict[str, Any], timeout: int = 30) -> requests.Response:
    """
    Scrape a URL using a proxy.
    
    Args:
        url: Target URL to scrape
        proxy_data: Proxy data from API
        timeout: Request timeout in seconds
        
    Returns:
        Response object
    """
    proxies = build_proxy_dict(proxy_data)
    
    print(f"🌐 Scraping {url}")
    print(f"📊 Using proxy: {proxy_data['ip']}:{proxy_data['port']}")
    print(f"⭐ Health Score: {proxy_data.get('health_score', 'N/A')}")
    print(f"⚡ Latency: {proxy_data.get('latency', 'N/A')}ms")
    print(f"✅ Working: {proxy_data.get('is_working', False)}")
    print()
    
    response = requests.get(url, proxies=proxies, timeout=timeout, verify=False)
    response.raise_for_status()
    
    return response


def scrape_with_httpx(url: str, proxy_data: Dict[str, Any], timeout: int = 30) -> httpx.Response:
    """
    Scrape a URL using httpx with a proxy.
    
    Args:
        url: Target URL to scrape
        proxy_data: Proxy data from API
        timeout: Request timeout in seconds
        
    Returns:
        Response object
    """
    protocol = proxy_data.get("protocol", "http").lower()
    ip = proxy_data["ip"]
    port = proxy_data["port"]
    username = proxy_data.get("username")
    password = proxy_data.get("password")
    
    # Build proxy URL
    if username and password:
        proxy_url = f"{protocol}://{username}:{password}@{ip}:{port}"
    else:
        proxy_url = f"{protocol}://{ip}:{port}"
    
    print(f"🌐 Scraping {url}")
    print(f"📊 Using proxy: {ip}:{port}")
    print(f"⭐ Health Score: {proxy_data.get('health_score', 'N/A')}")
    print(f"⚡ Latency: {proxy_data.get('latency', 'N/A')}ms")
    print(f"✅ Working: {proxy_data.get('is_working', False)}")
    print()
    
    with httpx.Client(proxies=proxy_url, timeout=timeout, verify=False) as client:
        response = client.get(url)
        response.raise_for_status()
        return response


def main():
    """Main function demonstrating web scraping with proxy."""
    
    # Initialize client
    client = ProxyManagerClient()
    
    # Configuration
    API_URL = "http://localhost:8000"
    USERNAME = "demo_user"
    PASSWORD = "demo123456"
    EMAIL = "demo@example.com"
    
    print("=" * 70)
    print("🚀 Web Scraping with Proxy Manager - Health Score Selection")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Login (or register if first time)
        print("📝 Step 1: Authenticating...")
        try:
            client.login(USERNAME, PASSWORD)
            print(f"✅ Logged in as {USERNAME}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"⚠️  User not found. Registering new user...")
                client.register(USERNAME, EMAIL, PASSWORD)
                print(f"✅ Registered user: {USERNAME}")
                client.login(USERNAME, PASSWORD)
                print(f"✅ Logged in as {USERNAME}")
            else:
                raise
        print()
        
        # Step 2: Get best proxy by health score
        print("📊 Step 2: Getting best proxy by health score...")
        proxy_data = client.get_best_proxy(strategy="health_score")
        
        print(f"✅ Got proxy:")
        print(f"   ID: {proxy_data['id']}")
        print(f"   Address: {proxy_data['address']}")
        print(f"   Protocol: {proxy_data.get('protocol', 'http')}")
        print(f"   Health Score: {proxy_data.get('health_score', 'N/A')}")
        print(f"   Latency: {proxy_data.get('latency', 'N/A')}ms")
        print(f"   Working: {proxy_data.get('is_working', False)}")
        print()
        
        # Step 3: Test proxy connection
        print("🧪 Step 3: Testing proxy connection...")
        test_url = "http://httpbin.org/ip"  # Simple test endpoint
        
        try:
            response = scrape_with_proxy(test_url, proxy_data, timeout=30)
            print(f"✅ Proxy connection successful!")
            print(f"📄 Response: {response.text[:200]}")
            print()
        except Exception as e:
            print(f"❌ Proxy connection failed: {e}")
            print("⚠️  Trying to get another proxy...")
            
            # Try to get another proxy
            proxy_data = client.get_best_proxy(strategy="health_score")
            print(f"✅ Got new proxy: {proxy_data['address']}")
            print()
        
        # Step 4: Web scraping example
        print("🕷️  Step 4: Web scraping example...")
        
        # Example 1: Simple GET request
        target_url = "https://httpbin.org/html"
        print(f"📥 Scraping: {target_url}")
        
        try:
            response = scrape_with_proxy(target_url, proxy_data, timeout=30)
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📄 Content length: {len(response.text)} characters")
            print()
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            print()
        
        # Example 2: Using httpx (alternative)
        print("🕷️  Step 5: Web scraping with httpx...")
        target_url = "https://httpbin.org/json"
        
        try:
            response = scrape_with_httpx(target_url, proxy_data, timeout=30)
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            print()
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            print()
        
        # Step 6: List all proxies with health scores
        print("📋 Step 6: Listing all proxies with health scores...")
        proxies = client.get_proxies_list(working_only=True, limit=10)
        
        print(f"✅ Found {len(proxies)} working proxies:")
        for proxy in proxies[:5]:  # Show first 5
            print(f"   - {proxy['address']}: Health Score = {proxy.get('health_score', 'N/A')}, "
                  f"Latency = {proxy.get('latency', 'N/A')}ms")
        print()
        
        print("=" * 70)
        print("✅ Web scraping demonstration complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


