# How to Run on YOUR System (macOS)

## Your System Info:
- ✅ Python 3.13.2 installed
- ✅ pip3 available at /opt/homebrew/bin/pip3
- ✅ Project location: /Users/yadhukrishna/Downloads/capstone/CapProj
- ⚠️ Dependencies not installed yet
- ⚠️ .env file not created yet

---

## EASIEST WAY - Run This Script:

```bash
./setup_and_run.sh
```

This will automatically:
1. Install all dependencies
2. Create .env file with secure tokens
3. Show you how to start the server

---

## MANUAL WAY - Step by Step:

### Step 1: Install Dependencies

```bash
# Install proxy_manager
cd proxy_manager
pip3 install -e .
cd ..

# Install mitm_forwarder  
cd mitm_forwarder
pip3 install -r requirements.txt
cd ..
```

### Step 2: Create .env File

```bash
cd /Users/yadhukrishna/Downloads/capstone/CapProj

# Generate secure tokens
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
SYSTEM_TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Create .env file
cat > .env << EOF
TEST_URL=https://httpbin.org/ip
CHECK_INTERVAL=300
MAX_THREADS=20
ROTATION_STRATEGY=round_robin
DB_URL=sqlite:///./proxy_manager.db
SECRET_KEY=${SECRET_KEY}
SYSTEM_TOKEN=${SYSTEM_TOKEN}
EOF
```

### Step 3: Start the Server

```bash
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Open Browser

Visit: **http://localhost:8000/docs**

---

## Quick Commands Reference:

**Start Server:**
```bash
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

**Check if running:**
```bash
curl http://localhost:8000/health
```

**Stop Server:**
Press `Ctrl+C` in the terminal where server is running

---

## Troubleshooting:

**If you get "port already in use":**
```bash
# Find what's using port 8000
lsof -i :8000
# Kill it or use different port
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --port 8001
```

**If you get "Module not found":**
```bash
# Reinstall dependencies
cd proxy_manager && pip3 install -e . && cd ..
```


