# 🎯 Complete Demonstration Guide - Connect to Proxy & Web Scraping

## 📋 Prerequisites

- ✅ Server running (`./run_server.sh`)
- ✅ Terminal/Command Prompt open
- ✅ Browser (for API docs)
- ✅ Python installed (for scraping examples)

---

## 🚀 Step-by-Step Demonstration

### STEP 1: Start the Server

**Open Terminal 1:**

```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
./run_server.sh
```

**Expected Output:**
```
🚀 Starting Proxy Manager Server...
📍 Server: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Keep this terminal open!** The server must stay running.

---

### STEP 2: Open API Documentation

**Open Browser:**
- Visit: **http://localhost:8000/docs**

You should see the Swagger UI with all available endpoints.

---

### STEP 3: Register a User (First Time Only)

**In the Swagger UI (http://localhost:8000/docs):**

1. **Find** `POST /auth/register` endpoint (under "auth" section)
2. **Click** "Try it out"
3. **Enter** user details:
   ```json
   {
     "username": "demo_user",
     "email": "demo@example.com",
     "password": "demo123456"
   }
   ```
4. **Click** "Execute"
5. **See Response:**
   ```json
   {
     "id": 1,
     "username": "demo_user",
     "email": "demo@example.com",
     "role": "admin",
     "is_active": true,
     "created_at": "2024-..."
   }
   ```

**✅ User registered!** (First user automatically becomes admin)

---

### STEP 4: Login to Get JWT Token

**In the Swagger UI:**

1. **Find** `POST /auth/login` endpoint (under "auth" section)
2. **Click** "Try it out"
3. **IMPORTANT:** The login endpoint uses **form data**, not JSON!
   - You should see form fields (not a JSON editor)
   - Enter:
     - `username`: `demo_user`
     - `password`: `demo123456`
4. **Click** "Execute"
5. **Copy the `access_token`** from response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

**✅ Save this token!** You'll need it for all authenticated requests.

**⚠️ Note:** If you see a JSON editor instead of form fields, look for a dropdown or button to switch to "form" mode.

---

### STEP 5: Authorize in Swagger UI

**⚠️ IMPORTANT:** The "Authorize" button shows OAuth2 form (username/password fields), but **there's no "Value" field** to paste your token directly.

**✅ Solution: Skip Authorize Button, Use Manual Headers**

**For each endpoint that needs authentication:**

1. **Click** "Try it out" on any endpoint (e.g., `GET /proxy`)
2. **Scroll down** to see the request parameters
3. **Look for** "Authorization" or "Headers" section
4. **Add** the token manually:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer YOUR_ACCESS_TOKEN_HERE`
     - Replace `YOUR_ACCESS_TOKEN_HERE` with your token from Step 4
     - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
5. **Click** "Execute"

**✅ Now the request will work with authentication!**

**📖 See `AUTHORIZATION_FIX.md` for detailed instructions.**

---

### STEP 6: Add a Proxy

**Option A: Using Swagger UI (Easiest)**

1. **Find** `POST /proxies` endpoint (under "proxies" section)
2. **Click** "Try it out"
3. **Enter** proxy details:
   ```json
   {
     "ip": "192.168.1.100",
     "port": 8080,
     "protocol": "http"
   }
   ```
   **Note:** Use a real proxy IP if you have one, or use a test proxy service.
4. **Click** "Execute"
5. **See Response:**
   ```json
   {
     "id": 1,
     "ip": "192.168.1.100",
     "port": 8080,
     "address": "192.168.1.100:8080",
     "protocol": "http",
     "is_working": false,
     "health_score": 0.0,
     "latency": null,
     "fail_count": 0
   }
   ```

**Option B: Using curl (Terminal)**

**Open Terminal 2** (keep Terminal 1 running):

```bash
# Replace YOUR_ACCESS_TOKEN with token from Step 4
curl -X POST "http://localhost:8000/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "ip": "192.168.1.100",
    "port": 8080,
    "protocol": "http"
  }'
```

**✅ Proxy added!**

---

### STEP 7: Test the Proxy

**In Swagger UI:**

1. **Find** `POST /proxies/{proxy_id}/test` endpoint
2. **Click** "Try it out"
3. **Enter** `proxy_id`: `1` (or the ID from Step 6)
4. **Click** "Execute"
5. **See Response:**
   ```json
   {
     "proxy_id": 1,
     "success": true,
     "latency": 150.5,
     "status_code": 200,
     "error": null
   }
   ```

**✅ Proxy tested!** Health score will be updated automatically.

---

### STEP 8: Get Best Proxy by Health Score ⭐ MOST IMPORTANT!

**🎯 This is the KEY feature - selecting proxy based on health score!**

**In Swagger UI:**

1. **Find** `GET /proxy` endpoint (under "proxy" section)
2. **Click** "Try it out"
3. **Set** `strategy`: `health_score` (this selects the best proxy!)
4. **Add** Authorization header (from Step 5):
   - Header name: `Authorization`
   - Header value: `Bearer YOUR_ACCESS_TOKEN_HERE`
5. **Click** "Execute"
6. **See Response:**
   ```json
   {
     "id": 1,
     "ip": "192.168.1.100",
     "port": 8080,
     "address": "192.168.1.100:8080",
     "protocol": "http",
     "is_working": true,
     "health_score": 85.5,
     "latency": 150.5,
     "fail_count": 0,
     "last_checked": "2024-..."
   }
   ```

**✅ Best proxy selected based on health score!**

**📊 Health Score Explained:**
- **0-100 rating** that considers:
  - ✅ Working status (40 points)
  - ✅ Latency (30 points) - lower is better
  - ✅ Failure count (20 points) - lower is better
  - ✅ Recency of check (10 points) - newer is better
- **Higher score = Better proxy**
- **Always use `strategy=health_score` for best results!**

**Using curl:**
```bash
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Accept: application/json"
```

**📖 See `WORKING_WEB_SCRAPING.md` for complete web scraping guide!**

---

### STEP 9: Connect to Proxy and Make Request (Python)

**Open Terminal 2** (or new terminal):

**Create a file `demo_scraping.py`:**

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # Replace with your token from Step 4
TARGET_URL = "https://httpbin.org/ip"  # Test URL

print("=" * 60)
print("PROXY MANAGER DEMONSTRATION")
print("=" * 60)
print()

# Step 1: Get best proxy
print("📡 Step 1: Getting best proxy (health score)...")
response = requests.get(
    f"{API_URL}/proxy?strategy=health_score",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
)
response.raise_for_status()
proxy_data = response.json()

print(f"✅ Proxy Selected:")
print(f"   Address: {proxy_data['address']}")
print(f"   Protocol: {proxy_data['protocol']}")
print(f"   Health Score: {proxy_data['health_score']:.2f}/100")
print(f"   Latency: {proxy_data.get('latency', 'N/A')}ms")
print(f"   Status: {'Working' if proxy_data['is_working'] else 'Not Working'}")
print()

# Step 2: Build proxy URL
if proxy_data.get('username') and proxy_data.get('password'):
    proxy_url = f"{proxy_data['protocol']}://{proxy_data['username']}:{proxy_data['password']}@{proxy_data['address']}"
else:
    proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

print("🔗 Step 2: Connecting through proxy...")
print(f"   Proxy URL: {proxy_url}")
print()

# Step 3: Make request through proxy
print("🌐 Step 3: Making request through proxy...")
print(f"   Target URL: {TARGET_URL}")
print()

try:
    response = requests.get(
        TARGET_URL,
        proxies=proxies,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    response.raise_for_status()
    
    print("✅ SUCCESS! Request completed through proxy")
    print()
    print("📊 Response Details:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response Time: {response.elapsed.total_seconds():.2f} seconds")
    print()
    print("📄 Response Content:")
    print(json.dumps(response.json(), indent=2))
    print()
    print("=" * 60)
    print("✅ DEMONSTRATION COMPLETE!")
    print("=" * 60)
    
except requests.exceptions.ProxyError as e:
    print(f"❌ Proxy Error: {e}")
    print("   The proxy might not be working. Try adding a different proxy.")
except requests.exceptions.Timeout:
    print("❌ Request Timeout")
    print("   The proxy might be slow or unreachable.")
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run the script:**
```bash
# Replace YOUR_ACCESS_TOKEN with your actual token
python3 demo_scraping.py
```

**Expected Output:**
```
============================================================
PROXY MANAGER DEMONSTRATION
============================================================

📡 Step 1: Getting best proxy (health score)...
✅ Proxy Selected:
   Address: 192.168.1.100:8080
   Protocol: http
   Health Score: 85.50/100
   Latency: 150.5ms
   Status: Working

🔗 Step 2: Connecting through proxy...
   Proxy URL: http://192.168.1.100:8080

🌐 Step 3: Making request through proxy...
   Target URL: https://httpbin.org/ip

✅ SUCCESS! Request completed through proxy

📊 Response Details:
   Status Code: 200
   Response Time: 0.25 seconds

📄 Response Content:
{
  "origin": "192.168.1.100"
}

============================================================
✅ DEMONSTRATION COMPLETE!
============================================================
```

---

### STEP 10: Advanced Demonstration - Web Scraping

**Create `demo_web_scraping.py`:**

```python
import requests
from bs4 import BeautifulSoup
import time

API_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

def get_best_proxy():
    """Get proxy with highest health score."""
    response = requests.get(
        f"{API_URL}/proxy?strategy=health_score",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    response.raise_for_status()
    return response.json()

def scrape_with_proxy(url):
    """Scrape a URL using the best proxy."""
    # Get best proxy
    proxy_data = get_best_proxy()
    print(f"🔄 Using proxy: {proxy_data['address']} (Health: {proxy_data['health_score']:.1f}/100)")
    
    # Build proxy
    proxy_url = f"{proxy_data['protocol']}://{proxy_data['address']}"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    # Scrape
    response = requests.get(
        url,
        proxies=proxies,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    response.raise_for_status()
    
    return response.text, proxy_data

# Demonstration
print("=" * 60)
print("WEB SCRAPING DEMONSTRATION")
print("=" * 60)
print()

# Example 1: Scrape httpbin.org/ip
print("📡 Example 1: Getting IP through proxy...")
html, proxy = scrape_with_proxy("https://httpbin.org/ip")
print(f"✅ Response received through proxy {proxy['address']}")
print(f"   Your IP: {html}")
print()

# Example 2: Scrape a real website
print("📡 Example 2: Scraping example.com...")
html, proxy = scrape_with_proxy("https://example.com")
soup = BeautifulSoup(html, 'html.parser')
title = soup.find('title')
print(f"✅ Page scraped successfully!")
print(f"   Page Title: {title.text if title else 'Not found'}")
print(f"   Proxy Used: {proxy['address']}")
print(f"   Health Score: {proxy['health_score']:.1f}/100")
print()

print("=" * 60)
print("✅ DEMONSTRATION COMPLETE!")
print("=" * 60)
```

**Run:**
```bash
python3 demo_web_scraping.py
```

---

### STEP 11: View Proxy Statistics

**In Swagger UI:**

1. **Find** `GET /health/proxies` endpoint
2. **Click** "Try it out"
3. **Click** "Execute"
4. **See Response:**
   ```json
   {
     "total": 1,
     "working": 1,
     "dead": 0,
     "statistics": {
       "total": 1,
       "working": 1,
       "dead": 0,
       "average_latency_ms": 150.5,
       "min_latency_ms": 150.5,
       "max_latency_ms": 150.5
     }
   }
   ```

**Using curl:**
```bash
curl -X GET "http://localhost:8000/health/proxies" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎤 Complete Demonstration Script

### For Live Presentation:

**1. Start Server (Terminal 1)**
```bash
./run_server.sh
```

**2. Open Browser**
- http://localhost:8000/docs

**3. Show Registration (if needed)**
- Register user → Show response

**4. Show Login**
- Login → Show access_token

**5. Show Proxy Addition**
- Add proxy → Show response with health_score

**6. Show Proxy Testing**
- Test proxy → Show latency and status

**7. Show Health Score Selection**
- Get proxy with `strategy=health_score` → Show health_score in response

**8. Show Web Scraping (Python)**
- Run `demo_scraping.py` → Show successful request through proxy

**9. Show Statistics**
- View `/health/proxies` → Show pool statistics

---

## 📊 Demonstration Checklist

- [ ] Server running
- [ ] API docs open (http://localhost:8000/docs)
- [ ] User registered
- [ ] User logged in (token obtained)
- [ ] Swagger UI authorized
- [ ] Proxy added
- [ ] Proxy tested
- [ ] Best proxy retrieved (health_score)
- [ ] Request made through proxy
- [ ] Statistics viewed

---

## 🎯 Key Points to Highlight

1. **Health Score System**: Show how health_score (0-100) is calculated
2. **Automatic Selection**: Best proxy selected automatically
3. **Real-time Monitoring**: Health checks update scores
4. **Easy Integration**: Simple API calls
5. **Production-Ready**: Authentication, logging, rate limiting

---

## 🆘 Troubleshooting

### "No working proxies available"
- Add more proxies
- Wait for health checks to complete (runs every 5 minutes)
- Test proxies manually

### "401 Unauthorized"
- Make sure you're logged in
- Check token is valid
- Re-login if token expired

### "Proxy connection failed"
- Verify proxy IP/port is correct
- Check proxy is actually working
- Try a different proxy

---

## 📝 Quick Reference Commands

```bash
# Get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"

# Add proxy
curl -X POST "http://localhost:8000/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"ip": "192.168.1.100", "port": 8080, "protocol": "http"}'

# Get best proxy
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer TOKEN"

# View statistics
curl -X GET "http://localhost:8000/health/proxies" \
  -H "Authorization: Bearer TOKEN"
```

---

**Ready to demonstrate! Follow the steps above for a complete walkthrough.** 🚀

