# Alternative Ways to Run the Server

## ✅ Fixed! Now try again:

```bash
./run_server.sh
```

---

## If you still get permission denied, try:

### Option 1: Use bash explicitly
```bash
bash run_server.sh
```

### Option 2: Run commands manually
```bash
source venv/bin/activate
python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: One-liner
```bash
source venv/bin/activate && python3 -m uvicorn proxy_manager.src.proxy_manager.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Quick Test:

After starting, open in browser:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## To Stop Server:
Press `Ctrl+C` in the terminal


