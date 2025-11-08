# ✅ SETUP COMPLETE! Here's how to run on YOUR system:

## 🚀 EASIEST WAY - Just Run:

```bash
./run_server.sh
```

This will:
- ✅ Activate virtual environment
- ✅ Start the server
- ✅ Show you the URLs

---

## 📝 MANUAL WAY:

### Step 1: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 2: Start Server
```bash
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Open Browser
Visit: **http://localhost:8000/docs**

---

## ✅ What's Already Done:
- ✅ Virtual environment created (`venv/`)
- ✅ Dependencies installed
- ✅ `.env` file created with secure tokens
- ✅ Run script created (`run_server.sh`)

---

## 🎯 Quick Commands:

**Start Server:**
```bash
./run_server.sh
```

**Or manually:**
```bash
source venv/bin/activate
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

**Stop Server:**
Press `Ctrl+C` in the terminal

**Check Health:**
```bash
curl http://localhost:8000/health
```

---

## 📍 Important URLs:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

---

## 🔧 If You Need to Reinstall:

```bash
# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
cd proxy_manager && pip install -e . && cd ..
cd mitm_forwarder && pip install -r requirements.txt && cd ..
```


