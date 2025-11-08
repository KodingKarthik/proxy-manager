# 🚀 Working Web Scraping with Proxy Health Score

## ✅ Complete Working Solution

This guide shows you how to connect to a proxy **based on health score** and perform web scraping.

---

## 🎯 Quick Start (3 Steps)

### Step 1: Start the Server

```bash
./run_server.sh
```

**Keep this terminal open!**

---

### Step 2: Test Proxy Connection

**Open a new terminal:**

```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
python3 simple_proxy_test.py
```

**This script will:**
- ✅ Login automatically (or register if needed)
- ✅ Get the best proxy by **health score**
- ✅ Test the connection
- ✅ Show you the proxy details

---

### Step 3: Full Web Scraping Example

```bash
python3 web_scraping_with_proxy.py
```

**This script demonstrates:**
- ✅ Getting proxy by health score
- ✅ Web scraping with `requests`
- ✅ Web scraping with `httpx`
- ✅ Listing all proxies with health scores

---

## 📊 Understanding Health Score

**Health Score** is a 0-100 rating that considers:

1. **Working Status (40 points)** - Is proxy currently working?
2. **Latency (30 points)** - Response time (lower = better)
3. **Failure Count (20 points)** - How many failures (lower = better)
4. **Recency (10 points)** - How recently tested (newer = better)

**Best Practice:** Always use `strategy=health_score` to get the **best proxy**.

---

## 🔧 Manual Usage

### 1. Get Token

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

**Copy the `access_token`!**

---

### 2. Get Best Proxy by Health Score

```bash
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

**Response:**
```json
{
  "id": 1,
  "ip": "192.168.1.100",
  "port": 8080,
  "address": "192.168.1.100:8080",
  "protocol": "http",
  "health_score": 85.5,
  "latency": 120.5,
  "is_working": true,
  "fail_count": 0
}
```

---

### 3. Use Proxy for Web Scraping

**Python Example:**

```python
import requests

# Get proxy (from Step 2)
proxy_data = {
    "ip": "192.168.1.100",
    "port": 8080,
    "protocol": "http",
    "username": None,
    "password": None
}

# Build proxy URL
proxy_url = f"{proxy_data['protocol']}://{proxy_data['ip']}:{proxy_data['port']}"

# Use proxy
proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Scrape website
response = requests.get(
    "https://example.com",
    proxies=proxies,
    timeout=30
)

print(response.text)
```

---

## 🐍 Python Client Class

**Use the provided `ProxyManagerClient` class:**

```python
from web_scraping_with_proxy import ProxyManagerClient, scrape_with_proxy

# Initialize client
client = ProxyManagerClient()

# Login
client.login("demo_user", "demo123456")

# Get best proxy by health score
proxy = client.get_best_proxy(strategy="health_score")

# Scrape website
response = scrape_with_proxy("https://example.com", proxy)
print(response.text)
```

---

## 📋 API Endpoints for Health Score

### Get Best Proxy by Health Score

```bash
GET /proxy?strategy=health_score
```

**Query Parameters:**
- `strategy`: `"health_score"` (required)
- `target_url`: Optional URL for blacklist checking

**Response:**
- Returns proxy with **highest health score**
- Includes `health_score` field (0-100)
- Includes `latency`, `is_working`, `fail_count`

---

### List All Proxies with Health Scores

```bash
GET /proxies?working_only=true&limit=100
```

**Response:**
- List of all proxies
- Each proxy includes `health_score`
- Sorted by ID (you can sort by health_score in your code)

---

## 🎯 Best Practices

### 1. Always Use Health Score Strategy

```python
proxy = client.get_best_proxy(strategy="health_score")
```

**Why?** Health score considers multiple factors, not just latency.

---

### 2. Handle Proxy Failures

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        proxy = client.get_best_proxy(strategy="health_score")
        response = scrape_with_proxy(url, proxy)
        break  # Success!
    except Exception as e:
        if attempt == max_retries - 1:
            raise  # Last attempt failed
        print(f"Proxy failed, retrying... ({attempt + 1}/{max_retries})")
```

---

### 3. Check Health Score Before Use

```python
proxy = client.get_best_proxy(strategy="health_score")

if proxy['health_score'] < 50:
    print("⚠️  Warning: Low health score, proxy might be unreliable")
else:
    print(f"✅ Good health score: {proxy['health_score']}")
```

---

## 🔍 Troubleshooting

### "No working proxies available"

**Solution:**
1. Add proxies using `POST /proxies`
2. Wait for health checks to run (every 5 minutes)
3. Or manually test proxies using `POST /proxies/{id}/test`

---

### "Proxy connection failed"

**Solution:**
1. Check if proxy is working: `is_working: true`
2. Check health score: Should be > 0
3. Try another proxy: Get a new one with `strategy=health_score`
4. Check proxy credentials (username/password)

---

### "401 Unauthorized"

**Solution:**
1. Make sure you're logged in
2. Include `Authorization: Bearer TOKEN` header
3. Token might be expired - login again

---

## 📚 Example Scripts

### 1. `simple_proxy_test.py`
- Minimal example
- Tests proxy connection
- Shows health score

### 2. `web_scraping_with_proxy.py`
- Full-featured example
- Multiple scraping methods
- Error handling
- Proxy listing

---

## 🎉 Summary

**To connect to a proxy by health score:**

1. ✅ Login to get token
2. ✅ Call `GET /proxy?strategy=health_score`
3. ✅ Use the proxy URL for web scraping
4. ✅ Handle errors and retry if needed

**The system automatically:**
- ✅ Calculates health scores
- ✅ Selects the best proxy
- ✅ Updates health scores periodically
- ✅ Excludes non-working proxies

---

**Ready to scrape! 🕷️**


