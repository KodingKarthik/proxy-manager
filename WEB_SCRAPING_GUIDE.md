# Web Scraping Guide - Using Proxy Manager

## Overview

This guide shows you how to use the Proxy Manager API to perform web scraping through managed proxies. The system automatically selects the best proxy based on health scores, latency, and reliability.

---

## 🚀 Quick Start

### Step 1: Get Your API Token

```bash
# Register (first time only)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "scraper",
    "email": "scraper@example.com",
    "password": "securepass123"
  }'

# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=scraper&password=securepass123"
```

Save the `access_token` from the response!

### Step 2: Get Best Proxy by Health Score

```bash
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

This returns the proxy with the **highest health score** (best overall performance).

---

## 📊 Health Score Explained

Health scores range from **0.0 to 100.0** and consider:

1. **Working Status (40 points)** - Is the proxy currently working?
2. **Latency (30 points)** - Response time (lower is better)
3. **Failure Count (20 points)** - How many times it failed (lower is better)
4. **Health Check Recency (10 points)** - How recently it was tested

**Best Practice:** Always use `strategy=health_score` for web scraping to get the most reliable proxy.

---

## 🐍 Python Web Scraping Examples

### Example 1: Basic Web Scraping with Requests

```python
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
TARGET_URL = "https://example.com"

def get_best_proxy():
    """Get the best proxy based on health score."""
    response = requests.get(
        f"{API_BASE_URL}/proxy?strategy=health_score",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    response.raise_for_status()
    return response.json()

def scrape_with_proxy(url, max_retries=3):
    """Scrape a URL using the best available proxy."""
    for attempt in range(max_retries):
        try:
            # Get best proxy
            proxy_data = get_best_proxy()
            print(f"Using proxy: {proxy_data['address']} (Health Score: {proxy_data['health_score']:.2f})")
            
            # Build proxy URL
            if proxy_data.get('username') and proxy_data.get('password'):
                proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
            else:
                proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
            
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            # Make request through proxy
            response = requests.get(
                url,
                proxies=proxies,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            print(f"✅ Success! Status: {response.status_code}")
            return response.text
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            else:
                raise
    
    return None

# Usage
if __name__ == "__main__":
    html_content = scrape_with_proxy(TARGET_URL)
    print(html_content[:500])  # Print first 500 characters
```

### Example 2: Advanced Scraping with BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup
import json

API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

class ProxyScraper:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_proxy(self, strategy="health_score"):
        """Get a proxy using specified strategy."""
        response = requests.get(
            f"{self.api_url}/proxy",
            params={"strategy": strategy},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response.raise_for_status()
        return response.json()
    
    def build_proxy_dict(self, proxy_data):
        """Build proxy dictionary for requests library."""
        if proxy_data.get('username') and proxy_data.get('password'):
            proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
        else:
            proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def scrape(self, url, strategy="health_score", retries=3):
        """Scrape a URL with automatic proxy rotation on failure."""
        for attempt in range(retries):
            try:
                # Get best proxy
                proxy_data = self.get_proxy(strategy=strategy)
                print(f"🔄 Attempt {attempt + 1}: Using proxy {proxy_data['address']} "
                      f"(Health: {proxy_data['health_score']:.1f}, Latency: {proxy_data.get('latency', 'N/A')}ms)")
                
                # Build proxies
                proxies = self.build_proxy_dict(proxy_data)
                
                # Make request
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=30,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                response.raise_for_status()
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(2)
                else:
                    raise
        
        return None
    
    def scrape_and_parse(self, url, strategy="health_score"):
        """Scrape URL and parse with BeautifulSoup."""
        html = self.scrape(url, strategy=strategy)
        if html:
            return BeautifulSoup(html, 'html.parser')
        return None

# Usage Example
scraper = ProxyScraper(API_BASE_URL, ACCESS_TOKEN)

# Scrape a website
soup = scraper.scrape_and_parse("https://example.com")
if soup:
    # Extract data
    title = soup.find('title')
    print(f"Page Title: {title.text if title else 'Not found'}")
```

### Example 3: Scraping Multiple Pages with Proxy Rotation

```python
import requests
from bs4 import BeautifulSoup
import time
from typing import List

API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

def scrape_multiple_pages(urls: List[str], access_token: str):
    """Scrape multiple pages, rotating proxies for each request."""
    results = []
    
    for i, url in enumerate(urls):
        try:
            # Get a new proxy for each request (round-robin)
            strategy = "round_robin" if i % 2 == 0 else "health_score"
            
            proxy_response = requests.get(
                f"{API_BASE_URL}/proxy",
                params={"strategy": strategy},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            proxy_data = proxy_response.json()
            
            # Build proxy URL
            if proxy_data.get('username') and proxy_data.get('password'):
                proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
            else:
                proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
            
            proxies = {"http": proxy_url, "https": proxy_url}
            
            # Scrape
            response = requests.get(
                url,
                proxies=proxies,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            
            results.append({
                "url": url,
                "status": response.status_code,
                "title": title.text if title else None,
                "proxy": proxy_data['address'],
                "health_score": proxy_data['health_score']
            })
            
            print(f"✅ Scraped {url} using proxy {proxy_data['address']}")
            
            # Be nice - delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

# Usage
urls = [
    "https://example.com",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent"
]

results = scrape_multiple_pages(urls, ACCESS_TOKEN)
for result in results:
    print(json.dumps(result, indent=2))
```

### Example 4: Using httpx (Async) for Faster Scraping

```python
import httpx
import asyncio

API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

async def scrape_with_proxy_async(url: str, access_token: str):
    """Async web scraping with proxy."""
    async with httpx.AsyncClient() as client:
        # Get best proxy
        proxy_response = await client.get(
            f"{API_BASE_URL}/proxy?strategy=health_score",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        proxy_data = proxy_response.json()
        
        # Build proxy URL
        if proxy_data.get('username') and proxy_data.get('password'):
            proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
        else:
            proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
        
        proxies = {
            "http://": proxy_url,
            "https://": proxy_url
        }
        
        # Scrape with proxy
        async with httpx.AsyncClient(proxies=proxies, timeout=30.0) as proxy_client:
            response = await proxy_client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            return response.text

# Usage
async def main():
    html = await scrape_with_proxy_async("https://example.com", ACCESS_TOKEN)
    print(html[:500])

# Run
asyncio.run(main())
```

---

## 🌐 Using with Selenium (Browser Automation)

```python
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import requests

API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

def get_proxy_for_selenium():
    """Get proxy formatted for Selenium."""
    response = requests.get(
        f"{API_BASE_URL}/proxy?strategy=health_score",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    proxy_data = response.json()
    
    # Selenium format: "host:port"
    return f"{proxy_data['ip']}:{proxy_data['port']}"

# Setup Selenium with proxy
proxy_address = get_proxy_for_selenium()
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = proxy_address
proxy.ssl_proxy = proxy_address

capabilities = webdriver.DesiredCapabilities.CHROME
proxy.add_to_capabilities(capabilities)

driver = webdriver.Chrome(desired_capabilities=capabilities)
driver.get("https://example.com")
print(driver.page_source)
driver.quit()
```

---

## 📈 Best Practices

### 1. Always Use Health Score Strategy
```python
# ✅ Good - Gets best proxy
proxy = get_proxy(strategy="health_score")

# ❌ Avoid - May get unreliable proxy
proxy = get_proxy(strategy="random")
```

### 2. Handle Proxy Failures Gracefully
```python
def scrape_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            proxy = get_proxy(strategy="health_score")
            # ... scrape with proxy
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise
```

### 3. Rotate Proxies for Multiple Requests
```python
# Use round_robin for even distribution
for url in urls:
    proxy = get_proxy(strategy="round_robin")
    # ... scrape
```

### 4. Monitor Proxy Health
```python
proxy_data = get_proxy(strategy="health_score")
if proxy_data['health_score'] < 50:
    print("⚠️ Warning: Proxy health score is low")
```

### 5. Respect Rate Limits
```python
import time

for url in urls:
    scrape(url)
    time.sleep(1)  # Be nice to the target server
```

---

## 🔍 Testing Your Setup

### Test 1: Check Proxy IP
```python
import requests

proxy_data = get_proxy(strategy="health_score")
proxies = build_proxy_dict(proxy_data)

response = requests.get("https://httpbin.org/ip", proxies=proxies)
print(f"Your IP through proxy: {response.json()}")
```

### Test 2: Check Proxy Speed
```python
import time

start = time.time()
proxy_data = get_proxy(strategy="health_score")
proxies = build_proxy_dict(proxy_data)
response = requests.get("https://httpbin.org/ip", proxies=proxies)
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f} seconds")
print(f"Proxy latency: {proxy_data.get('latency', 'N/A')}ms")
```

---

## 🛠️ Troubleshooting

### Problem: "No working proxies available"
**Solution:** Add more proxies or wait for health checks to complete.

### Problem: Proxy timeout
**Solution:** Use proxies with higher health scores or lower latency.

### Problem: Rate limiting
**Solution:** Rotate proxies more frequently or add delays between requests.

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/proxies
- **Proxy Statistics:** Check `/health/proxies` endpoint

---

## 🎯 Real-World Example: Scraping E-commerce Site

```python
import requests
from bs4 import BeautifulSoup
import json

class EcommerceScraper:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.token = token
    
    def get_proxy(self):
        response = requests.get(
            f"{self.api_url}/proxy?strategy=health_score",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
    
    def scrape_product(self, product_url):
        proxy_data = self.get_proxy()
        
        # Build proxy
        proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        # Scrape
        response = requests.get(
            product_url,
            proxies=proxies,
            headers={"User-Agent": "Mozilla/5.0..."}
        )
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product info
        return {
            "title": soup.find('h1').text if soup.find('h1') else None,
            "price": soup.find(class_='price').text if soup.find(class_='price') else None,
            "proxy_used": proxy_data['address'],
            "health_score": proxy_data['health_score']
        }

# Usage
scraper = EcommerceScraper("http://localhost:8000", "YOUR_TOKEN")
product = scraper.scrape_product("https://example-shop.com/product/123")
print(json.dumps(product, indent=2))
```

---

Happy Scraping! 🚀

