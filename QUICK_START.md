# Step-by-Step Guide to Run the Project

## Prerequisites Check
- ✅ Python 3.13+ installed (check with `python3 --version`)
- ✅ Terminal/Command Prompt open
- ✅ Project folder: `/Users/yadhukrishna/Downloads/capstone/CapProj`

---

## PART 1: Setup Proxy Manager (FastAPI Backend)

### Step 1: Open Terminal and Navigate to Project
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
```

### Step 2: Check Python Version
```bash
python3 --version
```
**Expected:** Python 3.13.x or higher

### Step 3: Install Dependencies

**Option A: Using uv (Recommended if installed)**
```bash
uv sync
```

**Option B: Using pip**
```bash
# Install proxy_manager dependencies
cd proxy_manager
pip install -e .
cd ..

# Install mitm_forwarder dependencies  
cd mitm_forwarder
pip install -r requirements.txt
cd ..
```

### Step 4: Create Environment File for Proxy Manager
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
cat > .env << 'EOF'
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
SECRET_KEY=your-secret-key-change-this-in-production
SYSTEM_TOKEN=your-system-token-change-this-in-production
EOF
```

**Or manually create `.env` file** in the root directory with:
```
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
SECRET_KEY=your-secret-key-change-this-in-production
SYSTEM_TOKEN=your-system-token-change-this-in-production
```

### Step 5: Start Proxy Manager Server

**Option A: Using uvicorn directly (if installed globally)**
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using Python module syntax**
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: If using uv workspace**
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
uv run uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Verify Backend is Running
Open your browser and visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "message": "Proxy manager is running"
}
```

**✅ Keep this terminal window open!** The server must stay running.

---

## PART 2: Setup mitm_forwarder (Optional - Only if you need proxy forwarding)

### Step 7: Open a NEW Terminal Window
Keep the first terminal running the backend, open a second terminal.

### Step 8: Navigate to Project Again
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj/mitm_forwarder
```

### Step 9: Create Environment File for mitm_forwarder
```bash
cat > .env << 'EOF'
SYSTEM_TOKEN=your-system-token-change-this-in-production
FASTAPI_BASE_URL=http://127.0.0.1:8000
BLACKLIST_REFRESH_SECONDS=60
HTTPX_TIMEOUT=30.0
MITM_LISTEN_PORT=8080
MAX_CONCURRENT_REQUESTS=100
REQUIRE_USER_JWT=true
EOF
```

**⚠️ IMPORTANT:** Use the SAME `SYSTEM_TOKEN` as in Step 4!

### Step 10: Start mitmproxy Forwarder
```bash
mitmdump -s src/mitm_forwarder/mitm_forwarder_addon.py -p 8080
```

**Expected Output:**
```
Loading script src/mitm_forwarder/mitm_forwarder_addon.py
Proxy server listening at http://*:8080
```

**✅ Keep this terminal window open too!**

---

## PART 3: Test the System

### Step 11: Register a User (Get JWT Token)

Open a THIRD terminal or use a tool like Postman/curl:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-..."
}
```

### Step 12: Login to Get JWT Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copy the `access_token` value!**

### Step 13: Add a Proxy

```bash
curl -X POST "http://localhost:8000/proxies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "ip": "192.168.1.100",
    "port": 8080,
    "protocol": "http"
  }'
```

Replace `YOUR_ACCESS_TOKEN_HERE` with the token from Step 12.

### Step 14: Get a Proxy (Test Rotation)

```bash
curl -X GET "http://localhost:8000/proxy?strategy=random" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Step 15: Test mitm_forwarder (If Running)

```bash
curl -x http://localhost:8080 https://httpbin.org/ip \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Quick Reference Commands

### Start Proxy Manager:
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

### Start mitm_forwarder:
```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj/mitm_forwarder
mitmdump -s src/mitm_forwarder/mitm_forwarder_addon.py -p 8080
```

### View API Documentation:
Open browser: http://localhost:8000/docs

### Check Health:
```bash
curl http://localhost:8000/health
```

---

## Troubleshooting

### Problem: "Module not found" error
**Solution:** Make sure you installed dependencies (Step 3)

### Problem: "Port 8000 already in use"
**Solution:** 
```bash
# Find what's using port 8000
lsof -i :8000
# Kill it or use a different port
uvicorn proxy_manager.src.proxy_manager.main:app --reload --port 8001
```

### Problem: "SYSTEM_TOKEN" error in mitm_forwarder
**Solution:** Make sure `.env` file in `mitm_forwarder` directory has `SYSTEM_TOKEN` matching the one in root `.env`

### Problem: "No working proxies available"
**Solution:** Add at least one proxy first (Step 13)

### Problem: "401 Unauthorized"
**Solution:** Make sure you're using a valid JWT token from login (Step 12)

---

## What's Running?

- **Terminal 1:** Proxy Manager (FastAPI) on port 8000
- **Terminal 2:** mitm_forwarder (mitmproxy) on port 8080 (optional)
- **Browser:** API docs at http://localhost:8000/docs

---

## Next Steps

1. ✅ Backend is running
2. ✅ User registered and logged in
3. ✅ Proxy added
4. 📝 Explore API endpoints at http://localhost:8000/docs
5. 📝 Add more proxies
6. 📝 Test different rotation strategies
7. 📝 Set up blacklist rules
8. 📝 View activity logs

---

**Need Help?** Check the main README.md files in each directory for detailed API documentation.

