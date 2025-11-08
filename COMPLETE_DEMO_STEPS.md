# 🎯 Complete Step-by-Step Demonstration

## ⚠️ Important: Register First!

The **401 Unauthorized** error means the user doesn't exist yet. You need to **register first**, then login.

---

## 📋 Complete Step-by-Step Guide

### STEP 1: Start Server

**Terminal 1:**
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
./run_server.sh
```

**Expected Output:**
```
🚀 Starting Proxy Manager Server...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Keep this terminal open!**

---

### STEP 2: Open API Documentation

**Browser:**
- Visit: **http://localhost:8000/docs**

---

### STEP 3: Register User (MUST DO FIRST!)

**In Swagger UI (http://localhost:8000/docs):**

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
5. **Expected Response:**
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

### STEP 4: Login to Get Token

**In Swagger UI:**

1. **Find** `POST /auth/login` endpoint
2. **Click** "Try it out"
3. **IMPORTANT:** Use **form data**, not JSON!
   - **username**: `demo_user`
   - **password**: `demo123456`
4. **Click** "Execute"
5. **Copy the `access_token`** from response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

**✅ Token obtained!**

---

### STEP 5: Authorize in Swagger UI

1. **Click** the green **"Authorize"** button (top right)
2. **Paste** your `access_token` in the "Value" field
3. **Click** "Authorize"
4. **Click** "Close"

**✅ Now all authenticated endpoints will work!**

---

### STEP 6: Add a Proxy

**In Swagger UI:**

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
   **Note:** Use a real proxy if you have one, or use a test proxy service.
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
     "latency": null
   }
   ```

**✅ Proxy added!**

---

### STEP 7: Test the Proxy

**In Swagger UI:**

1. **Find** `POST /proxies/{proxy_id}/test` endpoint
2. **Click** "Try it out"
3. **Enter** `proxy_id`: `1`
4. **Click** "Execute"
5. **See Response:**
   ```json
   {
     "proxy_id": 1,
     "success": true,
     "latency": 150.5,
     "status_code": 200
   }
   ```

**✅ Proxy tested!** Health score will be updated automatically.

---

### STEP 8: Get Best Proxy (Health Score)

**In Swagger UI:**

1. **Find** `GET /proxy` endpoint (under "proxy" section)
2. **Click** "Try it out"
3. **Set** `strategy`: `health_score`
4. **Click** "Execute"
5. **See Response:**
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
     "fail_count": 0
   }
   ```

**✅ Best proxy selected based on health score!**

---

### STEP 9: Connect to Proxy and Scrape (Python)

**Open Terminal 2** (keep Terminal 1 running):

**Create `demo.py`:**
```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # From Step 4
TARGET_URL = "https://httpbin.org/ip"

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
print(f"   Health Score: {proxy_data['health_score']:.2f}/100")
print(f"   Latency: {proxy_data.get('latency', 'N/A')}ms")
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
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run:**
```bash
python3 demo.py
```

**Replace** `YOUR_ACCESS_TOKEN_HERE` with your token from Step 4.

---

## 🔍 Common Issues & Solutions

### Issue 1: "401 Unauthorized" on Login
**Problem:** User doesn't exist  
**Solution:** Register first (Step 3)

### Issue 2: "Incorrect username or password"
**Problem:** Wrong credentials or user not registered  
**Solution:** 
- Make sure you registered first
- Use exact username/password from registration
- Check for typos

### Issue 3: "No working proxies available"
**Problem:** No proxies added or all proxies dead  
**Solution:** 
- Add at least one proxy (Step 6)
- Test the proxy (Step 7)
- Wait for automatic health checks (runs every 5 minutes)

### Issue 4: "Proxy connection failed"
**Problem:** Proxy not working  
**Solution:** 
- Use a real, working proxy
- Test proxy first (Step 7)
- Check proxy IP/port is correct

---

## 📝 Quick Reference Commands

### Register User:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "demo123456"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_user&password=demo123456"
```

### Add Proxy:
```bash
curl -X POST "http://localhost:8000/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ip": "192.168.1.100",
    "port": 8080,
    "protocol": "http"
  }'
```

### Get Best Proxy:
```bash
curl -X GET "http://localhost:8000/proxy?strategy=health_score" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Checklist

- [ ] Server running (`./run_server.sh`)
- [ ] API docs open (http://localhost:8000/docs)
- [ ] User registered (`POST /auth/register`)
- [ ] User logged in (`POST /auth/login`)
- [ ] Token copied
- [ ] Swagger UI authorized
- [ ] Proxy added (`POST /proxies`)
- [ ] Proxy tested (`POST /proxies/{id}/test`)
- [ ] Best proxy retrieved (`GET /proxy?strategy=health_score`)
- [ ] Request made through proxy (Python script)

---

## 🎯 For Your Presentation

**Flow:**
1. Show server running
2. Show API docs (http://localhost:8000/docs)
3. Register user → Show response
4. Login → Show token
5. Add proxy → Show response
6. Get best proxy → Show health score
7. Run Python script → Show web scraping through proxy

**Key Points:**
- Health score system (0-100)
- Automatic best proxy selection
- Easy integration
- Production-ready features

---

**Follow these steps in order, and everything will work!** 🚀

